"""
Estrategia de chunking semántico
Divide por cambios de tema usando embeddings
"""
from typing import List, Dict, Any
import re


class SemanticChunker:
    """Chunking basado en similitud semántica"""
    
    def __init__(self, chunk_size: int, chunk_overlap: int, min_chunk_size: int):
        self.chunk_size = chunk_size
        self.chunk_overlap = chunk_overlap
        self.min_chunk_size = min_chunk_size
        self.similarity_threshold = 0.6
    
    def chunk_text(self, text: str) -> List[str]:
        """
        Divide texto por cambios semánticos
        
        Nota: Esta es una implementación simplificada.
        Una versión completa usaría embeddings para detectar cambios de tema.
        """
        # Dividir en oraciones
        sentences = self._split_sentences(text)
        
        if not sentences:
            return []
        
        # Agrupar oraciones en chunks semánticamente coherentes
        chunks = []
        current_chunk = sentences[0]
        
        for i in range(1, len(sentences)):
            sentence = sentences[i]
            
            # Detectar cambio de tema (versión simplificada)
            # En versión completa: calcular similitud entre current_chunk y sentence
            if self._is_topic_change(current_chunk, sentence):
                if len(current_chunk) >= self.min_chunk_size:
                    chunks.append(current_chunk.strip())
                current_chunk = sentence
            else:
                # Verificar tamaño
                if len(current_chunk) + len(sentence) > self.chunk_size:
                    if len(current_chunk) >= self.min_chunk_size:
                        chunks.append(current_chunk.strip())
                    current_chunk = sentence
                else:
                    current_chunk += " " + sentence
        
        # Agregar último chunk
        if len(current_chunk) >= self.min_chunk_size:
            chunks.append(current_chunk.strip())
        
        return chunks
    
    def _split_sentences(self, text: str) -> List[str]:
        """Divide texto en oraciones"""
        # Patrón mejorado para español
        sentence_pattern = r'(?<=[.!?])\s+(?=[A-ZÁÉÍÓÚÑ])'
        sentences = re.split(sentence_pattern, text)
        return [s.strip() for s in sentences if s.strip()]
    
    def _is_topic_change(self, current_text: str, new_sentence: str) -> bool:
        """
        Detecta cambio de tema (versión heurística simple)
        
        Versión completa usaría:
        - Embeddings de current_text y new_sentence
        - Similitud coseno entre ambos
        - Threshold configurable
        """
        # Heurísticas simples para detectar cambios
        topic_indicators = [
            r'^(Por otro lado|Por otra parte|En cambio|Sin embargo|Además|Asimismo)',
            r'^(Capítulo|Sección|Artículo|Parte)',
            r'^\d+\.',  # Numeración
        ]
        
        for pattern in topic_indicators:
            if re.match(pattern, new_sentence, re.IGNORECASE):
                return True
        
        return False
