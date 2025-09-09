# 📧 Email Setup Guide for Password Reset

## Current Status
The forgot password feature is now working! It will show the password on screen for demo purposes, but you can set up real email sending using EmailJS.

## 🚀 Quick Setup (5 minutes)

### Step 1: Create EmailJS Account
1. Go to [https://www.emailjs.com/](https://www.emailjs.com/)
2. Sign up for a free account
3. Verify your email address

### Step 2: Add Email Service
1. In EmailJS dashboard, go to "Email Services"
2. Click "Add New Service"
3. Choose your email provider (Gmail, Outlook, etc.)
4. Follow the setup instructions
5. Copy your **Service ID**

### Step 3: Create Email Template
1. Go to "Email Templates"
2. Click "Create New Template"
3. Use this template:

**Subject:** Password Reset - {{company_name}}

**Body:**
```
Hello {{to_name}},

You requested a password reset for your {{company_name}} account.

Your login credentials:
Username: {{username}}
Password: {{password}}

Please log in at: {{reset_link}}

If you didn't request this reset, please ignore this email.

Best regards,
The Forecasting Company Team
```

4. Save the template and copy the **Template ID**

### Step 4: Get Public Key
1. Go to "Account" → "General"
2. Copy your **Public Key**

### Step 5: Update forgot-password.html
Replace these lines in `forgot-password.html`:

```javascript
const serviceId = 'YOUR_SERVICE_ID'; // Replace with your Service ID
const templateId = 'YOUR_TEMPLATE_ID'; // Replace with your Template ID  
const publicKey = 'YOUR_PUBLIC_KEY'; // Replace with your Public Key
```

## 🎯 How It Works Now

### Without EmailJS Setup:
- Shows password directly on screen
- Perfect for testing and demos
- No external dependencies

### With EmailJS Setup:
- Sends real emails to users
- Professional password reset experience
- Secure and reliable

## 🔧 Testing

1. Go to `forgot-password.html`
2. Enter `michaelonascooter@gmail.com`
3. Click "Send Reset Link"
4. You'll see the password displayed (or receive an email if EmailJS is configured)

## 📱 Alternative: Simple Mailto Link

If you prefer a simpler approach, I can also implement a mailto link that opens the user's email client with pre-filled content. Would you like me to add that option as well?

## 🛠️ Troubleshooting

- **Email not sending?** Check your EmailJS configuration
- **Template not working?** Verify template variables match the code
- **Service not connecting?** Check your email provider settings in EmailJS

## 💡 Pro Tips

- EmailJS free tier allows 200 emails/month
- You can customize the email template with your branding
- Consider adding a "Change Password" feature after login
- For production, consider server-side email sending for better security
