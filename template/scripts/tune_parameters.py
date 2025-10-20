"""
Script para experimentar con diferentes configuraciones de RAG
y encontrar los mejores parámetros
"""
import argparse
import sys
from pathlib import Path

sys.path.append(str(Path(__file__).parent.parent.parent))

from template.core import BaseAgent
from rich.console import Console
from rich.table import Table

console = Console()


def test_configuration(instance_path: str, query: str, configs: list):
    """
    Prueba diferentes configuraciones y compara resultados
    """
    console.print(f"\n[bold cyan]🧪 Testeando configuraciones para:[/bold cyan] '{query}'\n")
    
    agent = BaseAgent(instance_path)
    
    table = Table(title="Comparación de Configuraciones", show_lines=True)
    table.add_column("Config", style="cyan", width=30)
    table.add_column("n_results", style="magenta", width=10)
    table.add_column("temperature", style="yellow", width=12)
    table.add_column("Respuesta (preview)", style="green", width=80)
    
    for config in configs:
        n_results = config.get('n_results', 5)
        temperature = config.get('temperature', 0.3)
        
        try:
            response = agent.query(
                query,
                n_results=n_results,
                temperature=temperature
            )
            
            # Preview de la respuesta
            preview = response[:150] + "..." if len(response) > 150 else response
            preview = preview.replace('\n', ' ')
            
            config_name = f"n={n_results}, temp={temperature}"
            
            table.add_row(
                config_name,
                str(n_results),
                str(temperature),
                preview
            )
        except Exception as e:
            table.add_row(
                config_name,
                str(n_results),
                str(temperature),
                f"[red]Error: {str(e)[:100]}[/red]"
            )
    
    console.print(table)
    
    # Recomendaciones
    console.print("\n[bold magenta]💡 Guía de Parámetros:[/bold magenta]\n")
    console.print("  [cyan]n_results[/cyan] (número de chunks a recuperar):")
    console.print("    • 3-5: Para preguntas específicas y directas")
    console.print("    • 5-8: Para preguntas que requieren más contexto")
    console.print("    • 8-15: Para preguntas complejas o multi-parte\n")
    
    console.print("  [cyan]temperature[/cyan] (creatividad del modelo):")
    console.print("    • 0.0-0.3: Respuestas precisas y deterministas (recomendado para RAG)")
    console.print("    • 0.3-0.7: Balance entre precisión y creatividad")
    console.print("    • 0.7-1.0: Respuestas más creativas pero menos precisas\n")


def suggest_improvements(instance_path: str):
    """Analiza la configuración actual y sugiere mejoras"""
    console.print("\n[bold cyan]🔧 Analizando configuración actual...[/bold cyan]\n")
    
    agent = BaseAgent(instance_path)
    
    # Obtener estadísticas
    stats = agent.get_stats()
    config = agent.config
    
    console.print(f"[yellow]Configuración Actual:[/yellow]")
    console.print(f"  • Chunk size: [cyan]{config.preprocessing.chunk_size}[/cyan]")
    console.print(f"  • Chunk overlap: [cyan]{config.preprocessing.chunk_overlap}[/cyan]")
    console.print(f"  • Documentos en DB: [cyan]{stats['vectordb']['total_documents']}[/cyan]")
    console.print(f"  • Modelo embedding: [cyan]{config.embeddings.model}[/cyan]")
    console.print(f"  • Modelo LLM: [cyan]{config.llm.model}[/cyan]")
    console.print(f"  • Temperature: [cyan]{config.llm.temperature}[/cyan]\n")
    
    console.print("[bold magenta]📋 Recomendaciones de Mejora:[/bold magenta]\n")
    
    # Análisis de chunk size
    if config.preprocessing.chunk_size < 500:
        console.print("  ⚠️  [yellow]Chunk size muy pequeño[/yellow]")
        console.print("     → Aumenta a 800-1200 para más contexto por chunk")
    elif config.preprocessing.chunk_size > 1500:
        console.print("  ⚠️  [yellow]Chunk size muy grande[/yellow]")
        console.print("     → Reduce a 800-1200 para búsquedas más precisas")
    else:
        console.print("  ✅ [green]Chunk size adecuado[/green]")
    
    # Análisis de overlap
    overlap_ratio = config.preprocessing.chunk_overlap / config.preprocessing.chunk_size
    if overlap_ratio < 0.1:
        console.print("\n  ⚠️  [yellow]Overlap muy bajo[/yellow]")
        console.print("     → Aumenta a 10-20% del chunk_size para mantener contexto")
    elif overlap_ratio > 0.3:
        console.print("\n  ⚠️  [yellow]Overlap muy alto[/yellow]")
        console.print("     → Reduce a 10-20% para evitar redundancia")
    else:
        console.print("\n  ✅ [green]Overlap adecuado[/green]")
    
    # Análisis de documentos
    if stats['vectordb']['total_documents'] < 10:
        console.print("\n  ⚠️  [yellow]Pocos chunks en la base[/yellow]")
        console.print("     → Verifica que los PDFs tengan contenido suficiente")
        console.print("     → Considera agregar más documentos")
    
    # Recomendaciones de modelo
    console.print("\n  [cyan]💡 Modelos LLM alternativos:[/cyan]")
    console.print("     • llama3.1:8b - Mejor para contextos largos")
    console.print("     • mistral:7b - Más rápido, buena calidad")
    console.print("     • qwen2.5:14b - Mejor calidad (si tienes RAM)")


def main():
    parser = argparse.ArgumentParser(
        description="Experimenta con parámetros de RAG para encontrar la mejor configuración"
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
        help="Query de prueba"
    )
    parser.add_argument(
        "--analyze",
        action="store_true",
        help="Solo analizar configuración actual"
    )
    
    args = parser.parse_args()
    
    try:
        if args.analyze:
            suggest_improvements(args.instance)
        elif args.query:
            # Configuraciones a probar
            configs = [
                {'n_results': 3, 'temperature': 0.1},
                {'n_results': 5, 'temperature': 0.1},
                {'n_results': 5, 'temperature': 0.3},
                {'n_results': 8, 'temperature': 0.3},
                {'n_results': 10, 'temperature': 0.5},
            ]
            test_configuration(args.instance, args.query, configs)
        else:
            console.print("[yellow]Usa --query para probar configuraciones o --analyze para analizar[/yellow]")
            suggest_improvements(args.instance)
    
    except Exception as e:
        console.print(f"\n[red]❌ Error: {e}[/red]")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()
