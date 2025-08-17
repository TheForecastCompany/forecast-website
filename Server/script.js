import express from 'express';
import cors from 'cors';
import bodyParser from 'body-parser';
import authRoutes from './authRoutes.js';
import axios from 'axios';  // ✅ use axios for Flask API call

const app = express();
const PORT = 3001;

app.use(cors());
app.use(bodyParser.json());

// Authentication routes
app.use('/api', authRoutes);

// ✅ New Forecast API route (calls Flask backend)
app.post("/api/forecast", async (req, res) => {
  try {
    // Forward the request to Flask API
    const response = await axios.post('http://127.0.0.1:5000/forecast', req.body);
    res.json(response.data);
  } catch (err) {
    console.error("Error calling Flask API:", err.message);
    res.status(500).json({ error: "Failed to get forecast" });
  }
});

app.listen(PORT, () => {
  console.log(`Server running on http://localhost:${PORT}`);
});
