# 🚀 SISTEMA DE ESTRATEGIAS DE CHUNKING

## ✅ IMPLEMENTADO

Tu agente RAG ahora soporta **3 estrategias de chunking** configurables:

### 1. **Simple** - Para documentos generales
- División por párrafos y tamaño
- Uso: Blogs, artículos, textos narrativos simples

### 2. **Legal** - Para documentos estructurados ⭐ RECOMENDADO PARA BECA 18
- Detecta artículos, secciones, capítulos
- Respeta listas numeradas completas
- Mantiene integridad de estructura legal
- Uso: Leyes, reglamentos, bases, contratos

### 3. **Semantic** - Para documentos narrativos
- Divide por cambios de tema
- Chunks semánticamente coherentes
- Uso: Libros, manuales, documentación técnica

---

## 📝 CÓMO USAR

### Paso 1: Configurar Estrategia

Edita `instances/[tu_instancia]/config/agent_config.yaml`:

```yaml
preprocessing:
  chunk_size: 1000        # Tamaño de chunk
  chunk_overlap: 200      # Overlap (15-20% recomendado)
  min_chunk_size: 150     # Mínimo tamaño
  strategy: "legal"       # ← ESTRATEGIA: simple, legal o semantic
```

### Paso 2: Re-vectorizar

```bash
python template/scripts/vectorize.py --instance instances/beca18
```

**Listo!** Tu agente ahora usa la nueva estrategia.

---

## 🎯 GUÍA DE SELECCIÓN

### ¿Qué estrategia usar?

| Tipo de Documento | Estrategia | Configuración Recomendada |
|------------------|------------|---------------------------|
| **Leyes, Reglamentos, Bases** | `legal` | chunk: 1000, overlap: 200 |
| **Artículos, Blogs, Noticias** | `simple` | chunk: 800, overlap: 150 |
| **Libros, Manuales** | `semantic` | chunk: 1200, overlap: 250 |
| **Documentos técnicos** | `legal` o `semantic` | chunk: 1000, overlap: 200 |
| **FAQs, Preguntas cortas** | `simple` | chunk: 600, overlap: 100 |

---

## 🔍 EJEMPLO: BECA 18

### Configuración Actual (YA APLICADA)

```yaml
preprocessing:
  chunk_size: 1000
  chunk_overlap: 200
  min_chunk_size: 150
  strategy: "legal"  # ← Detecta artículos y secciones
```

### ¿Qué hace la estrategia legal?

**Antes (simple):**
```
Chunk 1: "...final del artículo 5. Artículo 6: Los requisitos son: 1) Edad..."
Chunk 2: "...entre 16-22 años 2) Promedio mayor a 14..."
```
❌ Corta el artículo en pedazos inconexos

**Ahora (legal):**
```
Chunk 1: "Artículo 6: Los requisitos son: 
1) Edad entre 16-22 años 
2) Promedio mayor a 14
3) No tener título universitario"
```
✅ Mantiene el artículo completo y coherente

---

## 🧪 COMPARAR ESTRATEGIAS

Puedes probar diferentes estrategias para el mismo documento:

```bash
# 1. Vectorizar con estrategia simple
# Cambiar en config.yaml: strategy: "simple"
python template/scripts/vectorize.py --instance instances/beca18

# Probar consultas
python template/scripts/query_agent.py --instance instances/beca18

# 2. Vectorizar con estrategia legal
# Cambiar en config.yaml: strategy: "legal"
python template/scripts/vectorize.py --instance instances/beca18

# Probar las mismas consultas y comparar
```

---

## 📊 MEJORAS IMPLEMENTADAS

### Para estrategia "legal":

✅ **Detecta patrones:**
- `Artículo X`, `Art. X`, `ARTÍCULO X`
- `Sección X`, `Capítulo X`, `Cap. X`
- Listas numeradas: `1)`, `2)`, `3)`

✅ **Mantiene integridad:**
- No corta en medio de un artículo
- Agrupa listas numeradas completas
- Preserva estructura jerárquica

✅ **Metadata mejorada:**
- Incluye header en cada chunk
- Contexto de sección/artículo

### Para estrategia "semantic":

✅ **Detecta cambios de tema:**
- "Por otro lado...", "En cambio..."
- Cambios de capítulo/sección
- Transiciones narrativas

✅ **Chunks coherentes:**
- Cada chunk = un concepto completo
- Tamaño variable pero semánticamente lógico

---

## 🛠️ PERSONALIZACIÓN AVANZADA

### Crear tu propia estrategia

1. Crea archivo: `template/preprocessing/strategies/mi_estrategia.py`

```python
class MiEstrategia:
    def __init__(self, chunk_size, chunk_overlap, min_chunk_size):
        self.chunk_size = chunk_size
        self.chunk_overlap = chunk_overlap
        self.min_chunk_size = min_chunk_size
    
    def chunk_text(self, text: str) -> List[str]:
        # Tu lógica aquí
        chunks = []
        # ...
        return chunks
```

2. Registrarla en `chunker.py`:

```python
strategies = {
    'simple': SimpleChunker,
    'legal': LegalChunker,
    'semantic': SemanticChunker,
    'mi_estrategia': MiEstrategia  # ← Agregar aquí
}
```

3. Usar en config:

```yaml
preprocessing:
  strategy: "mi_estrategia"
```

---

## 🎓 MEJORES PRÁCTICAS

### 1. Chunk Size

- **Documentos legales:** 1000-1200 caracteres
- **Documentos generales:** 800-1000 caracteres  
- **Preguntas/Respuestas:** 600-800 caracteres

### 2. Overlap

- **Regla:** 15-20% del chunk_size
- **Mínimo:** 100 caracteres
- **Máximo:** 300 caracteres

### 3. Min Chunk Size

- **Regla:** 15-20% del chunk_size
- Evita chunks muy cortos sin contexto

### 4. Re-vectorizar después de cambios

⚠️ **IMPORTANTE:** Siempre re-vectoriza después de cambiar:
- `chunk_size`
- `chunk_overlap`
- `strategy`

---

## 🐛 TROUBLESHOOTING

### Problema: "Estrategia 'legal' no soportada"

**Solución:** 
```bash
# Verifica que exista el archivo
ls template/preprocessing/strategies/legal_chunker.py

# Si no existe, clona de nuevo el repo o copia los archivos
```

### Problema: Chunks muy largos o muy cortos

**Solución:** Ajusta en config:
```yaml
preprocessing:
  chunk_size: 1000      # ← Aumenta/disminuye aquí
  min_chunk_size: 150   # ← Ajusta el mínimo
```

### Problema: No respeta artículos completos

**Solución:** 
1. Aumenta `chunk_size` a 1200-1500
2. Verifica que `strategy: "legal"` esté configurado
3. Re-vectoriza

---

## 📈 SIGUIENTE NIVEL

### Implementar en el futuro:

1. **Parent-Child Retrieval**
   - Chunks pequeños para búsqueda
   - Documentos grandes para contexto

2. **Hybrid Search**
   - Vector + Keyword search combinados

3. **Re-ranking**
   - Modelo adicional para ordenar resultados

4. **Query Expansion**
   - Reformular query de múltiples formas

---

## 🎉 RESULTADO

Con la estrategia **legal** implementada y configurada, tu agente Beca 18 ahora:

✅ Detecta y respeta artículos completos  
✅ Mantiene listas numeradas juntas  
✅ Preserva contexto legal  
✅ Mejor retrieval de información estructurada  
✅ Respuestas más precisas y completas  

**Próximo paso:** Re-vectoriza y prueba! 🚀
