#!/usr/bin/env python3
"""BM25 RAG: căutare lexicală + răspuns cu citări, de la zero (fără dependențe).

BM25 ordonează documentele după potrivirea de termeni: cuvintele rare care apar
în întrebare și în document contează mai mult. Este cel mai puternic baseline pe
date de firmă (coduri, acronime, nume de proiecte), de aceea îl predăm separat.

Rulare:
    python3 bm25_rag.py
"""

import math
import re
from collections import Counter

# Același corpus didactic ca în restul folderului (vezi corpus.py / rag.html).
PASSAGES = [
    ("P1", "Compania Pegas produce bicicleta electrică Vela."),
    ("P2", "Bicicleta Vela este asamblată la fabrica din Brașov."),
    ("P3", "Fabrica din Brașov folosește energie furnizată de compania Solaris."),
]


def tokenize(text):
    """Taie textul în cuvinte simple, cu litere mici (inclusiv diacritice)."""
    return re.findall(r"\w+", text.lower())


class BM25:
    """Implementare minimală BM25 Okapi (k1 și b sunt parametrii standard)."""

    def __init__(self, documents, k1=1.5, b=0.75):
        self.k1 = k1
        self.b = b
        self.docs = [tokenize(text) for _, text in documents]
        self.N = len(self.docs)
        self.avgdl = sum(len(d) for d in self.docs) / self.N

        # Frecvența documentară: în câte documente apare fiecare termen.
        df = Counter()
        for d in self.docs:
            for term in set(d):
                df[term] += 1

        # IDF: termenii rari primesc o pondere mai mare.
        self.idf = {
            term: math.log(1 + (self.N - n + 0.5) / (n + 0.5))
            for term, n in df.items()
        }

    def score(self, query_tokens, doc_index):
        """Scorul BM25 al unui document față de întrebare."""
        doc = self.docs[doc_index]
        freqs = Counter(doc)
        dl = len(doc)
        total = 0.0
        for term in query_tokens:
            if term not in freqs:
                continue
            tf = freqs[term]
            # Saturația frecvenței: al doilea apariției contează mai puțin decât prima.
            numer = tf * (self.k1 + 1)
            denom = tf + self.k1 * (1 - self.b + self.b * dl / self.avgdl)
            total += self.idf.get(term, 0.0) * numer / denom
        return total

    def search(self, question, k=3):
        """Întoarce primele k documente (index, scor), descrescător după scor."""
        q = tokenize(question)
        scored = [(i, self.score(q, i)) for i in range(self.N)]
        scored.sort(key=lambda t: t[1], reverse=True)
        return scored[:k]


def build_prompt(question, hits):
    """Promptul RAG: instrucțiuni + pasajele recuperate + întrebarea."""
    context = "\n".join(f"[{PASSAGES[i][0]}] {PASSAGES[i][1]}" for i, _ in hits)
    return (
        "Răspunde folosind exclusiv CONTEXTUL de mai jos. Citează sursele [P1], [P2].\n"
        "Dacă informația lipsește, spune ce nu poți stabili.\n\n"
        f"CONTEXT:\n{context}\n\nÎNTREBARE:\n{question}\n\nRĂSPUNS:"
    )


def main():
    bm25 = BM25(PASSAGES)
    question = "Unde este asamblată bicicleta Vela?"

    print(f"Întrebare: {question}\n")
    print("Clasament BM25 (scorurile nu sunt probabilități):")
    hits = bm25.search(question, k=len(PASSAGES))
    for rank, (i, score) in enumerate(hits, 1):
        pid, text = PASSAGES[i]
        print(f"  {rank}. [{pid}] bm25={score:.3f}  {text}")

    # Luăm primele 2 pasaje în context și construim promptul.
    top = hits[:2]
    print("\n" + build_prompt(question, top))


if __name__ == "__main__":
    main()
