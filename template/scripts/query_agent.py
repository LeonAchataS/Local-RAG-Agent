"""
Script para consultar a un agente mediante CLI
"""
import argparse
import sys
from pathlib import Path

# Agregar directorio raíz al path
sys.path.append(str(Path(__file__).parent.parent.parent))

from template.core import BaseAgent


def query_agent(instance_path: str | Path, query: str, n_results: int = 5, stream: bool = False):
    """
    Consulta a un agente
    
    Args:
        instance_path: Ruta a la instancia
        query: Pregunta
        n_results: Número de documentos a recuperar
        stream: Modo streaming
    """
    print("\n" + "="*60)
    print("LOCAL-RAG-AGENT - Consulta")
    print("="*60)
    
    # Inicializar agente
    print(f"\n🤖 Inicializando agente desde: {instance_path}")
    agent = BaseAgent(instance_path)
    
    print(f"✓ Agente: {agent.config.name}")
    print(f"✓ Documentos en base: {agent.vectordb.count()}")
    print(f"✓ Modelo LLM: {agent.config.llm.model}")
    
    # Realizar consulta
    print("\n" + "-"*60)
    print(f"❓ Pregunta: {query}")
    print("-"*60)
    
    if stream:
        print("\n💬 Respuesta (streaming):\n")
        for chunk in agent.query(query, n_results=n_results, stream=True):
            print(chunk, end='', flush=True)
        print("\n")
    else:
        print("\n💬 Respuesta:\n")
        response = agent.query(query, n_results=n_results)
        print(response)
    
    print("\n" + "="*60 + "\n")


def interactive_mode(instance_path: str | Path, n_results: int = 5):
    """
    Modo interactivo - conversación continua
    
    Args:
        instance_path: Ruta a la instancia
        n_results: Número de documentos a recuperar
    """
    print("\n" + "="*60)
    print("LOCAL-RAG-AGENT - Modo Interactivo")
    print("="*60)
    
    # Inicializar agente
    print(f"\n🤖 Inicializando agente desde: {instance_path}")
    agent = BaseAgent(instance_path)
    
    print(f"✓ Agente: {agent.config.name}")
    print(f"✓ Documentos: {agent.vectordb.count()}")
    print(f"✓ Modelo: {agent.config.llm.model}")
    
    print("\n" + "-"*60)
    print("Escribe 'salir' o 'exit' para terminar")
    print("Escribe 'stats' para ver estadísticas")
    print("-"*60 + "\n")
    
    while True:
        try:
            # Leer input del usuario
            query = input("🙋 Tu pregunta: ").strip()
            
            if not query:
                continue
            
            # Comandos especiales
            if query.lower() in ['salir', 'exit', 'quit']:
                print("\n👋 ¡Hasta luego!\n")
                break
            
            if query.lower() == 'stats':
                stats = agent.get_stats()
                print("\n📊 Estadísticas:")
                print(f"  - Agente: {stats['agent_name']}")
                print(f"  - Documentos: {stats['vectordb']['total_documents']}")
                print(f"  - Modelo LLM: {stats['llm_model']}")
                print(f"  - Modelo Embedding: {stats['embedding_model']}\n")
                continue
            
            # Generar respuesta
            print("\n🤖 Respuesta:\n")
            response = agent.query(query, n_results=n_results)
            print(response)
            print("\n" + "-"*60 + "\n")
            
        except KeyboardInterrupt:
            print("\n\n👋 ¡Hasta luego!\n")
            break
        except Exception as e:
            print(f"\n❌ Error: {e}\n")


def main():
    parser = argparse.ArgumentParser(
        description="Consulta a un agente RAG"
    )
    parser.add_argument(
        "--instance",
        type=str,
        required=True,
        help="Ruta a la instancia (ej: instances/beca18)"
    )
    parser.add_argument(
        "--query",
        type=str,
        default=None,
        help="Pregunta (si no se especifica, modo interactivo)"
    )
    parser.add_argument(
        "--n-results",
        type=int,
        default=5,
        help="Número de documentos a recuperar (default: 5)"
    )
    parser.add_argument(
        "--stream",
        action="store_true",
        help="Modo streaming (solo en query única)"
    )
    parser.add_argument(
        "--interactive",
        action="store_true",
        help="Modo interactivo"
    )
    
    args = parser.parse_args()
    
    try:
        if args.query:
            # Consulta única
            query_agent(args.instance, args.query, args.n_results, args.stream)
        else:
            # Modo interactivo
            interactive_mode(args.instance, args.n_results)
    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()