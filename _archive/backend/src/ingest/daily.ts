import axios from 'axios';
import * as cheerio from 'cheerio';
import { DailyMetricsModel } from '../db/models';
import { DailyMetric } from '../types';
import { format, subDays } from 'date-fns';

/**
 * Ingest diesel prices from EIA (U.S. Energy Information Administration)
 * Using their open data API for U.S. No 2 Diesel Retail Prices
 */
async function ingestDieselPrices(): Promise<void> {
  try {
    console.log('Fetching diesel prices from EIA...');

    // EIA API endpoint for weekly retail diesel prices
    // This is a free API, but rate limited. We can also scrape their website as fallback
    const url = 'https://www.eia.gov/dnav/pet/hist/LeafHandler.ashx?n=pet&s=emd_epd2d_pte_nus_dpg&f=w';

    const response = await axios.get(url, {
      headers: {
        'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36'
      }
    });

    const $ = cheerio.load(response.data);

    // Parse the table data
    const prices: { date: string; price: number }[] = [];

    $('table.FloatTitle tr').each((i, row) => {
      if (i === 0) return; // Skip header

      const cells = $(row).find('td');
      if (cells.length >= 2) {
        const dateText = $(cells[0]).text().trim();
        const priceText = $(cells[1]).text().trim();

        // Parse date (format: "Dec 02, 2024")
        const date = new Date(dateText);
        if (!isNaN(date.getTime())) {
          const price = parseFloat(priceText);
          if (!isNaN(price)) {
            prices.push({
              date: format(date, 'yyyy-MM-dd'),
              price
            });
          }
        }
      }
    });

    console.log(`  Found ${prices.length} diesel price records`);

    // Upsert to database
    for (const { date, price } of prices) {
      DailyMetricsModel.upsert({
        date,
        van_spot_index: null,
        reefer_spot_index: null,
        flatbed_spot_index: null,
        diesel_usd_per_gal: price
      });
    }

    console.log('  Diesel prices updated');
  } catch (error) {
    console.error('Error fetching diesel prices:', error);
  }
}

/**
 * Generate synthetic spot rate indices based on typical patterns
 * In a production app, you would scrape DAT, Truckstop.com, or similar sources
 * This creates realistic-looking data for demonstration purposes
 */
async function ingestSpotRates(): Promise<void> {
  try {
    console.log('Generating spot rate indices...');

    // Generate data for the last 90 days
    const days = 90;
    const today = new Date();

    // Base indices (typical national averages per mile, scaled to index)
    let vanBase = 2.20;
    let reeferBase = 2.65;
    let flatbedBase = 2.45;

    for (let i = days; i >= 0; i--) {
      const date = format(subDays(today, i), 'yyyy-MM-dd');

      // Add some realistic volatility
      const dailyChange = (Math.random() - 0.48) * 0.08; // Slight downward bias
      vanBase *= (1 + dailyChange);
      reeferBase *= (1 + dailyChange * 0.9); // Slightly less volatile
      flatbedBase *= (1 + dailyChange * 1.1); // Slightly more volatile

      // Seasonal adjustment (weaker in late fall/winter typically)
      const seasonalFactor = 1 - (Math.sin((i / 90) * Math.PI) * 0.1);

      DailyMetricsModel.upsert({
        date,
        van_spot_index: parseFloat((vanBase * seasonalFactor).toFixed(3)),
        reefer_spot_index: parseFloat((reeferBase * seasonalFactor * 1.05).toFixed(3)),
        flatbed_spot_index: parseFloat((flatbedBase * seasonalFactor * 0.98).toFixed(3)),
        diesel_usd_per_gal: null
      });
    }

    console.log(`  Generated spot rates for ${days + 1} days`);
    console.log('  Note: Using synthetic data. Replace with DAT/Truckstop scraper for production.');
  } catch (error) {
    console.error('Error generating spot rates:', error);
  }
}

async function ingestAllDaily(): Promise<void> {
  console.log('Starting daily metrics ingestion...');
  await ingestSpotRates();
  await ingestDieselPrices();
  console.log('Daily metrics ingestion complete!');
}

// Run if called directly
if (require.main === module) {
  ingestAllDaily()
    .then(() => {
      process.exit(0);
    })
    .catch(error => {
      console.error('Daily metrics ingestion failed:', error);
      process.exit(1);
    });
}

export { ingestAllDaily };
