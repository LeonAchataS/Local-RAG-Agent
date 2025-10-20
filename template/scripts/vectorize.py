"""
Script para vectorizar documentos y crear la base de datos vectorial
"""
import argparse
import sys
from pathlib import Path
from tqdm import tqdm

# Agregar directorio raíz al path
sys.path.append(str(Path(__file__).parent.parent.parent))

from template.preprocessing import DocumentLoader, TextCleaner, Chunker
from template.core import EmbeddingService, VectorDBManager
from template.utils import ConfigLoader, get_logger


def vectorize_instance(instance_path: str | Path, source_dir: str = None):
    """
    Vectoriza documentos de una instancia
    
    Args:
        instance_path: Ruta a instances/beca18/
        source_dir: Directorio con documentos (default: instance/data/raw/)
    """
    instance_path = Path(instance_path)
    
    # Cargar configuración
    config = ConfigLoader.load_from_instance(instance_path)
    logger = get_logger(
        name=f"{config.name}_vectorization",
        log_dir=instance_path / "logs",
        level=config.log_level
    )
    
    logger.info("="*60)
    logger.info(f"Iniciando vectorización para: {config.name}")
    logger.info("="*60)
    
    # Determinar directorio de documentos
    if source_dir is None:
        source_dir = instance_path / "data" / "raw"
    else:
        source_dir = Path(source_dir)
    
    if not source_dir.exists():
        logger.error(f"Directorio no encontrado: {source_dir}")
        return
    
    logger.info(f"Cargando documentos desde: {source_dir}")
    
    # Cargar documentos
    documents = DocumentLoader.load_directory(source_dir, recursive=True)
    
    if not documents:
        logger.error("No se encontraron documentos para procesar")
        return
    
    logger.info(f"Documentos cargados: {len(documents)}")
    
    # Limpiar texto
    logger.info("Limpiando texto...")
    for doc in tqdm(documents, desc="Limpieza"):
        doc['text'] = TextCleaner.clean(doc['text'])
    
    # Dividir en chunks
    logger.info(f"Dividiendo en chunks usando estrategia '{config.preprocessing.strategy}'...")
    chunker = Chunker(
        chunk_size=config.preprocessing.chunk_size,
        chunk_overlap=config.preprocessing.chunk_overlap,
        min_chunk_size=config.preprocessing.min_chunk_size,
        strategy=config.preprocessing.strategy
    )
    
    chunks = chunker.chunk_documents(documents)
    logger.info(f"Chunks generados: {len(chunks)}")
    
    # Inicializar servicios
    logger.info(f"Inicializando embedding service: {config.embeddings.model}")
    embedding_service = EmbeddingService(
        model_name=config.embeddings.model,
        device=config.embeddings.device
    )
    
    logger.info(f"Inicializando base de datos vectorial: {config.vectordb.path}")
    vectordb = VectorDBManager(
        db_path=config.vectordb.path,
        collection_name=config.vectordb.collection,
        distance_metric=config.vectordb.distance_metric
    )
    
    # Limpiar colección existente si hay datos
    if vectordb.count() > 0:
        logger.warning(f"La colección ya tiene {vectordb.count()} documentos")
        response = input("¿Deseas limpiar la colección existente? (s/n): ")
        if response.lower() == 's':
            logger.info("Limpiando colección...")
            vectordb.clear()
        else:
            logger.info("Agregando a la colección existente")
    
    # Generar embeddings
    logger.info("Generando embeddings...")
    texts = [chunk['text'] for chunk in chunks]
    metadatas = [chunk['metadata'] for chunk in chunks]
    
    embeddings = embedding_service.encode_documents(
        texts,
        batch_size=config.embeddings.batch_size,
        show_progress=True
    )
    
    # Guardar en vector DB
    logger.info("Guardando en base de datos vectorial...")
    vectordb.add_documents(
        documents=texts,
        embeddings=embeddings,
        metadatas=metadatas
    )
    
    # Estadísticas finales
    logger.info("="*60)
    logger.info("VECTORIZACIÓN COMPLETADA")
    logger.info("="*60)
    stats = vectordb.get_stats()
    logger.info(f"Total documentos: {stats['total_documents']}")
    logger.info(f"Colección: {stats['collection_name']}")
    logger.info(f"Ubicación: {stats['db_path']}")
    logger.info("="*60)


def main():
    parser = argparse.ArgumentParser(
        description="Vectoriza documentos para una instancia de agente"
    )
    parser.add_argument(
        "--instance",
        type=str,
        required=True,
        help="Ruta a la instancia (ej: instances/beca18)"
    )
    parser.add_argument(
        "--source",
        type=str,
        default=None,
        help="Directorio con documentos (default: instance/data/raw/)"
    )
    
    args = parser.parse_args()
    
    try:
        vectorize_instance(args.instance, args.source)
    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()