#!/usr/bin/env python3
"""Corpusul fictiv al cursului RAG (slide-urile 1, 3, 4, 5 din rag.html).

Trei paragrafe separate, fiecare cu o singură afirmație completă. Relațiile
sunt distribuite între paragrafe, așa încât unele întrebări se rezolvă dintr-un
singur pasaj, iar altele cer conectarea mai multor pasaje.

Vectorii de 4 dimensiuni sunt aleși manual pentru demonstrație, exact ca pe
slide-ul 4. Un model real ar calcula valorile și ar folosi sute sau mii de
dimensiuni; coordonatele de aici nu au etichete semantice prestabilite.
"""

# Slide 3 — chunking: fiecare paragraf devine un chunk (mapare unu-la-unu).
# Pentru fiecare chunk păstrăm: textul, identificatorul, documentul (sursa),
# o notă despre conținut și vectorul (slide 4).
CHUNKS = [
    {
        "id": "C1",
        "source": "P1",
        "text": "Compania Pegas produce bicicleta electrică Vela.",
        "note": "producător și produs",
        "vector": [0.90, 0.10, 0.20, 0.10],
    },
    {
        "id": "C2",
        "source": "P2",
        "text": "Bicicleta Vela este asamblată la fabrica din Brașov.",
        "note": "produs și fabrică",
        "vector": [0.20, 0.90, 0.10, 0.10],
    },
    {
        "id": "C3",
        "source": "P3",
        "text": "Fabrica din Brașov folosește energie furnizată de compania Solaris.",
        "note": "fabrică și furnizor",
        "vector": [0.10, 0.20, 0.90, 0.10],
    },
]

# Index rapid sursă -> chunk (P1 -> C1 ...).
BY_SOURCE = {c["source"]: c for c in CHUNKS}


# Întrebările din curs. Pentru fiecare reținem:
#   - vectorul didactic al întrebării (slide 5),
#   - dovezile necesare (gold evidence): ce paragrafe TREBUIE să fie în context,
#   - răspunsul susținut, folosit de generator DOAR dacă dovezile sunt prezente,
#   - tipul întrebării.
# Întrebarea B este cea compusă de pe slide 5, cu vectorul [0.9, 0.2, 0.15, 0.1].
QUESTIONS = [
    {
        "id": "A",
        "text": "Unde este asamblată bicicleta Vela?",
        "vector": [0.20, 0.90, 0.15, 0.10],
        "gold": ["P2"],
        "answer": "Bicicleta Vela este asamblată la fabrica din Brașov.",
        "kind": "single-hop",
    },
    {
        "id": "B",
        "text": "Cine furnizează energia fabricii care asamblează bicicleta produsă de Pegas?",
        "vector": [0.90, 0.20, 0.15, 0.10],
        "gold": ["P1", "P2", "P3"],
        "answer": "Solaris.",
        "kind": "multi-hop",
    },
    {
        "id": "C",
        "text": "Câți Wh are bateria Vela?",
        "vector": [0.25, 0.25, 0.20, 0.90],
        "gold": [],  # informația nu există în corpus
        "answer": None,
        "kind": "no-answer",
    },
]

# Instrucțiunea pentru generator (slide 6).
GENERATOR_INSTRUCTION = (
    "Răspunde pe baza fragmentelor oferite. Indică sursa. "
    "Dacă informația lipsește, spune ce nu poți stabili."
)
