"""
Limpieza y normalización de texto
"""
import re
from typing import List


class TextCleaner:
    """Limpiador de texto extraído de documentos"""
    
    @staticmethod
    def remove_extra_whitespace(text: str) -> str:
        """Elimina espacios, tabs y saltos de línea excesivos"""
        # Reemplazar múltiples espacios/tabs por uno solo
        text = re.sub(r'[ \t]+', ' ', text)
        # Reemplazar múltiples saltos de línea por máximo dos
        text = re.sub(r'\n{3,}', '\n\n', text)
        return text.strip()
    
    @staticmethod
    def remove_special_chars(text: str, keep_punctuation: bool = True) -> str:
        """
        Elimina caracteres especiales no deseados
        
        Args:
            text: Texto a limpiar
            keep_punctuation: Mantener puntuación básica
        """
        if keep_punctuation:
            # Mantener letras, números, puntuación básica y espacios
            text = re.sub(r'[^\w\s.,;:¿?¡!()"\'-áéíóúñÁÉÍÓÚÑ]', '', text)
        else:
            # Solo letras, números y espacios
            text = re.sub(r'[^\w\s]', '', text)
        
        return text
    
    @staticmethod
    def normalize_line_breaks(text: str) -> str:
        """Normaliza diferentes tipos de saltos de línea"""
        # Convertir \r\n y \r a \n
        text = text.replace('\r\n', '\n').replace('\r', '\n')
        return text
    
    @staticmethod
    def remove_urls(text: str) -> str:
        """Elimina URLs del texto"""
        url_pattern = r'https?://\S+|www\.\S+'
        return re.sub(url_pattern, '', text)
    
    @staticmethod
    def remove_emails(text: str) -> str:
        """Elimina direcciones de email"""
        email_pattern = r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b'
        return re.sub(email_pattern, '', text)
    
    @staticmethod
    def fix_pdf_artifacts(text: str) -> str:
        """Corrige artefactos comunes de extracción de PDFs"""
        # Eliminar guiones de separación de palabras al final de línea
        text = re.sub(r'-\n', '', text)
        # Unir palabras que quedaron separadas
        text = re.sub(r'(\w)\n(\w)', r'\1 \2', text)
        return text
    
    @staticmethod
    def remove_page_numbers(text: str) -> str:
        """Intenta eliminar números de página comunes"""
        # Números de página al inicio/final de líneas
        text = re.sub(r'^\s*\d+\s*$', '', text, flags=re.MULTILINE)
        # Patrones como "Página 5" o "Page 5"
        text = re.sub(r'(página|page)\s*\d+', '', text, flags=re.IGNORECASE)
        return text
    
    @classmethod
    def clean(
        cls,
        text: str,
        remove_urls: bool = True,
        remove_emails: bool = False,
        fix_pdf: bool = True,
        remove_page_nums: bool = True,
        normalize_whitespace: bool = True
    ) -> str:
        """
        Aplica pipeline de limpieza completo
        
        Args:
            text: Texto a limpiar
            remove_urls: Eliminar URLs
            remove_emails: Eliminar emails
            fix_pdf: Corregir artefactos de PDF
            remove_page_nums: Eliminar números de página
            normalize_whitespace: Normalizar espacios
        
        Returns:
            Texto limpio
        """
        if not text or not isinstance(text, str):
            return ""
        
        # Normalizar saltos de línea primero
        text = cls.normalize_line_breaks(text)
        
        # Correcciones específicas de PDF
        if fix_pdf:
            text = cls.fix_pdf_artifacts(text)
        
        # Eliminar elementos no deseados
        if remove_urls:
            text = cls.remove_urls(text)
        
        if remove_emails:
            text = cls.remove_emails(text)
        
        if remove_page_nums:
            text = cls.remove_page_numbers(text)
        
        # Normalizar espacios
        if normalize_whitespace:
            text = cls.remove_extra_whitespace(text)
        
        return text
    
    @classmethod
    def clean_batch(cls, texts: List[str], **kwargs) -> List[str]:
        """
        Limpia múltiples textos
        
        Args:
            texts: Lista de textos
            **kwargs: Parámetros para clean()
        
        Returns:
            Lista de textos limpios
        """
        return [cls.clean(text, **kwargs) for text in texts]