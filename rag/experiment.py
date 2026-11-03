#!/usr/bin/env python3
"""Experimentul complet al cursului RAG, rulabil cap-coadă (rag.html).

Reproduce, pe cele trei paragrafe fictive, exact pașii din curs:

  1. Chunking            (slide 3)  — 3 paragrafe -> 3 chunks
  2. Embeddings          (slide 4)  — un vector per chunk
  3. Căutare vectorială  (slide 5)  — scoruri + surse ÎNAINTE de răspuns
  4. Generare cu citări  (slide 6)  — răspuns susținut sau abținere
  5. GraphRAG            (slide 8)  — graf de relații + traversare multi-hop
  6. Evaluare            (slide 11) — recall al dovezilor, vector vs. graf

Rulare:
    python3 experiment.py          # din folderul rag/
Fără dependențe externe. Scorurile ies identice cu cele de pe slide-uri.
"""

import corpus
import graph_rag
import vector_rag


def rule(title):
    print("\n" + "=" * 72)
    print(title)
    print("=" * 72)


def retrieval_recall(gold, retrieved_sources):
    """Recall al dovezilor = câte pasaje necesare au fost recuperate."""
    gold = set(gold)
    if not gold:
        return None  # întrebare fără răspuns: recall-ul nu se aplică
    hit = gold & set(retrieved_sources)
    return len(hit), len(gold)


def main():
    # ---- 1. Chunking (slide 3) ------------------------------------------
    rule("1. CHUNKING — trei paragrafe, trei fragmente (slide 3)")
    for c in corpus.CHUNKS:
        print(f"  {c['source']} -> {c['id']}  ({c['note']})")
        print(f"       {c['text']}")

    # ---- 2. Embeddings (slide 4) ----------------------------------------
    rule("2. EMBEDDINGS — un vector per chunk (slide 4, vectori didactici)")
    for c in corpus.CHUNKS:
        print(f"  {c['id']} · {c['text']}")
        print(f"       vector = {c['vector']}")

    # ---- 3+4. Căutare vectorială + generare (slide 5, 6) ----------------
    rule("3. CĂUTARE VECTORIALĂ + GENERARE (slide 5, 6)")
    for q in corpus.QUESTIONS:
        print(f"\n  [{q['id']}] {q['text']}")
        print(f"      tip: {q['kind']}   vector întrebare: {q['vector']}")
        print(f"      dovezi necesare (gold): {q['gold'] or '— (nu există în corpus)'}")

        # Afișăm scorurile și sursele ÎNAINTE de răspuns (cerința slide 12).
        ranked = vector_rag.search(q["vector"], k=len(corpus.CHUNKS))
        print("      clasament vectorial:")
        for rank, (c, score) in enumerate(ranked, 1):
            print(f"        {rank}. {c['id']} [{c['source']}]  {score:.3f}  {c['text']}")

        # Răspundem la k = 1, 2, 3 ca să vedem efectul lui top-k (slide 5, 11).
        for k in (1, 2, 3):
            retrieved, answer, citations = vector_rag.answer_question(q, k=k)
            sources = [c["source"] for c, _ in retrieved]
            rec = retrieval_recall(q["gold"], sources)
            rec_txt = f"recall {rec[0]}/{rec[1]}" if rec else "recall n/a"
            print(f"      k={k}  context={sources}  {rec_txt}")
            print(f"            răspuns: {answer}")

    # ---- 5. GraphRAG (slide 8) ------------------------------------------
    rule("5. GRAPHRAG — conectăm cele trei paragrafe (slide 8)")
    print("  Afirmații structurate (subiect, relație, obiect, sursă):")
    for t in graph_rag.TRIPLES:
        print(f"    {t['subject']:14} --{t['relation']:14}--> {t['object']:16} [{t['source']}]")
    print("\n  Traversare pentru întrebarea compusă [B] (Pegas -> ... -> Solaris):")
    final, g_sources, steps = graph_rag.answer_multi_hop(start="Pegas")
    for s in steps:
        print(f"    {s}")
    print(f"\n  Răspuns din graf: {final}. [{', '.join(g_sources)}]")

    # ---- 6. Evaluare: vector vs. graf pe întrebarea compusă (slide 11) ---
    rule("6. EVALUARE — dovezi recuperate pentru întrebarea compusă [B] (slide 11)")
    qb = next(q for q in corpus.QUESTIONS if q["id"] == "B")

    for k in (1, 2, 3):
        retrieved, _, _ = vector_rag.answer_question(qb, k=k)
        sources = [c["source"] for c, _ in retrieved]
        hit, total = retrieval_recall(qb["gold"], sources)
        print(f"  vector top-{k}: {sources}  ->  recall {hit}/{total} ({hit/total:.0%})")

    hit, total = retrieval_recall(qb["gold"], g_sources)
    print(f"  graf (BFS):   {g_sources}  ->  recall {hit}/{total} ({hit/total:.0%})")

    print(
        "\n  Concluzie: căutarea vectorială ordonează după similaritate și poate rata\n"
        "  dovezi necesare unui lanț (top-1 aduce doar P1). Graful urmărește relații\n"
        "  explicite și recuperează întregul lanț Pegas -> Vela -> Fabrica Brașov -> Solaris."
    )


if __name__ == "__main__":
    main()
