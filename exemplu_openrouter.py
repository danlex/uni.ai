#!/usr/bin/env python3
"""Apel simplu către un model prin OpenRouter.

OpenRouter expune un singur API (compatibil OpenAI) pentru multe modele.
Cheia se citește din fișierul .env (variabila OPENROUTER_API_KEY).

Pregătire și rulare:
    python3 -m venv .venv
    .venv/bin/python -m pip install openai python-dotenv
    cp .env.example .env        # apoi pune cheia ta în .env
    .venv/bin/python exemplu_openrouter.py

Cheie gratuită: https://openrouter.ai/keys
"""

import os
import sys

from dotenv import load_dotenv
from openai import OpenAI

MODEL = "meta-llama/llama-3.3-70b-instruct"

load_dotenv()
api_key = os.getenv("OPENROUTER_API_KEY")
if not api_key:
    sys.exit("Lipsește OPENROUTER_API_KEY. Copiază .env.example în .env și pune cheia.")

# OpenRouter este compatibil OpenAI: schimbăm doar base_url și cheia.
client = OpenAI(base_url="https://openrouter.ai/api/v1", api_key=api_key)

raspuns = client.chat.completions.create(
    model=MODEL,
    messages=[
        {"role": "system", "content": "Ești un profesor de informatică. Răspunzi pe scurt, în română."},
        {"role": "user", "content": "Ce este căutarea binară?"},
    ],
)

print(raspuns.choices[0].message.content)
