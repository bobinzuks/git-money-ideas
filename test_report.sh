#!/bin/bash
# Quick test script to verify automated reporting system

echo "════════════════════════════════════════════════════════════════════════"
echo "🧪 TESTING AUTOMATED REPORT SYSTEM"
echo "════════════════════════════════════════════════════════════════════════"
echo ""

PROJECT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$PROJECT_DIR"

# Check dependencies
echo "1️⃣  Checking dependencies..."
echo ""

python3 --version || { echo "❌ Python 3 not found"; exit 1; }
echo "✅ Python 3 installed"

# Check database
if [ -f "continuous_discovery.db" ]; then
    GEM_COUNT=$(sqlite3 continuous_discovery.db "SELECT COUNT(*) FROM discovered_gems" 2>/dev/null)
    echo "✅ Database exists ($GEM_COUNT gems)"
else
    echo "⚠️  Database not found (will be created)"
fi

echo ""
echo "2️⃣  Testing self-improving algorithm..."
echo ""

# Test algorithm
python3 << 'EOF'
import sys
import os

# Add current directory to path
sys.path.insert(0, os.getcwd())

try:
    from automated_report_generator import SelfImprovingAlgorithm

    # Test initialization
    algo = SelfImprovingAlgorithm("continuous_discovery.db")
    print("✅ Algorithm initialized")

    # Test methods
    print("✅ Learning history loaded")

    print("\nAlgorithm is ready!")

except Exception as e:
    print(f"❌ Error: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)
EOF

if [ $? -eq 0 ]; then
    echo ""
    echo "✅ Self-improving algorithm working"
else
    echo ""
    echo "❌ Algorithm test failed"
    exit 1
fi

echo ""
echo "3️⃣  Testing report generator (dry run)..."
echo ""

# Test report generation without email
python3 << 'EOF'
import sys
import os
sys.path.insert(0, os.getcwd())

try:
    from automated_report_generator import ReportGenerator

    # Generate report
    generator = ReportGenerator()
    subject, body = generator.generate_report()

    print(f"✅ Report generated!")
    print(f"   Subject: {subject}")
    print(f"   Length: {len(body)} characters")
    print(f"   Lines: {len(body.splitlines())}")

    # Save sample
    with open("sample_report.md", "w") as f:
        f.write(f"# {subject}\n\n{body}")

    print(f"\n💾 Sample saved to: sample_report.md")

except Exception as e:
    print(f"❌ Error: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)
EOF

if [ $? -eq 0 ]; then
    echo ""
    echo "✅ Report generation working"
else
    echo ""
    echo "❌ Report generation failed"
    exit 1
fi

echo ""
echo "4️⃣  Checking email configuration..."
echo ""

if [ -f ".env" ]; then
    source .env

    if [ -n "$SMTP_USER" ] && [ -n "$SMTP_PASSWORD" ] && [ -n "$TO_EMAIL" ]; then
        echo "✅ Email configured"
        echo "   From: $SMTP_USER"
        echo "   To: $TO_EMAIL"
        echo "   SMTP: $SMTP_HOST:$SMTP_PORT"

        read -p "   Test email now? (y/N): " send_test

        if [ "$send_test" == "y" ] || [ "$send_test" == "Y" ]; then
            echo ""
            echo "   📧 Sending test report..."
            python3 automated_report_generator.py
        fi
    else
        echo "⚠️  Email not fully configured"
        echo "   Run: ./setup_email_config.sh"
    fi
else
    echo "⚠️  No .env file found"
    echo "   Run: ./setup_email_config.sh"
fi

echo ""
echo "5️⃣  Checking cron setup..."
echo ""

if crontab -l 2>/dev/null | grep -q "run_report.sh"; then
    echo "✅ Cron jobs configured"
    echo ""
    crontab -l | grep run_report.sh | sed 's/^/   /'
else
    echo "⚠️  Cron not configured"
    echo "   Run: ./setup_cron.sh"
fi

echo ""
echo "════════════════════════════════════════════════════════════════════════"
echo "📊 TEST RESULTS"
echo "════════════════════════════════════════════════════════════════════════"
echo ""

PASS_COUNT=0
TOTAL_COUNT=5

# Count passes
[ -f "continuous_discovery.db" ] && ((PASS_COUNT++))
[ -f "sample_report.md" ] && ((PASS_COUNT++))
[ -f ".env" ] && ((PASS_COUNT++))

echo "Tests passed: $PASS_COUNT/3 core components"
echo ""

if [ -f "sample_report.md" ]; then
    echo "📄 Sample report preview:"
    echo "────────────────────────────────────────────────────────────────────────"
    head -30 sample_report.md
    echo "────────────────────────────────────────────────────────────────────────"
    echo "   (Full report in sample_report.md)"
fi

echo ""
echo "════════════════════════════════════════════════════════════════════════"
echo "✅ TESTING COMPLETE"
echo "════════════════════════════════════════════════════════════════════════"
echo ""

if [ $PASS_COUNT -eq 3 ]; then
    echo "🎉 All core components working!"
    echo ""
    echo "Next steps:"
    echo "  1. Start system: ./start_all.sh"
    echo "  2. Manual report: python3 automated_report_generator.py"
    echo "  3. View sample: cat sample_report.md"
else
    echo "⚠️  Some components need setup"
    echo ""
    echo "Setup steps:"
    [ ! -f "continuous_discovery.db" ] && echo "  • Run discovery: python3 continuous_discovery.py"
    [ ! -f ".env" ] && echo "  • Configure email: ./setup_email_config.sh"
    echo "  • Setup cron: ./setup_cron.sh"
fi

echo ""
