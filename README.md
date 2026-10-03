# Cursul 1 · De la AI la primul agent de programare

Materiale pentru Cursul 1 — AI și programare (Facultatea de Matematică și Informatică, Universitatea din București).

## Conținut

- **`Curs_1_AI_Algorithm_Tutor_v30.html`** — slide-urile cursului (se deschid direct în browser).
- **`exemplu_colab_ai.ipynb`** — notebook pentru Google Colab: primul apel către un LLM (`google.colab.ai`) și tokenizare cu `tiktoken`.
- **`exemplu_tokeni.py`** — același exemplu de tokenizare, ca script local.
- **`img/`** — imaginile folosite în slide-uri.

## Cum deschizi slide-urile

Descarcă `Curs_1_AI_Algorithm_Tutor_v30.html` și deschide-l într-un browser. Folosește săgețile pentru navigare.

## Cum rulezi exemplele

### În Google Colab (recomandat)

1. Intră pe [colab.research.google.com](https://colab.research.google.com/).
2. **File → Upload notebook** → alege `exemplu_colab_ai.ipynb`.
3. Rulează celulele pe rând cu `Shift + Enter`.

> `from google.colab import ai` merge doar în Colab (modelul gratuit e oferit de mediul Colab).

### Local (doar tokenizarea)

```bash
python3 -m venv .venv
.venv/bin/python -m pip install tiktoken
.venv/bin/python exemplu_tokeni.py
```
