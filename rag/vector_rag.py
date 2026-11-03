#!/usr/bin/env python3
"""Căutare vectorială și generare cu citări (slide-urile 4, 5, 6 din rag.html).

Fără dependențe externe. Similaritatea se calculează din vectorii didactici de pe
slide-uri, așa că scorurile ies identice cu cele din curs (pentru întrebarea
compusă: C1 = 0.993, C2 = 0.439, C3 = 0.314).
"""

import math
from collections import namedtuple

from corpus import CHUNKS

# Un rezultat al căutării = un chunk împreună cu scorul lui.
# Îl ținem ca „Hit" ca să putem scrie hit.chunk și hit.score, nu hit[0]/hit[1].
Hit = namedtuple("Hit", ["chunk", "score"])


def cosine_similarity(a, b):
    """Cât de asemănători sunt doi vectori (1 = identici ca direcție, 0 = fără legătură)."""
    produs_scalar = sum(x * y for x, y in zip(a, b))
    lungime_a = math.sqrt(sum(x * x for x in a))
    lungime_b = math.sqrt(sum(y * y for y in b))
    return produs_scalar / (lungime_a * lungime_b)


def search(query_vector, k=3):
    """Compară întrebarea cu fiecare chunk și întoarce primele k rezultate.

    Pașii:
      1. calculăm scorul fiecărui chunk față de întrebare;
      2. le ordonăm de la cel mai mare scor la cel mai mic;
      3. păstrăm primele k.
    """
    rezultate = []
    for chunk in CHUNKS:
        scor = cosine_similarity(query_vector, chunk["vector"])
        rezultate.append(Hit(chunk, scor))

    rezultate.sort(key=lambda hit: hit.score, reverse=True)
    return rezultate[:k]


def generate(question, hits):
    """'Generator' cu răspunsuri predefinite (slide 6 — nu rulează un LLM).

    Regula e simplă: răspundem doar dacă toate dovezile necesare (gold) se află
    printre pasajele recuperate. Altfel ne abținem și spunem ce lipsește.
    """
    dovezi_necesare = set(question["gold"])
    surse_in_context = {hit.chunk["source"] for hit in hits}

    # Cazul 1: întrebare fără răspuns în corpus (ex. capacitatea bateriei).
    if not dovezi_necesare:
        return "Nu pot stabili capacitatea bateriei Vela din aceste surse. Este necesară fișa tehnică."

    # Cazul 2: lipsesc dovezi — nu inventăm răspunsul (slide 5).
    dovezi_lipsa = dovezi_necesare - surse_in_context
    if dovezi_lipsa:
        lipsa = ", ".join(sorted(dovezi_lipsa))
        return f"Nu pot susține răspunsul numai din pasajele recuperate. Lipsesc dovezile: {lipsa}."

    # Cazul 3: avem toate dovezile — răspuns susținut, cu citări.
    citari = ", ".join(sorted(dovezi_necesare))
    return f"{question['answer']} [{citari}]"


def answer_question(question, k=3):
    """Pipeline complet pentru o întrebare: mai întâi căutăm, apoi generăm."""
    hits = search(question["vector"], k=k)
    raspuns = generate(question, hits)
    return hits, raspuns


if __name__ == "__main__":
    # Verificare rapidă: reproducem scorurile de pe slide 5 (întrebarea compusă B).
    from corpus import QUESTIONS

    intrebarea_b = next(q for q in QUESTIONS if q["id"] == "B")
    for hit in search(intrebarea_b["vector"], k=len(CHUNKS)):
        chunk = hit.chunk
        print(f"{chunk['id']} [{chunk['source']}]  {hit.score:.3f}  {chunk['text']}")
