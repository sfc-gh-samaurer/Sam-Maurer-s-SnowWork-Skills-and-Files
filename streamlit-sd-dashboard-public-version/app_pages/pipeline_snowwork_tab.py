import streamlit as st

st.markdown("""
<style>
.sw-banner {
    background: linear-gradient(135deg, #0C4A6E 0%, #0284C7 55%, #29B5E8 100%);
    border-radius: 16px;
    padding: 24px 32px;
    margin-bottom: 22px;
    box-shadow: 0 6px 24px rgba(41,181,232,0.30);
}
.sw-banner-title {
    color: white !important;
    font-size: 4.4rem;
    font-weight: 800;
    margin: 0;
    letter-spacing: -0.02em;
    line-height: 1.15;
}
.sw-banner-sub {
    color: rgba(255,255,255,0.78);
    font-size: 0.92rem;
    margin: 5px 0 0;
}
.sw-section {
    background: white;
    border-radius: 12px;
    padding: 20px 24px;
    margin-bottom: 14px;
    border-left: 5px solid #29B5E8;
    box-shadow: 0 2px 10px rgba(0,0,0,0.06);
}
.sw-section-num {
    display: inline-block;
    background: linear-gradient(135deg, #0284C7, #29B5E8);
    color: white;
    font-size: 0.85rem;
    font-weight: 800;
    border-radius: 50%;
    width: 28px;
    height: 28px;
    line-height: 28px;
    text-align: center;
    margin-right: 10px;
    flex-shrink: 0;
}
.sw-section-title {
    font-size: 1.1rem;
    font-weight: 700;
    color: #11567F;
    display: flex;
    align-items: center;
    margin-bottom: 10px;
}
.sw-cmd {
    display: inline-block;
    background: #F1F5F9;
    border: 1px solid #CBD5E1;
    border-radius: 6px;
    padding: 3px 10px;
    font-family: monospace;
    font-size: 0.9rem;
    color: #0F172A;
    margin: 4px 0 8px;
}
.sw-install {
    font-size: 0.8rem;
    color: #64748B;
    background: #F8FAFC;
    border-radius: 6px;
    padding: 6px 10px;
    margin-top: 8px;
    font-family: monospace;
}
.sw-prework {
    background: #FFF7ED;
    border: 1px solid #FED7AA;
    border-radius: 10px;
    padding: 14px 18px;
    margin-bottom: 18px;
    font-size: 0.92rem;
    color: #7C2D12;
}
</style>
""", unsafe_allow_html=True)

st.markdown("""
<div class="sw-banner">
    <div>
        <p class="sw-banner-title">Use SnowWork</p>
        <p class="sw-banner-sub">Manage your pipeline, action items, and book of business in CoCo/SnowWork.</p>
    </div>
</div>
""", unsafe_allow_html=True)

st.markdown("""
The following prework and instructions will enable you to manage your tasks and pipeline through CoCo/SnowWork.
""")

st.markdown("""
<div class="sw-prework">
    <strong>⚠️ Prework:</strong> Install Google Workspace and Glean for Slack before getting started.
</div>
""", unsafe_allow_html=True)

st.markdown("""
<div class="sw-section">
    <div class="sw-section-title">
        <span class="sw-section-num">1</span> Opportunity Review
    </div>
    <p style="margin:0 0 8px;color:#334155;">Type:</p>
    <div class="sw-cmd">opportunity review for [account]</div>
    <p style="margin:8px 0;color:#475569;font-size:0.92rem;">
        Pulls Salesforce (including AE/SE running notes), Vivun use cases, Slack, and Drive into a single brief —
        use case, partner involvement, history timeline, next steps, and a PS recommendation.
    </p>
    <div class="sw-install">
        📁 Install: create <code>~/.snowflake/cortex/skills/opportunity-review/</code> and drop in the attached SKILL.md
    </div>
</div>

<div class="sw-section">
    <div class="sw-section-title">
        <span class="sw-section-num">2</span> Daily Summary
    </div>
    <p style="margin:0 0 8px;color:#334155;">Type:</p>
    <div class="sw-cmd">daily summary</div>
    <p style="margin:8px 0;color:#475569;font-size:0.92rem;">
        Reads your pipeline spreadsheet, Gmail, Calendar, Slack, and Zoom summaries. Outputs in-quarter and
        out-quarter opp tables with PS ACV and action items, plus active project status with what's due and what you owe.
    </p>
    <div class="sw-install">
        📁 Install: <code>~/.snowflake/cortex/skills/daily-summary/</code> + attached SKILL.md. Update the Google Sheet with your own notes/locator.
    </div>
</div>

<div class="sw-section">
    <div class="sw-section-title">
        <span class="sw-section-num">3</span> Weekly Project Status
    </div>
    <p style="margin:0 0 8px;color:#334155;">Type:</p>
    <div class="sw-cmd">run weekly summary for [project]</div>
    <p style="margin:8px 0;color:#475569;font-size:0.92rem;">
        Searches email, Slack, Zoom, and Drive for the week. Outputs a Slack-ready post: completed items,
        callouts, day-by-day plan for next week, and monthly goals.
    </p>
    <div class="sw-install">
        📁 Install: <code>~/.snowflake/cortex/skills/weekly-project-status/</code> + attached SKILL.md
    </div>
</div>
""", unsafe_allow_html=True)

st.caption("SnowWork works however you prefer — apps, skills, or just prompts. The main thing is getting your information somewhere it can find it.")
