# 🚀 GUÍA DE MEJORA PARA AGENTE RAG

## 🎯 TU PROBLEMA ACTUAL

> "Recupera documentos pero no responde bien algunas preguntas"

Esto significa:
- ✅ El retrieval funciona (encuentra documentos)
- ❌ Pero el LLM no usa bien el contexto o el contexto no es el correcto

## 📊 MÉTRICAS CLAVE PARA RAG

### 1. **Retrieval Metrics** (Calidad de búsqueda)

#### a) Similarity Score
- **Qué es:** Qué tan similar es el chunk recuperado a la pregunta
- **Rango:** 0.0 - 1.0 (mayor = mejor)
- **Meta:** > 0.5 para preguntas específicas
- **Cómo medirlo:**
```bash
python template/scripts/evaluate_retrieval.py --instance instances/beca18 --query "tu pregunta"
```

#### b) Precision@K
- **Qué es:** De los K chunks recuperados, cuántos son relevantes
- **Meta:** > 0.6 (60% o más relevantes)

#### c) Recall
- **Qué es:** Si recuperas toda la información necesaria
- **Meta:** > 0.8 (no dejar información importante fuera)

### 2. **Generation Metrics** (Calidad de respuesta)

#### a) Fidelidad (Faithfulness)
- **Qué es:** La respuesta se basa solo en el contexto (sin inventar)
- **Meta:** > 0.9 (90% de información del contexto)

#### b) Relevancia (Relevance)
- **Qué es:** La respuesta contesta la pregunta
- **Meta:** > 0.8

#### c) Completitud (Completeness)
- **Qué es:** La respuesta es completa, no parcial
- **Meta:** > 0.7

### 3. **System Metrics** (Rendimiento)

- **Latencia:** < 5 segundos por query
- **Costo:** $0 (todo local 😎)
- **Throughput:** Queries por minuto

## 🔧 CÓMO MEJORAR TU AGENTE

### Fase 1: DIAGNÓSTICO

```bash
# 1. Evaluar qué chunks recupera
python template/scripts/evaluate_retrieval.py --instance instances/beca18

# 2. Analizar configuración actual
python template/scripts/tune_parameters.py --instance instances/beca18 --analyze

# 3. Probar diferentes configuraciones
python template/scripts/tune_parameters.py --instance instances/beca18 --query "tu pregunta problemática"
```

### Fase 2: AJUSTAR CHUNKING

Edita `instances/beca18/config/agent_config.yaml`:

```yaml
preprocessing:
  # CONFIGURACIÓN ACTUAL
  chunk_size: 800        # ← PRUEBA: 1000-1200 para más contexto
  chunk_overlap: 100     # ← PRUEBA: 150-200 (15-20% del chunk_size)
  min_chunk_size: 100    # Está bien
```

**Después de cambiar, RE-VECTORIZAR:**
```bash
python template/scripts/vectorize.py --instance instances/beca18
```

### Fase 3: MEJORAR EL PROMPT

#### Prompt Actual (instances/beca18/prompts/system_prompt.txt)

**MEJORAS SUGERIDAS:**

```plaintext
Eres un asistente especializado en Beca 18, el programa de becas del gobierno peruano administrado por Pronabec.

Tu función es ayudar a estudiantes y postulantes a entender:
- Requisitos de postulación
- Proceso de inscripción  
- Modalidades de beca disponibles
- Beneficios y coberturas
- Cronogramas y fechas importantes
- Obligaciones de los becarios

INSTRUCCIONES CRÍTICAS:
1. Lee CUIDADOSAMENTE todo el contexto proporcionado antes de responder
2. Responde ÚNICAMENTE usando información explícita del contexto
3. Si la información está en el contexto pero no es clara, di "La información está presente pero necesita interpretación"
4. Si NO está en el contexto, di exactamente: "No encontré esa información en los documentos de Beca 18"
5. NO asumas, NO infiereas, NO completes información faltante
6. Cita el documento y sección cuando sea posible (ej: "Según el artículo 6.1...")
7. Si hay múltiples respuestas posibles, menciónalas todas

FORMATO DE RESPUESTA:
- Sé específico y directo
- Usa bullet points para listas
- Menciona números de artículo/sección cuando aplique
- Usa un tono profesional pero amigable

CONTEXTO DE LOS DOCUMENTOS:
{context}

Responde la pregunta del usuario basándote EXCLUSIVAMENTE en el contexto anterior.
```

### Fase 4: AJUSTAR PARÁMETROS DE QUERY

En tu código o al consultar:

```python
# PARA PREGUNTAS ESPECÍFICAS (ej: "¿Cuál es el artículo 6.1?")
response = agent.query(
    question=pregunta,
    n_results=3,          # Pocos chunks, más precisión
    temperature=0.1       # Muy determinista
)

# PARA PREGUNTAS GENERALES (ej: "¿Cómo funciona Beca 18?")
response = agent.query(
    question=pregunta,
    n_results=8,          # Más chunks, más contexto
    temperature=0.3       # Un poco más flexible
)

# PARA PREGUNTAS COMPLEJAS (ej: "Compara las modalidades...")
response = agent.query(
    question=pregunta,
    n_results=15,         # Muchos chunks
    temperature=0.2       # Balance
)
```

