const express = require('express');
const nodemailer = require('nodemailer');
const cors = require('cors');
const app = express();
const port = 3000;

// Middleware
app.use(cors());
app.use(express.json());

// Email database (same as frontend)
const emailDatabase = {
    'michaelonascooter@gmail.com': { 
        username: 'testuser', 
        password: 'password123', 
        company: 'Thomas Jefferson University Hospital' 
    },
    'wanda@forecasting.com': { 
        username: 'Wanda', 
        password: 'buyyourownbeverage2019', 
        company: 'Wanda BYOB Restaurant' 
    },
    'admin@forecasting.com': { 
        username: 'admin', 
        password: 'password', 
        company: 'Admin Panel' 
    },
    'hospital@forecasting.com': { 
        username: 'hospital', 
        password: 'password123', 
        company: 'Thomas Jefferson University Hospital' 
    }
};

// Email configuration (replace with your email settings)
const transporter = nodemailer.createTransporter({
    service: 'gmail', // or your email provider
    auth: {
        user: 'your-email@gmail.com', // Replace with your email
        pass: 'your-app-password' // Replace with your app password
    }
});

// Password reset endpoint
app.post('/api/forgot-password', async (req, res) => {
    const { email } = req.body;
    
    if (!emailDatabase[email]) {
        return res.status(404).json({ 
            success: false, 
            message: 'Email not found in our system' 
        });
    }
    
    const userData = emailDatabase[email];
    
    try {
        // Send email
        await transporter.sendMail({
            from: 'your-email@gmail.com',
            to: email,
            subject: `Password Reset - ${userData.company}`,
            html: `
                <h2>Password Reset Request</h2>
                <p>Hello ${userData.username},</p>
                <p>You requested a password reset for your ${userData.company} account.</p>
                <p><strong>Your login credentials:</strong></p>
                <ul>
                    <li>Username: ${userData.username}</li>
                    <li>Password: ${userData.password}</li>
                </ul>
                <p>Please log in at: <a href="http://localhost:8000/login.html">http://localhost:8000/login.html</a></p>
                <p>If you didn't request this reset, please ignore this email.</p>
                <p>Best regards,<br>The Forecasting Company Team</p>
            `
        });
        
        res.json({ 
            success: true, 
            message: `Password reset email sent to ${email}` 
        });
        
    } catch (error) {
        console.error('Email sending error:', error);
        res.status(500).json({ 
            success: false, 
            message: 'Failed to send email' 
        });
    }
});

app.listen(port, () => {
    console.log(`Email server running at http://localhost:${port}`);
});

