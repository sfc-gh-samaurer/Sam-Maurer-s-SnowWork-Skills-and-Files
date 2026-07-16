import streamlit as st
import pandas as pd
import altair as alt
from data import load_ps_history, _scope_key
from components import section_banner, empty_state, tab_tip

# ── Fiscal calendar helpers ─────────────────────────────────────────────────
# Snowflake fiscal year starts Feb 1. FY27 = Feb 2026 → Jan 2027.
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
    if pd.isna(v) or v is None:
        return "—"
    if is_dollar:
        if abs(v) >= 1_000_000:
            return f"${v/1_000_000:.1f}M"
        return f"${v:,.0f}"
    return f"{int(round(v)):,}"


def _fmt_full(v, is_dollar):
    """Full precision for tables."""
    if pd.isna(v) or v is None:
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
    df["FY_NUM"] = (y + (m >= 2).astype(int)).astype(int)
    df["FY_LABEL"] = "FY" + (df["FY_NUM"] % 100).astype(str).str.zfill(2)
    df["FM_IDX"] = (((m - 2) % 12) + 1).astype(int)
    df["FM_LABEL"] = df["FM_IDX"].map(lambda i: _FM_ORDER[i - 1])
    return df


def _aggregate(frame, group_cols, source_col):
    if source_col == "__COUNT__":
        g = frame.groupby(group_cols)["OPPORTUNITY_ID"].nunique().reset_index(name="VALUE")
    else:
        g = frame.groupby(group_cols)[source_col].sum().reset_index().rename(columns={source_col: "VALUE"})
    return g


def _fill_months(g, series_col, series_vals):
    """Ensure every (series, fiscal-month) cell exists; missing = 0 for continuous lines."""
    idx = pd.MultiIndex.from_product([series_vals, range(1, 13)], names=[series_col, "FM_IDX"])
    g = g.set_index([series_col, "FM_IDX"]).reindex(idx, fill_value=0).reset_index()
    g["FM_LABEL"] = g["FM_IDX"].map(lambda i: _FM_ORDER[i - 1])
    return g


def _make_chart(g, chart_type, series_col, series_sort, series_title, color_scale,
                y_title, metric_name, is_dollar):
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
        ).properties(height=380)
    return base.mark_line(point=True, strokeWidth=2.5).encode(**enc).properties(height=380)


def _current_fy_fm(hist):
    """Return (current_fy_label, current_max_fm_idx) based on the most recent data."""
    if hist.empty:
        return None, 12
    latest_fy = hist.sort_values("FY_NUM")["FY_LABEL"].iloc[-1]
    max_fm = int(hist[hist["FY_LABEL"] == latest_fy]["FM_IDX"].max())
    return latest_fy, max_fm


def _render_aggregate_section(frame, sel_fys, metric_name, source_col, is_dollar,
                               all_fys, chart_type, pacing_on, cur_fy, cur_fm):
    """Section 1: aggregate YoY trend with optional YTD pacing."""
    if not sel_fys:
        empty_state("Select at least one fiscal year to plot.")
        return

    # Apply pacing: cap prior FYs at cur_fm so comparison is apples-to-apples
    if pacing_on and cur_fy in sel_fys:
        display_frame = frame[
            (frame["FY_LABEL"] == cur_fy) |
            ((frame["FY_LABEL"] != cur_fy) & (frame["FM_IDX"] <= cur_fm))
        ]
    else:
        display_frame = frame[frame["FY_LABEL"].isin(sel_fys)]

    display_frame = display_frame[display_frame["FY_LABEL"].isin(sel_fys)]

    if display_frame.empty:
        empty_state("No closed-won PS&T for the selected fiscal years.")
        return

    g = _fill_months(_aggregate(display_frame, ["FY_LABEL", "FM_IDX"], source_col), "FY_LABEL", sel_fys)

    # KPI cards — YTD comparison when pacing is on
    totals = {fy: g[g["FY_LABEL"] == fy]["VALUE"].sum() for fy in sel_fys}
    kcols = st.columns(min(len(sel_fys), 4))
    for i, fy in enumerate(sel_fys[-4:]):
        val = totals.get(fy, 0)
        delta_str = None
        idx = all_fys.index(fy) if fy in all_fys else -1
        prior_fy = all_fys[idx - 1] if idx > 0 else None
        if prior_fy and prior_fy in sel_fys:
            prior_val = totals.get(prior_fy, 0)
            if prior_val:
                pct = (val - prior_val) / prior_val * 100
                delta_str = f"{pct:+.0f}% vs {prior_fy}"
                if pacing_on and fy == cur_fy:
                    delta_str += f" (FM1–FM{cur_fm})"
        label = f"{fy} {'YTD' if (pacing_on and fy == cur_fy) else 'Total'} · {metric_name}"
        kcols[i].metric(label, _fmt(val, is_dollar), delta=delta_str)

    # Chart
    _fy_scale = alt.Scale(domain=sel_fys, range=_FY_PALETTE[-len(sel_fys):])
    chart = _make_chart(g, chart_type, "FY_LABEL", sel_fys, "Fiscal Year",
                        _fy_scale, metric_name, metric_name, is_dollar)

    # Add vertical "current month" rule if pacing is on
    if pacing_on and cur_fy in sel_fys:
        cur_month_label = _FM_ORDER[cur_fm - 1]
        rule_df = pd.DataFrame({"FM_LABEL": [cur_month_label]})
        rule = (
            alt.Chart(rule_df)
            .mark_rule(strokeDash=[6, 4], color="#64748B", strokeWidth=1.5)
            .encode(x=alt.X("FM_LABEL:N", sort=_FM_ORDER))
        )
        chart = (chart + rule).resolve_scale(color="independent")

    st.altair_chart(chart, use_container_width=True)

    # Data table
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
            "pst_sales_trends.csv", "text/csv", key="trend_csv_agg",
        )


