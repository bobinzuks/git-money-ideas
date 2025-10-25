#!/bin/bash
# Setup Cron Job for 12-Hour Reports

echo "════════════════════════════════════════════════════════════════════════"
echo "⏰ CRON JOB SETUP - 12-Hour Automated Reports"
echo "════════════════════════════════════════════════════════════════════════"
echo ""

# Get absolute path to project directory
PROJECT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

echo "Project directory: $PROJECT_DIR"
echo ""

# Create wrapper script for cron
cat > "$PROJECT_DIR/run_report.sh" << EOF
#!/bin/bash
# Wrapper script for cron - runs report generator

# Load environment variables
if [ -f "$PROJECT_DIR/.env" ]; then
    export \$(cat "$PROJECT_DIR/.env" | grep -v '^#' | xargs)
fi

# Change to project directory
cd "$PROJECT_DIR"

# Run report generator
python3 "$PROJECT_DIR/automated_report_generator.py" >> "$PROJECT_DIR/reports.log" 2>&1

# Log completion
echo "Report generated at \$(date)" >> "$PROJECT_DIR/reports.log"
EOF

chmod +x "$PROJECT_DIR/run_report.sh"

echo "✅ Created wrapper script: run_report.sh"
echo ""

# Create cron entries
echo "Setting up cron jobs for 12-hour intervals..."
echo ""
echo "Choose when you want reports:"
echo "  1) 6 AM and 6 PM (06:00 and 18:00)"
echo "  2) 8 AM and 8 PM (08:00 and 20:00)"
echo "  3) 9 AM and 9 PM (09:00 and 21:00)"
echo "  4) 12 AM and 12 PM (00:00 and 12:00)"
echo "  5) Custom times"
echo ""
read -p "Choice (1-5): " time_choice

case $time_choice in
    1)
        HOUR1="6"
        HOUR2="18"
        TIME_DESC="6 AM and 6 PM"
        ;;
    2)
        HOUR1="8"
        HOUR2="20"
        TIME_DESC="8 AM and 8 PM"
        ;;
    3)
        HOUR1="9"
        HOUR2="21"
        TIME_DESC="9 AM and 9 PM"
        ;;
    4)
        HOUR1="0"
        HOUR2="12"
        TIME_DESC="12 AM and 12 PM"
        ;;
    5)
        read -p "First report hour (0-23): " HOUR1
        read -p "Second report hour (0-23): " HOUR2
        TIME_DESC="$HOUR1:00 and $HOUR2:00"
        ;;
    *)
        echo "❌ Invalid choice. Defaulting to 9 AM and 9 PM."
        HOUR1="9"
        HOUR2="21"
        TIME_DESC="9 AM and 9 PM"
        ;;
esac

# Create cron entries
CRON1="0 $HOUR1 * * * $PROJECT_DIR/run_report.sh"
CRON2="0 $HOUR2 * * * $PROJECT_DIR/run_report.sh"

echo ""
echo "════════════════════════════════════════════════════════════════════════"
echo "📋 Cron Configuration"
echo "════════════════════════════════════════════════════════════════════════"
echo ""
echo "Reports will run at: $TIME_DESC"
echo ""
echo "Cron entries:"
echo "  $CRON1"
echo "  $CRON2"
echo ""
read -p "Add these to crontab? (y/N): " confirm

if [ "$confirm" != "y" ] && [ "$confirm" != "Y" ]; then
    echo "❌ Cancelled."
    echo ""
    echo "To add manually, run:"
    echo "  crontab -e"
    echo ""
    echo "Then add these lines:"
    echo "  $CRON1"
    echo "  $CRON2"
    exit 0
fi

# Backup existing crontab
crontab -l > /tmp/crontab_backup_$(date +%Y%m%d_%H%M%S) 2>/dev/null

# Add to crontab (remove duplicates first)
(crontab -l 2>/dev/null | grep -v "run_report.sh"; echo "$CRON1"; echo "$CRON2") | crontab -

echo ""
echo "✅ Cron jobs added successfully!"
echo ""

# Verify
echo "Current crontab:"
echo "────────────────────────────────────────────────────────────────────────"
crontab -l | grep run_report.sh
echo "────────────────────────────────────────────────────────────────────────"
echo ""

echo "📧 Reports will be emailed to: $(grep TO_EMAIL .env 2>/dev/null | cut -d= -f2 || echo 'NOT CONFIGURED')"
echo "💾 Logs will be saved to: $PROJECT_DIR/reports.log"
echo ""

echo "════════════════════════════════════════════════════════════════════════"
echo "🧪 Testing"
echo "════════════════════════════════════════════════════════════════════════"
echo ""
echo "Would you like to run a test report now?"
read -p "(y/N): " run_test

if [ "$run_test" == "y" ] || [ "$run_test" == "Y" ]; then
    echo ""
    echo "🔄 Running test report..."
    echo ""
    "$PROJECT_DIR/run_report.sh"
    echo ""
    echo "Check your email and reports.log for results"
fi

echo ""
echo "════════════════════════════════════════════════════════════════════════"
echo "✅ CRON SETUP COMPLETE"
echo "════════════════════════════════════════════════════════════════════════"
echo ""
echo "Next reports at:"
echo "  • Today/Tomorrow $TIME_DESC"
echo ""
echo "Useful commands:"
echo "  • View cron jobs: crontab -l"
echo "  • Edit cron jobs: crontab -e"
echo "  • View logs: tail -f $PROJECT_DIR/reports.log"
echo "  • Manual run: $PROJECT_DIR/run_report.sh"
echo "  • Remove cron: crontab -e (then delete the lines)"
echo ""
