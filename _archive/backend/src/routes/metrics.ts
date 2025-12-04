import { Router, Request, Response } from 'express';
import { DailyMetricsModel, MacroMetricsModel } from '../db/models';
import { MetricsQuery } from '../types';
import { format, subDays } from 'date-fns';

const router = Router();

/**
 * GET /api/metrics/daily
 * Query params:
 *   - from: start date (YYYY-MM-DD)
 *   - to: end date (YYYY-MM-DD)
 */
router.get('/daily', (req: Request, res: Response) => {
  try {
    const query: MetricsQuery = {
      from: req.query.from as string | undefined,
      to: req.query.to as string | undefined
    };

    // Default to last 90 days if no range specified
    if (!query.from && !query.to) {
      query.from = format(subDays(new Date(), 90), 'yyyy-MM-dd');
      query.to = format(new Date(), 'yyyy-MM-dd');
    }

    const metrics = DailyMetricsModel.query(query);

    res.json({ data: metrics });
  } catch (error) {
    console.error('Error querying daily metrics:', error);
    res.status(500).json({ error: 'Failed to fetch daily metrics' });
  }
});

/**
 * GET /api/metrics/daily/latest
 * Returns the most recent daily metrics with comparison to previous period
 */
router.get('/daily/latest', (req: Request, res: Response) => {
  try {
    const latest = DailyMetricsModel.getLatest();

    if (!latest) {
      return res.status(404).json({ error: 'No metrics available' });
    }

    const previous = DailyMetricsModel.getPrevious(latest.date);

    // Calculate changes
    const changes = previous
      ? {
          van_spot_change: latest.van_spot_index && previous.van_spot_index
            ? latest.van_spot_index - previous.van_spot_index
            : null,
          reefer_spot_change: latest.reefer_spot_index && previous.reefer_spot_index
            ? latest.reefer_spot_index - previous.reefer_spot_index
            : null,
          flatbed_spot_change: latest.flatbed_spot_index && previous.flatbed_spot_index
            ? latest.flatbed_spot_index - previous.flatbed_spot_index
            : null,
          diesel_change: latest.diesel_usd_per_gal && previous.diesel_usd_per_gal
            ? latest.diesel_usd_per_gal - previous.diesel_usd_per_gal
            : null
        }
      : null;

    res.json({
      data: latest,
      previous,
      changes
    });
  } catch (error) {
    console.error('Error fetching latest metrics:', error);
    res.status(500).json({ error: 'Failed to fetch latest metrics' });
  }
});

/**
 * GET /api/metrics/macro
 * Query params:
 *   - from: start month (YYYY-MM)
 *   - to: end month (YYYY-MM)
 */
router.get('/macro', (req: Request, res: Response) => {
  try {
    const query: MetricsQuery = {
      from: req.query.from as string | undefined,
      to: req.query.to as string | undefined
    };

    const metrics = query.from || query.to
      ? MacroMetricsModel.query(query)
      : MacroMetricsModel.getAll();

    res.json({ data: metrics });
  } catch (error) {
    console.error('Error querying macro metrics:', error);
    res.status(500).json({ error: 'Failed to fetch macro metrics' });
  }
});

export default router;