def _render_district_scorecard(frame, all_fys, sel_fys, source_col, is_dollar,
                                metric_name, cur_fy, cur_fm, pacing_on):
    """Section 2: district scorecard — all districts × selected FYs with YoY%."""
    districts = sorted(frame["DISTRICT_NAME"].dropna().unique())
    if not districts:
        return

    # Build YTD-paced totals per district per FY
    rows = []
    for dist in districts:
        dframe = frame[frame["DISTRICT_NAME"] == dist]
        row = {"District": dist}
        for fy in sel_fys:
            fyf = dframe[dframe["FY_LABEL"] == fy]
            if pacing_on and fy == cur_fy:
                # current FY: all months up to cur_fm (already filtered by definition)
                val = _aggregate(fyf[fyf["FM_IDX"] <= cur_fm], ["FY_LABEL"], source_col)
            else:
                val = _aggregate(fyf, ["FY_LABEL"], source_col)
            row[fy] = float(val["VALUE"].sum()) if not val.empty else 0.0

        # YoY vs prior FY — always apples-to-apples (cap prior at cur_fm)
        if len(sel_fys) >= 2 and cur_fy in sel_fys:
            cur_idx = sel_fys.index(cur_fy)
            if cur_idx > 0:
                prior_fy = sel_fys[cur_idx - 1]
                prior_capped = dframe[
                    (dframe["FY_LABEL"] == prior_fy) & (dframe["FM_IDX"] <= cur_fm)
                ]
                prior_val_agg = _aggregate(prior_capped, ["FY_LABEL"], source_col)
                prior_val = float(prior_val_agg["VALUE"].sum()) if not prior_val_agg.empty else 0.0
                cur_val = row.get(cur_fy, 0.0)
                row[f"{prior_fy} (FM1–{cur_fm})"] = prior_val
                if prior_val > 0:
                    row["YoY %"] = (cur_val - prior_val) / prior_val * 100
                elif cur_val > 0:
                    row["YoY %"] = 100.0
                else:
                    row["YoY %"] = None
            else:
                row["YoY %"] = None
        else:
            row["YoY %"] = None

        rows.append(row)

    score_df = pd.DataFrame(rows)
    if score_df.empty:
        return

    # Sort control — user picks which FY to rank by
    fy_sort_options = [c for c in sel_fys if c in score_df.columns]
    _default_sort = cur_fy if cur_fy in fy_sort_options else (fy_sort_options[-1] if fy_sort_options else None)
    if len(fy_sort_options) > 1:
        sort_col = st.selectbox(
            "Rank districts by",
            fy_sort_options,
            index=fy_sort_options.index(_default_sort) if _default_sort in fy_sort_options else len(fy_sort_options) - 1,
            key="scorecard_sort_by",
        )
    else:
        sort_col = _default_sort or (sel_fys[-1] if sel_fys else None)

    if sort_col and sort_col in score_df.columns:
        score_df = score_df.sort_values(sort_col, ascending=False).reset_index(drop=True)

    # Ranked bar chart
    if sort_col and sort_col in score_df.columns:
        bar_df = score_df[score_df[sort_col] != 0][["District", sort_col]].copy()
        if not bar_df.empty:
            _y_order = bar_df.sort_values(sort_col, ascending=False)["District"].tolist()
            _ax = alt.Axis(format="$,.0f") if is_dollar else alt.Axis(format=",d")
            _tip_fmt = "$,.0f" if is_dollar else ",d"
            _bar = (
                alt.Chart(bar_df)
                .mark_bar()
                .encode(
                    y=alt.Y("District:N", sort=_y_order, title=None),
                    x=alt.X(f"{sort_col}:Q", title=f"{sort_col} · {metric_name}", axis=_ax),
                    color=alt.value("#0284C7"),
                    tooltip=[
                        alt.Tooltip("District:N", title="District"),
                        alt.Tooltip(f"{sort_col}:Q", title=metric_name, format=_tip_fmt),
                    ],
                )
                .properties(height=max(220, len(bar_df) * 24))
            )
            st.altair_chart(_bar, use_container_width=True)

    # Format for display
    def _style_yoy(val):
        if pd.isna(val):
            return ""
        color = "#16A34A" if val > 0 else "#DC2626" if val < 0 else "#64748B"
        return f"color: {color}; font-weight: 700"

    fmt_cols = {c: ("${:,.0f}" if is_dollar else "{:,.0f}")
                for c in score_df.columns if c not in ("District", "YoY %")}
    fmt_cols["YoY %"] = lambda v: "—" if pd.isna(v) else f"{v:+.0f}%"

    styled = (
        score_df.style
        .format(fmt_cols)
        .applymap(_style_yoy, subset=["YoY %"])
    )

    st.dataframe(styled, use_container_width=True, hide_index=True)
    st.download_button(
        ":material/download: Export CSV",
        score_df.to_csv(index=False),
        "pst_district_scorecard.csv", "text/csv",
        key="scorecard_csv",
    )

    return score_df


