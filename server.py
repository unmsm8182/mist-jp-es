import logging
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from pipeline import MISTPipeline

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(title="MIST-JP/ES API")

# Habilitar CORS para permitir llamadas desde el frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Para desarrollo local permitimos todo
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Inicializar el pipeline en memoria
mist_pipeline = None

@app.on_event("startup")
def load_pipeline():
    global mist_pipeline
    logger.info("Inicializando pipeline en el servidor...")
    mist_pipeline = MISTPipeline()
    logger.info("Pipeline cargado y listo para recibir peticiones.")

import re

class TranslateRequest(BaseModel):
    text: str

@app.post("/api/translate")
def translate(req: TranslateRequest):
    """
    Recibe un diálogo completo, lo desglosa y traduce cada fragmento.
    """
    logger.info(f"Petición recibida: {req.text}")
    try:
        # Desglosar por puntuación de finalización de oración en japonés o saltos de línea
        # Utilizamos regex para mantener la puntuación con la oración
        raw_sentences = re.split(r'(?<=[。！？\n])', req.text)
        sentences = [s.strip() for s in raw_sentences if s.strip()]
        
        results = []
        for i, sentence in enumerate(sentences):
            # El contexto es la oración anterior (si existe)
            context = sentences[i-1] if i > 0 else ""
            res = mist_pipeline.run(japanese_text=sentence, context_text=context)
            results.append(res)
            
        return {
            "success": True,
            "data": results
        }
    except Exception as e:
        logger.error(f"Error procesando petición: {str(e)}")
        return {
            "success": False,
            "error": str(e)
        }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("server:app", host="0.0.0.0", port=8000, reload=True)
