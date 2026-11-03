# Experimentul RAG — reproducere cap-coadă

Implementarea rulabilă a experimentului din cursul
[Retrieval-Augmented Generation](https://danlex.github.io/uni.ai/rag.html)
(master Engineering for AI). Reproduce, pe cele trei paragrafe fictive, exact pașii
prezentați pe slide-uri: chunking, embeddings, căutare vectorială, generare cu
citări, GraphRAG și evaluare.

Răspunde cerinței de pe slide-ul 12: *„implementează indexarea celor trei paragrafe,
afișează scorurile și sursele înainte de răspuns, apoi construiește manual graful și
compară procesele de recuperare."*

## Corpusul (cazul fictiv din curs)

| Paragraf | Chunk | Text |
|----------|-------|------|
| P1 | C1 | Compania Pegas produce bicicleta electrică Vela. |
| P2 | C2 | Bicicleta Vela este asamblată la fabrica din Brașov. |
| P3 | C3 | Fabrica din Brașov folosește energie furnizată de compania Solaris. |

Trei întrebări, cu grad diferit de dificultate:

- **A** (un singur pasaj) — *Unde este asamblată Vela?* → dovada e P2.
- **B** (multi-hop) — *Cine furnizează energia fabricii care asamblează bicicleta Pegas?*
  → cere P1 + P2 + P3.
- **C** (fără răspuns) — *Câți Wh are bateria Vela?* → informația nu există în corpus,
  sistemul trebuie să se abțină.

## Pași de execuție

### 1. Experimentul principal (fără nicio dependență)

Deterministic. Folosește vectorii didactici de pe slide-uri, deci scorurile ies
identice cu cele din curs (B: C1 = 0.993, C2 = 0.439, C3 = 0.314).

```bash
cd rag
python3 experiment.py
```

Afișează, pe rând:

1. **Chunking** — 3 paragrafe → 3 chunks (slide 3)
2. **Embeddings** — câte un vector per chunk (slide 4)
3. **Căutare + generare** — scorurile și sursele **înainte** de răspuns, pentru
   fiecare întrebare și pentru `k = 1, 2, 3` (slide 5, 6)
4. **GraphRAG** — afirmațiile structurate și traversarea
   `Pegas → Vela → Fabrica Brașov → Solaris` (slide 8)
5. **Evaluare** — recall-ul dovezilor, vector vs. graf (slide 11)

Ce ar trebui să observi:

- întrebarea **B** cu `top-1` aduce doar P1 (recall 1/3) și nu poate justifica „Solaris";
  cu `top-2` ajunge la 2/3 (exact cazul de pe slide 11); abia `top-3` acoperă tot lanțul;
- **graful** urmărește relațiile explicite și recuperează tot lanțul dintr-un singur mers;
- întrebarea **C** se termină cu abținere, chiar dacă vectorial există „vecini" apropiați.

### 2. Varianta cu embeddings reale (opțional)

Același pipeline de căutare, dar cu vectori calculați de un model real
(`all-MiniLM-L6-v2`, local, gratuit), nu cu numerele alese manual.

```bash
cd rag
python3 -m venv .venv
.venv/bin/python -m pip install -r requirements.txt
.venv/bin/python rag_real.py
```

Modelul (~90 MB) se descarcă o singură dată, la prima rulare.

### 3. Laboratorul complet din slide-uri (`rag_local.py`)

Varianta prezentată pe pagina cursului: encoder real E5 pe 6 paragrafe (două lanțuri
de produse, ca să existe și distractori) plus generare locală opțională prin Ollama.
Setările sunt constante în capul fișierului (`QUESTION`, `K`, `ENCODER`, `OFFLINE`, `LLM`).

```bash
cd rag
python3 -m venv .venv
.venv/bin/python -m pip install "sentence-transformers>=3.0,<6"
.venv/bin/python rag_local.py
```

Encoderul E5 (~470 MB) se descarcă o singură dată, la prima rulare. Pentru generare,
instalează [Ollama](https://ollama.com), descarcă un model (`ollama pull llama3:8b`),
apoi pune `LLM = 'llama3:8b'` în fișier și rulează din nou.

## Structura folderului

| Fișier | Rol |
|--------|-----|
| `corpus.py` | Paragrafele, chunk-urile, vectorii didactici și întrebările (cu dovezile necesare). |
| `vector_rag.py` | Similaritate cosinus, căutare top-k, generator cu citări și abținere. |
| `graph_rag.py` | Extragerea relațiilor, construirea grafului și traversarea multi-hop. |
| `experiment.py` | Orchestratorul care rulează și afișează tot experimentul. |
| `rag_real.py` | Varianta opțională cu embeddings reale (3 paragrafe, ca restul folderului). |
| `rag_local.py` | Laboratorul complet din slide-uri: encoder E5 real pe 6 paragrafe + generare locală opțională prin Ollama. |
| `requirements.txt` | Dependența pentru varianta reală (doar `sentence-transformers`). |

Fiecare modul se poate rula și separat (`python3 vector_rag.py`, `python3 graph_rag.py`)
pentru a vedea doar partea respectivă.
