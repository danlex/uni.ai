import { Tiktoken } from './vendor/js-tiktoken/core.js';
import ranks from './vendor/js-tiktoken/o200k_base.js';

// Keep vocabulary construction and BPE computation off the presentation thread.
const encoder = new Tiktoken(ranks);
const utf8 = new TextDecoder('utf-8', { fatal: true });
self.postMessage({ type: 'ready' });
self.onmessage = ({ data }) => {
  if (data.type !== 'encode') return;
  try {
    const ids = encoder.encode(data.text, [], []);
    const tokens = ids.map(id => {
      // Pinned js-tiktoken exposes raw bytes; individual tokens can split UTF-8.
      const bytes = encoder.textMap.get(id);
      let text = null;
      try { text = utf8.decode(bytes); } catch { /* Display partial bytes as hex. */ }
      return { id, text, bytes: Array.from(bytes) };
    });
    self.postMessage({ type: 'result', request: data.request, tokens,
      roundtrip: encoder.decode(ids) === data.text });
  } catch {
    self.postMessage({ type: 'error', request: data.request });
  }
};
