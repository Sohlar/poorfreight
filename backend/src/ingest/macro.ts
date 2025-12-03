import { MacroMetricsModel } from '../db/models';
import { MacroMetric } from '../types';
import { format, subMonths } from 'date-fns';

/**
 * Ingest macro freight indices
 *
 * In production, these would be scraped from:
 * - Cass Freight Index: https://www.cassinfo.com/freight-audit-indexes
 * - ATA Truck Tonnage Index: https://www.trucking.org/
 * - FTR Trucking Conditions Index: https://ftrintel.com/
 *
 * For this demo, we'll generate realistic synthetic data
 */

async function ingestMacroMetrics(): Promise<void> {
  try {
    console.log('Generating macro metrics...');

    // Generate data for the last 24 months
    const months = 24;
    const today = new Date();

    // Base indices (normalized to ~100-130 range)
    let cassBase = 120.5;
    let ataBase = 115.2;
    let ftrBase = 8.5; // FTR uses a different scale (-10 to +10)

    for (let i = months; i >= 0; i--) {
      const date = subMonths(today, i);
      const month = format(date, 'yyyy-MM');

      // Add monthly volatility with trends
      const monthlyChange = (Math.random() - 0.52) * 0.03; // Slight downward trend
      cassBase *= (1 + monthlyChange);
      ataBase *= (1 + monthlyChange * 1.1);
      ftrBase += (Math.random() - 0.55) * 0.8; // FTR has different dynamics

      // Keep FTR in reasonable bounds (-10 to +10)
      ftrBase = Math.max(-10, Math.min(10, ftrBase));

      const metric: MacroMetric = {
        month,
        cass_shipments_index: parseFloat(cassBase.toFixed(2)),
        ata_tonnage_index: parseFloat(ataBase.toFixed(2)),
        ftr_trucking_conditions_index: parseFloat(ftrBase.toFixed(2))
      };

      MacroMetricsModel.upsert(metric);
    }

    console.log(`  Generated macro metrics for ${months + 1} months`);
    console.log('  Note: Using synthetic data. Replace with actual scraping for production.');
  } catch (error) {
    console.error('Error generating macro metrics:', error);
  }
}

async function ingestAllMacro(): Promise<void> {
  console.log('Starting macro metrics ingestion...');
  await ingestMacroMetrics();
  console.log('Macro metrics ingestion complete!');
}

// Run if called directly
if (require.main === module) {
  ingestAllMacro()
    .then(() => {
      process.exit(0);
    })
    .catch(error => {
      console.error('Macro metrics ingestion failed:', error);
      process.exit(1);
    });
}

export { ingestAllMacro };
