import { v4 as uuidv4 } from 'uuid';
import FeedParser from 'feedparser';
import request from 'request';

export class FeedManager {
  constructor() {
    this.feeds = new Map();
    this.toSee = [];
    this.alreadySeen = [];
  }

  async newFeed(url) {
    await this.addFeed(url);
    await this.sync();
    return this.getFeed(url);
  }

  async addFeed(url) {
    if (!this.feeds.has(url)) {
      this.feeds.set(url, { id: uuidv4(), entries: [] });
    }
  }

  removeFeedByUrl(url) {
    this.feeds.delete(url);
  }

  getFeed(url) {
    return this.feeds.get(url);
  }

  async sync() {
    this.toSee = [];
    const tasks = [];

    for (const url of this.feeds.keys()) {
      tasks.push(this.fetchFeed(url));
    }

    const results = await Promise.allSettled(tasks);
    
    for (const result of results) {
      if (result.status === 'fulfilled') {
        const { url, entries } = result.value;
        this.feeds.set(url, { 
          id: this.feeds.get(url)?.id || uuidv4(), 
          entries 
        });

        for (const entry of entries) {
          if (!this.toSee.some(e => e.guid === entry.guid)) {
            this.toSee.push(entry);
          }
        }
      }
    }
  }

  fetchFeed(url) {
    return new Promise((resolve, reject) => {
      const entries = [];
      const req = request(url);

      req.on('error', reject);

      req.pipe(new FeedParser())
        .on('error', reject)
        .on('meta', function(meta) {
          // Feed metadata available
        })
        .on('readable', function() {
          let entry;
          while (entry = this.read()) {
            entries.push({
              guid: entry.guid || entry.link,
              title: entry.title || '',
              link: entry.link || '',
              description: entry.description || '',
              summary: entry.summary || '',
              author: entry.author || '',
              categories: entry.categories || [],
              date: entry.pubdate || new Date(),
              content: entry.content || entry.description || ''
            });
          }
        })
        .on('end', () => {
          resolve({ url, entries });
        });
    });
  }
}
