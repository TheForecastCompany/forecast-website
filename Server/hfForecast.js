// server/hfForecast.js
import express from 'express';
import { spawn } from 'child_process';
import path from 'path';
import { fileURLToPath } from 'url';

const router = express.Router();
const __filename = fileURLToPath(import.meta.url);
const __dirname = path.dirname(__filename);

router.post('/forecast', (req, res) => {
  const { date } = req.body;

  if (!date) {
    return res.status(400).json({ message: 'Date is required' });
  }

  const scriptPath = path.join(__dirname, 'huggingface_forecast.py');
  const python = spawn('python3', [scriptPath, date]);

  let data = '';
  python.stdout.on('data', (chunk) => {
    data += chunk.toString();
  });

  python.stderr.on('data', (err) => {
    console.error('Python error:', err.toString());
  });

  python.on('close', () => {
    try {
      const result = JSON.parse(data);
      res.json({ forecast: result[0], safeEstimate: result[1] });
    } catch (err) {
      console.error('Error parsing Python output:', err);
      res.status(500).json({ message: 'Internal server error' });
    }
  });
});

export default router;
