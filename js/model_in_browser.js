import * as webllm from "https://esm.run/@mlc-ai/web-llm";

// --- Configurare -------------------------------------------------------------
const TITLE_LOAD = "1 · încărcarea modelului";
const TITLE_CHAT = "2 · apelul cu rolurile";
const CAPTION_LOAD = "Pasul 1: codul care descarcă și pornește modelul în browser.";

const FULL_EXAMPLE = [
  'import * as webllm from "https://esm.run/@mlc-ai/web-llm";',
  "",
  "// 1. Descarcă modelul și pornește-l pe WebGPU (o singură dată)",
  'const engine = await webllm.CreateMLCEngine("Llama-3.2-1B-Instruct-q4f16_1-MLC");',
  "",
  "// 2. Conversația = o listă de mesaje cu roluri",
  "const messages = [",
  '  { role: "system", content: "Ești profesor de informatică. Răspunzi în română." },',
  '  { role: "user",   content: "Ce este căutarea binară?" },',
  "];",
  "",
  "// 3. Trimitem cererea; răspunsul vine bucată cu bucată (stream)",
  "const raspuns = await engine.chat.completions.create({ messages, stream: true });",
  "for await (const parte of raspuns) {",
  '  process.stdout.write(parte.choices[0]?.delta?.content || "");',
  "}",
].join("\n");

// --- Referințe DOM -----------------------------------------------------------
const $ = (id) => document.getElementById(id);
const ui = {
  model: $("model"), load: $("load"), bar: $("bar"), barFill: $("bar").firstElementChild,
  status: $("status"), chatCard: $("chatCard"), system: $("system"), chat: $("chat"),
  input: $("input"), send: $("send"), reset: $("reset"), nogpu: $("nogpu"),
  codeView: $("codeView"), codeTitle: $("codeTitle"), codeCaption: $("codeCaption"), codeFull: $("codeFull"),
};

// --- Stare -------------------------------------------------------------------
const state = { engine: null, messages: [], busy: false };

// --- Panoul de cod: colorare simplă + generatoare de exemple ------------------
const KEYWORDS = /\b(const|let|await|import|from|for|of|function|return)\b/g;
const escapeHtml = (text) => text.replace(/&/g, "&amp;").replace(/</g, "&lt;").replace(/>/g, "&gt;");

function highlight(code) {
  return code.split("\n").map((line) => {
    if (/^\s*\/\//.test(line)) return `<span class="c">${escapeHtml(line)}</span>`;
    return escapeHtml(line)
      .replace(/"[^"\n]*"/g, (str) => `<span class="s">${str}</span>`)
      .replace(KEYWORDS, '<span class="k">$1</span>');
  }).join("\n");
}

const truncate = (text, max = 60) => {
  const t = text.replace(/\s+/g, " ").trim();
  return t.length > max ? `${t.slice(0, max)}…` : t;
};

function snippetLoad(model) {
  return [
    'import * as webllm from "@mlc-ai/web-llm";',
    "",
    "// Descarcă modelul și pornește-l pe placa video (WebGPU)",
    `const engine = await webllm.CreateMLCEngine("${model}");`,
  ].join("\n");
}

function snippetChat(messages) {
  const rows = messages.map(
    (m) => `  { role: ${`"${m.role}",`.padEnd(13)} content: "${truncate(m.content)}" },`
  );
  return [
    "const messages = [",
    ...rows,
    "];",
    "",
    "// Trimitem toată conversația; răspunsul vine în flux (stream)",
    "const raspuns = await engine.chat.completions.create({ messages, stream: true });",
  ].join("\n");
}

// --- Funcții de interfață -----------------------------------------------------
function showCode(code, title, caption) {
  ui.codeView.innerHTML = highlight(code);
  ui.codeTitle.textContent = title;
  ui.codeCaption.textContent = caption;
}

function addBubble(role, text) {
  const bubble = document.createElement("div");
  bubble.className = `msg ${role}`;

  const who = document.createElement("div");
  who.className = "who";
  who.textContent = role === "user" ? "Tu (user)" : "Model (assistant)";

  const body = document.createElement("span");
  body.textContent = text;

  bubble.append(who, body);
  ui.chat.append(bubble);
  bubble.scrollIntoView({ behavior: "smooth", block: "end" });
  return body;
}

// --- Acțiuni -----------------------------------------------------------------
async function loadModel() {
  const model = ui.model.value;
  ui.load.disabled = true;
  ui.bar.style.display = "block";
  showCode(snippetLoad(model), TITLE_LOAD, "Se execută acum: descărcarea și pornirea modelului.");

  try {
    state.engine = await webllm.CreateMLCEngine(model, {
      initProgressCallback: ({ text, progress }) => {
        ui.status.textContent = text;
        if (typeof progress === "number") ui.barFill.style.width = `${Math.round(progress * 100)}%`;
      },
    });
    ui.status.textContent = "Model pregătit. Poți pune întrebări.";
    ui.bar.style.display = "none";
    ui.chatCard.classList.add("enabled");
    ui.input.focus();
  } catch (err) {
    ui.status.textContent = `Eroare la încărcare: ${err.message}`;
    ui.load.disabled = false;
  }
}

async function send() {
  if (state.busy || !state.engine) return;
  const text = ui.input.value.trim();
  if (!text) return;

  state.busy = true;
  ui.send.disabled = true;
  ui.input.value = "";

  if (state.messages.length === 0) state.messages.push({ role: "system", content: ui.system.value });
  state.messages.push({ role: "user", content: text });
  addBubble("user", text);
  showCode(snippetChat(state.messages), TITLE_CHAT,
    `Apelul curent trimite ${state.messages.length} mesaje (system, user, assistant…).`);

  const out = addBubble("assistant", "…");
  try {
    const stream = await state.engine.chat.completions.create({ messages: state.messages, stream: true });
    let reply = "";
    for await (const chunk of stream) {
      reply += chunk.choices[0]?.delta?.content ?? "";
      out.textContent = reply;
    }
    state.messages.push({ role: "assistant", content: reply });
    showCode(snippetChat(state.messages), TITLE_CHAT,
      `Răspunsul (assistant) a fost adăugat în istoric: acum ${state.messages.length} mesaje.`);
  } catch (err) {
    out.textContent = `Eroare: ${err.message}`;
  } finally {
    state.busy = false;
    ui.send.disabled = false;
    ui.input.focus();
  }
}

function resetConversation() {
  state.messages = [];
  ui.chat.innerHTML = "";
  showCode(snippetLoad(ui.model.value), TITLE_LOAD, "Conversație nouă. Pune o întrebare ca să vezi apelul.");
  ui.input.focus();
}

// --- Inițializare ------------------------------------------------------------
function init() {
  if (!navigator.gpu) {
    ui.nogpu.classList.remove("hidden");
    ui.load.disabled = true;
  }

  ui.codeFull.innerHTML = highlight(FULL_EXAMPLE);
  showCode(snippetLoad(ui.model.value), TITLE_LOAD, CAPTION_LOAD);

  ui.model.addEventListener("change", () => {
    if (!state.engine) showCode(snippetLoad(ui.model.value), TITLE_LOAD, CAPTION_LOAD);
  });
  ui.load.addEventListener("click", loadModel);
  ui.send.addEventListener("click", send);
  ui.reset.addEventListener("click", resetConversation);
  ui.input.addEventListener("keydown", (e) => {
    if (e.key === "Enter" && !e.shiftKey) { e.preventDefault(); send(); }
  });
}

init();
