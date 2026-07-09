import streamlit as st
import pandas as pd
import altair as alt
from data import load_ps_history, _scope_key
from components import section_banner, empty_state, tab_tip

# ── Fiscal calendar helpers ─────────────────────────────────────────────────
# Snowflake fiscal year starts Feb 1. FY26 = Feb 2025 → Jan 2026.
# Fiscal month index: Feb=1 … Jan=12.
_FM_ORDER = ["Feb", "Mar", "Apr", "May", "Jun", "Jul", "Aug", "Sep", "Oct", "Nov", "Dec", "Jan"]

# Metric name → (source column | "__COUNT__", is_dollar)
# Education Services excluded — Professional (Technical) Services only.
_METRICS = {
    "PS Services $":  ("PS_SERVICES_ACV", True),
    "Deals Sold (#)": ("__COUNT__",       False),
}

# Fiscal-year line colors (oldest → light, newest → dark Snowflake blue)
_FY_PALETTE = ["#CBD5E1", "#94A3B8", "#29B5E8", "#0284C7", "#0C4A6E"]
_DISTRICT_PALETTE = ["#0284C7", "#29B5E8", "#0C4A6E", "#16A34A", "#D97706",
                     "#9333EA", "#DC2626", "#0891B2", "#65A30D", "#DB2777"]


def _fmt(v, is_dollar):
    if pd.isna(v):
        return "—"
    return f"${v:,.0f}" if is_dollar else f"{int(round(v)):,}"


def _prep(df):
    """Add fiscal year / fiscal month columns off CLOSE_DATE."""
    df = df.copy()
    df["CLOSE_DATE"] = pd.to_datetime(df["CLOSE_DATE"], errors="coerce")
    df = df.dropna(subset=["CLOSE_DATE"])
    if df.empty:
        return df
    m = df["CLOSE_DATE"].dt.month
    y = df["CLOSE_DATE"].dt.year
    df["FY_NUM"] = (y + (m >= 2).astype(int)).astype(int)          # e.g. 2026
    df["FY_LABEL"] = "FY" + (df["FY_NUM"] % 100).astype(str).str.zfill(2)
    df["FM_IDX"] = (((m - 2) % 12) + 1).astype(int)                # Feb→1 … Jan→12
    df["FM_LABEL"] = df["FM_IDX"].map(lambda i: _FM_ORDER[i - 1])
    return df


def _aggregate(frame, group_cols, source_col):
    if source_col == "__COUNT__":
        g = frame.groupby(group_cols)["OPPORTUNITY_ID"].nunique().reset_index(name="VALUE")
    else:
        g = frame.groupby(group_cols)[source_col].sum().reset_index().rename(columns={source_col: "VALUE"})
    return g


def _fill_months(g, series_col, series_vals):
    """Ensure every (series, fiscal-month) cell exists; missing sales = 0 so lines are continuous."""
    idx = pd.MultiIndex.from_product([series_vals, range(1, 13)], names=[series_col, "FM_IDX"])
    g = g.set_index([series_col, "FM_IDX"]).reindex(idx, fill_value=0).reset_index()
    g["FM_LABEL"] = g["FM_IDX"].map(lambda i: _FM_ORDER[i - 1])
    return g


def _make_chart(g, chart_type, series_col, series_sort, series_title, color_scale,
                y_title, metric_name, is_dollar):
    """Build a grouped-bar or line chart with x = fiscal month, series = series_col."""
    y_axis = alt.Axis(format="$,.0f") if is_dollar else alt.Axis(format=",d")
    tip_fmt = "$,.0f" if is_dollar else ",d"
    enc = dict(
        x=alt.X("FM_LABEL:N", sort=_FM_ORDER, title="Fiscal Month"),
        y=alt.Y("VALUE:Q", title=y_title, axis=y_axis),
        color=alt.Color(f"{series_col}:N", title=series_title, scale=color_scale, sort=series_sort),
        tooltip=[
            alt.Tooltip(f"{series_col}:N", title=series_title),
            alt.Tooltip("FM_LABEL:N", title="Month"),
            alt.Tooltip("VALUE:Q", title=metric_name, format=tip_fmt),
        ],
    )
    base = alt.Chart(g)
    if chart_type == "Bars":
        return base.mark_bar().encode(
            xOffset=alt.XOffset(f"{series_col}:N", sort=series_sort), **enc
        ).properties(height=420)
    return base.mark_line(point=True, strokeWidth=2.5).encode(**enc).properties(height=420)


