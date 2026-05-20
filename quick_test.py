#!/usr/bin/env python3
"""
Quick Start Script
Script de inicio rápido para probar MIST-JP/ES localmente

Uso:
    python quick_test.py
"""

import sys
import os

# Agregar el directorio actual al path para imports locales
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from modules.intent_classifier import IntentClassifier
from modules.tone_classifier import ToneClassifier


def quick_test():
    """
    Prueba rápida de los módulos clasificadores sin necesidad
    de descargar el modelo de traducción completo.
    """
    print("\n" + "=" * 60)
    print("QUICK TEST: Clasificadores MIST-JP/ES")
    print("=" * 60 + "\n")
    
    # Instanciar clasificadores
    print("✓ Inicializando IntentClassifier...")
    intent_classifier = IntentClassifier()
    
    print("✓ Inicializando ToneClassifier...")
    tone_classifier = ToneClassifier()
    
    # Oraciones de prueba
    test_sentences = [
        "ちょっと難しいですね...",
        "本当にありがとうございます！",
        "行けるかな...",
        "よろしくお願いします",
        "本当ですか？",
        "そうですよね"
    ]
    
    print("\n" + "-" * 60)
    print("Clasificando oraciones de prueba:")
    print("-" * 60 + "\n")
    
    for sentence in test_sentences:
        intent = intent_classifier.predict(sentence)
        tone = tone_classifier.predict(sentence)
        
        print(f"📝 {sentence}")
        print(f"   Intención: {intent['label']:12} (confianza: {intent['confidence']:.0%})")
        print(f"   Tono:      {tone['label']:12} (confianza: {tone['confidence']:.0%})")
        print()
    
    print("=" * 60)
    print("✓ Quick test completado exitosamente")
    print("=" * 60 + "\n")
    print("Nota: Para usar el traductor, ejecuta: python demo.py")
    print("      Esto descargará los modelos necesarios (~2GB)\n")


if __name__ == "__main__":
    try:
        quick_test()
    except Exception as e:
        print(f"\n✗ Error en quick test: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
