import json
import sys
from pathlib import Path

INPUT_PATH = Path("data/processed/corpus_sample.jsonl")
OUTPUT_PATH = Path("data/processed/corpus_annotated.jsonl")

def make_key(rec):
    return f"{rec.get('document_id')}::{rec.get('target_sequence')}"

def main():
    if len(sys.argv) < 2:
        print("Uso: python append_annotations.py '<json_annotations_string>'")
        sys.exit(1)
        
    try:
        annotations = json.loads(sys.argv[1])
    except Exception as e:
        print(f"Error parsing JSON input: {e}")
        sys.exit(1)
        
    # Cargar todos los registros del input para buscar los datos originales
    records_by_key = {}
    with open(INPUT_PATH, "r", encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if line:
                rec = json.loads(line)
                records_by_key[make_key(rec)] = rec
                
    # Cargar registros ya anotados para evitar duplicados
    annotated_keys = set()
    if OUTPUT_PATH.exists():
        with open(OUTPUT_PATH, "r", encoding="utf-8") as f:
            for line in f:
                line = line.strip()
                if line:
                    rec = json.loads(line)
                    annotated_keys.add(make_key(rec))
                    
    added_count = 0
    with open(OUTPUT_PATH, "a", encoding="utf-8") as f:
        for ann in annotations:
            # Obtener key
            if "target_sequence" in ann:
                key = f"{ann['document_id']}::{ann['target_sequence']}"
            else:
                # Si no se pasó target_sequence, buscar en records_by_key coincidencia única
                matching_keys = [k for k in records_by_key.keys() if k.startswith(ann["document_id"] + "::")]
                if not matching_keys:
                    print(f"Error: document_id {ann['document_id']} no encontrado.")
                    continue
                if len(matching_keys) > 1:
                    print(f"Error: document_id {ann['document_id']} tiene múltiples secuencias. Por favor especifique target_sequence.")
                    continue
                key = matching_keys[0]
                
            if key in annotated_keys:
                print(f"Registro {key} ya existe en el archivo anotado. Saltando.")
                continue
                
            if key not in records_by_key:
                print(f"Error: clave {key} no encontrada en el corpus original.")
                continue
                
            orig = records_by_key[key]
            merged = {
                **orig,
                "context_es": ann["context_es"],
                "current_es": ann["current_es"],
                "intent": ann["intent"],
                "sentiment": ann["sentiment"]
            }
            f.write(json.dumps(merged, ensure_ascii=False) + "\n")
            annotated_keys.add(key)
            added_count += 1
            
    print(f"Se agregaron exitosamente {added_count} registros anotados.")

if __name__ == "__main__":
    main()
