"""
Gestor de base de datos vectorial usando ChromaDB
Maneja almacenamiento y búsqueda de vectores
"""
import chromadb
from chromadb.config import Settings
from typing import List, Dict, Any, Optional
from pathlib import Path
import numpy as np


class VectorDBManager:
    """Gestor de base de datos vectorial con ChromaDB"""
    
    def __init__(
        self,
        db_path: str | Path,
        collection_name: str = "documents",
        distance_metric: str = "cosine"
    ):
        """
        Inicializa el gestor de base de datos vectorial
        
        Args:
            db_path: Ruta donde se almacenará la DB
            collection_name: Nombre de la colección
            distance_metric: Métrica de distancia ('cosine', 'l2', 'ip')
        """
        self.db_path = Path(db_path)
        self.db_path.mkdir(parents=True, exist_ok=True)
        
        self.collection_name = collection_name
        self.distance_metric = distance_metric
        
        # Inicializar cliente ChromaDB
        self.client = chromadb.PersistentClient(
            path=str(self.db_path),
            settings=Settings(
                anonymized_telemetry=False,
                allow_reset=True
            )
        )
        
        # Obtener o crear colección
        self.collection = self._get_or_create_collection()
    
    def _get_or_create_collection(self):
        """Obtiene colección existente o crea una nueva"""
        # Mapeo de métricas
        metric_map = {
            "cosine": "cosine",
            "l2": "l2",
            "ip": "ip"  # inner product
        }
        
        return self.client.get_or_create_collection(
            name=self.collection_name,
            metadata={
                "hnsw:space": metric_map.get(self.distance_metric, "cosine")
            }
        )
    
    def add_documents(
        self,
        documents: List[str],
        embeddings: np.ndarray,
        metadatas: Optional[List[Dict[str, Any]]] = None,
        ids: Optional[List[str]] = None
    ) -> None:
        """
        Agrega documentos a la base de datos vectorial
        
        Args:
            documents: Lista de textos
            embeddings: Array de embeddings (shape: [n_docs, embedding_dim])
            metadatas: Metadata opcional para cada documento
            ids: IDs únicos para cada documento (se generan si no se proveen)
        """
        n_docs = len(documents)
        
        # Generar IDs si no se proveen
        if ids is None:
            ids = [f"doc_{i}_{hash(doc)}" for i, doc in enumerate(documents)]
        
        # Generar metadatas vacías si no se proveen
        if metadatas is None:
            metadatas = [{} for _ in range(n_docs)]
        
        # Convertir embeddings a lista
        if isinstance(embeddings, np.ndarray):
            embeddings = embeddings.tolist()
        
        # Agregar a ChromaDB
        self.collection.add(
            documents=documents,
            embeddings=embeddings,
            metadatas=metadatas,
            ids=ids
        )
    
    def query(
        self,
        query_embedding: np.ndarray,
        n_results: int = 5,
        where: Optional[Dict[str, Any]] = None,
        where_document: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Busca documentos similares a un query
        
        Args:
            query_embedding: Vector de embedding del query
            n_results: Número de resultados a retornar
            where: Filtros sobre metadata (ej: {"source": "legal"})
            where_document: Filtros sobre el texto del documento
        
        Returns:
            Dict con 'documents', 'metadatas', 'distances', 'ids'
        """
        # Convertir embedding a lista
        if isinstance(query_embedding, np.ndarray):
            if query_embedding.ndim == 1:
                query_embedding = [query_embedding.tolist()]
            else:
                query_embedding = query_embedding.tolist()
        
        # Buscar en ChromaDB
        results = self.collection.query(
            query_embeddings=query_embedding,
            n_results=n_results,
            where=where,
            where_document=where_document
        )
        
        return results
    
    def get_by_ids(self, ids: List[str]) -> Dict[str, Any]:
        """
        Obtiene documentos por sus IDs
        
        Args:
            ids: Lista de IDs de documentos
        
        Returns:
            Dict con documentos y metadatas
        """
        return self.collection.get(ids=ids)
    
    def count(self) -> int:
        """Retorna el número de documentos en la colección"""
        return self.collection.count()
    
    def delete(self, ids: List[str]) -> None:
        """
        Elimina documentos por ID
        
        Args:
            ids: Lista de IDs a eliminar
        """
        self.collection.delete(ids=ids)
    
    def clear(self) -> None:
        """Elimina todos los documentos de la colección"""
        self.client.delete_collection(self.collection_name)
        self.collection = self._get_or_create_collection()
    
    def update_metadata(self, ids: List[str], metadatas: List[Dict[str, Any]]) -> None:
        """
        Actualiza metadata de documentos existentes
        
        Args:
            ids: Lista de IDs
            metadatas: Nueva metadata para cada ID
        """
        self.collection.update(ids=ids, metadatas=metadatas)
    
    def get_stats(self) -> Dict[str, Any]:
        """Retorna estadísticas de la colección"""
        return {
            "collection_name": self.collection_name,
            "total_documents": self.count(),
            "db_path": str(self.db_path),
            "distance_metric": self.distance_metric
        }
    
    def peek(self, limit: int = 10) -> Dict[str, Any]:
        """
        Muestra una muestra de documentos
        
        Args:
            limit: Número de documentos a mostrar
        
        Returns:
            Muestra de documentos
        """
        return self.collection.peek(limit=limit)