def _render_district_detail(frame, district, sel_fys, metric_name, source_col,
                             is_dollar, all_fys, chart_type, pacing_on, cur_fy, cur_fm):
    """Section 3: single-district YoY chart (inline drill-down)."""
    dframe = frame[frame["DISTRICT_NAME"] == district]
    if pacing_on and cur_fy in sel_fys:
        display_frame = dframe[
            (dframe["FY_LABEL"] == cur_fy) |
            ((dframe["FY_LABEL"] != cur_fy) & (dframe["FM_IDX"] <= cur_fm))
        ]
    else:
        display_frame = dframe

    display_frame = display_frame[display_frame["FY_LABEL"].isin(sel_fys)]

    if display_frame.empty:
        empty_state(f"No closed-won PS&T for {district} in the selected fiscal years.")
        return

    g = _fill_months(_aggregate(display_frame, ["FY_LABEL", "FM_IDX"], source_col), "FY_LABEL", sel_fys)
    totals = {fy: g[g["FY_LABEL"] == fy]["VALUE"].sum() for fy in sel_fys}

    kcols = st.columns(min(len(sel_fys), 4))
    for i, fy in enumerate(sel_fys[-4:]):
        val = totals.get(fy, 0)
        delta_str = None
        idx = all_fys.index(fy) if fy in all_fys else -1
        prior_fy = all_fys[idx - 1] if idx > 0 else None
        if prior_fy and prior_fy in sel_fys:
            prior_val = totals.get(prior_fy, 0)
            if prior_val:
                pct = (val - prior_val) / prior_val * 100
                delta_str = f"{pct:+.0f}% vs {prior_fy}"
        label = f"{fy} {'YTD' if (pacing_on and fy == cur_fy) else 'Total'}"
        kcols[i].metric(label, _fmt(val, is_dollar), delta=delta_str)

    _fy_scale = alt.Scale(domain=sel_fys, range=_FY_PALETTE[-len(sel_fys):])
    chart = _make_chart(g, chart_type, "FY_LABEL", sel_fys, "Fiscal Year",
                        _fy_scale, f"{metric_name} · {district}", metric_name, is_dollar)

    if pacing_on and cur_fy in sel_fys:
        cur_month_label = _FM_ORDER[cur_fm - 1]
        rule_df = pd.DataFrame({"FM_LABEL": [cur_month_label]})
        rule = (
            alt.Chart(rule_df)
            .mark_rule(strokeDash=[6, 4], color="#64748B", strokeWidth=1.5)
            .encode(x=alt.X("FM_LABEL:N", sort=_FM_ORDER))
        )
        chart = (chart + rule).resolve_scale(color="independent")

    st.altair_chart(chart, use_container_width=True)

    _safe = "".join(ch if ch.isalnum() else "_" for ch in str(district))[:40]
    piv = g.pivot_table(index="FY_LABEL", columns="FM_IDX", values="VALUE", aggfunc="sum", fill_value=0)
    piv = piv.reindex(columns=range(1, 13), fill_value=0)
    piv.columns = _FM_ORDER
    piv = piv.reindex(sel_fys)
    piv["Total"] = piv.sum(axis=1)
    with st.expander("Data table", expanded=False):
        fmt_map = {c: ("${:,.0f}" if is_dollar else "{:,.0f}") for c in piv.columns}
        st.dataframe(piv.style.format(fmt_map), use_container_width=True)
        st.download_button(
            ":material/download: Export CSV", piv.to_csv(),
            f"pst_{_safe}_yoy.csv", "text/csv", key=f"detail_csv_{_safe}",
        )


