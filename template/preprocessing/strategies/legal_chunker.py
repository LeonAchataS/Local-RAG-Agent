"""
Estrategia de chunking para documentos legales/estructurados
Detecta artículos, secciones, listas y mantiene su integridad
"""
from typing import List, Dict, Any
import re


class LegalChunker:
    """Chunking especializado para documentos legales y estructurados"""
    
    def __init__(self, chunk_size: int, chunk_overlap: int, min_chunk_size: int):
        self.chunk_size = chunk_size
        self.chunk_overlap = chunk_overlap
        self.min_chunk_size = min_chunk_size
        
        # Patrones para detectar estructura
        self.article_pattern = re.compile(
            r'^(Artículo|ARTÍCULO|Art\.|ART\.)\s*\d+[\.:)]',
            re.MULTILINE | re.IGNORECASE
        )
        self.section_pattern = re.compile(
            r'^(Sección|SECCIÓN|Capítulo|CAPÍTULO|Cap\.|CAP\.)\s*\d+',
            re.MULTILINE | re.IGNORECASE
        )
        self.list_pattern = re.compile(
            r'^\s*[\d+\)\.]\s+',
            re.MULTILINE
        )
    
    def chunk_text(self, text: str) -> List[str]:
        """
        Divide texto respetando estructura legal
        """
        # Detectar secciones principales (artículos, capítulos)
        sections = self._split_by_sections(text)
        
        chunks = []
        for section in sections:
            section_chunks = self._chunk_section(section)
            chunks.extend(section_chunks)
        
        return chunks
    
    def _split_by_sections(self, text: str) -> List[Dict[str, str]]:
        """
        Divide texto por artículos/secciones principales
        """
        sections = []
        
        # Buscar todos los artículos
        article_matches = list(self.article_pattern.finditer(text))
        
        if not article_matches:
            # Si no hay artículos, buscar secciones
            section_matches = list(self.section_pattern.finditer(text))
            if not section_matches:
                # Si no hay estructura clara, tratar como texto simple
                return [{'header': '', 'content': text}]
            matches = section_matches
        else:
            matches = article_matches
        
        # Extraer cada sección con su contenido
        for i, match in enumerate(matches):
            start = match.start()
            end = matches[i + 1].start() if i + 1 < len(matches) else len(text)
            
            section_text = text[start:end].strip()
            header = match.group(0)
            
            sections.append({
                'header': header,
                'content': section_text
            })
        
        # Si hay texto antes del primer artículo/sección
        if matches and matches[0].start() > 0:
            preamble = text[:matches[0].start()].strip()
            if len(preamble) > self.min_chunk_size:
                sections.insert(0, {'header': '', 'content': preamble})
        
        return sections
    
    def _chunk_section(self, section: Dict[str, str]) -> List[str]:
        """
        Divide una sección en chunks, intentando mantenerla completa
        """
        header = section['header']
        content = section['content']
        
        # Si la sección completa cabe en un chunk, mantenerla
        if len(content) <= self.chunk_size * 1.2:  # 20% de tolerancia
            return [content]
        
        # Si es muy grande, dividir por párrafos pero mantener el header
        chunks = []
        paragraphs = content.split('\n\n')
        current_chunk = ""
        
        for para in paragraphs:
            para = para.strip()
            if not para:
                continue
            
            # Detectar si es una lista numerada completa
            if self._is_list_start(para):
                list_content = self._extract_complete_list(paragraphs, paragraphs.index(para))
                if list_content:
                    para = list_content
            
            # Si agregar excede el tamaño
            if len(current_chunk) + len(para) > self.chunk_size:
                if len(current_chunk) >= self.min_chunk_size:
                    chunks.append(current_chunk.strip())
                
                # Si el párrafo es muy largo, dividirlo
                if len(para) > self.chunk_size:
                    para_chunks = self._smart_split(para)
                    chunks.extend(para_chunks)
                    current_chunk = ""
                else:
                    # Nuevo chunk con contexto del header
                    if header:
                        current_chunk = f"{header}\n\n{para}"
                    else:
                        current_chunk = para
            else:
                if current_chunk:
                    current_chunk += "\n\n" + para
                else:
                    if header:
                        current_chunk = f"{header}\n\n{para}"
                    else:
                        current_chunk = para
        
        if len(current_chunk) >= self.min_chunk_size:
            chunks.append(current_chunk.strip())
        
        return chunks
    
    def _is_list_start(self, text: str) -> bool:
        """Detecta si el texto es el inicio de una lista numerada"""
        return bool(self.list_pattern.match(text))
    
    def _extract_complete_list(self, paragraphs: List[str], start_idx: int) -> str:
        """Extrae una lista numerada completa"""
        list_items = [paragraphs[start_idx]]
        
        for i in range(start_idx + 1, len(paragraphs)):
            para = paragraphs[i].strip()
            if self._is_list_start(para):
                list_items.append(para)
            else:
                break
        
        # Solo unir si es una lista pequeña
        full_list = '\n'.join(list_items)
        if len(full_list) <= self.chunk_size:
            return full_list
        return None
    
    def _smart_split(self, text: str) -> List[str]:
        """División inteligente de texto largo"""
        chunks = []
        sentences = re.split(r'(?<=[.!?])\s+', text)
        
        current_chunk = ""
        for sentence in sentences:
            if len(current_chunk) + len(sentence) > self.chunk_size:
                if current_chunk:
                    chunks.append(current_chunk.strip())
                current_chunk = sentence
            else:
                current_chunk += " " + sentence if current_chunk else sentence
        
        if current_chunk:
            chunks.append(current_chunk.strip())
        
        return chunks
