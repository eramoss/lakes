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
    title: feed.title || 'Untitled',
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
