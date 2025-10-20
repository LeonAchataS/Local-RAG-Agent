"""
Estrategia simple de chunking - Método actual mejorado
División por párrafos con tamaño controlado
"""
from typing import List, Dict, Any
import re


class SimpleChunker:
    """Chunking simple por párrafos y tamaño fijo"""
    
    def __init__(self, chunk_size: int, chunk_overlap: int, min_chunk_size: int):
        self.chunk_size = chunk_size
        self.chunk_overlap = chunk_overlap
        self.min_chunk_size = min_chunk_size
    
    def chunk_text(self, text: str) -> List[str]:
        """
        Divide texto en chunks respetando párrafos
        """
        # Dividir por párrafos
        paragraphs = text.split('\n\n')
        paragraphs = [p.strip() for p in paragraphs if p.strip()]
        
        chunks = []
        current_chunk = ""
        
        for paragraph in paragraphs:
            # Si agregar el párrafo excede el tamaño
            if len(current_chunk) + len(paragraph) > self.chunk_size:
                # Guardar chunk actual si cumple tamaño mínimo
                if len(current_chunk) >= self.min_chunk_size:
                    chunks.append(current_chunk.strip())
                
                # Si el párrafo solo es muy grande, dividirlo
                if len(paragraph) > self.chunk_size:
                    para_chunks = self._chunk_by_chars(paragraph)
                    chunks.extend(para_chunks)
                    current_chunk = ""
                else:
                    current_chunk = paragraph
            else:
                # Agregar párrafo al chunk actual
                if current_chunk:
                    current_chunk += "\n\n" + paragraph
                else:
                    current_chunk = paragraph
        
        # Agregar último chunk
        if len(current_chunk) >= self.min_chunk_size:
            chunks.append(current_chunk.strip())
        
        return chunks
    
    def _chunk_by_chars(self, text: str) -> List[str]:
        """División por caracteres con overlap"""
        chunks = []
        start = 0
        text_len = len(text)
        
        while start < text_len:
            end = start + self.chunk_size
            
            # Si no es el último chunk, buscar el final de oración más cercano
            if end < text_len:
                search_end = min(end + 100, text_len)
                sentence_end = max(
                    text.rfind('.', end - 100, search_end),
                    text.rfind('!', end - 100, search_end),
                    text.rfind('?', end - 100, search_end)
                )
                
                if sentence_end > end - 100:
                    end = sentence_end + 1
            
            chunk = text[start:end].strip()
            
            if len(chunk) >= self.min_chunk_size:
                chunks.append(chunk)
            
            # Mover el inicio con overlap
            start = end - self.chunk_overlap
        
        return chunks