# ── Load & prep ──────────────────────────────────────────────────────────────
_hist = _prep(load_ps_history(_scope=_scope_key()))
if not _hist.empty and "PRODUCT_FAMILIES" in _hist.columns:
    _hist = _hist[
        _hist["PRODUCT_FAMILIES"].fillna("").str.contains("Technical Services")
    ].reset_index(drop=True)

section_banner(
    "Sales Data Reports",
    "MoM and YoY trends for closed-won Professional (Technical) Services",
)

if _hist.empty:
    empty_state("No closed-won PS&T history found for the selected scope.")
else:
    tab_tip(
        "Trends use **Snowflake fiscal years** (FY starts Feb 1 — e.g. **FY27 = Feb 2026 → Jan 2027**). "
        "**YTD Pacing** (on by default) caps prior fiscal years at the current month so you compare "
        "the same number of months across years — e.g. if it's FM6, prior FYs also show FM1–FM6 only. "
        "Data is closed-won **Technical Services** opportunities, scoped to your sidebar selection.",
        title="How to read this tab",
    )

    _all_fys = sorted(_hist["FY_LABEL"].unique())
    _default_fys = _all_fys[-3:]
    _cur_fy, _cur_fm = _current_fy_fm(_hist)
    _cur_month_name = _FM_ORDER[_cur_fm - 1] if _cur_fm else "?"
    _districts_in_scope = sorted(_hist["DISTRICT_NAME"].dropna().unique())
    _multi_district = len(_districts_in_scope) > 1

    # ── Controls ─────────────────────────────────────────────────────────────
    c1, c2, c3, c4 = st.columns([1.2, 2.0, 1.2, 0.9])
    with c1:
        metric_name = st.selectbox("Metric", list(_METRICS.keys()), index=0, key="trend_metric")
    source_col, is_dollar = _METRICS[metric_name]

    with c2:
        sel_fys = st.multiselect(
            "Fiscal years", _all_fys, default=_default_fys, key="trend_fys",
        )

    with c3:
        pacing_label = f"YTD pacing  (through {_cur_month_name} · FM{_cur_fm})" if _cur_fm else "YTD pacing"
        pacing_on = st.checkbox(pacing_label, value=True, key="trend_pacing")

    with c4:
        chart_type = st.radio("Chart", ["Lines", "Bars"], horizontal=True, key="trend_chart_type")

    if not sel_fys:
        empty_state("Select at least one fiscal year above.")
    else:
        # ── Section 1: Aggregate YoY ─────────────────────────────────────────
        st.markdown("#### Aggregate YoY Trend")
        _render_aggregate_section(
            _hist, sel_fys, metric_name, source_col, is_dollar,
            _all_fys, chart_type, pacing_on, _cur_fy, _cur_fm,
        )

        # ── Section 2: District Scorecard ────────────────────────────────────
        if _multi_district:
            st.markdown("---")
            st.markdown("#### District Scorecard")
            _pacing_note = (
                f"YoY% compares {_cur_fy} YTD (FM1–FM{_cur_fm}) to {sel_fys[-2] if len(sel_fys) >= 2 else '—'} "
                f"FM1–FM{_cur_fm} — same-period comparison."
                if pacing_on and _cur_fy in sel_fys and len(sel_fys) >= 2
                else "Showing full-year totals per fiscal year."
            )
            st.caption(_pacing_note)
            score_df = _render_district_scorecard(
                _hist, _all_fys, sel_fys, source_col, is_dollar,
                metric_name, _cur_fy, _cur_fm, pacing_on,
            )

            # ── Section 3: District Detail (inline drill-down) ────────────────
            st.markdown("---")
            st.markdown("#### District Detail")
            sel_district = st.selectbox(
                "Select a district to see its YoY trend",
                _districts_in_scope, index=0, key="trend_detail_district",
            )
            _render_district_detail(
                _hist, sel_district, sel_fys, metric_name, source_col,
                is_dollar, _all_fys, chart_type, pacing_on, _cur_fy, _cur_fm,
            )
