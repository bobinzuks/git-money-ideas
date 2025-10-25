#!/bin/bash
# Master startup script for GitHub Codespaces

echo "════════════════════════════════════════════════════════════════════════"
echo "🚀 AGENTDB DISCOVERY - COMPLETE AUTOMATION STARTUP"
echo "════════════════════════════════════════════════════════════════════════"
echo ""

PROJECT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$PROJECT_DIR"

# Check if .env exists
if [ ! -f ".env" ]; then
    echo "⚠️  No .env file found!"
    echo ""
    echo "You need to configure email and GitHub token first."
    echo ""
    read -p "Do you want to run setup now? (y/N): " run_setup

    if [ "$run_setup" == "y" ] || [ "$run_setup" == "Y" ]; then
        chmod +x setup_email_config.sh
        ./setup_email_config.sh
    else
        echo ""
        echo "Please run: ./setup_email_config.sh"
        exit 1
    fi
fi

# Load environment
export $(cat .env | grep -v '^#' | xargs)

echo "✅ Environment loaded"
echo ""

# Check if discovery is already running
if pgrep -f "continuous_discovery.py" > /dev/null; then
    echo "✅ Discovery engine already running"
    DISCOVERY_PID=$(pgrep -f "continuous_discovery.py")
    echo "   PID: $DISCOVERY_PID"
else
    echo "🔄 Starting discovery engine..."
    nohup python3 continuous_discovery.py >> discovery_v2.log 2>&1 &
    DISCOVERY_PID=$!
    echo "✅ Discovery started (PID: $DISCOVERY_PID)"
fi

echo ""

# Check if dashboard API is running
if pgrep -f "flask run" > /dev/null; then
    echo "✅ Dashboard API already running"
else
    echo "🔄 Starting dashboard API..."
    cd wasm-web
    nohup python3 -m flask run --host=0.0.0.0 --port=5000 >> ../dashboard.log 2>&1 &
    cd ..
    echo "✅ Dashboard API started (http://localhost:5000)"
fi

echo ""

# Setup or verify cron
if crontab -l 2>/dev/null | grep -q "run_report.sh"; then
    echo "✅ Cron jobs already configured"
    echo ""
    echo "Current schedule:"
    crontab -l | grep run_report.sh
else
    echo "⚠️  Cron jobs not configured"
    echo ""
    read -p "Do you want to setup 12-hour reports now? (y/N): " setup_cron

    if [ "$setup_cron" == "y" ] || [ "$setup_cron" == "Y" ]; then
        chmod +x setup_cron.sh
        ./setup_cron.sh
    else
        echo ""
        echo "Run later: ./setup_cron.sh"
    fi
fi

echo ""
echo "════════════════════════════════════════════════════════════════════════"
echo "📊 SYSTEM STATUS"
echo "════════════════════════════════════════════════════════════════════════"
echo ""

# Count gems in database
if [ -f "continuous_discovery.db" ]; then
    GEM_COUNT=$(sqlite3 continuous_discovery.db "SELECT COUNT(*) FROM discovered_gems" 2>/dev/null || echo "N/A")
    PERFECT_GEMS=$(sqlite3 continuous_discovery.db "SELECT COUNT(*) FROM discovered_gems WHERE stars >= 5 AND stars <= 100 AND forks > 0 AND agentdb_multiplier >= 15" 2>/dev/null || echo "N/A")
    IDEAS_COUNT=$(sqlite3 continuous_discovery.db "SELECT COUNT(*) FROM generated_ideas" 2>/dev/null || echo "N/A")

    echo "Database Stats:"
    echo "  • Total Gems: $GEM_COUNT"
    echo "  • Perfect Gems: $PERFECT_GEMS"
    echo "  • Ideas Generated: $IDEAS_COUNT"
else
    echo "⚠️  Database not yet created (will be created on first discovery)"
fi

echo ""
echo "Running Processes:"
ps aux | grep -E "continuous_discovery|flask" | grep -v grep || echo "  (checking...)"

echo ""
echo "════════════════════════════════════════════════════════════════════════"
echo "🎯 QUICK ACTIONS"
echo "════════════════════════════════════════════════════════════════════════"
echo ""
echo "View discovery logs:     tail -f discovery_v2.log"
echo "View dashboard logs:     tail -f dashboard.log"
echo "View report logs:        tail -f reports.log"
echo "Generate report now:     python3 automated_report_generator.py"
echo "View database:           sqlite3 continuous_discovery.db"
echo "Open dashboard:          http://localhost:5000"
echo ""
echo "Stop discovery:          kill $DISCOVERY_PID"
echo "Stop all:                pkill -f 'continuous_discovery|flask'"
echo ""
echo "════════════════════════════════════════════════════════════════════════"
echo "✅ ALL SYSTEMS RUNNING"
echo "════════════════════════════════════════════════════════════════════════"
echo ""
echo "🤖 The self-improving algorithm will:"
echo "   • Discover hidden gems 24/7"
echo "   • Learn from patterns every cycle"
echo "   • Email you reports every 12 hours"
echo "   • Get smarter with every discovery"
echo ""
echo "Reports will be sent to: ${TO_EMAIL:-'NOT CONFIGURED'}"
echo ""