def _render_fy_overlay(frame, sel_fys, metric_name, source_col, is_dollar,
                       all_fys, chart_type, key_suffix, csv_name):
    """YoY overlay: one line per fiscal year (x = fiscal month). `frame` is
    pre-filtered by the caller (all scope, or a single district)."""
    if not sel_fys:
        empty_state("Select at least one fiscal year to plot.")
        return
    fsub = frame[frame["FY_LABEL"].isin(sel_fys)]
    if fsub.empty:
        empty_state("No closed-won PS&T for the selected fiscal years / filters.")
        return
    g = _fill_months(_aggregate(fsub, ["FY_LABEL", "FM_IDX"], source_col), "FY_LABEL", sel_fys)

    # KPI cards: full-FY total per selected fiscal year (+ YoY delta vs prior FY)
    totals = {fy: g[g["FY_LABEL"] == fy]["VALUE"].sum() for fy in sel_fys}
    kcols = st.columns(min(len(sel_fys), 4))
    for i, fy in enumerate(sel_fys[-4:]):
        delta = None
        idx = all_fys.index(fy)
        if idx > 0 and all_fys[idx - 1] in totals:
            prior = totals[all_fys[idx - 1]]
            if prior:
                delta = f"{(totals[fy] - prior) / prior * 100:+.0f}% YoY"
        kcols[i].metric(f"{fy} · {metric_name}", _fmt(totals[fy], is_dollar), delta=delta)

    _fy_scale = alt.Scale(domain=sel_fys, range=_FY_PALETTE[-len(sel_fys):])
    chart = _make_chart(g, chart_type, "FY_LABEL", sel_fys, "Fiscal Year",
                        _fy_scale, metric_name, metric_name, is_dollar)
    st.altair_chart(chart, use_container_width=True)

    piv = g.pivot_table(index="FY_LABEL", columns="FM_IDX", values="VALUE", aggfunc="sum", fill_value=0)
    piv = piv.reindex(columns=range(1, 13), fill_value=0)
    piv.columns = _FM_ORDER
    piv = piv.reindex(sel_fys)
    piv["Total"] = piv.sum(axis=1)
    with st.expander("Data table (fiscal year × month)", expanded=False):
        fmt_map = {c: ("${:,.0f}" if is_dollar else "{:,.0f}") for c in piv.columns}
        st.dataframe(piv.style.format(fmt_map), use_container_width=True)
        st.download_button(
            ":material/download: Export CSV", piv.to_csv(),
            csv_name, "text/csv", key=f"trend_csv_{key_suffix}",
        )


# ── Load & prep ─────────────────────────────────────────────────────────────
_hist = _prep(load_ps_history(_scope=_scope_key()))
# Exclude Education Services: keep only opps that sold Professional (Technical)
# Services. This drops education-only deals from counts and $.
if not _hist.empty and "PRODUCT_FAMILIES" in _hist.columns:
    _hist = _hist[
        _hist["PRODUCT_FAMILIES"].fillna("").str.contains("Technical Services")
    ].reset_index(drop=True)

section_banner(
    "Sales Data Reports",
    "Year-over-year monthly trend of closed-won Professional (Technical) Services",
)

if _hist.empty:
    empty_state("No closed-won PS&T history found for the selected scope.")
