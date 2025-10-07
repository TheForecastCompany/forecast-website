// Simple authentication without Prisma for now
// TODO: Set up Prisma properly for production

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

    const { username, password } = req.body;

    if (!username || !password) {
        return res.status(400).json({ message: 'Missing credentials' });
    }

    // Simple hardcoded authentication for now
    const users = {
        'testuser': 'password123',
        'Wanda': 'buyyourownbeverage2019',
        'admin': 'password',
        'hospital': 'password123'
    };

    if (!users[username] || users[username] !== password) {
        return res.status(401).json({ message: 'Invalid username or password' });
    }

    res.json({
        message: 'Login successful',
        username: username,
    });
}
