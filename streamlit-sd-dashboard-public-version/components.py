import streamlit as st
import html as _html
from constants import SFDC_BASE, GRADIENT_PRIMARY, SF_STAR_BLUE


def section_banner(title: str, subtitle: str = "", anchor: str = ""):
    anchor_attr = f' id="{anchor}"' if anchor else ""
    sub_html = f'<p class="sf-banner-sub">{_html.escape(subtitle)}</p>' if subtitle else ""
    st.markdown(
        f'<div class="sf-banner"{anchor_attr}>'
        f'<p class="sf-banner-title">{_html.escape(title)}</p>{sub_html}'
        f"</div>",
        unsafe_allow_html=True,
    )


def kpi_row(metrics: list):
    cols = st.columns(len(metrics))
    for col, m in zip(cols, metrics):
        with col:
            delta = m.get("delta")
            st.metric(
                label=m.get("label", ""),
                value=m.get("value", "—"),
                delta=delta,
            )


def empty_state(message: str, icon: str = "ℹ️"):
    st.markdown(
        f'<div class="sf-empty-state">{icon} {_html.escape(message)}</div>',
        unsafe_allow_html=True,
    )


def error_state(message: str):
    st.markdown(
        f'<div class="sf-error-state">⚠️ {_html.escape(message)}</div>',
        unsafe_allow_html=True,
    )


def sfdc_link(sfdc_id: str, object_type: str = "Account") -> str | None:
    if sfdc_id and str(sfdc_id).strip():
        return f"{SFDC_BASE}/{object_type}/{sfdc_id}/view"
    return None


def opp_link(opp_id: str) -> str | None:
    return sfdc_link(opp_id, "Opportunity")
