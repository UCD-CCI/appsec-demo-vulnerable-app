const STORAGE_KEY = 'break-ai-app-workshop-notes-v1';
const statusNode = document.getElementById('notes-status');
const challengeNodes = [...document.querySelectorAll('.notes-challenge')];

function collectNotes() {
  return challengeNodes.map(section => ({
    number: section.dataset.number,
    title: section.dataset.title,
    fields: Object.fromEntries(
      [...section.querySelectorAll('textarea')].map(area => [area.dataset.field, area.value])
    )
  }));
}

function storeNotes(message = 'Autosaved') {
  localStorage.setItem(STORAGE_KEY, JSON.stringify(collectNotes()));
  if (statusNode) {
    statusNode.textContent = message;
    window.setTimeout(() => { statusNode.textContent = ''; }, 1600);
  }
}

function restoreNotes() {
  const raw = localStorage.getItem(STORAGE_KEY);
  if (!raw) return;
  try {
    const saved = JSON.parse(raw);
    saved.forEach(savedSection => {
      const section = challengeNodes.find(node => node.dataset.number === savedSection.number);
      if (!section) return;
      Object.entries(savedSection.fields || {}).forEach(([field, value]) => {
        const area = section.querySelector(`[data-field="${field}"]`);
        if (area) area.value = value;
      });
    });
  } catch (_) {
    localStorage.removeItem(STORAGE_KEY);
  }
}

function markdownText() {
  const lines = [
    '# Break the AI App — Workshop Notes',
    '',
    `Generated: ${new Date().toLocaleString()}`,
    ''
  ];
  collectNotes().forEach(section => {
    lines.push(`## Challenge ${section.number} — ${section.title}`, '');
    lines.push('### FLAG', section.fields.flag || '', '');
    lines.push('### Root cause', section.fields['root-cause'] || '', '');
    lines.push('### Business impact', section.fields['business-impact'] || '', '');
    lines.push('### Remediation', section.fields.remediation || '', '');
  });
  return lines.join('\n');
}

async function saveMarkdown() {
  storeNotes('Saved in browser');
  const content = markdownText();
  const suggestedName = 'break-ai-app-workshop-notes.md';

  if ('showSaveFilePicker' in window) {
    try {
      const handle = await window.showSaveFilePicker({
        suggestedName,
        types: [{description: 'Markdown document', accept: {'text/markdown': ['.md']}}]
      });
      const writable = await handle.createWritable();
      await writable.write(content);
      await writable.close();
      statusNode.textContent = 'Markdown file saved';
      return;
    } catch (error) {
      if (error.name === 'AbortError') return;
    }
  }

  const blob = new Blob([content], {type: 'text/markdown;charset=utf-8'});
  const url = URL.createObjectURL(blob);
  const link = document.createElement('a');
  link.href = url;
  link.download = suggestedName;
  document.body.appendChild(link);
  link.click();
  link.remove();
  URL.revokeObjectURL(url);
  statusNode.textContent = 'Markdown downloaded';
}

restoreNotes();
document.querySelectorAll('textarea').forEach(area => area.addEventListener('input', () => storeNotes()));
document.getElementById('save-markdown')?.addEventListener('click', saveMarkdown);
document.getElementById('clear-notes')?.addEventListener('click', () => {
  if (!window.confirm('Clear all workshop notes?')) return;
  document.querySelectorAll('textarea').forEach(area => { area.value = ''; });
  localStorage.removeItem(STORAGE_KEY);
  statusNode.textContent = 'Notes cleared';
});
