// Mock forecast API - Python execution not supported on Vercel
// TODO: Implement proper forecast logic or use external API

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

    const { date } = req.body;

    if (!date) {
        return res.status(400).json({ message: 'Date is required' });
    }

    try {
        // Mock forecast data for now
        // In production, you would implement proper forecast logic here
        const mockForecast = {
            forecast: Math.floor(Math.random() * 10000) + 5000, // Random forecast between 5000-15000
            safeEstimate: Math.floor(Math.random() * 12000) + 6000 // Random safe estimate between 6000-18000
        };

        res.json(mockForecast);
    } catch (error) {
        console.error('Forecast error:', error);
        res.status(500).json({ message: 'Internal server error' });
    }
}
