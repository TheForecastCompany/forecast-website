// Import Prisma client
const { PrismaClient } = require('@prisma/client');

const prisma = new PrismaClient();

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

    try {
        const user = await prisma.user.findUnique({
            where: { username },
        });

        if (!user || user.password !== password) {
            return res.status(401).json({ message: 'Invalid username or password' });
        }

        res.json({
            message: 'Login successful',
            username: user.username,
        });
    } catch (error) {
        console.error('Login error:', error);
        res.status(500).json({ message: 'Internal server error' });
    } finally {
        await prisma.$disconnect();
    }
}
