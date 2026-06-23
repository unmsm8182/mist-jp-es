# Corpus JA-ES — Flujo de trabajo

Corpus bilingüe japonés-español basado en OpenSubtitles (OPUS), con anotación pragmática automática vía Gemini.

## Requisitos previos

```bash
cd corpus
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt   # o según el entorno del proyecto
```

Crea un archivo `corpus/.env` con tu clave de Gemini:

```
GEMINI_API_KEY=<tu-clave>
```

---

## Flujo completo

```
OPUS API
   │
   ▼
[0] download_corpus.py          → data/es-ja.tmx  (230 MB)
   │
   ▼
[1] script_01_explore.py        → análisis exploratorio del TMX
   │
   ▼
[2] script_02_process.py        → corpus_es_ja.jsonl  (extracción básica)
   │
   ▼
[3] script_03_pipeline.ipynb    → corpus_base.jsonl
   │                               corpus_contextual.jsonl
   │                               corpus_filtered.jsonl
   ▼
[4] script_04_annotate.ipynb    → pilot_annotations.json
    run_annotation_pipeline.py  → corpus_annotated.jsonl
```

---

## Paso a paso

### 0 · Descargar el corpus

Consulta la API de OPUS y descarga el archivo TMX (~230 MB comprimido, ~50 MB en `.gz`):

```bash
python download_corpus.py
```

Genera: `data/es-ja.tmx`

---

### 1 · Exploración

Analiza una muestra del TMX sin cargarlo completo en memoria. Útil para entender la distribución de longitudes, idiomas y posibles problemas de calidad.

```bash
python script_01_explore.py
```

No genera archivos de salida — solo imprime estadísticas en consola.

---

### 2 · Procesamiento básico

Extrae, limpia y filtra los pares de traducción del TMX. Aplica filtros de longitud mínima/máxima y ratio entre lenguas.

```bash
python script_02_process.py
```

Genera: `data/processed/corpus_es_ja.jsonl`

---

### 3 · Pipeline completo

Ejecuta las dos etapas del pipeline:

- **Etapa 1 — Extracción + filtro:** produce `corpus_base.jsonl` (~1.3 M pares limpios)
- **Etapa 2 — Enriquecimiento contextual:** añade ventana de contexto y detecta partículas japonesas pragmáticas (よ, ね, んだ…)

Abre y ejecuta el notebook:

```bash
jupyter notebook script_03_pipeline.ipynb
```

Genera en `data/processed/`:
| Archivo | Descripción |
|---|---|
| `corpus_base.jsonl` | Pares limpios sin contexto (316 MB) |
| `corpus_contextual.jsonl` | Pares con ventana de contexto `[SEP]` (615 MB) |
| `corpus_filtered.jsonl` | Solo pares con partícula detectada (115 MB) |
| `pipeline_report.json` | Estadísticas de todo el pipeline |

---

### 4 · Anotación pragmática

Anota `intent` y `sentiment` usando Gemini vía Google Antigravity SDK. Hay dos opciones:

**Opción A — Notebook interactivo** (recomendado para pilotos):

```bash
export GEMINI_API_KEY=$(grep GEMINI_API_KEY .env | cut -d= -f2)
jupyter notebook script_04_annotate.ipynb
```

Ejecuta primero la celda de **validación piloto** (~20 ejemplos por partícula) antes de lanzar la anotación completa.

**Opción B — Script en línea de comandos** (para producción):

```bash
export GEMINI_API_KEY=$(grep GEMINI_API_KEY .env | cut -d= -f2)
python run_annotation_pipeline.py
```

El script es incremental: si se interrumpe, retoma desde donde quedó.

Genera en `data/processed/`:
| Archivo | Descripción |
|---|---|
| `pilot_sample.json` | Muestra estratificada del piloto |
| `pilot_annotations.json` | Anotaciones del piloto para revisión manual |
| `corpus_annotated.jsonl` | corpus completo anotado |

---

## Estructura de un registro anotado

```json
{
  "document_id": "2013/2930778/5345175",
  "target_sequence": 12,
  "context_ja": "...[SEP]...",
  "current_ja": "そうですか",
  "context_es": "...[SEP]...",
  "current_es": "¿En serio?",
  "particle": "か",
  "particles_detected": ["か"],
  "intent": "Pregunta",
  "sentiment": "Neutral"
}
```

---

## Agregar anotaciones manuales

Para añadir correcciones manuales al archivo anotado sin reprocesar todo:

```bash
python append_annotations.py '[{"document_id": "...", "intent": "Afirmación", "sentiment": "Positivo", "context_es": "...", "current_es": "..."}]'
```
