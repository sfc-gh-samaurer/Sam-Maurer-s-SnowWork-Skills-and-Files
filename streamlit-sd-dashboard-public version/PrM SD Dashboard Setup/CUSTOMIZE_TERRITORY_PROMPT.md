# SD Dashboard — Customize for Your Territory

Copy everything in the **"PASTE INTO COCO"** block below into your CoCo session after setup is complete.

---

## PASTE INTO COCO ↓

```
I need to customize my SD Dashboard to show data for my territory instead of the default (Erik Schneider / Raymond Navarro).

---

## Step 1 — Ask me for my territory details

Please ask me for the following:
1. The full names of my District Manager(s) exactly as they appear in Salesforce (e.g. "Erik Schneider") — I can have 1 or more
2. The district label(s) for the app header (e.g. "EntBayAreaTech1", "EntPacNorthwest") — used for display only
3. My name (for the PM byline in the header)

---

## Step 2 — Find the app directory

The app is at:
  $HOME/.snowflake/cortex/github-skills/streamlit-sd-dashboard/

(or wherever I extracted it if I used the zip)

---

## Step 3 — Update all hardcoded DM names in data.py

In data.py, every SQL query filters by DM name using this pattern:
  WHERE ACCOUNT_OWNER_MANAGER_C IN ('Erik Schneider', 'Raymond Navarro')
  WHERE o.DM IN ('Erik Schneider', 'Raymond Navarro')
  WHERE uc.ACCOUNT_DM IN ('Erik Schneider', 'Raymond Navarro')
  WHERE ra.ACCOUNT_OWNER_MANAGER_C IN ('Erik Schneider', 'Raymond Navarro')
  WHERE a.ACCOUNT_OWNER_MANAGER_C IN ('Erik Schneider', 'Raymond Navarro')

Replace ALL occurrences of the IN (...) list with my DM name(s). For example, if I have one DM "Jane Smith":
  IN ('Jane Smith')

If I have two DMs "Jane Smith" and "John Doe":
  IN ('Jane Smith', 'John Doe')

---

## Step 4 — Update the app header in streamlit_app.py

Find these two lines in streamlit_app.py:
  st.markdown("## :material/dashboard: Enterprise Expansion, Northwest - SD Dashboard")
  st.caption("DMs: Erik Schneider, EntBayAreaTech1 & Raymond Navarro, EntPacNorthwest — PM: Sam Maurer")

Replace them with my territory info and my name.

Also update the page_title in st.set_page_config() near the top of the file.

---

## Step 5 — Update action_planner_tab.py

In app_pages/action_planner_tab.py, find:
  st.error("No pipeline data found for EntBayAreaTech1 / EntPacNorthwest districts.")

Update the district names in that error message to match my districts.

---

## Step 6 — Verify the changes

Show me a summary of every line that was changed across all files so I can confirm everything looks right before restarting.

---

## Step 7 — Restart the app

Run:
  pkill -f "streamlit run" 2>/dev/null; sleep 1 && launchctl load ~/Library/LaunchAgents/com.<my-username>.sd-dashboard.plist

Then verify it's running at http://localhost:8501.

---

## Important note on DM names

The DM names must match EXACTLY what is in Salesforce (ACCOUNT_OWNER_MANAGER_C column). If unsure, I can verify with this SQL in Snowsight:

  USE ROLE SALES_ENGINEER;
  USE SECONDARY ROLES ALL;
  SELECT DISTINCT ACCOUNT_OWNER_MANAGER_C
  FROM SALES.RAVEN.ACCOUNT
  WHERE ACCOUNT_STATUS_C = 'Active'
  ORDER BY 1;
```
