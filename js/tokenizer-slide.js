const root = document.getElementById('s25live');
const input = root.querySelector('#tokenizer-input');
const ribbon = root.querySelector('.live-token-ribbon');
const count = root.querySelector('.live-token-count');
const status = root.querySelector('.live-token-status');
const detail = root.querySelector('.live-token-detail');
const retry = root.querySelector('.live-token-retry');
const defaultText = input.value;
const samples = {
  default: defaultText,
  english: 'Ana is learning Python and wants to write a program that sorts a list of numbers.',
  code: 'def medie(valori):\n    return sum(valori) / len(valori)',
  emoji: 'Salut! 👋 Învățăm AI împreună. 🧠'
};
let worker, ready = false, timer, request = 0, selected = 0, tokens = [];

function visibleText(token) {
  return token.text === null
    ? '⟨' + token.bytes.map(b => b.toString(16).padStart(2, '0').toUpperCase()).join(' ') + '⟩'
    : token.text.replaceAll(' ', '·').replaceAll('\n', '↵').replaceAll('\r', '␍').replaceAll('\t', '⇥');
}
function select(index) {
  selected = index;
  [...ribbon.children].forEach((el, i) => el.setAttribute('aria-pressed', String(i === index)));
  const token = tokens[index];
  detail.replaceChildren();
  if (!token) { detail.textContent = 'Scrie un text pentru a vedea tokenii.'; return; }
  const title = document.createElement('strong');
  title.textContent = visibleText(token);
  const info = document.createElement('p');
  info.textContent = 'Tokenul ' + (index + 1) + ' · ID ' + token.id;
  const bytes = document.createElement('p');
  bytes.className = 'live-token-bytes';
  bytes.textContent = 'Bytes: ' + token.bytes.map(b => b.toString(16).padStart(2, '0').toUpperCase()).join(' ');
  detail.append(title, info, bytes);
  if (token.text === null) {
    const note = document.createElement('p');
    note.textContent = 'Acest token conține doar o parte dintr-un caracter UTF-8. Afișăm bytes în hexazecimal.';
    detail.append(note);
  }
}
function fail() {
  ready = false;
  worker?.terminate(); worker = null;
  ribbon.replaceChildren(); count.textContent = '—';
  detail.textContent = 'Rezultatul nu este disponibil.';
  status.textContent = 'Tokenizatorul nu s-a încărcat. Poți reîncerca.';
  retry.hidden = false;
  root.setAttribute('aria-busy', 'false');
}
function encode() {
  clearTimeout(timer);
  request++;
  root.setAttribute('aria-busy', 'true');
  status.textContent = ready ? 'Se calculează…' : 'Se încarcă vocabularul…';
  // Remove stale output immediately so it is never attributed to the new input.
  ribbon.replaceChildren(); count.textContent = '—';
  detail.textContent = 'Rezultatul se actualizează.';
  if (ready) worker.postMessage({ type: 'encode', request, text: input.value });
}
function start() {
  if (worker) return;
  retry.hidden = true;
  try {
    worker = new Worker(new URL('./tokenizer-worker.js', import.meta.url), { type: 'module' });
    worker.onerror = fail;
    worker.onmessage = ({ data }) => {
      if (data.type === 'ready') { ready = true; encode(); return; }
      if (data.request !== request) return;
      if (data.type === 'error' || !data.roundtrip) { fail(); return; }
      tokens = data.tokens;
      ribbon.replaceChildren();
      const fragment = document.createDocumentFragment();
      tokens.forEach((token, i) => {
        const button = document.createElement('button');
        button.type = 'button'; button.className = 'live-token';
        button.dataset.color = i % 6;
        const text = document.createElement('span'); text.textContent = visibleText(token);
        const id = document.createElement('small'); id.textContent = token.id;
        button.append(text, id);
        button.setAttribute('aria-label', 'Token ' + (i + 1) + ': ' + visibleText(token) + ', ID ' + token.id);
        button.addEventListener('click', () => select(i));
        fragment.append(button);
      });
      ribbon.append(fragment);
      count.textContent = tokens.length;
      status.textContent = tokens.length ? 'Tokenizare calculată local · fragmente și ID-uri reale' : 'Text gol · 0 tokeni';
      select(Math.min(selected, Math.max(0, tokens.length - 1)));
      root.setAttribute('aria-busy', 'false');
    };
  } catch { fail(); }
}
input.addEventListener('input', event => {
  if (event.isComposing) return;
  clearTimeout(timer);
  // Invalidate queued results before the debounce expires.
  request++;
  timer = setTimeout(() => { start(); encode(); }, 120);
});
input.addEventListener('compositionend', () => { start(); encode(); });
root.querySelectorAll('[data-sample]').forEach(button => button.addEventListener('click', () => {
  input.value = samples[button.dataset.sample]; selected = 0; start(); encode();
}));
retry.addEventListener('click', () => { start(); encode(); });
const observer = new IntersectionObserver(entries => {
  if (entries.some(entry => entry.isIntersecting)) { start(); observer.disconnect(); }
}, { rootMargin: '200px' });
observer.observe(root);
