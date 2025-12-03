import Parser from 'rss-parser';
import { NewsModel } from '../db/models';
import { NewsArticle } from '../types';
import crypto from 'crypto';

const parser = new Parser({
  customFields: {
    item: [
      ['description', 'description'],
      ['content:encoded', 'contentEncoded'],
      ['summary', 'summary']
    ]
  }
});

interface RSSSource {
  name: string;
  url: string;
}

const RSS_SOURCES: RSSSource[] = [
  {
    name: 'FreightWaves',
    url: 'https://www.freightwaves.com/feed'
  },
  {
    name: 'Supply Chain Dive',
    url: 'https://www.supplychaindive.com/feeds/news/'
  },
  {
    name: 'Transport Topics',
    url: 'https://www.ttnews.com/rss/feed/top-news'
  },
  {
    name: 'JOC',
    url: 'https://www.joc.com/rss/all-categories'
  }
];

function generateId(source: string, title: string, url: string): string {
  return crypto.createHash('md5').update(`${source}-${url}`).digest('hex');
}

function extractSummary(item: any): string {
  // Try multiple fields for summary/description
  const content = item.contentEncoded || item.description || item.summary || item.content || '';

  // Strip HTML tags
  const stripped = content.replace(/<[^>]*>/g, '');

  // Decode HTML entities
  const decoded = stripped
    .replace(/&nbsp;/g, ' ')
    .replace(/&amp;/g, '&')
    .replace(/&lt;/g, '<')
    .replace(/&gt;/g, '>')
    .replace(/&quot;/g, '"')
    .replace(/&#39;/g, "'");

  // Truncate to 300 characters
  return decoded.substring(0, 300).trim() + (decoded.length > 300 ? '...' : '');
}

async function fetchFeed(source: RSSSource): Promise<NewsArticle[]> {
  try {
    console.log(`Fetching ${source.name}...`);
    const feed = await parser.parseURL(source.url);

    const articles: NewsArticle[] = feed.items.map(item => ({
      id: generateId(source.name, item.title || '', item.link || ''),
      source: source.name,
      title: item.title || 'Untitled',
      url: item.link || '',
      published_at: item.isoDate || item.pubDate || new Date().toISOString(),
      summary: extractSummary(item)
    }));

    console.log(`  Found ${articles.length} articles from ${source.name}`);
    return articles;
  } catch (error) {
    console.error(`Error fetching ${source.name}:`, error);
    return [];
  }
}

async function ingestAllNews(): Promise<void> {
  console.log('Starting news ingestion...');

  const allArticles: NewsArticle[] = [];

  for (const source of RSS_SOURCES) {
    const articles = await fetchFeed(source);
    allArticles.push(...articles);
  }

  if (allArticles.length > 0) {
    const inserted = NewsModel.insertMany(allArticles);
    console.log(`\nInserted/updated ${inserted} total articles`);
  } else {
    console.log('\nNo articles to insert');
  }
}

// Run if called directly
if (require.main === module) {
  ingestAllNews()
    .then(() => {
      console.log('News ingestion complete!');
      process.exit(0);
    })
    .catch(error => {
      console.error('News ingestion failed:', error);
      process.exit(1);
    });
}

export { ingestAllNews };
