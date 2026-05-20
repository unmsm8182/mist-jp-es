"""
Pipeline Module
Pipeline Principal del Sistema MIST-JP/ES

Orquesta la ejecución completa del pipeline de traducción
con clasificación de intención y tono.
"""

import logging
from typing import Dict, Any
from modules.intent_classifier import IntentClassifier
from modules.tone_classifier import ToneClassifier
from modules.translator import Translator

logger = logging.getLogger(__name__)


class MISTPipeline:
    """
    Pipeline Principal del Sistema MIST-JP/ES.
    
    Orquesta la ejecución del flujo completo:
    1. Clasificación de intención
    2. Clasificación de tono
    3. Traducción estándar (baseline)
    4. Traducción enriquecida con señales pragmáticas
    
    Attributes:
        intent_classifier (IntentClassifier): Módulo clasificador de intención
        tone_classifier (ToneClassifier): Módulo clasificador de tono
        translator (Translator): Módulo traductor
    """
    
    def __init__(self) -> None:
        """
        Inicializa el Pipeline MIST-JP/ES.
        
        Instancia los tres módulos principales del sistema:
        - Clasificador de Intención
        - Clasificador de Tono
        - Traductor
        
        Raises:
            RuntimeError: Si hay error en la inicialización de algún módulo
        """
        try:
            logger.info("Inicializando MISTPipeline...")
            
            logger.info("Inicializando IntentClassifier...")
            self.intent_classifier = IntentClassifier()
            
            logger.info("Inicializando ToneClassifier...")
            self.tone_classifier = ToneClassifier()
            
            logger.info("Inicializando Translator...")
            self.translator = Translator()
            
            logger.info("MISTPipeline inicializado exitosamente")
            
        except Exception as e:
            logger.error(f"Error inicializando pipeline: {e}")
            raise RuntimeError(f"Error inicializando MISTPipeline: {e}")
    
    def run(self, japanese_text: str) -> Dict[str, Any]:
        """
        Ejecuta el pipeline completo sobre un texto japonés.
        
        Realiza las siguientes operaciones en secuencia:
        1. Clasifica la intención del texto
        2. Clasifica el tono emocional del texto
        3. Genera traducción estándar (sin señales)
        4. Construye input enriquecido con señales pragmáticas
        5. Genera traducción con señales pragmáticas
        
        Args:
            japanese_text (str): Texto en japonés a procesar
            
        Returns:
            Dict[str, Any]: Diccionario con estructura:
                {
                    "input": str (texto original),
                    "intent": {
                        "label": str,
                        "confidence": float
                    },
                    "tone": {
                        "label": str,
                        "confidence": float
                    },
                    "enriched_input": str (input con señales),
                    "baseline_translation": str (sin señales),
                    "mist_translation": str (con señales)
                }
                
        Raises:
            ValueError: Si el texto está vacío
            RuntimeError: Si hay error en alguna etapa del pipeline
        """
        if not japanese_text or not japanese_text.strip():
            raise ValueError("El texto japonés no puede estar vacío")
        
        try:
            logger.info(f"Ejecutando pipeline para: {japanese_text}")
            
            # Etapa 1: Clasificar intención
            logger.debug("Clasificando intención...")
            intent_result = self.intent_classifier.predict(japanese_text)
            
            # Etapa 2: Clasificar tono
            logger.debug("Clasificando tono...")
            tone_result = self.tone_classifier.predict(japanese_text)
            
            # Etapa 3: Traducción estándar (baseline)
            logger.debug("Generando traducción baseline...")
            baseline_translation = self.translator.translate(japanese_text)
            
            # Etapa 4: Construir input enriquecido
            enriched_input = (
                f"[INTENT:{intent_result['label']}][TONE:{tone_result['label']}] "
                f"{japanese_text}"
            )
            logger.debug(f"Input enriquecido: {enriched_input}")
            
            # Etapa 5: Traducción con señales pragmáticas
            logger.debug("Generando traducción MIST con señales...")
            mist_translation = self.translator.translate_with_signals(
                japanese_text,
                intent_result['label'],
                tone_result['label']
            )
            
            # Construir resultado final
            result = {
                "input": japanese_text,
                "intent": intent_result,
                "tone": tone_result,
                "enriched_input": enriched_input,
                "baseline_translation": baseline_translation,
                "mist_translation": mist_translation
            }
            
            logger.info("Pipeline ejecutado exitosamente")
            return result
            
        except Exception as e:
            logger.error(f"Error ejecutando pipeline: {e}")
            raise RuntimeError(f"Error en pipeline: {e}")
    
    def compare(self, japanese_text: str) -> None:
        """
        Ejecuta el pipeline y imprime tabla comparativa en consola.
        
        Muestra un resumen formateado con:
        - Texto de entrada en japonés
        - Intención detectada y confianza
        - Tono detectado y confianza
        - Traducción baseline (sin señales)
        - Traducción MIST-JP/ES (con señales)
        
        Args:
            japanese_text (str): Texto en japonés a procesar
            
        Raises:
            RuntimeError: Si hay error en la ejecución del pipeline
        """
        try:
            result = self.run(japanese_text)
            
            # Formato: convertir confianzas a porcentaje
            intent_confidence_pct = int(result["intent"]["confidence"] * 100)
            tone_confidence_pct = int(result["tone"]["confidence"] * 100)
            
            # Imprimir tabla comparativa
            print("\n" + "=" * 60)
            print(f"INPUT: {result['input']}")
            print(f"INTENCIÓN: {result['intent']['label']} ({intent_confidence_pct}%)")
            print(f"TONO: {result['tone']['label']} ({tone_confidence_pct}%)")
            print("-" * 60)
            print(f"BASELINE:   {result['baseline_translation']}")
            print(f"MIST-JP/ES: {result['mist_translation']}")
            print("=" * 60)
            
        except Exception as e:
            logger.error(f"Error en compare: {e}")
            print(f"\nError procesando texto: {e}")
            raise
