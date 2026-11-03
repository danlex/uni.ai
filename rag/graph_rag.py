#!/usr/bin/env python3
"""GraphRAG: extragem relații și conectăm paragrafele (slide 8 din rag.html).

Din fiecare paragraf extragem o afirmație structurată (subiect, relație, obiect,
sursă). Entitatea comună „Fabrica Brașov”, prezentă în P2 și P3, devine același
nod (pasul de rezolvare a identității). Apoi urmărim lanțul de relații pentru a
răspunde la întrebarea compusă, recuperând și pasajele-suport pentru verificare.
"""

from collections import deque

# Pas 1 — afirmații structurate extrase din cele trei paragrafe (slide 8).
# Fiecare muchie își păstrează sursa (proveniența).
TRIPLES = [
    {"subject": "Pegas", "relation": "produce", "object": "Vela", "source": "P1"},
    {"subject": "Vela", "relation": "asamblată la", "object": "Fabrica Brașov", "source": "P2"},
    {"subject": "Fabrica Brașov", "relation": "energie de la", "object": "Solaris", "source": "P3"},
]


def build_graph(triples=TRIPLES):
    """Construiește lista de adiacență: nod -> [(obiect, relație, sursă)]."""
    graph = {}
    for t in triples:
        graph.setdefault(t["subject"], []).append(
            (t["object"], t["relation"], t["source"])
        )
        graph.setdefault(t["object"], [])  # ne asigurăm că nodul există
    return graph


def traverse(start, graph=None):
    """BFS din `start`, urmărind relațiile.

    Întoarce (ordinea nodurilor vizitate, sursele pasajelor folosite,
    lista de pași subiect -> obiect [sursă]).
    """
    if graph is None:
        graph = build_graph()

    visited = [start]
    seen = {start}
    sources = []
    steps = []
    queue = deque([start])
    while queue:
        node = queue.popleft()
        for obj, rel, src in graph.get(node, []):
            steps.append(f"{node} --{rel}--> {obj} [{src}]")
            if src not in sources:
                sources.append(src)
            if obj not in seen:
                seen.add(obj)
                visited.append(obj)
                queue.append(obj)
    return visited, sources, steps


def answer_multi_hop(start="Pegas"):
    """Răspunde la întrebarea compusă urmărind lanțul din graf.

    Pegas -> Vela -> Fabrica Brașov -> Solaris. Nodul final al lanțului este
    răspunsul; sursele parcurse sunt dovezile recuperate.
    """
    visited, sources, steps = traverse(start)
    final = visited[-1]
    return final, sources, steps


if __name__ == "__main__":
    final, sources, steps = answer_multi_hop()
    for s in steps:
        print(s)
    print(f"\nRăspuns: {final}. [{', '.join(sources)}]")
