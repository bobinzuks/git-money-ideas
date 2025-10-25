#!/bin/bash
# Email Configuration Setup for Automated Reports

echo "════════════════════════════════════════════════════════════════════════"
echo "📧 EMAIL CONFIGURATION SETUP"
echo "════════════════════════════════════════════════════════════════════════"
echo ""
echo "This script will help you configure email delivery for 12-hour reports."
echo ""
echo "You'll need:"
echo "  1. Email address to send FROM (e.g., your Gmail)"
echo "  2. Email address to send TO (where you want reports)"
echo "  3. App password (NOT your regular password)"
echo ""
echo "════════════════════════════════════════════════════════════════════════"
echo ""

# Check if .env exists
if [ -f ".env" ]; then
    echo "⚠️  .env file already exists"
    read -p "Do you want to overwrite it? (y/N): " overwrite
    if [ "$overwrite" != "y" ] && [ "$overwrite" != "Y" ]; then
        echo "Cancelled. Keeping existing .env"
        exit 0
    fi
fi

echo ""
echo "📝 STEP 1: Configure SMTP Server"
echo "────────────────────────────────────────────────────────────────────────"
echo ""
echo "Select your email provider:"
echo "  1) Gmail (smtp.gmail.com)"
echo "  2) Outlook/Hotmail (smtp-mail.outlook.com)"
echo "  3) Yahoo (smtp.mail.yahoo.com)"
echo "  4) Custom"
echo ""
read -p "Choice (1-4): " smtp_choice

case $smtp_choice in
    1)
        SMTP_HOST="smtp.gmail.com"
        SMTP_PORT="587"
        echo "✅ Selected: Gmail"
        ;;
    2)
        SMTP_HOST="smtp-mail.outlook.com"
        SMTP_PORT="587"
        echo "✅ Selected: Outlook"
        ;;
    3)
        SMTP_HOST="smtp.mail.yahoo.com"
        SMTP_PORT="587"
        echo "✅ Selected: Yahoo"
        ;;
    4)
        read -p "SMTP Host: " SMTP_HOST
        read -p "SMTP Port (usually 587): " SMTP_PORT
        echo "✅ Custom SMTP configured"
        ;;
    *)
        echo "❌ Invalid choice. Defaulting to Gmail."
        SMTP_HOST="smtp.gmail.com"
        SMTP_PORT="587"
        ;;
esac

echo ""
echo "📝 STEP 2: Email Credentials"
echo "────────────────────────────────────────────────────────────────────────"
echo ""

read -p "Your email address (FROM): " FROM_EMAIL

echo ""
echo "⚠️  IMPORTANT: Use an APP PASSWORD, not your regular password!"
echo ""
echo "How to get an app password:"
echo ""
if [ "$smtp_choice" == "1" ]; then
    echo "Gmail:"
    echo "  1. Go to https://myaccount.google.com/apppasswords"
    echo "  2. Sign in to your Google account"
    echo "  3. Select 'Mail' and 'Other (Custom name)'"
    echo "  4. Enter 'AgentDB Reports' as the name"
    echo "  5. Click 'Generate'"
    echo "  6. Copy the 16-character password"
    echo ""
elif [ "$smtp_choice" == "2" ]; then
    echo "Outlook:"
    echo "  1. Go to https://account.microsoft.com/security"
    echo "  2. Select 'Advanced security options'"
    echo "  3. Under 'App passwords', select 'Create a new app password'"
    echo "  4. Copy the password"
    echo ""
fi

read -sp "App password (hidden): " SMTP_PASSWORD
echo ""

echo ""
echo "📝 STEP 3: Recipient Email"
echo "────────────────────────────────────────────────────────────────────────"
echo ""

read -p "Where should reports be sent (TO): " TO_EMAIL

echo ""
echo "════════════════════════════════════════════════════════════════════════"
echo "📋 Configuration Summary"
echo "════════════════════════════════════════════════════════════════════════"
echo ""
echo "SMTP Host: $SMTP_HOST"
echo "SMTP Port: $SMTP_PORT"
echo "From Email: $FROM_EMAIL"
echo "To Email: $TO_EMAIL"
echo "Password: ******** (hidden)"
echo ""
read -p "Is this correct? (y/N): " confirm

