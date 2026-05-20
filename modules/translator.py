"""
Translator Module
Traductor Automático para el Sistema MIST-JP/ES

Responsable de traducir texto de japonés a español,
con soporte para enriquecimiento con señales pragmáticas.
"""

import logging
from typing import Optional
from transformers import AutoTokenizer, AutoModelForSeq2SeqLM

logger = logging.getLogger(__name__)


class Translator:
    """
    Traductor Automático de Japonés a Español.
    
    Esta clase maneja la traducción de texto japonés a español.
    Utiliza el modelo Helsinki-NLP/opus-mt-ja-es como base.
    Soporta traducción estándar y traducción enriquecida con
    señales pragmáticas de intención y tono.
    
    Attributes:
        model_name (str): Identificador del modelo de traducción
        tokenizer: Tokenizador de Marian
        model: Modelo de Marian para traducción
    """
    
    def __init__(self, model_name: str = "Helsinki-NLP/opus-mt-ja-es") -> None:
        """
        Inicializa el Traductor.
        
        Carga el modelo de traducción Marian y su tokenizador
        desde Hugging Face.
        
        Args:
            model_name (str): Identificador del modelo a usar
            
        Raises:
            RuntimeError: Si hay error al cargar el modelo o tokenizador
        """
        self.model_name = model_name
        
        try:
            logger.info(f"Cargando tokenizador para {model_name}...")
            self.tokenizer = AutoTokenizer.from_pretrained(model_name)
            logger.info(f"Tokenizador cargado exitosamente")
            
            logger.info(f"Cargando modelo de traducción {model_name}...")
            self.model = AutoModelForSeq2SeqLM.from_pretrained(model_name)
            logger.info(f"Modelo de traducción cargado exitosamente")
            
        except Exception as e:
            logger.error(f"Error cargando modelo/tokenizador: {e}")
            raise RuntimeError(
                f"No se pudo cargar el modelo de traducción {model_name}: {e}"
            )
    
    def translate(self, text: str) -> str:
        """
        Traduce texto de japonés a español sin señales pragmáticas.
        
        Realiza una traducción estándar del texto japonés.
        Esta es la línea base (baseline) contra la cual se compara
        la traducción enriquecida con señales.
        
        Args:
            text (str): Texto en japonés a traducir
            
        Returns:
            str: Texto traducido al español
            
        Raises:
            ValueError: Si el texto está vacío
        """
        if not text or not text.strip():
            raise ValueError("El texto a traducir no puede estar vacío")
        
        try:
            # Tokenizar el texto
            inputs = self.tokenizer(text, return_tensors="pt", padding=True)
            
            # Generar traducción
            outputs = self.model.generate(**inputs)
            
            # Decodificar resultado
            translation = self.tokenizer.batch_decode(outputs, skip_special_tokens=True)[0]
            
            logger.debug(f"Traducción estándar completada: {text[:50]}... → {translation[:50]}...")
            return translation
            
        except Exception as e:
            logger.error(f"Error durante traducción: {e}")
            raise RuntimeError(f"Error en traducción: {e}")
    
    def translate_with_signals(
        self,
        text: str,
        intent: str,
        tone: str
    ) -> str:
        """
        Traduce texto enriquecido con señales pragmáticas de control.
        
        Construye un input enriquecido con prefijos que contienen
        información sobre la intención y tono, permitiendo que el
        modelo de traducción tome en cuenta estas dimensiones pragmáticas.
        
        Formato del input enriquecido:
        "[INTENT:{intent}][TONE:{tone}] {text}"
        
        Args:
            text (str): Texto en japonés a traducir
            intent (str): Etiqueta de intención (ej: "afirmacion")
            tone (str): Etiqueta de tono (ej: "positivo")
            
        Returns:
            str: Texto traducido al español con señales pragmáticas
            
        Raises:
            ValueError: Si alguno de los parámetros está vacío
        """
        if not text or not text.strip():
            raise ValueError("El texto a traducir no puede estar vacío")
        if not intent or not intent.strip():
            raise ValueError("La intención no puede estar vacía")
        if not tone or not tone.strip():
            raise ValueError("El tono no puede estar vacío")
        
        try:
            # Construir input enriquecido con señales pragmáticas
            enriched_input = f"[INTENT:{intent}][TONE:{tone}] {text}"
            
            logger.debug(f"Input enriquecido: {enriched_input}")
            
            # Tokenizar el input enriquecido
            inputs = self.tokenizer(enriched_input, return_tensors="pt", padding=True)
            
            # Generar traducción
            outputs = self.model.generate(**inputs)
            
            # Decodificar resultado
            translation = self.tokenizer.batch_decode(outputs, skip_special_tokens=True)[0]
            
            logger.debug(f"Traducción con señales completada: {enriched_input[:60]}... → {translation[:50]}...")
            return translation
            
        except Exception as e:
            logger.error(f"Error durante traducción con señales: {e}")
            raise RuntimeError(f"Error en traducción con señales: {e}")
