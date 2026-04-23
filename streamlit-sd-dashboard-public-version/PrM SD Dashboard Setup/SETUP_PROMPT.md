# SD Dashboard — CoCo Setup Prompt

Copy everything in the **"PASTE INTO COCO"** block below and paste it into a new CoCo session. CoCo will handle the rest automatically.

---

## PASTE INTO COCO ↓

```
Set up and launch the SD Account Dashboard Streamlit app for me. Here is everything you need to know:

---

## What this app is

A local Streamlit dashboard for Snowflake Services Delivery that tracks capacity contracts, renewals, use cases, PS&T projects, and generates AI-powered SD action plans via Cortex. It runs locally and connects to Snowflake via SSO.

---

## Step 1 — Find the app directory

The app lives in the CoCo github-skills directory. Check if it exists at:
  $HOME/.snowflake/cortex/github-skills/streamlit-sd-dashboard/streamlit_app.py

If it does NOT exist, tell me and stop — I need to sync the GitHub skill first.

If it DOES exist, proceed with the steps below.

---

## Step 2 — Ask me for my Snowflake connection name

Ask me: "What is your Snowflake connection name from ~/.snowflake/connections.toml?"

I can verify my available connections by running:
  cat ~/.snowflake/connections.toml

Use whatever name I provide in the steps below (referred to as MY_CONNECTION_NAME).

---

## Step 3 — Create secrets.toml

The file $HOME/.snowflake/cortex/github-skills/streamlit-sd-dashboard/.streamlit/secrets.toml is gitignored and must be created locally by each user.

Create it with this content (substituting MY_CONNECTION_NAME):

  [connections.snowflake]
  connection_name = "MY_CONNECTION_NAME"

---

## Step 4 — Install dependencies if needed

Check that these packages are available to python3:
  streamlit, snowflake-snowpark-python, pandas

If any are missing, install them:
  pip install streamlit snowflake-snowpark-python pandas

---

## Step 5 — Set up launchd auto-start (macOS only)

This keeps the app running persistently across reboots without needing CoCo.

1. Find the real python3 path using: which python3

2. Create a launchd plist at:
   $HOME/Library/LaunchAgents/com.<my-username>.sd-dashboard.plist

   Use this template (fill in the real python3 path, real app path, and MY_CONNECTION_NAME):

   <?xml version="1.0" encoding="UTF-8"?>
   <!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN" "http://www.apple.com/DTDs/PropertyList-1.0.dtd">
   <plist version="1.0">
   <dict>
       <key>Label</key>
       <string>com.<my-username>.sd-dashboard</string>
       <key>ProgramArguments</key>
       <array>
           <string><python3-path></string>
           <string>-m</string>
           <string>streamlit</string>
           <string>run</string>
           <string><full-path-to>/streamlit-sd-dashboard/streamlit_app.py</string>
           <string>--server.port</string>
           <string>8501</string>
           <string>--server.headless</string>
           <string>true</string>
       </array>
       <key>EnvironmentVariables</key>
       <dict>
           <key>SNOWFLAKE_CONNECTION_NAME</key>
           <string>MY_CONNECTION_NAME</string>
       </dict>
       <key>RunAtLoad</key>
       <true/>
       <key>KeepAlive</key>
       <true/>
       <key>StandardOutPath</key>
       <string>/tmp/sd-dashboard.log</string>
       <key>StandardErrorPath</key>
       <string>/tmp/sd-dashboard.log</string>
   </dict>
   </plist>

3. Kill any existing streamlit process on port 8501, then load the plist:
   pkill -f "streamlit run" 2>/dev/null; sleep 1
   launchctl load $HOME/Library/LaunchAgents/com.<my-username>.sd-dashboard.plist

---

## Step 6 — Verify it's running

1. Check launchctl: launchctl list | grep sd-dashboard
2. Check HTTP: curl -s -o /dev/null -w "%{http_code}" http://localhost:8501
   (should return 200)
3. Tell me the app URL: http://localhost:8501

---

## Step 7 — Tell me how to manage it

Print the three management commands (start, stop, view logs) so I can save them.

---

## Notes

- On first load, the browser will open an SSO login prompt — complete it to load data.
- The app caches all data for 24 hours. Use the Refresh button in the top-right to reload.
- If data.py is changed, restart with: pkill -f "streamlit run" then re-load the plist.
- Tab files (app_pages/*.py) hot-reload automatically on save.
- Full documentation is in DASHBOARD_BUILD_GUIDE.md in the same directory.
```

---

## Troubleshooting

| Problem | Fix |
|---------|-----|
| "File does not exist" error | The github-skills repo isn't synced. Go to CoCo Settings → Skills and sync `streamlit-sd-dashboard`. |
| SSO popup not appearing | Check your browser for a popup blocked notification, or look for it behind other windows. |
| Port 8501 already in use | Run `pkill -f "streamlit run"` then reload the plist. |
| "Default connection not found" | Your `secrets.toml` has the wrong connection name. Run `cat ~/.snowflake/connections.toml` to find the right one. |
| Data not loading / blank tables | Complete the SSO login in the browser. Each tab triggers a separate auth request on first load. |
| launchd not starting on login | Run `launchctl list | grep sd-dashboard` — if missing, re-run the `launchctl load` command. |
