#!/bin/bash
# SD Dashboard — One-time setup script
# Run this from the streamlit-sd-dashboard directory:
#   chmod +x setup.sh && ./setup.sh

set -e

APP_DIR="$(cd "$(dirname "$0")" && pwd)"
USERNAME="$(whoami)"
PYTHON=$(which python3)

echo ""
echo "=== SD Dashboard Setup ==="
echo "App directory: $APP_DIR"
echo "Python:        $PYTHON"
echo "User:          $USERNAME"
echo ""

# ── 1. Connection name ────────────────────────────────────────────────────────
echo "Your available Snowflake connections:"
echo ""
grep '^\[' ~/.snowflake/connections.toml 2>/dev/null | sed 's/\[//;s/\]//' | while read -r line; do
  echo "  - $line"
done
echo ""
read -rp "Enter your Snowflake connection name: " CONN_NAME

# ── 2. secrets.toml ───────────────────────────────────────────────────────────
SECRETS_FILE="$APP_DIR/.streamlit/secrets.toml"
echo ""
echo "[1/4] Creating $SECRETS_FILE..."
cat > "$SECRETS_FILE" <<EOF
[connections.snowflake]
connection_name = "$CONN_NAME"
EOF
echo "      Done."

# ── 3. Install dependencies ───────────────────────────────────────────────────
echo "[2/4] Checking Python dependencies..."
$PYTHON -c "import streamlit, snowflake.connector, pandas" 2>/dev/null || {
  echo "      Installing missing packages..."
  $PYTHON -m pip install streamlit snowflake-snowpark-python pandas --quiet
}
echo "      Done."

# ── 4. launchd plist ──────────────────────────────────────────────────────────
PLIST_PATH="$HOME/Library/LaunchAgents/com.${USERNAME}.sd-dashboard.plist"
echo "[3/4] Creating launchd plist at $PLIST_PATH..."
cat > "$PLIST_PATH" <<EOF
<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN" "http://www.apple.com/DTDs/PropertyList-1.0.dtd">
<plist version="1.0">
<dict>
    <key>Label</key>
    <string>com.${USERNAME}.sd-dashboard</string>
    <key>ProgramArguments</key>
    <array>
        <string>${PYTHON}</string>
        <string>-m</string>
        <string>streamlit</string>
        <string>run</string>
        <string>${APP_DIR}/streamlit_app.py</string>
        <string>--server.port</string>
        <string>8501</string>
        <string>--server.headless</string>
        <string>true</string>
    </array>
    <key>EnvironmentVariables</key>
    <dict>
        <key>SNOWFLAKE_CONNECTION_NAME</key>
        <string>${CONN_NAME}</string>
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
EOF
echo "      Done."

# ── 5. Launch ─────────────────────────────────────────────────────────────────
echo "[4/4] Launching app..."
pkill -f "streamlit run" 2>/dev/null || true
sleep 1
launchctl unload "$PLIST_PATH" 2>/dev/null || true
launchctl load "$PLIST_PATH"
sleep 4

STATUS=$(curl -s -o /dev/null -w "%{http_code}" http://localhost:8501 2>/dev/null || echo "000")
if [ "$STATUS" = "200" ]; then
  echo "      App is running at http://localhost:8501"
else
  echo "      App may still be starting. Check: tail -f /tmp/sd-dashboard.log"
fi

echo ""
echo "=== Setup Complete ==="
echo ""
echo "Management commands:"
echo "  Stop:      launchctl unload ~/Library/LaunchAgents/com.${USERNAME}.sd-dashboard.plist"
echo "  Start:     launchctl load ~/Library/LaunchAgents/com.${USERNAME}.sd-dashboard.plist"
echo "  Logs:      tail -f /tmp/sd-dashboard.log"
echo "  Restart:   pkill -f 'streamlit run' && launchctl load ~/Library/LaunchAgents/com.${USERNAME}.sd-dashboard.plist"
echo ""
echo "On first load, complete the SSO login popup in your browser."
echo "Full docs: $APP_DIR/DASHBOARD_BUILD_GUIDE.md"
