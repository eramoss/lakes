export class NaiveBayesClassifier {
  constructor(alpha = 1.0) {
    this.alpha = alpha;
    this.tokens = new Set();
    this.tokenLikedCounts = new Map();
    this.tokenDislikedCounts = new Map();
    this.dislikedEntriesCount = 0;
    this.likedEntriesCount = 0;
    this.isPrepared = false;
  }

  static tokenize(text) {
    const regex = /[a-z0-9']+/g;
    const matches = text.match(regex) || [];
    return new Set(matches);
  }

  train(entries) {
    for (const entry of entries) {
      this.incrementEntryClassificationCount(entry);
      const tokens = NaiveBayesClassifier.tokenize(entry.allContent.toLowerCase());
      
      for (const token of tokens) {
        this.tokens.add(token);
        this.incrementTokenCount(token, entry.liked);
      }
    }
  }

  classify(entry) {
    if (!this.isPrepared) return 1.0;
		console.log("classifing: ", entry);
    const allContent = `${entry.title} ${entry.summary} ${entry.content} ${entry.author} ${entry.categories.join(' ')} ${entry.link}`.toLowerCase();
    const messageTokens = NaiveBayesClassifier.tokenize(allContent);
    const [probIfDislike, probIfLike] = this.probabilitiesOfMessage(messageTokens);
    
    return probIfLike / (probIfLike + probIfDislike);
  }

  probabilitiesOfMessage(messageTokens) {
    let logProbIfDislike = 0;
    let logProbIfLike = 0;
    const epsilon = 1e-9;

    for (const token of this.tokens) {
      const [probIfDisliked, probIfLike] = this.probabilitiesOfToken(token);
      
      const pDisliked = Math.max(epsilon, Math.min(1 - epsilon, probIfDisliked));
      const pLike = Math.max(epsilon, Math.min(1 - epsilon, probIfLike));

      if (messageTokens.has(token)) {
        logProbIfDislike += Math.log(pDisliked);
        logProbIfLike += Math.log(pLike);
      } else {
        logProbIfDislike += Math.log(1 - pDisliked);
        logProbIfLike += Math.log(1 - pLike);
      }
    }

    return [Math.exp(logProbIfDislike), Math.exp(logProbIfLike)];
  }

  probabilitiesOfToken(token) {
    const dislikedCount = this.tokenDislikedCounts.get(token) || 0;
    const likedCount = this.tokenLikedCounts.get(token) || 0;

    const probDisliked = (dislikedCount + this.alpha) / 
      (this.dislikedEntriesCount + 2 * this.alpha);
    const probLiked = (likedCount + this.alpha) / 
      (this.likedEntriesCount + 2 * this.alpha);

    return [probDisliked, probLiked];
  }

  incrementEntryClassificationCount(entry) {
    if (entry.liked) {
      this.dislikedEntriesCount++;
    } else {
      this.likedEntriesCount++;
    }
  }

  incrementTokenCount(token, liked) {
    if (!this.tokenDislikedCounts.has(token)) {
      this.tokenDislikedCounts.set(token, 0);
    }
    if (!this.tokenLikedCounts.has(token)) {
      this.tokenLikedCounts.set(token, 0);
    }

    if (liked) {
      this.tokenLikedCounts.set(token, (this.tokenLikedCounts.get(token) || 0) + 1);
    } else {
      this.tokenDislikedCounts.set(token, (this.tokenDislikedCounts.get(token) || 0) + 1);
    }
  }
}
