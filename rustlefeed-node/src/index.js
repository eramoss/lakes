import express from 'express';
import { FeedManager } from './feedManager.js';
import { NaiveBayesClassifier } from './classifier.js';
import { Persistence } from './persistence.js';
import { entryToHtml } from './parser.js';
import path from 'path';
import { fileURLToPath } from 'url';

const __dirname = path.dirname(fileURLToPath(import.meta.url));
const app = express();
const PORT = 3000;

app.use(express.json());
app.use(express.static(path.join(__dirname, '../assets')));

const dbPath = path.join(__dirname, '../db/FeedHistory.db');
const persistence = new Persistence(dbPath);

let manager = new FeedManager();
let classifier = new NaiveBayesClassifier();

async function initializeApp() {
  persistence.loadFeedsFromDb(manager);
  await manager.sync();
  classifier = persistence.loadClassifier();
}

app.post('/next', (req, res) => {
  const { liked } = req.body;

  if (liked !== null && liked !== undefined) {
    const last = manager.toSee.pop();
    if (last) {
      manager.alreadySeen.push([last, liked]);
    }
  }

  while (manager.toSee.length > 0) {
    const current = manager.toSee[manager.toSee.length - 1];
    const possibility = classifier.classify(current);

    if (possibility >= 0.5) {
      const isDuplicate = manager.alreadySeen.some(
        ([e]) => e.guid === current.guid
      );
      if (isDuplicate) {
        manager.toSee.pop();
        continue;
      }
      return res.send(entryToHtml(current));
    }
    manager.toSee.pop();
  }

  res.send('No more entries');
});

app.post('/add-feed', async (req, res) => {
  const { url } = req.body;

  if (manager.getFeed(url)) {
    return res.status(400).json({ error: 'Feed already added' });
  }

  try {
    await manager.newFeed(url);
    res.status(202).json({ message: 'Feed addition task started' });
  } catch (err) {
    res.status(400).json({ error: 'Error adding feed' });
  }
});

app.post('/delete-feed', async (req, res) => {
  const { url } = req.body;

  try {
    persistence.purgeFeed(manager, url);
    await manager.sync();
    res.status(202).json({ message: 'Feed deletion task started' });
  } catch (err) {
    res.status(400).json({ error: 'Error deleting feed' });
  }
});

app.get('/feeds', (req, res) => {
  const feeds = Array.from(manager.feeds.entries()).map(([url, feed]) => ({
    title: feed.title || url,
    url
  }));
  res.json(feeds);
});

app.get('/', (req, res) => {
  res.sendFile(path.join(__dirname, '../assets/index.html'));
});

app.get('/:file(*)', (req, res) => {
  res.sendFile(path.join(__dirname, '../assets', req.params.file));
});

app.listen(PORT, async () => {
  await initializeApp();
  console.log(`Server running at http://localhost:${PORT}`);
});

// Graceful shutdown
process.on('SIGINT', () => {
  persistence.saveAlreadySeen(manager.alreadySeen);
  persistence.saveFeeds(manager);
  process.exit(0);
});


export async function seedDatabase() {
  const sampleFeeds = [
    'https://news.ycombinator.com/rss',
		'https://stackoverflow.blog/feed/',
		'http://feeds.bbci.co.uk/news/world/rss.xml',
    'https://feeds.arstechnica.com/arstechnica/index',
    'https://www.theverge.com/rss/index.xml'
  ];

  console.log('Seeding database with sample feeds...');
  
  for (const feedUrl of sampleFeeds) {
    try {
      console.log(`Adding feed: ${feedUrl}`);
      await manager.newFeed(feedUrl);
      console.log(`✓ Successfully added: ${feedUrl}`);
    } catch (err) {
      console.error(`✗ Failed to add ${feedUrl}:`, err.message);
    }
  }

  persistence.saveFeeds(manager);
  
  // Generate training data by marking entries as liked/disliked
  console.log('\nGenerating training data...');
  const trainingDataSize = Math.min(150, manager.toSee.length);
  
  for (let i = 0; i < trainingDataSize; i++) {
    if (manager.toSee.length === 0) break;
    
    const entry = manager.toSee.pop();
    // Simulate user preference: like entries with certain keywords
    const likeKeywords = ['ai', 'machine learning', 'javascript', 'node', 'tech', 'open source'];
    const entryText = `${entry.title} ${entry.summary} ${entry.content}`.toLowerCase();
    const isLiked = likeKeywords.some(keyword => entryText.includes(keyword));
    
    manager.alreadySeen.push([entry, isLiked]);
    if ((i + 1) % 25 === 0) {
      console.log(`Generated ${i + 1} training entries...`);
    }
  }

  persistence.saveAlreadySeen(manager.alreadySeen);
  console.log(`\nDatabase seeded with ${manager.alreadySeen.length} training entries!`);
  console.log('Classifier is now ready to use.');
  process.exit(0);
}

// Run seed if called with --seed flag
if (process.argv[2] === '--seed') {
  seedDatabase().catch(err => {
    console.error('Seed failed:', err);
    process.exit(1);
  });
}
