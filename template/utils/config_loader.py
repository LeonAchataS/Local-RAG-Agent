"""
Cargador de configuración YAML para instancias de agentes
Permite configs reutilizables y específicas por instancia
"""
import yaml
from pathlib import Path
from typing import Dict, Any, Optional
from dataclasses import dataclass, field


@dataclass
class LLMConfig:
    """Configuración del modelo LLM"""
    model: str = "qwen2.5:7b"
    temperature: float = 0.3
    max_tokens: int = 1000
    context_window: int = 4096


@dataclass
class EmbeddingConfig:
    """Configuración de embeddings"""
    model: str = "paraphrase-multilingual-MiniLM-L12-v2"
    device: str = "cpu"  # "cuda" si tienes GPU
    batch_size: int = 32


@dataclass
class VectorDBConfig:
    """Configuración de base de datos vectorial"""
    path: str = "./data/vectordb"
    collection: str = "documents"
    distance_metric: str = "cosine"


@dataclass
class PreprocessingConfig:
    """Configuración de preprocesamiento"""
    chunk_size: int = 800
    chunk_overlap: int = 100
    min_chunk_size: int = 100
    strategy: str = "simple"  # 'simple', 'legal', 'semantic'


@dataclass
class PromptsConfig:
    """Rutas a archivos de prompts"""
    system: str = "./prompts/system_prompt.txt"
    template: str = "./prompts/query_template.txt"


@dataclass
class AgentConfig:
    """Configuración completa del agente"""
    name: str = "RAG Agent"
    description: str = "Agente especializado"
    instance_path: Path = field(default_factory=lambda: Path("."))
    
    llm: LLMConfig = field(default_factory=LLMConfig)
    embeddings: EmbeddingConfig = field(default_factory=EmbeddingConfig)
    vectordb: VectorDBConfig = field(default_factory=VectorDBConfig)
    preprocessing: PreprocessingConfig = field(default_factory=PreprocessingConfig)
    prompts: PromptsConfig = field(default_factory=PromptsConfig)
    
    metadata: Dict[str, Any] = field(default_factory=dict)
    log_level: str = "INFO"


class ConfigLoader:
    """Cargador de configuraciones YAML para instancias de agentes"""
    
    @staticmethod
    def load(config_path: str | Path) -> AgentConfig:
        """
        Carga configuración desde archivo YAML
        
        Args:
            config_path: Ruta al archivo agent_config.yaml
        
        Returns:
            AgentConfig con toda la configuración
        """
        config_path = Path(config_path)
        
        if not config_path.exists():
            raise FileNotFoundError(f"Archivo de config no encontrado: {config_path}")
        
        with open(config_path, 'r', encoding='utf-8') as f:
            data = yaml.safe_load(f)
        
        if not data:
            raise ValueError(f"Archivo de config vacío: {config_path}")
        
        # Parsear configuración
        config = AgentConfig(
            name=data.get('agent', {}).get('name', 'RAG Agent'),
            description=data.get('agent', {}).get('description', ''),
            instance_path=config_path.parent.parent,  # instances/beca18/
            log_level=data.get('log_level', 'INFO')
        )
        
        # LLM config
        if 'llm' in data:
            config.llm = LLMConfig(**data['llm'])
        
        # Embeddings config
        if 'embeddings' in data:
            config.embeddings = EmbeddingConfig(**data['embeddings'])
        
        # VectorDB config
        if 'vectordb' in data:
            vdb_data = data['vectordb'].copy()
            # Convertir rutas relativas a absolutas
            if 'path' in vdb_data:
                vdb_data['path'] = str(config.instance_path / vdb_data['path'])
            config.vectordb = VectorDBConfig(**vdb_data)
        
        # Preprocessing config
        if 'preprocessing' in data:
            config.preprocessing = PreprocessingConfig(**data['preprocessing'])
        
        # Prompts config
        if 'prompts' in data:
            prompts_data = data['prompts'].copy()
            # Convertir rutas relativas a absolutas
            if 'system' in prompts_data:
                prompts_data['system'] = str(config.instance_path / prompts_data['system'])
            if 'template' in prompts_data:
                prompts_data['template'] = str(config.instance_path / prompts_data['template'])
            config.prompts = PromptsConfig(**prompts_data)
        
        # Metadata adicional
        if 'metadata' in data:
            config.metadata = data['metadata']
        
        return config
    
    @staticmethod
    def load_from_instance(instance_path: str | Path) -> AgentConfig:
        """
        Carga config desde una carpeta de instancia
        Busca automáticamente config/agent_config.yaml
        
        Args:
            instance_path: Ruta a instances/beca18/
        
        Returns:
            AgentConfig configurado
        """
        instance_path = Path(instance_path)
        config_file = instance_path / "config" / "agent_config.yaml"
        
        if not config_file.exists():
            raise FileNotFoundError(
                f"No se encontró agent_config.yaml en {config_file}\n"
                f"Asegúrate de tener la estructura: {instance_path}/config/agent_config.yaml"
            )
        
        return ConfigLoader.load(config_file)
    
    @staticmethod
    def load_prompt(prompt_path: str | Path) -> str:
        """
        Carga un archivo de prompt
        
        Args:
            prompt_path: Ruta al archivo de prompt
        
        Returns:
            Contenido del prompt como string
        """
        prompt_path = Path(prompt_path)
        
        if not prompt_path.exists():
            raise FileNotFoundError(f"Archivo de prompt no encontrado: {prompt_path}")
        
        with open(prompt_path, 'r', encoding='utf-8') as f:
            return f.read().strip()