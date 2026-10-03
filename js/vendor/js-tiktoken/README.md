# Browser tokenizer dependencies

Vendored on 2026-10-03 for the interactive course slide. No remote runtime dependency.

- `core.js`: js-tiktoken 1.0.21, `dist/chunk-VL2OQCWN.js`. Only change: the base64-js import points to the local file.
- `o200k_base.js`: js-tiktoken 1.0.21, `dist/ranks/o200k_base.js`, unchanged.
- `base64-js.js`: base64-js 1.5.1 ESM bundle from jsDelivr.
- MIT license notices retained in `LICENSE` and `LICENSE-base64-js`.

Sources:
https://github.com/dqbd/tiktoken
https://cdn.jsdelivr.net/npm/js-tiktoken@1.0.21/dist/chunk-VL2OQCWN.js
https://cdn.jsdelivr.net/npm/js-tiktoken@1.0.21/dist/ranks/o200k_base.js
https://cdn.jsdelivr.net/npm/base64-js@1.5.1/+esm

The worker uses the pinned encoder's `textMap` to preserve token bytes. Individual tokens need not be valid UTF-8; the UI shows hex bytes for these instead of misleading replacement characters. Special-token strings typed by users are encoded as ordinary text. The UI does not estimate Gemini usage or chat message overhead.