if [ "$confirm" != "y" ] && [ "$confirm" != "Y" ]; then
    echo "❌ Cancelled. Please run the script again."
    exit 1
fi

# Create .env file
cat > .env << EOF
# AgentDB Discovery - Email Configuration
# Generated: $(date)

# SMTP Server Configuration
SMTP_HOST=$SMTP_HOST
SMTP_PORT=$SMTP_PORT

# Email Credentials
SMTP_USER=$FROM_EMAIL
SMTP_PASSWORD=$SMTP_PASSWORD

# Email Addresses
FROM_EMAIL=$FROM_EMAIL
TO_EMAIL=$TO_EMAIL

# GitHub Token (from previous setup)
GITHUB_TOKEN=${GITHUB_TOKEN}
EOF

echo ""
echo "✅ Configuration saved to .env"
echo ""
echo "⚠️  SECURITY NOTE:"
echo "   The .env file contains sensitive credentials."
echo "   Make sure it's in .gitignore (it should be by default)"
echo ""

# Add .env to .gitignore if not already there
if ! grep -q "^\.env$" .gitignore 2>/dev/null; then
    echo ".env" >> .gitignore
    echo "✅ Added .env to .gitignore"
fi

echo ""
echo "🧪 Testing email configuration..."
echo ""

# Test email
python3 -c "
import os
from dotenv import load_dotenv
load_dotenv()

print('SMTP Host:', os.getenv('SMTP_HOST'))
print('From:', os.getenv('FROM_EMAIL'))
print('To:', os.getenv('TO_EMAIL'))
print('Password:', '********' if os.getenv('SMTP_PASSWORD') else 'NOT SET')
" 2>/dev/null

if [ $? -eq 0 ]; then
    echo ""
    echo "✅ Configuration looks good!"
    echo ""
    echo "Would you like to send a test email now?"
    read -p "(y/N): " send_test

    if [ "$send_test" == "y" ] || [ "$send_test" == "Y" ]; then
        echo ""
        echo "📧 Sending test email..."
        python3 - << 'PYTHON_EOF'
import os
import smtplib
from email.mime.text import MIMEText
from dotenv import load_dotenv

load_dotenv()

smtp_host = os.getenv('SMTP_HOST')
smtp_port = int(os.getenv('SMTP_PORT', '587'))
smtp_user = os.getenv('SMTP_USER')
smtp_password = os.getenv('SMTP_PASSWORD')
from_email = os.getenv('FROM_EMAIL')
to_email = os.getenv('TO_EMAIL')

try:
    msg = MIMEText('This is a test email from AgentDB Discovery automated reporting system. If you received this, email configuration is working! 🎉')
    msg['Subject'] = '✅ AgentDB Discovery - Test Email'
    msg['From'] = from_email
    msg['To'] = to_email

    with smtplib.SMTP(smtp_host, smtp_port) as server:
        server.starttls()
        server.login(smtp_user, smtp_password)
        server.send_message(msg)

    print('✅ Test email sent successfully!')
    print(f'📬 Check {to_email} for the test message')
except Exception as e:
    print(f'❌ Test failed: {e}')
    print('\nPlease check:')
    print('  1. App password is correct (not regular password)')
    print('  2. "Less secure app access" enabled (if using Gmail)')
    print('  3. SMTP host and port are correct')
PYTHON_EOF
    fi
else
    echo ""
    echo "⚠️  Install python-dotenv to test:"
    echo "   pip install python-dotenv"
fi

echo ""
echo "════════════════════════════════════════════════════════════════════════"
echo "✅ EMAIL SETUP COMPLETE"
echo "════════════════════════════════════════════════════════════════════════"
echo ""
echo "Next steps:"
echo "  1. Run: source .env"
echo "  2. Test report: python3 automated_report_generator.py"
echo "  3. Setup cron: ./setup_cron.sh"
echo ""
