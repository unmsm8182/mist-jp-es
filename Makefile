# Makefile para MIST-JP/ES

.PHONY: help install test demo quick-test clean docs

help:
	@echo "MIST-JP/ES - Pipeline Modular de Traducción Automática"
	@echo ""
	@echo "Comandos disponibles:"
	@echo "  make install      - Instala dependencias"
	@echo "  make quick-test   - Prueba rápida de clasificadores (sin descargar modelos)"
	@echo "  make demo         - Ejecuta demostración completa (descarga modelos)"
	@echo "  make clean        - Limpia archivos generados"
	@echo "  make docs         - Muestra documentación"
	@echo ""

install:
	@echo "Instalando dependencias..."
	pip install -r requirements.txt
	@echo "✓ Dependencias instaladas"

quick-test:
	@echo "Ejecutando quick test (sin descargar modelos)..."
	python quick_test.py

demo:
	@echo "Ejecutando demostración completa..."
	@echo "Nota: Primera ejecución descargará modelos (~2GB)"
	python demo.py

clean:
	@echo "Limpiando archivos generados..."
	find . -type f -name "*.pyc" -delete
	find . -type d -name "__pycache__" -delete
	find . -type d -name ".pytest_cache" -delete
	@echo "✓ Limpieza completada"

docs:
	@echo "Documentación de MIST-JP/ES:"
	@echo ""
	@echo "1. Descripción general: Ver README.md"
	@echo "2. Uso rápido: python quick_test.py"
	@echo "3. Demostración completa: python demo.py"
	@echo ""
	@echo "Estructura de archivos:"
	@echo "  - config.py: Configuración y constantes"
	@echo "  - modules/intent_classifier.py: Clasificador de intención"
	@echo "  - modules/tone_classifier.py: Clasificador de tono"
	@echo "  - modules/translator.py: Traductor automático"
	@echo "  - pipeline.py: Orquestador principal"
	@echo "  - demo.py: Script de demostración"
	@echo ""

.DEFAULT_GOAL := help
