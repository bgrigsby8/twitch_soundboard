import express, { json } from 'express';
import axios from 'axios';
import cors from 'cors';

const app = express();
const PORT = 5000;

// Enable CORS for all requests
app.use(cors());
app.use(json());

// Proxy route to fetch Streamlabs socket token
app.get('/socket/token', async (req, res) => {
  try {
    const response = await axios.get('https://streamlabs.com/api/v1.0/socket/token', {
      headers: {
        Authorization: `Bearer ${req.headers.authorization}`, // Pass the token from the frontend
      },
    });

    res.json(response.data);
  } catch (error) {
    console.error('Error fetching socket token:', error.response?.data || error.message);
    res.status(500).json({ error: 'Failed to fetch socket token' });
  }
});

app.listen(PORT, () => {
  console.log(`Proxy server running on http://localhost:${PORT}`);
});
