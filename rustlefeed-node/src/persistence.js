
import Database from 'better-sqlite3';
import { NaiveBayesClassifier } from './classifier.js';

export class Persistence {
  constructor(dbPath) {
    this.db = new Database(dbPath);
    this.initTables();
  }

  initTables() {
    this.db.exec(`
      CREATE TABLE IF NOT EXISTS already_seen (
        id TEXT PRIMARY KEY,
        title TEXT,
        authors TEXT,
        content TEXT,
        links TEXT,
        summary TEXT,
        categories TEXT,
        language TEXT,
        is_liked INTEGER
      );

      CREATE TABLE IF NOT EXISTS feeds (
        id TEXT PRIMARY KEY,
        url TEXT
      );
    `);
  }

  saveAlreadySeen(alreadySeen) {
    const insert = this.db.prepare(`
      INSERT OR REPLACE INTO already_seen 
      (id, title, authors, content, links, summary, categories, language, is_liked)
      VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
    `);

    for (const [entry, isLiked] of alreadySeen) {
      insert.run(
        entry.guid,
        entry.title,
        JSON.stringify([entry.author].filter(Boolean)),
        entry.content,
        entry.link,
        entry.summary,
        JSON.stringify(entry.categories),
        '',
        isLiked ? 1 : 0
      );
    }
  }

  loadFeedsFromDb(manager) {
    const rows = this.db.prepare('SELECT url FROM feeds').all();
    for (const row of rows) {
      manager.addFeed(row.url);
    }
  }

  saveFeeds(manager) {
    const insert = this.db.prepare('INSERT OR REPLACE INTO feeds (id, url) VALUES (?, ?)');
    for (const [url, feed] of manager.feeds) {
      insert.run(feed.id, url);
    }
  }

  purgeFeed(manager, url) {
    this.db.prepare('DELETE FROM feeds WHERE url = ?').run(url);
    manager.removeFeedByUrl(url);
  }

  loadClassifier() {
    const rows = this.db.prepare('SELECT * FROM already_seen').all();
    const classifier = new NaiveBayesClassifier(1.0);
    
    if (rows.length > 100) {
      const entries = rows.map(row => ({
        allContent: `${row.title} ${row.summary} ${row.content} ${row.authors} ${row.categories} ${row.links}`,
        liked: row.is_liked === 1
      }));
      classifier.train(entries);
      classifier.isPrepared = true;
    }

    return classifier;
  }
}

