import nodemailer from 'nodemailer';

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
const transporter = nodemailer.createTransport({
    service: 'gmail', // or your email provider
    auth: {
        user: process.env.EMAIL_USER || 'your-email@gmail.com', // Use environment variable
        pass: process.env.EMAIL_PASS || 'your-app-password' // Use environment variable
    }
});

export default async function handler(req, res) {
    // Enable CORS
    res.setHeader('Access-Control-Allow-Credentials', true);
    res.setHeader('Access-Control-Allow-Origin', '*');
    res.setHeader('Access-Control-Allow-Methods', 'GET,OPTIONS,PATCH,DELETE,POST,PUT');
    res.setHeader('Access-Control-Allow-Headers', 'X-CSRF-Token, X-Requested-With, Accept, Accept-Version, Content-Length, Content-MD5, Content-Type, Date, X-Api-Version');

    if (req.method === 'OPTIONS') {
        res.status(200).end();
        return;
    }

    if (req.method !== 'POST') {
        return res.status(405).json({ message: 'Method not allowed' });
    }

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
            from: process.env.EMAIL_USER || 'your-email@gmail.com',
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
                <p>Please log in at: <a href="${process.env.VERCEL_URL ? `https://${process.env.VERCEL_URL}` : 'http://localhost:3000'}/login.html">Login Page</a></p>
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
}
