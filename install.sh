#!/usr/bin/env bash
# Install script para MIST-JP/ES
# Uso: ./install.sh

set -e

echo "=========================================="
echo "MIST-JP/ES Installation Script"
echo "=========================================="
echo ""

# Detectar directorio del proyecto
PROJECT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
echo "📁 Project directory: $PROJECT_DIR"
echo ""

# Verificar Python
echo "✓ Checking Python installation..."
if ! command -v python3 &> /dev/null; then
    echo "✗ Python 3 is not installed"
    exit 1
fi

PYTHON_VERSION=$(python3 --version 2>&1 | awk '{print $2}')
echo "  Python version: $PYTHON_VERSION"
echo ""

# Crear venv si no existe
if [ ! -d "$PROJECT_DIR/venv" ]; then
    echo "📦 Creating virtual environment..."
    python3 -m venv "$PROJECT_DIR/venv"
    echo "  ✓ Virtual environment created"
else
    echo "✓ Virtual environment already exists"
fi
echo ""

# Activar venv
echo "🔌 Activating virtual environment..."
source "$PROJECT_DIR/venv/bin/activate"
echo "  ✓ Virtual environment activated"
echo ""

# Upgrade pip
echo "⬆️  Upgrading pip..."
pip install --upgrade pip setuptools wheel > /dev/null 2>&1
echo "  ✓ pip upgraded"
echo ""

# Instalar dependencias
echo "📥 Installing dependencies..."
pip install -r "$PROJECT_DIR/mist_jp_es/requirements.txt"
echo "  ✓ Dependencies installed"
echo ""

# Verificar instalación
echo "✅ Verifying installation..."
python3 -c "import transformers; import torch; import sentencepiece; import sacremoses" && \
echo "  ✓ All packages imported successfully"
echo ""

echo "=========================================="
echo "✓ Installation completed successfully!"
echo "=========================================="
echo ""
echo "Next steps:"
echo "  1. Activate venv: source venv/bin/activate"
echo "  2. Quick test:    python mist_jp_es/quick_test.py"
echo "  3. Full demo:     python mist_jp_es/demo.py"
echo ""
