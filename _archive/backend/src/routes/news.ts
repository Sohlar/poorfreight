import { Router, Request, Response } from 'express';
import { NewsModel } from '../db/models';
import { NewsQuery } from '../types';

const router = Router();

/**
 * GET /api/news
 * Query params:
 *   - source: comma-separated list of sources
 *   - q: text search
 *   - days: filter to last N days
 *   - limit: pagination limit (default 50)
 *   - offset: pagination offset (default 0)
 */
router.get('/', (req: Request, res: Response) => {
  try {
    const query: NewsQuery = {
      source: req.query.source as string | undefined,
      q: req.query.q as string | undefined,
      days: req.query.days ? parseInt(req.query.days as string) : undefined,
      limit: req.query.limit ? parseInt(req.query.limit as string) : 50,
      offset: req.query.offset ? parseInt(req.query.offset as string) : 0
    };

    const articles = NewsModel.query(query);
    const total = NewsModel.count(query);

    res.json({
      data: articles,
      total,
      limit: query.limit,
      offset: query.offset
    });
  } catch (error) {
    console.error('Error querying news:', error);
    res.status(500).json({ error: 'Failed to fetch news' });
  }
});

/**
 * GET /api/news/sources
 * Returns list of available news sources
 */
router.get('/sources', (req: Request, res: Response) => {
  try {
    const sources = [
      'FreightWaves',
      'Supply Chain Dive',
      'Transport Topics',
      'JOC'
    ];

    res.json({ data: sources });
  } catch (error) {
    console.error('Error fetching sources:', error);
    res.status(500).json({ error: 'Failed to fetch sources' });
  }
});

export default router;
