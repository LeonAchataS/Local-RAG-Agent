"""
Servicio de embeddings reutilizable
Genera vectores usando Sentence Transformers
"""
from sentence_transformers import SentenceTransformer
from typing import List, Union
import numpy as np
from pathlib import Path


class EmbeddingService:
    """Servicio para generar embeddings de texto"""
    
    def __init__(
        self,
        model_name: str = "paraphrase-multilingual-MiniLM-L12-v2",
        device: str = "cpu",
        cache_folder: str = None
    ):
        """
        Inicializa el servicio de embeddings
        
        Args:
            model_name: Nombre del modelo de Sentence Transformers
            device: 'cpu' o 'cuda' para GPU
            cache_folder: Carpeta para cachear modelos (opcional)
        """
        self.model_name = model_name
        self.device = device
        
        # Configurar cache si se especifica
        if cache_folder:
            cache_folder = Path(cache_folder)
            cache_folder.mkdir(parents=True, exist_ok=True)
        
        # Cargar modelo
        self.model = SentenceTransformer(
            model_name,
            device=device,
            cache_folder=cache_folder
        )
        
        self.embedding_dim = self.model.get_sentence_embedding_dimension()
    
    def encode(
        self,
        texts: Union[str, List[str]],
        batch_size: int = 32,
        show_progress: bool = False,
        normalize: bool = True
    ) -> np.ndarray:
        """
        Genera embeddings para uno o más textos
        
        Args:
            texts: Texto único o lista de textos
            batch_size: Tamaño de batch para procesamiento
            show_progress: Mostrar barra de progreso
            normalize: Normalizar vectores (recomendado para cosine similarity)
        
        Returns:
            Array numpy con embeddings (shape: [n_texts, embedding_dim])
        """
        # Convertir string único a lista
        if isinstance(texts, str):
            texts = [texts]
        
        # Generar embeddings
        embeddings = self.model.encode(
            texts,
            batch_size=batch_size,
            show_progress_bar=show_progress,
            normalize_embeddings=normalize,
            convert_to_numpy=True
        )
        
        return embeddings
    
    def encode_query(self, query: str) -> np.ndarray:
        """
        Genera embedding para una consulta (query)
        Optimizado para búsqueda
        
        Args:
            query: Texto de la consulta
        
        Returns:
            Vector de embedding
        """
        return self.encode(query, show_progress=False)[0]
    
    def encode_documents(
        self,
        documents: List[str],
        batch_size: int = 32,
        show_progress: bool = True
    ) -> np.ndarray:
        """
        Genera embeddings para múltiples documentos
        Optimizado para indexación masiva
        
        Args:
            documents: Lista de textos a vectorizar
            batch_size: Tamaño de batch
            show_progress: Mostrar progreso
        
        Returns:
            Array con embeddings
        """
        return self.encode(
            documents,
            batch_size=batch_size,
            show_progress=show_progress
        )
    
    def similarity(self, embedding1: np.ndarray, embedding2: np.ndarray) -> float:
        """
        Calcula similitud coseno entre dos embeddings
        
        Args:
            embedding1: Primer vector
            embedding2: Segundo vector
        
        Returns:
            Score de similitud (0-1, mayor es más similar)
        """
        # Si los embeddings están normalizados, el producto punto es la similitud coseno
        return float(np.dot(embedding1, embedding2))
    
    def get_model_info(self) -> dict:
        """Retorna información del modelo"""
        return {
            "model_name": self.model_name,
            "embedding_dim": self.embedding_dim,
            "device": self.device,
            "max_seq_length": self.model.max_seq_length
        }