import express, { Request, Response } from 'express';
import cors from 'cors';
import dotenv from 'dotenv';
import newsRoutes from './routes/news';
import metricsRoutes from './routes/metrics';

// Load environment variables
dotenv.config();

const app = express();
const PORT = process.env.PORT || 3001;

// Middleware
app.use(cors());
app.use(express.json());

// Request logging
app.use((req: Request, res: Response, next) => {
  console.log(`${new Date().toISOString()} - ${req.method} ${req.path}`);
  next();
});

// Health check
app.get('/health', (req: Request, res: Response) => {
  res.json({ status: 'ok', timestamp: new Date().toISOString() });
});

// API routes
app.use('/api/news', newsRoutes);
app.use('/api/metrics', metricsRoutes);

// 404 handler
app.use((req: Request, res: Response) => {
  res.status(404).json({ error: 'Not found' });
});

// Error handler
app.use((err: Error, req: Request, res: Response, next: any) => {
  console.error('Error:', err);
  res.status(500).json({ error: 'Internal server error' });
});

// Start server
app.listen(PORT, () => {
  console.log(`\n🚚 Freight Intelligence API Server`);
  console.log(`📡 Listening on http://localhost:${PORT}`);
  console.log(`\nAvailable endpoints:`);
  console.log(`  GET  /health`);
  console.log(`  GET  /api/news`);
  console.log(`  GET  /api/news/sources`);
  console.log(`  GET  /api/metrics/daily`);
  console.log(`  GET  /api/metrics/daily/latest`);
  console.log(`  GET  /api/metrics/macro`);
  console.log(`\nRun data ingestion:`);
  console.log(`  npm run ingest:all`);
  console.log(``);
});

export default app;
