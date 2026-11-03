#!/usr/bin/env python3
"""Căutare vectorială și generare cu citări (slide-urile 4, 5, 6 din rag.html).

Fără dependențe externe: similaritatea cosinus se calculează din vectorii
didactici de pe slide-uri, deci scorurile ies identice cu cele afișate în curs
(C1 = 0.993, C2 = 0.439, C3 = 0.314 pentru întrebarea compusă).
"""

import math

from corpus import BY_SOURCE, CHUNKS


def cosine(a, b):
    """Similaritate cosinus între doi vectori."""
    dot = sum(x * y for x, y in zip(a, b))
    na = math.sqrt(sum(x * x for x in a))
    nb = math.sqrt(sum(y * y for y in b))
    return dot / (na * nb)


def search(query_vector, k=3):
    """Ordonează chunk-urile după similaritate și întoarce primele k.

    Întoarce o listă de (chunk, scor), descrescător după scor.
    """
    scored = [(c, cosine(query_vector, c["vector"])) for c in CHUNKS]
    scored.sort(key=lambda t: t[1], reverse=True)
    return scored[:k]


def generate(question, retrieved):
    """'Generator' cu răspunsuri predefinite (slide 6 — nu rulează un LLM).

    Răspunde DOAR dacă toate dovezile necesare (gold) sunt în contextul
    recuperat. Dacă lipsesc dovezi, se abține și spune ce nu poate stabili.
    `retrieved` este lista de (chunk, scor) venită de la retriever.
    """
    gold = set(question["gold"])
    sources_in_context = {c["source"] for c, _ in retrieved}

    # Întrebare fără răspuns în corpus (ex. capacitatea bateriei).
    if not gold:
        return (
            "Nu pot stabili capacitatea bateriei Vela din aceste surse. "
            "Este necesară fișa tehnică.",
            [],
        )

    missing = gold - sources_in_context
    if missing:
        # Dovezi insuficiente: nu inventăm răspunsul (slide 5).
        return (
            "Nu pot susține răspunsul numai din pasajele recuperate. "
            f"Lipsesc dovezile: {', '.join(sorted(missing))}.",
            sorted(sources_in_context & gold),
        )

    # Toate dovezile sunt prezente: răspuns susținut, cu citări.
    citations = sorted(gold)
    answer = f"{question['answer']} [{', '.join(citations)}]"
    return answer, citations


def answer_question(question, k=3):
    """Pipeline complet pentru o întrebare: căutare -> generare."""
    retrieved = search(question["vector"], k=k)
    text, citations = generate(question, retrieved)
    return retrieved, text, citations


if __name__ == "__main__":
    # Verificare rapidă: reproducem scorurile de pe slide 5 pentru întrebarea B.
    from corpus import QUESTIONS

    qb = next(q for q in QUESTIONS if q["id"] == "B")
    for chunk, score in search(qb["vector"], k=len(CHUNKS)):
        print(f"{chunk['id']} [{chunk['source']}]  {score:.3f}  {chunk['text']}")
