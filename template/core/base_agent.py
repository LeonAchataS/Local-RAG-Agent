"""
Agente base que orquesta todos los componentes
"""
from pathlib import Path
from typing import List, Dict, Any, Optional
import sys

# Agregar el directorio raíz al path para imports
sys.path.append(str(Path(__file__).parent.parent.parent))

from template.core.embedding_service import EmbeddingService
from template.core.vectordb_manager import VectorDBManager
from template.core.llm_service import LLMService
from template.utils.config_loader import ConfigLoader, AgentConfig
from template.utils.logger import get_logger


class BaseAgent:
    """Agente RAG que combina búsqueda vectorial y LLM"""
    
    def __init__(self, config: AgentConfig | str | Path):
        """
        Args:
            config: AgentConfig objeto o ruta al config/instance
        """
        # Cargar configuración
        if isinstance(config, (str, Path)):
            config_path = Path(config)
            if config_path.is_dir():
                # Es una instancia, cargar su config
                self.config = ConfigLoader.load_from_instance(config_path)
            else:
                # Es un archivo de config
                self.config = ConfigLoader.load(config_path)
        else:
            self.config = config
        
        # Setup logger
        self.logger = get_logger(
            name=self.config.name.lower().replace(' ', '_'),
            log_dir=self.config.instance_path / "logs",
            level=self.config.log_level
        )
        
        self.logger.info(f"Inicializando {self.config.name}")
        
        # Inicializar servicios
        self._init_services()
        
        # Cargar prompts
        self._load_prompts()
        
        self.logger.info("Agente inicializado correctamente")
    
    def _init_services(self):
        """Inicializa los servicios de embeddings, vectordb y LLM"""
        # Embeddings
        self.logger.info(f"Cargando modelo de embeddings: {self.config.embeddings.model}")
        self.embedding_service = EmbeddingService(
            model_name=self.config.embeddings.model,
            device=self.config.embeddings.device
        )
        
        # VectorDB
        self.logger.info(f"Conectando a base de datos vectorial: {self.config.vectordb.path}")
        self.vectordb = VectorDBManager(
            db_path=self.config.vectordb.path,
            collection_name=self.config.vectordb.collection,
            distance_metric=self.config.vectordb.distance_metric
        )
        
        # LLM
        self.logger.info(f"Conectando a modelo LLM: {self.config.llm.model}")
        self.llm = LLMService(
            model=self.config.llm.model,
            temperature=self.config.llm.temperature,
            max_tokens=self.config.llm.max_tokens,
            context_window=self.config.llm.context_window
        )
    
    def _load_prompts(self):
        """Carga los prompts desde archivos"""
        try:
            self.system_prompt = ConfigLoader.load_prompt(self.config.prompts.system)
            self.logger.info("System prompt cargado")
        except FileNotFoundError:
            self.logger.warning("System prompt no encontrado, usando default")
            self.system_prompt = self._get_default_system_prompt()
        
        try:
            self.query_template = ConfigLoader.load_prompt(self.config.prompts.template)
            self.logger.info("Query template cargado")
        except FileNotFoundError:
            self.logger.warning("Query template no encontrado, usando default")
            self.query_template = self._get_default_query_template()
    
    def _get_default_system_prompt(self) -> str:
        """Prompt de sistema por defecto"""
        return """Eres un asistente especializado que responde preguntas basándote únicamente en la información proporcionada en el contexto.

REGLAS:
- Responde solo con información del contexto
- Si no encuentras la respuesta en el contexto, di "No tengo esa información en los documentos"
- Sé preciso y conciso
- Cita la fuente cuando sea relevante

CONTEXTO:
{context}

PREGUNTA: {query}"""
    
    def _get_default_query_template(self) -> str:
        """Template de query por defecto"""
        return "{context}\n\nPregunta: {query}\nRespuesta:"
    
    def retrieve_context(
        self,
        query: str,
        n_results: int = 5,
        filters: Optional[Dict[str, Any]] = None
    ) -> tuple[List[str], List[Dict[str, Any]]]:
        """
        Recupera contexto relevante de la base vectorial
        
        Args:
            query: Pregunta del usuario
            n_results: Número de chunks a recuperar
            filters: Filtros de metadata
        
        Returns:
            Tuple de (documentos, metadatas)
        """
        # Generar embedding del query
        query_embedding = self.embedding_service.encode_query(query)
        
        # Buscar documentos similares
        results = self.vectordb.query(
            query_embedding=query_embedding,
            n_results=n_results,
            where=filters
        )
        
        documents = results['documents'][0] if results['documents'] else []
        metadatas = results['metadatas'][0] if results['metadatas'] else []
        
        self.logger.info(f"Recuperados {len(documents)} documentos relevantes")
        
        return documents, metadatas
    
    def format_context(self, documents: List[str], metadatas: List[Dict[str, Any]]) -> str:
        """
        Formatea los documentos recuperados en un contexto legible
        
        Args:
            documents: Lista de textos
            metadatas: Lista de metadatas
        
        Returns:
            Contexto formateado
        """
        context_parts = []
        
        for i, (doc, meta) in enumerate(zip(documents, metadatas), 1):
            source = meta.get('filename', meta.get('source', 'Desconocido'))
            context_parts.append(f"[Documento {i} - {source}]\n{doc}")
        
        return "\n\n".join(context_parts)
    
    def query(
        self,
        question: str,
        n_results: int = 5,
        filters: Optional[Dict[str, Any]] = None,
        temperature: Optional[float] = None,
        stream: bool = False
    ) -> str:
        """
        Realiza una consulta al agente
        
        Args:
            question: Pregunta del usuario
            n_results: Número de documentos a recuperar
            filters: Filtros de metadata
            temperature: Override de temperatura
            stream: Generar respuesta en streaming
        
        Returns:
            Respuesta generada
        """
        self.logger.info(f"Query: {question}")
        
        # Recuperar contexto
        documents, metadatas = self.retrieve_context(question, n_results, filters)
        
        if not documents:
            return "No encontré información relevante en los documentos para responder tu pregunta."
        
        # Formatear contexto
        context = self.format_context(documents, metadatas)
        
        # Log para debug - ver qué contexto se está pasando
        self.logger.debug(f"Contexto recuperado (primeros 500 chars): {context[:500]}...")
        
        # Construir system prompt con contexto
        system_prompt_with_context = self.system_prompt.replace("{context}", context)
        
        # Generar respuesta
        if stream:
            return self.llm.generate_stream(
                prompt=question,
                system_prompt=system_prompt_with_context,
                temperature=temperature
            )
        else:
            response = self.llm.generate(
                prompt=question,
                system_prompt=system_prompt_with_context,
                temperature=temperature
            )
            self.logger.info("Respuesta generada")
            return response
    
    def get_stats(self) -> Dict[str, Any]:
        """Retorna estadísticas del agente"""
        return {
            "agent_name": self.config.name,
            "instance_path": str(self.config.instance_path),
            "vectordb": self.vectordb.get_stats(),
            "llm_model": self.config.llm.model,
            "embedding_model": self.config.embeddings.model
        }