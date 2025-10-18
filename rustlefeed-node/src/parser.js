export function entryToHtml(entry) {
  const categories = Array.isArray(entry.categories) 
    ? entry.categories.join(', ') 
    : '';
  
  return `
    <h1 class="feed-item-title">${escapeHtml(entry.title)}</h1>
    <p>${escapeHtml(new Date(entry.date).toString())}</p>
    <p class="feed-item-summary">${escapeHtml(entry.author)}</p>
    <p class="feed-item-summary">${escapeHtml(categories)}</p>
    <p class="feed-item-summary">${escapeHtml(entry.summary)}</p>
    <p class="feed-item-content">${entry.content}</p>
    <a class="feed-item-link" href="${escapeHtml(entry.link)}">Read more</a>
  `;
}

function escapeHtml(str) {
  const div = document.createElement('div');
  div.textContent = str;
  return div.innerHTML;
}
