#!/usr/bin/env python3
"""Graph RAG: un graf de documente + recuperare multi-hop (fără dependențe).

Graph RAG leagă documentele prin entități comune, apoi urmărește lanțul de
dovezi. Așa rezolvăm întrebări care cer conectarea mai multor pasaje
(Pegas -> Vela -> fabrica din Brașov -> Solaris), pe care un singur top-k le ratează.

Rulare:
    python3 graphrag_demo.py
"""

from collections import deque

# Corpusul didactic (același ca în restul folderului).
PASSAGES = {
    "P1": "Compania Pegas produce bicicleta electrică Vela.",
    "P2": "Bicicleta Vela este asamblată la fabrica din Brașov.",
    "P3": "Fabrica din Brașov folosește energie furnizată de compania Solaris.",
}

# Entitățile urmărite. Într-un sistem real le-ar extrage un model NER (ex. GLiNER2);
# aici le enumerăm, ca exemplul să rămână simplu.
ENTITIES = ["Pegas", "Vela", "fabrica din Brașov", "Solaris"]


def entities_in(text):
    """Entitățile care apar într-un text."""
    return {e for e in ENTITIES if e.lower() in text.lower()}


def build_graph():
    """Noduri = paragrafe; muchie între două paragrafe care împart o entitate.

    Întoarce (entități per paragraf, vecini per paragraf ca (vecin, entitate comună)).
    """
    ents = {pid: entities_in(text) for pid, text in PASSAGES.items()}
    edges = {pid: [] for pid in PASSAGES}
    for a in PASSAGES:
        for b in PASSAGES:
            if a < b:
                for shared in ents[a] & ents[b]:
                    edges[a].append((b, shared))
                    edges[b].append((a, shared))
    return ents, edges


def retrieve(query, ents, edges):
    """Pornim din paragrafele cu entități din întrebare și extindem prin vecini.

    Întoarce pasajele recuperate și pașii de traversare (doar descoperirile noi).
    """
    seeds = [pid for pid, es in ents.items() if es & entities_in(query)]

    found = list(seeds)
    steps = []
    queue = deque(seeds)
    while queue:
        node = queue.popleft()
        for neighbor, shared in edges[node]:
            if neighbor not in found:
                found.append(neighbor)
                steps.append(f"{node} --[{shared}]--> {neighbor}")
                queue.append(neighbor)
    return found, steps


def main():
    ents, edges = build_graph()

    print("GRAFUL DE DOCUMENTE (noduri = paragrafe, muchii = entitate comună)")
    for pid in PASSAGES:
        neighbors = ", ".join(f"{n} [{e}]" for n, e in edges[pid])
        print(f"  {pid}  entități={sorted(ents[pid])}  ->  {neighbors or '—'}")

    query = "Cine furnizează energia fabricii care asamblează bicicleta produsă de Pegas?"
    print(f"\nÎntrebare multi-hop:\n  {query}")

    found, steps = retrieve(query, ents, edges)
    print("\nTraversare pe graf (din Pegas, prin entități comune):")
    for step in steps:
        print(f"  {step}")

    print("\nLanțul de dovezi recuperat:")
    for pid in found:
        print(f"  [{pid}] {PASSAGES[pid]}")

    print("\nRăspuns: Solaris. [" + ", ".join(found) + "]")


if __name__ == "__main__":
    main()
