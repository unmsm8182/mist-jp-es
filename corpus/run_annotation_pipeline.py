import asyncio
import json
import os
import sys
from pathlib import Path
from typing import Optional, Literal

import pydantic
from google.antigravity import Agent, LocalAgentConfig

INPUT_PATH  = Path("data/processed/corpus_sample.jsonl")
OUTPUT_PATH = Path("data/processed/corpus_annotated.jsonl")

GEMINI_API_KEY = os.environ["GEMINI_API_KEY"]
MODEL_NAME     = "gemini-3.5-flash"

class AnnotationResponse(pydantic.BaseModel):
    context_es: str
    current_es: str
    intent: Literal["Afirmación", "Rechazo", "Solicitud", "Pregunta", "Duda"]
    sentiment: Literal["Positivo", "Negativo", "Neutral", "Incierto"]

ANNOTATION_PROMPT = """Eres un anotador lingüístico especializado en pragmática japonesa, análisis discursivo y traducción japonés-español.

OBJETIVO

Realizar una anotación de un corpus japonés-español para validar una taxonomía de intención comunicativa y tono afectivo-pragmático.

TAREAS

Para cada registro:

1. Analizar conjuntamente:
   * context_ja
   * current_ja
   * context_es
   * current_es
   * particle
   * particles_detected

2. Revisar las traducciones de:
   * context_es
   * current_es

3. Corregir únicamente cuando exista un error real de traducción, omisión relevante, adición de significado inexistente o pérdida pragmática importante respecto al japonés original.

4. Etiquetar:
   * intent
   * sentiment

REGLAS DE TRADUCCIÓN

* NO reformules por estilo.
* NO sustituyas expresiones simplemente porque existe una traducción mejor.
* NO modernice el lenguaje.
* NO hagas cambios cosméticos.
* Conserva la traducción original cuando sea aceptable y transmita correctamente el significado.

IMPORTANTE:

Si la traducción es adecuada, devuelve exactamente la misma traducción.
La corrección debe ser conservadora.
Sólo modifica una traducción cuando exista evidencia clara de que no representa correctamente el contenido japonés.

REGLAS DE ANOTACIÓN

* Analiza principalmente current_ja junto con context_ja.
* Utiliza context_es y current_es únicamente como apoyo interpretativo.
* La partícula es una evidencia secundaria.
* No asumas que una partícula determina automáticamente una categoría.
* Si existe conflicto entre la partícula y el significado global del enunciado, prevalece el significado global.
* Selecciona exactamente una categoría de intención.
* Selecciona exactamente una categoría de sentimiento.
* Nunca inventes categorías nuevas.
* No expliques tu razonamiento.
* No agregues comentarios.
* No agregues campos adicionales.

TAXONOMÍA DE INTENCIÓN

Afirmación: Acuerdo, aceptación o confirmación genuina (Marcadores frecuentes: はい, そうです, そうだ, よ)
Rechazo: Negación, desacuerdo, oposición o rechazo directo o indirecto (Marcadores frecuentes: いいえ, de mo, けど, けれど, けれども)
Solicitud: Petición o requerimiento dirigido al interlocutor (Marcadores frecuentes: ～てください, ～ていただけますか, ～てもらえますか)
Pregunta: Búsqueda de información o confirmación (Marcadores frecuentes: ～ですか, ～でしょうか, か final)
Duda: Incertidumbre, vacilación, reflexión o falta de seguridad (Marcadores frecuentes: ～kana, ～daroaka, んだけど)

TAXONOMÍA DE TONO AFECTIVO-PRAGMÁTICO

Positivo: Tono cálido, amistoso, cooperativo o de aprobación.
Negativo: Tono agresivo, tenso, amenazante, frustrado o de desaprobación.
Neutral: Tono descriptivo o informativo sin carga afectiva marcada.
Incierto: Tono dubitativo, vacilante, reflexivo o especulativo.

SALIDA

Devuelve únicamente un objeto JSON válido con la siguiente estructura:

{
  "context_es": "...",
  "current_es": "...",
  "intent": "Afirmación|Rechazo|Solicitud|Pregunta|Duda",
  "sentiment": "Positivo|Negativo|Neutral|Incierto"
}

Si una traducción no requiere cambios, devuelve exactamente el mismo texto original.
No incluyas explicaciones.
No uses Markdown.
No envuelvas la respuesta en bloques de código.

REGISTRO A PROCESAR:
{{INPUT_JSON}}"""

MAX_RETRIES       = 3
RETRY_BASE_DELAY  = 2.0
PROGRESS_EVERY    = 50


def load_jsonl(path: Path) -> list[dict]:
    records = []
    with open(path, encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if line:
                records.append(json.loads(line))
    return records


async def call_gemini(record: dict, agent: Agent) -> Optional[dict]:
    prompt = ANNOTATION_PROMPT.replace(
        "{{INPUT_JSON}}",
        json.dumps(record, ensure_ascii=False, indent=2)
    )
    for attempt in range(MAX_RETRIES):
        try:
            response = await agent.chat(prompt)
            result = await response.structured_output()
            if result:
                if not isinstance(result, dict):
                    result = result.model_dump()
                return result
            print(f"    ✗ respuesta inválida (intento {attempt + 1})")
        except Exception as e:
            print(f"    ✗ error API (intento {attempt + 1}): {e}")
        if attempt < MAX_RETRIES - 1:
            await asyncio.sleep(RETRY_BASE_DELAY * (2 ** attempt))
    return None


async def run_pipeline(agent: Agent):
    records = load_jsonl(INPUT_PATH)
    total = len(records)
    print(f"Registros a anotar: {total:,}")

    OUTPUT_PATH.parent.mkdir(parents=True, exist_ok=True)
    annotated_keys: set[str] = set()
    if OUTPUT_PATH.exists():
        for rec in load_jsonl(OUTPUT_PATH):
            annotated_keys.add(rec.get("document_id", ""))

    ok = 0
    errors: list[dict] = []
    with open(OUTPUT_PATH, "a", encoding="utf-8") as f:
        for i, rec in enumerate(records, 1):
            doc_id = rec.get("document_id", "")
            if doc_id in annotated_keys:
                continue
            result = await call_gemini(rec, agent)
            if result:
                merged = {**rec, **result}
                f.write(json.dumps(merged, ensure_ascii=False) + "\n")
                annotated_keys.add(doc_id)
                ok += 1
            else:
                errors.append({"index": i, "document_id": doc_id})
            if i % PROGRESS_EVERY == 0 or i == total:
                print(f"  [{i:>5}/{total}] ok={ok:,} errores={len(errors):,}")

    print(f"\nGuardado: {OUTPUT_PATH}")
    if errors:
        print(f"✗ {len(errors)} registros fallidos")
    return {"total": total, "annotated": ok, "errors": len(errors)}


async def main():
    config = LocalAgentConfig(
        model=MODEL_NAME,
        response_schema=AnnotationResponse,
        api_key=GEMINI_API_KEY,
    )
    async with Agent(config=config) as agent:
        result = await run_pipeline(agent)
    print(result)


if __name__ == "__main__":
    asyncio.run(main())
