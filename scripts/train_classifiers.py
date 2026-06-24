import os
import json
import logging
import torch
from typing import List, Dict, Tuple
from datasets import Dataset
from transformers import (
    AutoTokenizer,
    AutoModelForSequenceClassification,
    TrainingArguments,
    Trainer
)
import numpy as np
from sklearn.model_selection import train_test_split
from sklearn.metrics import accuracy_score, precision_recall_fscore_support

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Configuración
MODEL_NAME = "cl-tohoku/bert-base-japanese"
DATA_PATH = "../corpus/data/processed/corpus_annotated.jsonl"
INTENT_MODEL_PATH = "../models/intent_model"
TONE_MODEL_PATH = "../models/tone_model"

INTENT_LABELS = ["afirmacion", "rechazo", "solicitud", "pregunta", "duda"]
TONE_LABELS = ["positivo", "negativo", "neutral", "incierto"]

def normalize_label(label: str) -> str:
    """Normaliza las etiquetas del JSONL a las esperadas por el sistema."""
    label = label.lower().strip()
    if label == "afirmación":
        return "afirmacion"
    return label

def load_data(file_path: str) -> Tuple[List[str], List[int], List[int]]:
    """Carga los textos y las etiquetas del archivo JSONL."""
    texts = []
    intents = []
    tones = []
    
    with open(file_path, "r", encoding="utf-8") as f:
        for line in f:
            data = json.loads(line)
            text = data.get("current_ja", "")
            
            raw_intent = data.get("intent", "Afirmación")
            raw_tone = data.get("sentiment", "Neutral")
            
            intent = normalize_label(raw_intent)
            tone = normalize_label(raw_tone)
            
            # Mapear a IDs
            if intent in INTENT_LABELS and tone in TONE_LABELS:
                texts.append(text)
                intents.append(INTENT_LABELS.index(intent))
                tones.append(TONE_LABELS.index(tone))
            else:
                logger.warning(f"Etiquetas desconocidas - intent: {intent}, tone: {tone}")
                
    return texts, intents, tones

def compute_metrics(eval_pred):
    predictions, labels = eval_pred
    predictions = np.argmax(predictions, axis=1)
    precision, recall, f1, _ = precision_recall_fscore_support(labels, predictions, average='weighted')
    acc = accuracy_score(labels, predictions)
    return {
        'accuracy': acc,
        'f1': f1,
        'precision': precision,
        'recall': recall
    }

def train_model(
    task_name: str,
    texts: List[str],
    labels: List[int],
    label_names: List[str],
    output_dir: str,
    num_train_epochs: int = 3
):
    logger.info(f"Iniciando entrenamiento para: {task_name}")
    
    # Split datos
    train_texts, val_texts, train_labels, val_labels = train_test_split(
        texts, labels, test_size=0.1, random_state=42, stratify=labels
    )
    
    # Cargar Tokenizador y Modelo
    tokenizer = AutoTokenizer.from_pretrained(MODEL_NAME)
    model = AutoModelForSequenceClassification.from_pretrained(
        MODEL_NAME, 
        num_labels=len(label_names),
        id2label={str(i): label for i, label in enumerate(label_names)},
        label2id={label: i for i, label in enumerate(label_names)}
    )
    
    # Tokenizar
    train_encodings = tokenizer(train_texts, truncation=True, padding=True)
    val_encodings = tokenizer(val_texts, truncation=True, padding=True)
    
    # Crear Datasets
    class SimpleDataset(torch.utils.data.Dataset):
        def __init__(self, encodings, labels):
            self.encodings = encodings
            self.labels = labels

        def __getitem__(self, idx):
            item = {key: torch.tensor(val[idx]) for key, val in self.encodings.items()}
            item['labels'] = torch.tensor(self.labels[idx])
            return item

        def __len__(self):
            return len(self.labels)
            
    train_dataset = SimpleDataset(train_encodings, train_labels)
    val_dataset = SimpleDataset(val_encodings, val_labels)
    
    # Configurar argumentos de entrenamiento
    training_args = TrainingArguments(
        output_dir=f"./results_{task_name}",
        num_train_epochs=num_train_epochs,
        per_device_train_batch_size=16,
        per_device_eval_batch_size=64,
        warmup_steps=50,
        weight_decay=0.01,
        logging_dir=f"./logs_{task_name}",
        logging_steps=10,
        eval_strategy="epoch",
        save_strategy="epoch",
        load_best_model_at_end=True
    )
    
    trainer = Trainer(
        model=model,
        args=training_args,
        train_dataset=train_dataset,
        eval_dataset=val_dataset,
        compute_metrics=compute_metrics
    )
    
    # Entrenar
    trainer.train()
    
    # Evaluar
    eval_results = trainer.evaluate()
    logger.info(f"Resultados de validación ({task_name}): {eval_results}")
    
    # Guardar modelo y tokenizador localmente
    model.save_pretrained(output_dir)
    tokenizer.save_pretrained(output_dir)
    logger.info(f"Modelo de {task_name} guardado en {output_dir}")


if __name__ == "__main__":
    # Asegurarnos de que estamos en el directorio correcto
    current_dir = os.path.dirname(os.path.abspath(__file__))
    os.chdir(current_dir)
    
    logger.info("Cargando dataset...")
    texts, intents, tones = load_data(DATA_PATH)
    logger.info(f"Cargados {len(texts)} ejemplos.")
    
    # Entrenar modelo de intención
    train_model(
        task_name="Intent",
        texts=texts,
        labels=intents,
        label_names=INTENT_LABELS,
        output_dir=INTENT_MODEL_PATH,
        num_train_epochs=5
    )
    
    # Entrenar modelo de tono
    train_model(
        task_name="Tone",
        texts=texts,
        labels=tones,
        label_names=TONE_LABELS,
        output_dir=TONE_MODEL_PATH,
        num_train_epochs=5
    )
    
    logger.info("¡Fine-tuning completado exitosamente!")
