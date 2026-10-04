const chatForm = document.getElementById('chat-form');
const chat = document.getElementById('chat');
const gameLevelLabel = document.getElementById('game-level-label');
const gameLevelTitle = document.getElementById('game-level-title');
const gameObjective = document.getElementById('game-objective');
const gameAttempts = document.getElementById('game-attempts');
const gameLevelAttempts = document.getElementById('game-level-attempts');
const sessionLevelLine = document.getElementById('session-level-line');
const gameProgressBar = document.getElementById('game-progress-bar');
const gameLevels = document.getElementById('game-levels');
const gameHint = document.getElementById('game-hint');
const gameJudgeReason = document.getElementById('game-judge-reason');
const gameBanner = document.getElementById('game-banner');
const gameInstructions = document.getElementById('game-instructions');
const gameInstructionsList = document.getElementById('game-instructions-list');
const gamePassCriteria = document.getElementById('game-pass-criteria');
const gameScoring = document.getElementById('game-scoring');
const scoringFlags = document.getElementById('scoring-flags');
const gameReset = document.getElementById('game-reset');

function addMessage(kind, text) {
  if (!chat) return;
  const item = document.createElement('div');
  item.className = `message ${kind}`;
  if (kind !== 'level-clear') {
    const label = document.createElement('strong');
    label.textContent = kind === 'user' ? 'You' : 'AIDA';
    item.appendChild(label);
  }
  const content = document.createElement('pre');
  content.textContent = text;
  item.appendChild(content);
  chat.appendChild(item);
  chat.scrollTop = chat.scrollHeight;
}

function renderProgressBar(state) {
  if (!gameProgressBar) return;
  const total = state.total_levels || 0;
  const current = state.completed ? total + 1 : state.current_level_index || 1;
  gameProgressBar.replaceChildren();
  for (let i = 1; i <= total; i += 1) {
    const seg = document.createElement('span');
    seg.className = 'level-seg';
    if (i < current || state.completed) seg.classList.add('cleared');
    else if (i === current) seg.classList.add('current');
    gameProgressBar.appendChild(seg);
  }
}

function renderLevelList(state) {
  if (!gameLevels) return;
  gameLevels.replaceChildren();
  (state.levels || []).forEach(level => {
    const row = document.createElement('div');
    row.className = `challenge level-row status-${level.status}`;
    const num = document.createElement('span');
    num.textContent = String(level.number).padStart(2, '0');
    const body = document.createElement('div');
    const title = document.createElement('strong');
    title.textContent = level.title;
    const status = document.createElement('small');
    status.textContent =
      level.status === 'cleared' ? 'Cleared' : level.status === 'current' ? 'Current' : 'Locked';
    body.append(title, status);
    row.append(num, body);
    gameLevels.appendChild(row);
  });
}

function renderInstructionList(items) {
  if (!gameInstructionsList || !gameInstructions) return;
  gameInstructionsList.replaceChildren();
  if (!items || !items.length) {
    gameInstructions.hidden = true;
    return;
  }
  items.forEach(text => {
    const item = document.createElement('li');
    item.textContent = text;
    gameInstructionsList.appendChild(item);
  });
  gameInstructions.hidden = false;
}

function renderScoring(state) {
  const collaborative = (state.scoring || {}).model === 'collaborative';
  if (gameScoring) {
    if (collaborative) {
      const cleared = (state.cleared || []).length;
      const total = state.total_levels || 0;
      gameScoring.textContent =
        cleared >= total && total > 0
          ? `All ${total} levels cleared — debrief in Notes.`
          : `Work together on Level ${state.current_level_index || 1}. Cleared: ${cleared} of ${total}.`;
    } else {
      const points = state.scoring?.points_per_level ?? 10;
      gameScoring.textContent = `${points} pts when you clear this level. Record flag and Notes fields for learning.`;
    }
  }
  if (!scoringFlags) return;
  scoringFlags.replaceChildren();
  const flags = state.cleared_flags || [];
  if (!flags.length) {
    scoringFlags.hidden = true;
    return;
  }
  flags.forEach(flag => {
    const item = document.createElement('li');
    const code = document.createElement('code');
    code.textContent = flag;
    item.append(collaborative ? 'Level cleared — ' : 'Collected: ', code);
    scoringFlags.appendChild(item);
  });
  scoringFlags.hidden = false;
}

