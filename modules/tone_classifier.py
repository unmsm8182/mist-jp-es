"""
Tone Classifier Module
Clasificador de Tono para el Sistema MIST-JP/ES

Responsable de identificar el tono emocional del texto japonés.
Utiliza inferencia de red neuronal basada en un modelo BERT fine-tuned.
"""

from typing import Dict
import logging
import torch
import torch.nn.functional as F
from transformers import AutoTokenizer, AutoModelForSequenceClassification

import config

logger = logging.getLogger(__name__)

class ToneClassifier:
    """
    Clasificador de Tono Emocional.
    
    Esta clase identifica el tono emocional del usuario en texto japonés
    utilizando un modelo BERT fine-tuned.
    
    Attributes:
        model_name (str): Identificador del modelo o ruta local
    """
    
    def __init__(self, model_name: str = config.TONE_MODEL) -> None:
        """
        Inicializa el Clasificador de Tono cargando el modelo real.
        
        Args:
            model_name (str): Nombre del modelo a usar
            
        Raises:
            RuntimeError: Si hay error en la inicialización del modelo
        """
        self.model_name = model_name
        self.device = torch.device("mps" if torch.backends.mps.is_available() else ("cuda" if torch.cuda.is_available() else "cpu"))
        
        logger.info(f"ToneClassifier inicializando con modelo: {model_name} en device: {self.device}")
        
        try:
            self.tokenizer = AutoTokenizer.from_pretrained(model_name)
            self.model = AutoModelForSequenceClassification.from_pretrained(model_name)
            self.model.to(self.device)
            self.model.eval()
            logger.info("Modelo de tono cargado exitosamente.")
        except Exception as e:
            logger.error(f"Error cargando modelo: {e}")
            raise RuntimeError(f"No se pudo cargar el modelo de tono: {model_name}. Error: {e}")
    
    def predict(self, text: str) -> Dict[str, any]:
        """
        Predice el tono emocional del texto japonés utilizando el modelo neural.
        
        Args:
            text (str): Texto en japonés a clasificar
            
        Returns:
            Dict[str, any]: Diccionario con estructura:
                {
                    "label": str (tono predicho),
                    "confidence": float (confianza de la predicción)
                }
        """
        if not text or not text.strip():
            return {"label": "neutral", "confidence": 0.0}
            
        try:
            inputs = self.tokenizer(text, return_tensors="pt", truncation=True, padding=True).to(self.device)
            
            with torch.no_grad():
                outputs = self.model(**inputs)
                logits = outputs.logits
                probs = F.softmax(logits, dim=1)
                
            confidence, predicted_class_id = torch.max(probs, dim=1)
            label = self.model.config.id2label[predicted_class_id.item()]
            
            result = {
                "label": label,
                "confidence": round(confidence.item(), 4)
            }
            
            logger.debug(f"Tone prediction for '{text}': {result}")
            return result
            
        except Exception as e:
            logger.error(f"Error en predicción de tono: {e}")
            return {"label": "neutral", "confidence": 0.0}
