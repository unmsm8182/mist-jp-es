"""
Demo Script
Script de Demostración del Sistema MIST-JP/ES

Ejecuta el pipeline completo sobre un conjunto de oraciones
de demostración hardcodeadas en config.py
"""

import logging
import sys
from pipeline import MISTPipeline
from config import DEMO_SENTENCES

# Configurar logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


def main() -> None:
    """
    Función principal.
    
    1. Instancia el pipeline MIST-JP/ES
    2. Itera sobre las oraciones de demostración
    3. Para cada oración, ejecuta la comparativa
    4. Imprime resultados formateados
    """
    try:
        logger.info("=" * 60)
        logger.info("Iniciando Demostración del Sistema MIST-JP/ES")
        logger.info("=" * 60)
        
        # Instanciar pipeline
        logger.info("Instanciando MISTPipeline...")
        pipeline = MISTPipeline()
        
        logger.info(f"Procesando {len(DEMO_SENTENCES)} oraciones de demostración...")
        print("\n" + "=" * 60)
        print("DEMOSTRACIÓN DEL SISTEMA MIST-JP/ES")
        print("Pipeline Modular de Traducción con Señales Pragmáticas")
        print("=" * 60)
        
        # Iterar sobre las oraciones de demostración
        for idx, sentence in enumerate(DEMO_SENTENCES, 1):
            logger.info(f"Procesando oración {idx}/{len(DEMO_SENTENCES)}: {sentence}")
            pipeline.compare(sentence)
        
        logger.info("=" * 60)
        logger.info("Demostración completada exitosamente")
        logger.info("=" * 60)
        print("\n✓ Demostración completada exitosamente")
        
    except KeyboardInterrupt:
        logger.warning("Demostración interrumpida por el usuario")
        print("\n\n⚠ Demostración interrumpida por el usuario")
        sys.exit(0)
        
    except Exception as e:
        logger.error(f"Error fatal en demostración: {e}", exc_info=True)
        print(f"\n✗ Error en demostración: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
