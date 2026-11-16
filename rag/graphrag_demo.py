#!/usr/bin/env python3
"""Graph RAG: construim un graf de documente și răspundem multi-hop (fără dependențe).

Spre deosebire de căutarea vectorială sau BM25, Graph RAG leagă documentele între
ele prin entități comune și prin mențiuni, apoi urmărește lanțul de dovezi. Așa
rezolvăm întrebări care cer conectarea mai multor pasaje (ex. Pegas -> Solaris),
pe care un singur top-k le ratează.

Rulare:
    python3 graphrag_demo.py
"""

import re

# Corpusul didactic (același ca în restul folderului).
PASSAGES = {
    "P1": "Compania Pegas produce bicicleta electrică Vela.",
    "P2": "Bicicleta Vela este asamblată la fabrica din Brașov.",
    "P3": "Fabrica din Brașov folosește energie furnizată de compania Solaris.",
}

# Entitățile pe care le urmărim (într-un sistem real le-ar extrage un model NER
# gen GLiNER2; aici le enumerăm explicit, ca exemplul să rămână simplu).
ENTITIES = ["Pegas", "Vela", "fabrica din Brașov", "Solaris"]


def entities_in(text):
    """Ce entități apare în text (potrivire simplă, fără diacritice sensibile)."""
    low = text.lower()
    return {e for e in ENTITIES if e.lower() in low}


def build_graph():
    """Noduri = paragrafe. Muchie între două paragrafe dacă împart o entitate.

    Întoarce:
      - ents: paragraf -> mulțimea de entități,
      - edges: paragraf -> set de (vecin, entitatea comună).
    """
    ents = {pid: entities_in(text) for pid, text in PASSAGES.items()}
    edges = {pid: set() for pid in PASSAGES}
    ids = list(PASSAGES)
    for a in ids:
        for b in ids:
            if a >= b:
                continue
            comune = ents[a] & ents[b]
            for e in comune:
                edges[a].add((b, e))
                edges[b].add((a, e))
    return ents, edges


def seeds_for(question, ents):
    """Paragrafele de pornire: cele care conțin o entitate din întrebare."""
    qents = entities_in(question)
    return [pid for pid, es in ents.items() if es & qents], qents


def graph_retrieve(question):
    """Recuperare pe graf: pornim din semințe și extindem prin vecini (multi-hop).

    Întoarce pasajele recuperate (în ordinea descoperirii) și pașii parcurși.
    """
    ents, edges = build_graph()
    seeds, qents = seeds_for(question, ents)

    recuperate = list(seeds)
    pasi = []
    frontiera = list(seeds)
    while frontiera:
        nod = frontiera.pop(0)
        for vecin, entitate in sorted(edges[nod]):
            pasi.append(f"{nod} --[{entitate}]--> {vecin}")
            if vecin not in recuperate:
                recuperate.append(vecin)
                frontiera.append(vecin)
    return qents, recuperate, pasi


def main():
    ents, edges = build_graph()

    print("GRAFUL DE DOCUMENTE (noduri = paragrafe, muchii = entitate comună)")
    for pid in PASSAGES:
        legaturi = ", ".join(f"{v} [{e}]" for v, e in sorted(edges[pid]))
        print(f"  {pid}  entități={sorted(ents[pid])}")
        print(f"       vecini: {legaturi or '—'}")

    # Întrebare multi-hop: lanțul Pegas -> Vela -> fabrica din Brașov -> Solaris.
    question = "Cine furnizează energia fabricii care asamblează bicicleta produsă de Pegas?"
    print(f"\nÎntrebare multi-hop:\n  {question}")

    qents, recuperate, pasi = graph_retrieve(question)
    print(f"\nEntități în întrebare: {sorted(qents)}")
    print("Traversare pe graf:")
    for p in pasi:
        print(f"  {p}")

    print("\nPasaje recuperate (lanțul complet de dovezi):")
    for pid in recuperate:
        print(f"  [{pid}] {PASSAGES[pid]}")

    # Răspunsul iese din capătul lanțului (ultima entitate nouă atinsă).
    print("\nRăspuns: Solaris. [" + ", ".join(recuperate) + "]")


if __name__ == "__main__":
    main()
