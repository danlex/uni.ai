#!/usr/bin/env python3
"""Hybrid RAG: BM25 + vector + graph, fuzionate cu RRF (fără dependențe).

Niciun retriever singur nu câștigă pe date de firmă. Aici combinăm trei:
  - BM25      — potrivire lexicală (termeni exacți, coduri, acronime);
  - vector    — similaritate semantică (prinde reformulări);
  - graph     — vecini prin entități comune (leagă documente fără cuvinte comune);
iar RRF (Reciprocal Rank Fusion) le unește într-un singur clasament.

Corpusul e modelat pe un cluster real din EnterpriseRAG-Bench: autentificarea CI
între cloud-uri (GCP / AWS), plus un document-distractor.

Rulare:
    python3 hybrid_rag.py
"""

import math
import re
from collections import Counter

K = 60  # constanta RRF

# Documente în stil EnterpriseRAG-Bench (id scurt + text).
DOCS = {
    "327df8aa": "GCP CI auth uses Workload Identity Federation: GitHub Actions assumes a "
                "service account with IAM token create permissions, MFA enforced.",
    "ed15f3ae": "AWS staging CI fails with AccessDenied on AssumeRoleWithWebIdentity; the "
                "Terraform role trust policy is misconfigured.",
    "846e635d": "Centralized audit across GCP and AWS aggregates Workload Identity Federation "
                "and AssumeRoleWithWebIdentity events into one CloudTrail sink, with KMS.",
    "b1ffac02": "Monthly cloud billing report: GCP and AWS spend by project and team; no auth "
                "or identity details.",
}

# Entitățile urmărite de graf (într-un sistem real le extrage GLiNER2).
ENTITIES = ["Workload Identity Federation", "AssumeRoleWithWebIdentity",
            "GitHub Actions", "CloudTrail", "Terraform", "IAM"]

# Vectori semantici didactici pe 4 concepte: [auth/identity, gcp, aws, billing].
# Un model real i-ar calcula; aici sunt aleși manual ca demonstrația să fie clară.
VECTORS = {
    "327df8aa": [0.9, 0.9, 0.1, 0.0],
    "ed15f3ae": [0.9, 0.1, 0.9, 0.0],
    "846e635d": [0.8, 0.7, 0.7, 0.1],
    "b1ffac02": [0.1, 0.6, 0.6, 0.9],
}

QUESTION = "Why does CI authentication fail on both GCP and AWS?"
QUERY_VECTOR = [0.9, 0.7, 0.7, 0.0]


def tokenize(text):
    return re.findall(r"\w+", text.lower())


# --- BM25 (lexical) ---------------------------------------------------
def bm25_ranking(question, k1=1.5, b=0.75):
    docs = {d: tokenize(t) for d, t in DOCS.items()}
    avg_len = sum(len(t) for t in docs.values()) / len(docs)
    doc_freq = Counter(term for t in docs.values() for term in set(t))
    idf = {term: math.log(1 + (len(docs) - df + 0.5) / (df + 0.5)) for term, df in doc_freq.items()}

    scores = {}
    for d, toks in docs.items():
        freq = Counter(toks)
        norm = 1 - b + b * len(toks) / avg_len
        scores[d] = sum(idf.get(w, 0) * freq[w] * (k1 + 1) / (freq[w] + k1 * norm)
                        for w in tokenize(question) if freq[w])
    return sorted(DOCS, key=lambda d: scores[d], reverse=True)


# --- Vector (semantic) ------------------------------------------------
def cosine(a, b):
    dot = sum(x * y for x, y in zip(a, b))
    return dot / (math.sqrt(sum(x * x for x in a)) * math.sqrt(sum(y * y for y in b)))


def vector_ranking(query_vector):
    return sorted(DOCS, key=lambda d: cosine(query_vector, VECTORS[d]), reverse=True)


# --- Graph (vecini prin entități comune) ------------------------------
def entities_in(text):
    return {e for e in ENTITIES if e.lower() in text.lower()}


def graph_candidates(seeds):
    """Al doilea hop: pornește din semințele retrieval-ului și adaugă vecinii lor.

    Doi vecini sunt legați dacă împart o entitate. Așa aducem documentul-punte pe
    care BM25 și vectorii îl ratează.
    """
    ents = {d: entities_in(t) for d, t in DOCS.items()}
    neighbors = {b for a in seeds for b in DOCS if a != b and ents[a] & ents[b]}
    return set(seeds) | neighbors


# --- RRF (fuziune) ----------------------------------------------------
def rrf(rankings, graph_set):
    """Fuzionează mai multe clasamente plus apartenența la graf, prin 1/(K+rang)."""
    scores = {d: 0.0 for d in DOCS}
    for ranking in rankings:
        for rank, d in enumerate(ranking, start=1):
            scores[d] += 1 / (K + rank)
    for d in graph_set:                       # graful votează ca un „rang 1"
        scores[d] += 1 / (K + 1)
    return sorted(DOCS, key=lambda d: scores[d], reverse=True), scores


def show(title, ranking):
    print(f"\n{title}")
    for rank, d in enumerate(ranking, start=1):
        print(f"  {rank}. {d}  {DOCS[d][:52]}…")


def main():
    print(f"Întrebare: {QUESTION}")

    bm25 = bm25_ranking(QUESTION)
    vector = vector_ranking(QUERY_VECTOR)
    seeds = {bm25[0], vector[0]}                 # top-1 din fiecare retriever
    graph = graph_candidates(seeds)

    show("BM25 (lexical):", bm25)
    show("Vector (semantic):", vector)
    print(f"\nGraph (al doilea hop din semințele {sorted(seeds)}): {sorted(graph)}")

    fused, scores = rrf([bm25, vector], graph)
    print("\nHYBRID (RRF: BM25 + vector + graph):")
    for rank, d in enumerate(fused, start=1):
        print(f"  {rank}. {d}  RRF={scores[d]:.4f}  {DOCS[d][:46]}…")

    print(f"\nLanțul de dovezi (GCP + bridge + AWS): "
          f"{[d for d in fused if d != 'b1ffac02'][:3]} — distractorul de billing cade jos.")


if __name__ == "__main__":
    main()
