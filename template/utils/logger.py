"""
Logger configurable para Local-RAG-Agent
Soporta múltiples instancias sin conflictos
"""
import logging
import sys
from pathlib import Path
from datetime import datetime


class AgentLogger:
    """Logger reutilizable para cualquier instancia de agente"""
    
    _loggers = {}  # Cache de loggers por instancia
    
    @classmethod
    def get_logger(cls, name: str = "rag-agent", log_dir: Path = None, level: str = "INFO"):
        """
        Obtiene o crea un logger para una instancia específica
        
        Args:
            name: Nombre del logger (ej: "beca18", "sbs_agent")
            log_dir: Directorio para guardar logs (opcional)
            level: Nivel de logging (DEBUG, INFO, WARNING, ERROR)
        
        Returns:
            Logger configurado
        """
        # Si ya existe, devolverlo
        if name in cls._loggers:
            return cls._loggers[name]
        
        # Crear nuevo logger
        logger = logging.getLogger(name)
        logger.setLevel(getattr(logging, level.upper()))
        
        # Evitar duplicación de handlers
        if logger.handlers:
            return logger
        
        # Formato de logs
        formatter = logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(message)s',
            datefmt='%Y-%m-%d %H:%M:%S'
        )
        
        # Handler para consola (siempre activo)
        console_handler = logging.StreamHandler(sys.stdout)
        console_handler.setLevel(logging.INFO)
        console_handler.setFormatter(formatter)
        logger.addHandler(console_handler)
        
        # Handler para archivo (opcional)
        if log_dir:
            log_dir = Path(log_dir)
            log_dir.mkdir(parents=True, exist_ok=True)
            
            log_file = log_dir / f"{name}_{datetime.now().strftime('%Y%m%d')}.log"
            file_handler = logging.FileHandler(log_file, encoding='utf-8')
            file_handler.setLevel(getattr(logging, level.upper()))
            file_handler.setFormatter(formatter)
            logger.addHandler(file_handler)
            
            logger.info(f"Logs guardándose en: {log_file}")
        
        # Cachear logger
        cls._loggers[name] = logger
        
        return logger
    
    @classmethod
    def reset_logger(cls, name: str):
        """Elimina un logger del cache (útil para testing)"""
        if name in cls._loggers:
            logger = cls._loggers[name]
            for handler in logger.handlers[:]:
                handler.close()
                logger.removeHandler(handler)
            del cls._loggers[name]


# Función de conveniencia para uso rápido
def get_logger(name: str = "rag-agent", log_dir: Path = None, level: str = "INFO"):
    """Wrapper conveniente para obtener logger"""
    return AgentLogger.get_logger(name, log_dir, level)