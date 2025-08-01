import express from 'express';
import prisma from './prismaClient.js';

const router = express.Router();

router.post('/login', async (req, res) => {
  const { username, password } = req.body;

  if (!username || !password) {
    return res.status(400).json({ message: 'Missing credentials' });
  }

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
});

export default router;