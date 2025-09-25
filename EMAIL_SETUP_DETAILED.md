# 📧 Complete Email Setup Guide

## 🚀 Quick Setup (5 minutes)

### Step 1: Create EmailJS Account
1. Go to [https://www.emailjs.com/](https://www.emailjs.com/)
2. Click "Sign Up" and create account
3. Verify your email address

### Step 2: Add Email Service
1. In dashboard, go to "Email Services"
2. Click "Add New Service"
3. Choose "Gmail" (or your preferred provider)
4. Follow the setup instructions
5. **Copy your Service ID** (looks like: `service_abc123`)

### Step 3: Create Email Template
1. Go to "Email Templates"
2. Click "Create New Template"
3. Use this template:

**Template ID:** `password_reset` (or any name you want)

**Subject:** `Password Reset - {{company_name}}`

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

4. **Save the template** and copy the Template ID

### Step 4: Get Public Key
1. Go to "Account" → "General"
2. **Copy your Public Key** (looks like: `user_abc123def456`)

### Step 5: Update the Code
Replace these lines in `forgot-password.html`:

```javascript
// Find these lines around line 254-256:
const serviceId = 'YOUR_SERVICE_ID'; // Replace with your Service ID
const templateId = 'YOUR_TEMPLATE_ID'; // Replace with your Template ID  
const publicKey = 'YOUR_PUBLIC_KEY'; // Replace with your Public Key
```

**Example:**
```javascript
const serviceId = 'service_abc123';
const templateId = 'password_reset';
const publicKey = 'user_abc123def456';
```

## 🎯 How It Works

1. **User enters email** → System checks if email exists
2. **If email exists** → EmailJS sends real email with password
3. **If email doesn't exist** → Shows error message
4. **If EmailJS fails** → Shows password on screen as fallback

## ✅ Testing

1. Set up EmailJS (5 minutes)
2. Update the 3 keys in the code
3. Test with `michaelonascooter@gmail.com`
4. Check your email inbox!

## 🔧 Alternative: Server-Side Email

For production, you might want server-side email sending using:
- **Node.js + Nodemailer**
- **Python + SMTP**
- **PHP + Mail**
- **AWS SES**
- **SendGrid**

But EmailJS is perfect for your current setup!

