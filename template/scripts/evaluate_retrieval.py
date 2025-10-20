"""
Script para evaluar la calidad del retrieval (recuperación de documentos)
Te muestra qué chunks está recuperando y sus scores de similitud
"""
import argparse
import sys
from pathlib import Path

sys.path.append(str(Path(__file__).parent.parent.parent))

from template.core import BaseAgent
from rich.console import Console
from rich.table import Table
from rich.panel import Panel
from rich import print as rprint

console = Console()


def evaluate_query(instance_path: str, query: str, n_results: int = 10):
    """
    Evalúa qué documentos recupera una query y con qué score
    """
    console.print(f"\n[bold cyan]Evaluando retrieval para:[/bold cyan] '{query}'", style="bold")
    
    # Inicializar agente
    agent = BaseAgent(instance_path)
    
    # Recuperar documentos con detalles
    query_embedding = agent.embedding_service.encode_query(query)
    results = agent.vectordb.query(
        query_embedding=query_embedding,
        n_results=n_results
    )
    
    documents = results['documents'][0] if results['documents'] else []
    metadatas = results['metadatas'][0] if results['metadatas'] else []
    distances = results['distances'][0] if results['distances'] else []
    
    console.print(f"\n[green]✓ Recuperados {len(documents)} documentos[/green]\n")
    
    # Crear tabla
    table = Table(title=f"Top {n_results} Chunks Recuperados", show_lines=True)
    table.add_column("#", style="cyan", width=3)
    table.add_column("Score", style="magenta", width=8)
    table.add_column("Fuente", style="yellow", width=25)
    table.add_column("Chunk", style="green", width=15)
    table.add_column("Contenido (preview)", style="white", width=60)
    
    for i, (doc, meta, dist) in enumerate(zip(documents, metadatas, distances), 1):
        # Calcular similarity score (ChromaDB devuelve distancia, menor = mejor)
        similarity = 1 - dist if dist < 1 else 0
        
        source = meta.get('filename', 'Desconocido')
        chunk_idx = meta.get('chunk_index', '?')
        total_chunks = meta.get('total_chunks', '?')
        
        # Preview del contenido (primeros 200 chars)
        preview = doc[:200] + "..." if len(doc) > 200 else doc
        preview = preview.replace('\n', ' ')
        
        table.add_row(
            str(i),
            f"{similarity:.3f}",
            source,
            f"{chunk_idx}/{total_chunks}",
            preview
        )
    
    console.print(table)
    
    # Análisis de calidad
    console.print("\n[bold yellow]📊 Análisis de Calidad:[/bold yellow]\n")
    
    if distances:
        avg_dist = sum(distances) / len(distances)
        avg_sim = 1 - avg_dist
        
        console.print(f"  • Similitud promedio: [cyan]{avg_sim:.3f}[/cyan]")
        console.print(f"  • Mejor match: [green]{1-min(distances):.3f}[/green]")
        console.print(f"  • Peor match: [red]{1-max(distances):.3f}[/red]")
        
        # Recomendaciones
        console.print("\n[bold magenta]💡 Recomendaciones:[/bold magenta]\n")
        
        if avg_sim < 0.3:
            console.print("  ❌ [red]SIMILITUD MUY BAJA[/red] - Los documentos recuperados no son relevantes")
            console.print("     → Verifica que el documento contenga información sobre este tema")
            console.print("     → Intenta reformular la pregunta con términos más específicos")
        elif avg_sim < 0.5:
            console.print("  ⚠️  [yellow]SIMILITUD REGULAR[/yellow] - Recuperación aceptable pero mejorable")
            console.print("     → Considera aumentar chunk_size para más contexto")
            console.print("     → Prueba con más documentos relacionados")
        else:
            console.print("  ✅ [green]SIMILITUD BUENA[/green] - Recuperación de calidad")
            console.print("     → Si aún falla, el problema está en el prompt o el LLM")
    
    # Mostrar contenido completo del mejor match
    if documents:
        console.print("\n[bold cyan]📄 Contenido completo del mejor match:[/bold cyan]\n")
        best_doc = documents[0]
        best_meta = metadatas[0]
        
        panel = Panel(
            best_doc,
            title=f"Documento: {best_meta.get('filename', 'N/A')} - Chunk {best_meta.get('chunk_index', '?')}",
            border_style="green"
        )
        console.print(panel)


def interactive_evaluation(instance_path: str):
    """Modo interactivo para evaluar múltiples queries"""
    console.print("\n[bold green]🔍 Modo Evaluación Interactiva[/bold green]\n")
    console.print("Escribe 'salir' para terminar\n")
    
    while True:
        try:
            query = console.input("[bold cyan]❓ Query a evaluar: [/bold cyan]")
            
            if query.lower() in ['salir', 'exit', 'quit']:
                console.print("\n[green]👋 ¡Hasta luego![/green]\n")
                break
            
            if not query.strip():
                continue
            
            evaluate_query(instance_path, query)
            console.print("\n" + "="*100 + "\n")
            
        except KeyboardInterrupt:
            console.print("\n\n[green]👋 ¡Hasta luego![/green]\n")
            break


def main():
    parser = argparse.ArgumentParser(
        description="Evalúa la calidad del retrieval de documentos"
    )
    parser.add_argument(
        "--instance",
        type=str,
        required=True,
        help="Ruta a la instancia"
    )
    parser.add_argument(
        "--query",
        type=str,
        help="Query a evaluar (opcional, si no se especifica modo interactivo)"
    )
    parser.add_argument(
        "--n-results",
        type=int,
        default=10,
        help="Número de documentos a mostrar (default: 10)"
    )
    
    args = parser.parse_args()
    
    try:
        if args.query:
            evaluate_query(args.instance, args.query, args.n_results)
        else:
            interactive_evaluation(args.instance)
    except Exception as e:
        console.print(f"\n[red]❌ Error: {e}[/red]")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()
