#!/usr/bin/env python3
"""GraphRAG: extragem relații și conectăm paragrafele (slide 8 din rag.html).

Din fiecare paragraf extragem o afirmație structurată (subiect, relație, obiect,
sursă). Entitatea „Fabrica Brașov" apare în P2 și P3 și devine același nod, deci
putem urmări un lanț care trece prin mai multe paragrafe:

    Pegas --produce--> Vela --asamblată la--> Fabrica Brașov --energie de la--> Solaris
"""

# Pas 1 — afirmațiile extrase din cele trei paragrafe (slide 8).
# Fiecare relație își păstrează sursa (din ce paragraf provine).
RELATIONS = [
    {"from": "Pegas", "label": "produce", "to": "Vela", "source": "P1"},
    {"from": "Vela", "label": "asamblată la", "to": "Fabrica Brașov", "source": "P2"},
    {"from": "Fabrica Brașov", "label": "energie de la", "to": "Solaris", "source": "P3"},
]


def relatii_din(nod):
    """Toate relațiile care pornesc dintr-un nod dat."""
    return [r for r in RELATIONS if r["from"] == nod]


def follow_chain(start):
    """Urmărește lanțul de relații pornind dintr-un nod.

    La fiecare pas mergem de la nodul curent la vecinul lui prin relația găsită,
    strângând pașii și sursele parcurse. Întoarce:
      - nodul final al lanțului (răspunsul),
      - sursele folosite, în ordine,
      - descrierea fiecărui pas (pentru verificare).
    """
    nod_curent = start
    surse = []
    pasi = []

    relatii = relatii_din(nod_curent)
    while relatii:
        relatie = relatii[0]  # lanțul nostru are câte o singură ieșire per nod
        pasi.append(f"{relatie['from']} --{relatie['label']}--> {relatie['to']} [{relatie['source']}]")
        surse.append(relatie["source"])

        nod_curent = relatie["to"]       # avansăm la nodul următor
        relatii = relatii_din(nod_curent)

    return nod_curent, surse, pasi


def answer_multi_hop(start="Pegas"):
    """Răspunde la întrebarea compusă urmărind lanțul din graf.

    Pegas -> Vela -> Fabrica Brașov -> Solaris. Capătul lanțului este răspunsul,
    iar sursele parcurse sunt dovezile recuperate.
    """
    nod_final, surse, pasi = follow_chain(start)
    return nod_final, surse, pasi


if __name__ == "__main__":
    nod_final, surse, pasi = answer_multi_hop()
    for pas in pasi:
        print(pas)
    print(f"\nRăspuns: {nod_final}. [{', '.join(surse)}]")
