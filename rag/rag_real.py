#!/usr/bin/env python3
"""Variantă OPȚIONALĂ: același experiment, dar cu embeddings reale.

Spre deosebire de `experiment.py` (vectori didactici, deterministic), aici
calculăm vectorii cu un model real de embeddings și rulăm aceeași căutare
vectorială pe cele trei paragrafe. Scopul este să vezi că pipeline-ul funcționează
și cu reprezentări învățate, nu doar cu numerele alese manual din curs.

Pregătire și rulare:
    python3 -m venv .venv
    .venv/bin/python -m pip install -r requirements.txt
    .venv/bin/python rag_real.py

Modelul (all-MiniLM-L6-v2, ~90 MB) se descarcă o singură dată, la prima rulare.
"""

import math

from corpus import CHUNKS, QUESTIONS


def cosine(a, b):
    dot = sum(x * y for x, y in zip(a, b))
    na = math.sqrt(sum(x * x for x in a))
    nb = math.sqrt(sum(y * y for y in b))
    return dot / (na * nb)


def main():
    try:
        from sentence_transformers import SentenceTransformer
    except ImportError:
        raise SystemExit(
            "Lipsește sentence-transformers. Rulează:\n"
            "    .venv/bin/python -m pip install -r requirements.txt"
        )

    print("Încarc modelul de embeddings (all-MiniLM-L6-v2)...")
    model = SentenceTransformer("all-MiniLM-L6-v2")

    # Vectorizăm fiecare chunk cu modelul real.
    chunk_vectors = model.encode([c["text"] for c in CHUNKS]).tolist()
    print(f"Fiecare paragraf are acum un vector de {len(chunk_vectors[0])} dimensiuni.\n")

    for q in QUESTIONS:
        qv = model.encode(q["text"]).tolist()
        scored = [
            (c, cosine(qv, cv)) for c, cv in zip(CHUNKS, chunk_vectors)
        ]
        scored.sort(key=lambda t: t[1], reverse=True)

        print(f"[{q['id']}] {q['text']}")
        for rank, (c, score) in enumerate(scored, 1):
            print(f"    {rank}. {c['id']} [{c['source']}]  {score:.3f}  {c['text']}")
        print()


if __name__ == "__main__":
    main()
