import os
import snowflake.connector

APP_DIR = "/tmp/sam-maurer-repo/streamlit-sd-dashboard-public version"
STAGE = "snow://streamlit/SD_APPS_DB.SD_CENTER.\"SD Presales Run the Business Dashboard\"/versions/live"

FILES = [
    "streamlit_app.py",
    "data.py",
    "pyproject.toml",
    "app_pages/exec_summary_tab.py",
    "app_pages/capacity_renewals.py",
    "app_pages/use_cases_tab.py",
    "app_pages/pst_tab.py",
    "app_pages/sd_opportunities_tab.py",
    "app_pages/action_planner_tab.py",
    "app_pages/pipeline_snowwork_tab.py",
    "app_pages/account_details_tab.py",
]

conn = snowflake.connector.connect(
    connection_name=os.getenv("SNOWFLAKE_CONNECTION_NAME") or "sfcogsops-snowhouse_aws_us_west_2",
    role="TECHNICAL_ACCOUNT_MANAGER"
)
cs = conn.cursor()

for f in FILES:
    local_path = os.path.join(APP_DIR, f)
    stage_dir = f"{STAGE}/{os.path.dirname(f)}" if os.path.dirname(f) else STAGE
    cs.execute(f"PUT 'file://{local_path}' '{stage_dir}' OVERWRITE=TRUE AUTO_COMPRESS=FALSE")
    print(f"✓ {f}")

cs.close()
conn.close()
print("\nDeploy complete.")
