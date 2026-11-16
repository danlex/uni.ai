#!/usr/bin/env python3
"""BM25 RAG: căutare lexicală + prompt cu citări, de la zero (fără dependențe).

BM25 ordonează documentele după potrivirea de termeni: cuvintele rare din
întrebare care apar în document contează cel mai mult. Este cel mai puternic
baseline pe date de firmă (coduri, acronime, nume de proiecte).

Rulare:
    python3 bm25_rag.py
"""

import math
import re
from collections import Counter

# Corpusul didactic (același ca în restul folderului).
PASSAGES = {
    "P1": "Compania Pegas produce bicicleta electrică Vela.",
    "P2": "Bicicleta Vela este asamblată la fabrica din Brașov.",
    "P3": "Fabrica din Brașov folosește energie furnizată de compania Solaris.",
}

K1 = 1.5  # cât de repede saturează frecvența unui termen
B = 0.75  # cât de mult normalizăm după lungimea documentului


def tokenize(text):
    """Taie textul în cuvinte cu litere mici."""
    return re.findall(r"\w+", text.lower())


class BM25:
    """BM25 Okapi minimal peste o colecție de documente."""

    def __init__(self, passages):
        self.ids = list(passages)
        self.docs = {pid: tokenize(text) for pid, text in passages.items()}
        self.avg_len = sum(len(d) for d in self.docs.values()) / len(self.docs)
        self.idf = self._compute_idf()

    def _compute_idf(self):
        """Termenii rari primesc pondere mai mare (inverse document frequency)."""
        n_docs = len(self.docs)
        doc_freq = Counter(term for doc in self.docs.values() for term in set(doc))
        return {
            term: math.log(1 + (n_docs - df + 0.5) / (df + 0.5))
            for term, df in doc_freq.items()
        }

    def score(self, query, pid):
        """Scorul BM25 al unui document față de întrebare."""
        freq = Counter(self.docs[pid])
        length_norm = 1 - B + B * len(self.docs[pid]) / self.avg_len
        total = 0.0
        for term in tokenize(query):
            tf = freq[term]
            if tf:
                total += self.idf.get(term, 0.0) * tf * (K1 + 1) / (tf + K1 * length_norm)
        return total

    def search(self, query, k):
        """Primele k documente ca (pid, scor), descrescător după scor."""
        scored = [(pid, self.score(query, pid)) for pid in self.ids]
        scored.sort(key=lambda hit: hit[1], reverse=True)
        return scored[:k]


def build_prompt(query, hits):
    """Promptul RAG: instrucțiuni + pasajele recuperate + întrebarea."""
    context = "\n".join(f"[{pid}] {PASSAGES[pid]}" for pid, _ in hits)
    return (
        "Răspunde folosind exclusiv CONTEXTUL de mai jos. Citează sursele [P1], [P2].\n"
        "Dacă informația lipsește, spune ce nu poți stabili.\n\n"
        f"CONTEXT:\n{context}\n\nÎNTREBARE:\n{query}\n\nRĂSPUNS:"
    )


def main():
    bm25 = BM25(PASSAGES)
    query = "Unde este asamblată bicicleta Vela?"

    print(f"Întrebare: {query}\n")
    print("Clasament BM25 (scorurile nu sunt probabilități):")
    for rank, (pid, score) in enumerate(bm25.search(query, k=len(PASSAGES)), start=1):
        print(f"  {rank}. [{pid}] bm25={score:.3f}  {PASSAGES[pid]}")

    print("\n" + build_prompt(query, bm25.search(query, k=2)))


if __name__ == "__main__":
    main()
