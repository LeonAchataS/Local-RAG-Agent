"""
División de documentos en chunks para vectorización
"""
from typing import List, Dict, Any
import re


class Chunker:
    """Divide documentos en chunks manejables"""
    
    def __init__(
        self,
        chunk_size: int = 800,
        chunk_overlap: int = 100,
        min_chunk_size: int = 100
    ):
        """
        Args:
            chunk_size: Tamaño aproximado de cada chunk en caracteres
            chunk_overlap: Solapamiento entre chunks para mantener contexto
            min_chunk_size: Tamaño mínimo de un chunk
        """
        self.chunk_size = chunk_size
        self.chunk_overlap = chunk_overlap
        self.min_chunk_size = min_chunk_size
    
    def split_by_sentences(self, text: str) -> List[str]:
        """
        Divide texto en oraciones
        
        Args:
            text: Texto a dividir
        
        Returns:
            Lista de oraciones
        """
        # Patrones de fin de oración
        sentence_endings = r'[.!?]+[\s\n]'
        sentences = re.split(sentence_endings, text)
        
        # Limpiar y filtrar oraciones vacías
        sentences = [s.strip() for s in sentences if s.strip()]
        
        return sentences
    
    def chunk_by_chars(self, text: str) -> List[str]:
        """
        Divide texto en chunks de tamaño fijo con overlap
        
        Args:
            text: Texto a dividir
        
        Returns:
            Lista de chunks
        """
        chunks = []
        start = 0
        text_len = len(text)
        
        while start < text_len:
            end = start + self.chunk_size
            
            # Si no es el último chunk, buscar el final de oración más cercano
            if end < text_len:
                # Buscar punto, exclamación o interrogación en los últimos 100 chars
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
    
    def chunk_by_paragraphs(self, text: str) -> List[str]:
        """
        Divide texto en chunks respetando párrafos
        
        Args:
            text: Texto a dividir
        
        Returns:
            Lista de chunks
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
                    para_chunks = self.chunk_by_chars(paragraph)
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
    
    def chunk_text(
        self,
        text: str,
        method: str = "paragraphs"
    ) -> List[str]:
        """
        Divide texto en chunks usando el método especificado
        
        Args:
            text: Texto a dividir
            method: Método de división ('chars', 'paragraphs', 'sentences')
        
        Returns:
            Lista de chunks
        """
        if not text or not text.strip():
            return []
        
        if method == "chars":
            return self.chunk_by_chars(text)
        elif method == "paragraphs":
            return self.chunk_by_paragraphs(text)
        elif method == "sentences":
            sentences = self.split_by_sentences(text)
            # Agrupar oraciones en chunks
            return self._group_sentences(sentences)
        else:
            raise ValueError(f"Método no soportado: {method}")
    
    def _group_sentences(self, sentences: List[str]) -> List[str]:
        """Agrupa oraciones en chunks del tamaño especificado"""
        chunks = []
        current_chunk = ""
        
        for sentence in sentences:
            if len(current_chunk) + len(sentence) > self.chunk_size:
                if len(current_chunk) >= self.min_chunk_size:
                    chunks.append(current_chunk.strip())
                current_chunk = sentence
            else:
                if current_chunk:
                    current_chunk += " " + sentence
                else:
                    current_chunk = sentence
        
        if len(current_chunk) >= self.min_chunk_size:
            chunks.append(current_chunk.strip())
        
        return chunks
    
    def chunk_document(
        self,
        document: Dict[str, Any],
        method: str = "paragraphs"
    ) -> List[Dict[str, Any]]:
        """
        Divide un documento completo en chunks con metadata
        
        Args:
            document: Dict con 'text' y 'metadata'
            method: Método de chunking
        
        Returns:
            Lista de chunks con metadata
        """
        text = document.get('text', '')
        base_metadata = document.get('metadata', {})
        
        chunks = self.chunk_text(text, method=method)
        
        # Crear documentos chunkeados con metadata
        chunked_docs = []
        for i, chunk in enumerate(chunks):
            chunk_metadata = base_metadata.copy()
            chunk_metadata.update({
                'chunk_index': i,
                'total_chunks': len(chunks),
                'chunk_size': len(chunk)
            })
            
            chunked_docs.append({
                'text': chunk,
                'metadata': chunk_metadata
            })
        
        return chunked_docs
    
    def chunk_documents(
        self,
        documents: List[Dict[str, Any]],
        method: str = "paragraphs"
    ) -> List[Dict[str, Any]]:
        """
        Divide múltiples documentos en chunks
        
        Args:
            documents: Lista de documentos
            method: Método de chunking
        
        Returns:
            Lista de todos los chunks
        """
        all_chunks = []
        
        for doc in documents:
            chunks = self.chunk_document(doc, method=method)
            all_chunks.extend(chunks)
        
        return all_chunks