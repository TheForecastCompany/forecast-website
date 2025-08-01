// server/index.js
import express from 'express';
import cors from 'cors';
import bodyParser from 'body-parser';
import authRoutes from './authRoutes.js';

const app = express();
const PORT = 3001;

app.use(cors());
app.use(bodyParser.json());

app.use('/api', authRoutes);

app.listen(PORT, () => {
  console.log(`Server running on http://localhost:${PORT}`);
});