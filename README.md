# Local-RAG-Agent

Sistema RAG (Retrieval-Augmented Generation) modular para crear agentes especializados con conocimiento privado local.

## Características

- 🔒 100% local y privado
- 🤖 Integración con Ollama (LLMs locales)
- 📚 Vectorización de documentos (PDF, DOCX, TXT, Excel)
- 🏢 Multi-instancia (múltiples agentes especializados)
- ⚡ ChromaDB para búsqueda vectorial eficiente
- 🎯 Arquitectura modular

## Requisitos

- Python 3.10+
- Ollama instalado
- ~10GB RAM (más si usas modelos grandes)

## Instalación

### 1. Clonar e instalar dependencias

```bash
git clone <tu-repo>
cd Local-RAG-Agent

# Crear entorno virtual
python -m venv venv
source venv/bin/activate  # En Windows: venv\Scripts\activate

# Instalar dependencias
pip install -r requirements.txt
```

### 2. Instalar Ollama y descargar modelo

```bash
# Instalar Ollama desde: https://ollama.com/download

# Descargar modelo
ollama pull qwen2.5:7b
```

## Uso Rápido

### 1. Preparar documentos

Coloca tus PDFs en la carpeta de la instancia:

```bash
cp mi_documento.pdf instances/beca18/data/raw/
```

### 2. Vectorizar documentos

```bash
python template/scripts/vectorize.py --instance instances/beca18
```

### 3. Consultar al agente

**Modo interactivo:**
```bash
python template/scripts/query_agent.py --instance instances/beca18
```

**Consulta única:**
```bash
python template/scripts/query_agent.py \
  --instance instances/beca18 \
  --query "¿Cuáles son los requisitos?"
```

## Estructura del Proyecto

```
Local-RAG-Agent/
├── template/              # Código base
│   ├── core/             # Servicios principales
│   ├── preprocessing/    # Procesamiento de documentos
│   ├── scripts/          # Scripts CLI
│   └── utils/            # Utilidades
│
├── instances/            # Instancias de agentes
│   └── beca18/
│       ├── config/       # Configuración
│       ├── data/
│       │   ├── raw/      # PDFs originales
│       │   └── vectordb/ # Base vectorial (generada)
│       └── prompts/      # Prompts personalizados
│
└── requirements.txt
```

## Crear Nueva Instancia

```bash
# Copiar estructura
cp -r instances/beca18 instances/mi_agente

# Editar configuración
nano instances/mi_agente/config/agent_config.yaml

# Personalizar prompts
nano instances/mi_agente/prompts/system_prompt.txt

# Agregar documentos
cp docs/* instances/mi_agente/data/raw/

# Vectorizar
python template/scripts/vectorize.py --instance instances/mi_agente
```

## Configuración

Edita `instances/<tu_instancia>/config/agent_config.yaml`:

```yaml
agent:
  name: "Mi Agente"
  description: "Descripción"

llm:
  model: "qwen2.5:7b"
  temperature: 0.3

embeddings:
  model: "paraphrase-multilingual-MiniLM-L12-v2"
  device: "cpu"

preprocessing:
  chunk_size: 800
  chunk_overlap: 100
```

## Modelos Recomendados

### LLMs (Ollama)
- `qwen2.5:7b` - Excelente español, recomendado
- `llama3.1:8b` - Bueno general, contexto largo
- `mistral:7b` - Rápido

### Embeddings
- `paraphrase-multilingual-MiniLM-L12-v2` - Default, multilenguaje
- `intfloat/multilingual-e5-large` - Mayor calidad, más pesado

## Solución de Problemas

**Error: "Modelo no encontrado"**
```bash
ollama pull qwen2.5:7b
```

**Error: "No se puede conectar con Ollama"**
```bash
# Verificar que Ollama está corriendo
ollama list
```

**Base vectorial vacía**
```bash
# Verificar que tienes PDFs en data/raw/
ls instances/beca18/data/raw/

# Re-vectorizar
python template/scripts/vectorize.py --instance instances/beca18
```

## Licencia

MIT

## Contribuciones

¡Contribuciones bienvenidas! Abre un issue o PR.