# Cursul 1 · Inginerie pentru AI

Materiale pentru Cursul 1 — AI și programare (Facultatea de Matematică și Informatică, Universitatea din București).

## Conținut

- **`Curs_1_AI_Algorithm_Tutor_v30.html`** — slide-urile cursului (se deschid direct în browser).
- **`exemplu_colab_ai.ipynb`** — notebook pentru Google Colab: primul apel către un LLM (`google.colab.ai`) și tokenizare cu `tiktoken`.
- **`exemplu_tokeni.py`** — același exemplu de tokenizare, ca script local.
- **`img/`** — imaginile folosite în slide-uri.
- **`js/`** — tokenizatorul interactiv, cu vocabularul `o200k_base` și dependențele locale.

## Cum deschizi slide-urile

Pentru toate funcțiile interactive, servește întregul folder prin HTTP:

```bash
python3 -m http.server 7777 --bind 127.0.0.1
```

Deschide [cursul local](http://127.0.0.1:7777/Curs_1_AI_Algorithm_Tutor_v30.html). Tokenizarea interactivă este pe slide-ul „Scrie un text. Vezi tokenii.”, după exemplul fix de tokenizare. Are text editabil, exemple în română și engleză, cod Python și emoji. Calculul rulează local într-un Web Worker, fără API; vocabularul se încarcă la apropierea de slide. Deschiderea directă prin `file://` poate bloca modulele și worker-ul.

Pe copertă, „Cursul pe telefon” afișează un QR către versiunea publică GitHub Pages. Apasă pentru codul mărit, linkul direct și accesul la tokenizator sau materialele de laborator. QR-ul este un SVG local, fără serviciu de tracking sau redirecționare.

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
