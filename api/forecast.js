import { spawn } from 'child_process';
import path from 'path';
import { fileURLToPath } from 'url';

const __filename = fileURLToPath(import.meta.url);
const __dirname = path.dirname(__filename);

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
        const scriptPath = path.join(process.cwd(), 'Server', 'hugging_forecast.py');
        const python = spawn('python3', [scriptPath, date]);

        let data = '';
        let errorData = '';

        python.stdout.on('data', (chunk) => {
            data += chunk.toString();
        });

        python.stderr.on('data', (err) => {
            errorData += err.toString();
            console.error('Python error:', err.toString());
        });

        python.on('close', (code) => {
            if (code !== 0) {
                console.error('Python script exited with code:', code);
                console.error('Error data:', errorData);
                return res.status(500).json({ message: 'Python script execution failed' });
            }

            try {
                const result = JSON.parse(data);
                res.json({ forecast: result[0], safeEstimate: result[1] });
            } catch (err) {
                console.error('Error parsing Python output:', err);
                console.error('Raw output:', data);
                res.status(500).json({ message: 'Error parsing forecast results' });
            }
        });

        python.on('error', (err) => {
            console.error('Failed to start Python process:', err);
            res.status(500).json({ message: 'Failed to start forecast process' });
        });

    } catch (error) {
        console.error('Forecast error:', error);
        res.status(500).json({ message: 'Internal server error' });
    }
}