function updateGamePanel(state, judge) {
  if (!state || !state.enabled) return;
  const total = state.total_levels || 6;
  const index = state.current_level_index || 1;
  if (gameLevelLabel) {
    gameLevelLabel.textContent = state.completed
      ? `LEVEL COMPLETE / ${String(total).padStart(2, '0')}`
      : `LEVEL #${String(index).padStart(2, '0')} / ${String(total).padStart(2, '0')}`;
  }
  if (gameLevelTitle) gameLevelTitle.textContent = state.current_level_title ?? '';
  if (gameObjective) gameObjective.textContent = state.objective ?? '';
  const levelAttempts = state.level_attempts ?? 0;
  const totalAttempts = state.attempts ?? 0;
  if (sessionLevelLine) {
    const levelNum = state.completed ? total : index;
    // Rebuild heading so the span stays for updates
    sessionLevelLine.replaceChildren();
    sessionLevelLine.append(
      document.createTextNode(`LEVEL ${levelNum} · Attempt `),
    );
    const levelSpan = document.createElement('span');
    levelSpan.id = 'game-level-attempts';
    levelSpan.textContent = String(levelAttempts);
    sessionLevelLine.appendChild(levelSpan);
  } else if (gameLevelAttempts) {
    gameLevelAttempts.textContent = String(levelAttempts);
  }
  if (gameAttempts) gameAttempts.textContent = String(totalAttempts);
  renderInstructionList(state.instructions);
  if (gamePassCriteria) {
    if (state.pass_criteria) {
      gamePassCriteria.hidden = false;
      gamePassCriteria.textContent = `Pass: ${state.pass_criteria}`;
    } else {
      gamePassCriteria.hidden = true;
      gamePassCriteria.textContent = '';
    }
  }
  renderScoring(state);
  if (gameHint) {
    if (state.hint) {
      gameHint.hidden = false;
      const tier = state.hint_tier ?? 0;
      const fails = state.level_fails ?? 0;
      const label = tier > 0 ? `Extra hint (${fails} attempts on this level)` : 'Hint';
      gameHint.textContent = `${label}: ${state.hint}`;
    } else {
      gameHint.hidden = true;
      gameHint.textContent = '';
    }
  }
  if (gameBanner) {
    gameBanner.hidden = true;
    gameBanner.textContent = '';
  }
  if (gameJudgeReason) {
    if (judge && judge.reason) {
      const outcome = judge.pass ? 'Pass' : 'No pass';
      gameJudgeReason.textContent = `${outcome}: ${judge.reason}`;
    } else {
      gameJudgeReason.textContent = '';
    }
  }
  renderProgressBar(state);
  renderLevelList(state);
}

async function refreshGameState() {
  try {
    const response = await fetch('/api/game-state', {headers: {'Accept': 'application/json'}});
    if (!response.ok) throw new Error(`${response.status} ${response.statusText}`);
    const state = await response.json();
    updateGamePanel(state, null);
  } catch (error) {
    if (gameJudgeReason) gameJudgeReason.textContent = `Unable to load game state: ${String(error)}`;
  }
}

if (chatForm) {
  addMessage('assistant', 'Welcome. I am AIDA, your internal operations assistant. How can I help?');
  chatForm.addEventListener('submit', async event => {
    event.preventDefault();
    const input = document.getElementById('message');
    const message = input.value.trim();
    if (!message) return;
    addMessage('user', message);
    input.value = '';
    try {
      const response = await fetch('/api/chat', {
        method: 'POST',
        headers: {'Content-Type': 'application/json'},
        body: JSON.stringify({message})
      });
      const data = await response.json();
      addMessage('assistant', data.reply || JSON.stringify(data, null, 2));
      if (data.game?.just_cleared && data.game?.banner) {
        addMessage('level-clear', data.game.banner);
      }
      updateGamePanel(data.game, data.judge);
      // Avoid wiping a just-cleared banner via a second game-state fetch.
      if (!data.game?.just_cleared) {
        await refreshGameState();
      }
    } catch (error) {
      addMessage('assistant', `Request failed: ${String(error)}`);
    }
  });
}

if (document.getElementById('level-panel')) refreshGameState();
if (gameReset) {
  gameReset.addEventListener('click', async () => {
    try {
      const response = await fetch('/api/game/reset', {method: 'POST'});
      if (!response.ok) throw new Error(`${response.status} ${response.statusText}`);
      const state = await response.json();
      updateGamePanel(state, null);
      addMessage('assistant', 'Progress reset. Level 1 is active again.');
    } catch (error) {
      if (gameJudgeReason) gameJudgeReason.textContent = `Reset failed: ${String(error)}`;
    }
  });
}