### Fase 5: MEJORAR MODELO LLM

Si `qwen2.5:7b` no funciona bien:

```bash
# Opción 1: Modelo más grande (mejor comprensión)
ollama pull qwen2.5:14b

# Opción 2: Mejor contexto largo
ollama pull llama3.1:8b

# Opción 3: Más rápido pero bueno
ollama pull mistral:7b
```

Cambiar en `agent_config.yaml`:
```yaml
llm:
  model: "llama3.1:8b"  # ← Cambiar aquí
  temperature: 0.2       # ← Reducir para más precisión
  max_tokens: 2000       # ← Aumentar para respuestas completas
```

### Fase 6: REFORMULAR PREGUNTAS

**Mal ❌**
```
"Dame info sobre requisitos"
```

**Bien ✅**
```
"¿Cuáles son los requisitos de postulación para Beca 18 según las bases?"
```

**Por qué:** Preguntas específicas → mejor retrieval → mejores respuestas

## 🧪 EXPERIMENTOS RECOMENDADOS

### Experimento 1: Chunk Size
```bash
# Probar con chunks más grandes
# Editar agent_config.yaml: chunk_size: 1200
python template/scripts/vectorize.py --instance instances/beca18
python template/scripts/query_agent.py --instance instances/beca18
# ¿Mejora? → Mantener. ¿Empeora? → Revertir
```

### Experimento 2: N_results
```bash
# Probar recuperando más chunks
python template/scripts/tune_parameters.py \
  --instance instances/beca18 \
  --query "pregunta que falla"
# Ver cuál configuración funciona mejor
```

### Experimento 3: Modelo LLM
```bash
# Probar diferentes modelos
ollama pull llama3.1:8b
# Cambiar en config y probar
```

## 📈 CHECKLIST DE OPTIMIZACIÓN

### Nivel 1: Básico (haz esto YA)
- [ ] Ejecutar `evaluate_retrieval.py` para ver scores
- [ ] Ejecutar `tune_parameters.py --analyze` 
- [ ] Verificar que chunk_size esté entre 800-1200
- [ ] Verificar que temperature sea <= 0.3

### Nivel 2: Intermedio
- [ ] Aumentar chunk_overlap a 15-20% del chunk_size
- [ ] Re-vectorizar con nueva configuración
- [ ] Mejorar system_prompt con instrucciones más específicas
- [ ] Probar n_results entre 5-10 en lugar de 5

### Nivel 3: Avanzado
- [ ] Probar diferentes modelos de embeddings
- [ ] Implementar re-ranking de chunks
- [ ] Agregar filtros de metadata
- [ ] Implementar hybrid search (keyword + vector)

## 🎓 RECURSOS PARA MEJORAR

### Modelos de embeddings alternativos
```python
# En agent_config.yaml
embeddings:
  # Actual: paraphrase-multilingual-MiniLM-L12-v2
  
  # Alternativa 1: Mejor calidad (más pesado)
  model: "intfloat/multilingual-e5-large"
  
  # Alternativa 2: Español específico
  model: "hiiamsid/sentence_similarity_spanish_es"
```

### Técnicas avanzadas
1. **Hypothetical Document Embeddings (HyDE):** Genera una respuesta hipotética y busca con eso
2. **Query Expansion:** Reformula la pregunta de múltiples formas
3. **Re-ranking:** Usa un modelo para re-ordenar los chunks recuperados
4. **Parent Document Retrieval:** Recupera chunks pequeños pero devuelve documentos completos

## 🚦 SEÑALES DE QUE ESTÁ FUNCIONANDO

✅ **BUENO:**
- Similarity scores > 0.5
- Responde preguntas específicas correctamente
- Cita fuentes cuando es relevante
- Dice "no sé" cuando no tiene info

❌ **MALO:**
- Similarity scores < 0.3
- Inventa información
- Respuestas genéricas sin usar el contexto
- Siempre dice "no tengo esa información"

## 💡 TIPS FINALES

1. **Itera gradualmente:** Cambia una cosa a la vez
2. **Mide antes y después:** Usa las herramientas de evaluación
3. **Documenta qué funciona:** Lleva un registro de cambios
4. **Testea con queries reales:** Usa preguntas que harían tus usuarios
5. **Balance:** A veces menos es más (menos chunks puede ser mejor)

---

## 🛠️ COMANDOS ÚTILES

```bash
# Ver qué recupera una query
python template/scripts/evaluate_retrieval.py --instance instances/beca18

# Analizar configuración
python template/scripts/tune_parameters.py --instance instances/beca18 --analyze

# Probar configuraciones
python template/scripts/tune_parameters.py --instance instances/beca18 --query "tu pregunta"

# Re-vectorizar después de cambios
python template/scripts/vectorize.py --instance instances/beca18

# Consultar
python template/scripts/query_agent.py --instance instances/beca18
```
