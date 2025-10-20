"""
Script de prueba para verificar importaciones y detectar problemas
"""

print("=" * 60)
print("PRUEBA DE IMPORTACIONES - Local-RAG-Agent")
print("=" * 60)

# 1. Verificar imports básicos
print("\n1. Verificando imports de Python estándar...")
try:
    from pathlib import Path
    import sys
    import yaml
    print("   ✓ Imports estándar OK")
except ImportError as e:
    print(f"   ✗ Error: {e}")

# 2. Verificar paquetes externos
print("\n2. Verificando paquetes externos...")

packages = {
    "chromadb": "chromadb",
    "sentence_transformers": "sentence-transformers",
    "ollama": "ollama",
    "pypdf": "pypdf",
    "docx": "python-docx",
    "openpyxl": "openpyxl",
    "yaml": "pyyaml",
    "tqdm": "tqdm"
}

missing = []
for module, package in packages.items():
    try:
        __import__(module)
        print(f"   ✓ {package}")
    except ImportError:
        print(f"   ✗ {package} - FALTA INSTALAR")
        missing.append(package)

# 3. Verificar imports locales
print("\n3. Verificando módulos locales...")

# Agregar path
sys.path.insert(0, str(Path(__file__).parent))

try:
    from template.core import EmbeddingService, VectorDBManager, LLMService, BaseAgent
    print("   ✓ template.core")
except ImportError as e:
    print(f"   ✗ template.core - Error: {e}")

try:
    from template.preprocessing import DocumentLoader, TextCleaner, Chunker
    print("   ✓ template.preprocessing")
except ImportError as e:
    print(f"   ✗ template.preprocessing - Error: {e}")

try:
    from template.utils import ConfigLoader, get_logger
    print("   ✓ template.utils")
except ImportError as e:
    print(f"   ✗ template.utils - Error: {e}")

# 4. Verificar estructura de instancia
print("\n4. Verificando estructura de instancia...")
instance_path = Path(__file__).parent / "instances" / "beca18"
required_paths = [
    instance_path / "config" / "agent_config.yaml",
    instance_path / "data" / "raw",
    instance_path / "data" / "vectordb",
    instance_path / "logs",
    instance_path / "prompts" / "system_prompt.txt",
    instance_path / "prompts" / "query_template.txt"
]

for path in required_paths:
    if path.exists():
        print(f"   ✓ {path.relative_to(instance_path.parent)}")
    else:
        print(f"   ✗ {path.relative_to(instance_path.parent)} - NO EXISTE")

# 5. Verificar documentos
print("\n5. Verificando documentos...")
raw_dir = instance_path / "data" / "raw"
if raw_dir.exists():
    docs = list(raw_dir.glob("*.pdf")) + list(raw_dir.glob("*.docx")) + list(raw_dir.glob("*.txt"))
    print(f"   Documentos encontrados: {len(docs)}")
    for doc in docs:
        print(f"     - {doc.name}")
else:
    print("   ✗ Directorio data/raw no existe")

# 6. Resumen
print("\n" + "=" * 60)
print("RESUMEN")
print("=" * 60)

if missing:
    print(f"\n❌ FALTAN {len(missing)} PAQUETES:")
    print(f"\n   Instalar con:")
    print(f"   pip install {' '.join(missing)}")
else:
    print("\n✅ Todos los paquetes necesarios están instalados")

print("\n" + "=" * 60)
