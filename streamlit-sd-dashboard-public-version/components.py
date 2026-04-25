import streamlit as st
import html as _html
from constants import SFDC_BASE


def section_banner(title: str, subtitle: str = "", anchor: str = "", count: int | None = None):
    anchor_attr = f' id="{anchor}"' if anchor else ""
    sub_html = f'<p class="sf-banner-sub">{_html.escape(subtitle)}</p>' if subtitle else ""
    count_html = (
        f'<span class="sf-banner-count">{count:,}</span>' if count is not None else ""
    )
    st.markdown(
        f'<div class="sf-banner"{anchor_attr}>'
        f'<div><p class="sf-banner-title">{_html.escape(title)}</p>{sub_html}</div>'
        f'{count_html}'
        f"</div>",
        unsafe_allow_html=True,
    )


def kpi_row(metrics: list):
    cols = st.columns(len(metrics))
    for col, m in zip(cols, metrics):
        with col:
            st.metric(
                label=m.get("label", ""),
                value=m.get("value", "—"),
                delta=m.get("delta"),
            )


def data_section_header(label: str, count: int, df=None, filename: str = "export.csv"):
    h_left, h_right = st.columns([4, 1])
    with h_left:
        st.markdown(
            f'<p class="sf-section-label">{_html.escape(label)} &nbsp;<span style="color:#334155;font-weight:800;font-size:0.85rem;">{count:,}</span></p>',
            unsafe_allow_html=True,
        )
    with h_right:
        if df is not None and not df.empty:
            st.download_button(
                ":material/download: CSV",
                data=df.to_csv(index=False),
                file_name=filename,
                mime="text/csv",
                use_container_width=True,
                key=f"_dsheader_dl_{filename}",
            )


def empty_state(message: str, icon: str = "ℹ️"):
    st.markdown(
        f'<div class="sf-empty-state">{icon}&nbsp; {_html.escape(message)}</div>',
        unsafe_allow_html=True,
    )


def error_state(message: str):
    st.markdown(
        f'<div class="sf-error-state">⚠️&nbsp; {_html.escape(message)}</div>',
        unsafe_allow_html=True,
    )


def sfdc_link(sfdc_id: str, object_type: str = "Account") -> str | None:
    if sfdc_id and str(sfdc_id).strip():
        return f"{SFDC_BASE}/{object_type}/{sfdc_id}/view"
    return None


def opp_link(opp_id: str) -> str | None:
    return sfdc_link(opp_id, "Opportunity")
