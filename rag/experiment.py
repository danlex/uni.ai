#!/usr/bin/env python3
"""Experimentul complet al cursului RAG, rulabil cap-coadă (rag.html).

Reproduce, pe cele trei paragrafe fictive, pașii din curs:

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


def titlu(text):
    """Afișează un titlu de secțiune, ca separatoarele dintre slide-uri."""
    print("\n" + "=" * 72)
    print(text)
    print("=" * 72)


def recall_dovezi(dovezi_necesare, surse_recuperate):
    """Câte dintre dovezile necesare au fost recuperate, ca fracție (ex. 2/3)."""
    necesare = set(dovezi_necesare)
    gasite = necesare & set(surse_recuperate)
    return len(gasite), len(necesare)


def pas_1_chunking():
    titlu("1. CHUNKING — trei paragrafe, trei fragmente (slide 3)")
    for chunk in corpus.CHUNKS:
        print(f"  {chunk['source']} -> {chunk['id']}  ({chunk['note']})")
        print(f"       {chunk['text']}")


def pas_2_embeddings():
    titlu("2. EMBEDDINGS — un vector per chunk (slide 4, vectori didactici)")
    for chunk in corpus.CHUNKS:
        print(f"  {chunk['id']} · {chunk['text']}")
        print(f"       vector = {chunk['vector']}")


def pas_3_cautare_si_generare():
    titlu("3. CĂUTARE VECTORIALĂ + GENERARE (slide 5, 6)")
    for intrebare in corpus.QUESTIONS:
        print(f"\n  [{intrebare['id']}] {intrebare['text']}")
        print(f"      tip: {intrebare['kind']}   vector întrebare: {intrebare['vector']}")
        dovezi = intrebare["gold"] or "— (nu există în corpus)"
        print(f"      dovezi necesare (gold): {dovezi}")

        # Afișăm scorurile și sursele ÎNAINTE de răspuns (cerința slide 12).
        clasament = vector_rag.search(intrebare["vector"], k=len(corpus.CHUNKS))
        print("      clasament vectorial:")
        for loc, hit in enumerate(clasament, start=1):
            c = hit.chunk
            print(f"        {loc}. {c['id']} [{c['source']}]  {hit.score:.3f}  {c['text']}")

        # Răspundem la k = 1, 2, 3 ca să vedem efectul lui top-k (slide 5, 11).
        for k in (1, 2, 3):
            hits, raspuns = vector_rag.answer_question(intrebare, k=k)
            surse = [hit.chunk["source"] for hit in hits]
            if intrebare["gold"]:
                gasite, total = recall_dovezi(intrebare["gold"], surse)
                recall = f"recall {gasite}/{total}"
            else:
                recall = "recall n/a"
            print(f"      k={k}  context={surse}  {recall}")
            print(f"            răspuns: {raspuns}")


def pas_5_graphrag():
    titlu("5. GRAPHRAG — conectăm cele trei paragrafe (slide 8)")
    print("  Afirmații structurate (subiect, relație, obiect, sursă):")
    for r in graph_rag.RELATIONS:
        print(f"    {r['from']:14} --{r['label']:14}--> {r['to']:16} [{r['source']}]")

    print("\n  Traversare pentru întrebarea compusă [B] (Pegas -> ... -> Solaris):")
    raspuns, surse, pasi = graph_rag.answer_multi_hop(start="Pegas")
    for pas in pasi:
        print(f"    {pas}")
    print(f"\n  Răspuns din graf: {raspuns}. [{', '.join(surse)}]")
    return surse


def pas_6_evaluare(surse_graf):
    titlu("6. EVALUARE — dovezi recuperate pentru întrebarea compusă [B] (slide 11)")
    intrebarea_b = next(q for q in corpus.QUESTIONS if q["id"] == "B")

    # Căutarea vectorială la diferite valori ale lui k.
    for k in (1, 2, 3):
        hits, _ = vector_rag.answer_question(intrebarea_b, k=k)
        surse = [hit.chunk["source"] for hit in hits]
        gasite, total = recall_dovezi(intrebarea_b["gold"], surse)
        print(f"  vector top-{k}: {surse}  ->  recall {gasite}/{total} ({gasite / total:.0%})")

    # Graful, pentru comparație.
    gasite, total = recall_dovezi(intrebarea_b["gold"], surse_graf)
    print(f"  graf (lanț):  {surse_graf}  ->  recall {gasite}/{total} ({gasite / total:.0%})")

    print(
        "\n  Concluzie: căutarea vectorială ordonează după similaritate și poate rata\n"
        "  dovezi necesare unui lanț (top-1 aduce doar P1). Graful urmărește relații\n"
        "  explicite și recuperează întregul lanț Pegas -> Vela -> Fabrica Brașov -> Solaris."
    )


def main():
    pas_1_chunking()
    pas_2_embeddings()
    pas_3_cautare_si_generare()
    surse_graf = pas_5_graphrag()
    pas_6_evaluare(surse_graf)


if __name__ == "__main__":
    main()
