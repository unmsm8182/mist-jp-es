"""
MIST-JP/ES Configuration Module
Sistema de Pipeline Modular de Traducción Automática Japonés-Español
con Señales Pragmáticas de Control
"""

# Intent Labels - Etiquetas de Intención
INTENT_LABELS = [
    "afirmacion",
    "rechazo",
    "solicitud",
    "pregunta",
    "duda"
]

# Tone Labels - Etiquetas de Tono
TONE_LABELS = [
    "positivo",
    "negativo",
    "neutral",
    "incierto"
]

# Model Identifiers
TRANSLATION_MODEL = "Helsinki-NLP/opus-mt-ja-es"
INTENT_MODEL = "models/intent_model"
TONE_MODEL = "models/tone_model"

# Demo Sentences - Oraciones en Japonés para Demostración
DEMO_SENTENCES = [
    "ちょっと難しいですね...",
    "本当にありがとうございます！",
    "行けるかな...",
    "よろしくお願いします",
    "本当ですか？",
    "そうですよね"
]
