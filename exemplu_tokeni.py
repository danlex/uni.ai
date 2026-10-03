#!/usr/bin/env python3
"""Exemplu simplu de tokenizare cu tiktoken (slide-ul 24 din curs).

Rulare:
    .venv/bin/python -m pip install tiktoken   # o singură dată
    .venv/bin/python exemplu_tokeni.py
"""

import tiktoken

text = "Ana învață Python și vrea să scrie un program care sortează o listă de numere."

# Împărțim textul în tokeni (identificatori numerici).
enc = tiktoken.get_encoding("o200k_base")
token_ids = enc.encode(text)

print(f"Text: {text}")
print(f"Număr de tokeni: {len(token_ids)}\n")

print("Nr. | ID token | Fragment")
print("----+----------+---------")
for i, token_id in enumerate(token_ids, 1):
    fragment = enc.decode([token_id])
    print(f"{i:3} | {token_id:8} | {fragment!r}")