else:
    tab_tip(
        "Trends use **Snowflake fiscal years** (FY starts Feb 1 — e.g. **FY26 = Feb 2025 → Jan 2026**) "
        "and are grouped by fiscal month (Feb…Jan). Each line is one fiscal year so you can compare the "
        "same month across years. Months with no closed-won deals show as **0**. "
        "Data is closed-won opportunities that sold **Technical Services**, scoped to your "
        "sidebar selection.",
        title="How to read this tab",
    )

    _all_fys = sorted(_hist["FY_LABEL"].unique())            # e.g. ['FY23','FY24','FY25','FY26']
    _default_fys = _all_fys[-3:]                             # last 3 fiscal years
    _districts_in_scope = sorted(_hist["DISTRICT_NAME"].dropna().unique())
    _multi_district = len(_districts_in_scope) > 1

    # ── Controls ──────────────────────────────────────────────────────────
    c1, c2, c3 = st.columns([1.2, 1.6, 1.0])
    with c1:
        metric_name = st.selectbox("Metric", list(_METRICS.keys()), index=0, key="trend_metric")
    source_col, is_dollar = _METRICS[metric_name]

    with c2:
        if _multi_district:
            view_mode = st.radio(
                "District view",
                ["Aggregate (YoY)", "By District (single FY)", "Single District (YoY)"],
                horizontal=True, key="trend_view_mode",
            )
        else:
            view_mode = "Aggregate (YoY)"
            st.caption(f"District: **{_districts_in_scope[0] if _districts_in_scope else '—'}**")

    with c3:
        chart_type = st.radio("Chart", ["Bars", "Line"], horizontal=True, key="trend_chart_type")

    frame = _hist

    # ── Chart ────────────────────────────────────────────────────────────
    if view_mode == "Aggregate (YoY)":
        sel_fys = st.multiselect(
            "Fiscal years to overlay", _all_fys, default=_default_fys, key="trend_fys",
        )
        _render_fy_overlay(
            frame, sel_fys, metric_name, source_col, is_dollar,
            _all_fys, chart_type, "agg", "pst_sales_trends.csv",
        )

    elif view_mode == "Single District (YoY)":
        sc1, sc2 = st.columns([1, 2])
        with sc1:
            sel_district = st.selectbox("District", _districts_in_scope, index=0, key="trend_one_district")
        with sc2:
            sel_fys = st.multiselect(
                "Fiscal years to overlay", _all_fys, default=_default_fys, key="trend_fys_one",
            )
        st.caption(f"Year-over-year trend for **{sel_district}**.")
        _dframe = frame[frame["DISTRICT_NAME"] == sel_district]
        _safe = "".join(ch if ch.isalnum() else "_" for ch in str(sel_district))[:40]
        _render_fy_overlay(
            _dframe, sel_fys, f"{metric_name} · {sel_district}", source_col, is_dollar,
            _all_fys, chart_type, "one_district", f"pst_sales_trends_{_safe}_yoy.csv",
        )

    else:  # By District — one line per district within a single fiscal year
        dc1, dc2 = st.columns([1, 2])
        with dc1:
            sel_fy = st.selectbox("Fiscal year", _all_fys, index=len(_all_fys) - 1, key="trend_fy_single")
        with dc2:
            sel_districts = st.multiselect(
                "Districts", _districts_in_scope, default=_districts_in_scope[:6], key="trend_districts",
            )
        st.caption("Comparing districts within a single fiscal year. Switch metric or year above.")

        if not sel_districts:
            empty_state("Select at least one district to plot.")
        else:
            fsub = frame[(frame["FY_LABEL"] == sel_fy) & (frame["DISTRICT_NAME"].isin(sel_districts))]
            if fsub.empty:
                empty_state(f"No {sel_fy} closed-won PS&T for the selected districts.")
            else:
                g = _fill_months(
                    _aggregate(fsub, ["DISTRICT_NAME", "FM_IDX"], source_col),
                    "DISTRICT_NAME", sel_districts,
                )

                totals = {d: g[g["DISTRICT_NAME"] == d]["VALUE"].sum() for d in sel_districts}
                _top = sorted(totals.items(), key=lambda kv: kv[1], reverse=True)[:4]
                kcols = st.columns(len(_top))
                for i, (d, v) in enumerate(_top):
                    kcols[i].metric(f"{d} · {sel_fy}", _fmt(v, is_dollar))

                _d_scale = alt.Scale(domain=sel_districts, range=_DISTRICT_PALETTE[:len(sel_districts)])
                chart = _make_chart(g, chart_type, "DISTRICT_NAME", sel_districts, "District",
                                    _d_scale, f"{metric_name} · {sel_fy}", metric_name, is_dollar)
                st.altair_chart(chart, use_container_width=True)

                piv = g.pivot_table(index="DISTRICT_NAME", columns="FM_IDX", values="VALUE", aggfunc="sum", fill_value=0)
                piv = piv.reindex(columns=range(1, 13), fill_value=0)
                piv.columns = _FM_ORDER
                piv["Total"] = piv.sum(axis=1)
                with st.expander(f"Data table ({sel_fy} · district × month)", expanded=False):
                    fmt_map = {c: ("${:,.0f}" if is_dollar else "{:,.0f}") for c in piv.columns}
                    st.dataframe(piv.style.format(fmt_map), use_container_width=True)
                    st.download_button(
                        ":material/download: Export CSV", piv.to_csv(),
                        f"pst_sales_trends_{sel_fy}_by_district.csv", "text/csv", key="trend_csv_dist",
                    )
