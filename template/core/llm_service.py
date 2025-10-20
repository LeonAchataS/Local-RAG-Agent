"""
Servicio de LLM usando Ollama
Maneja interacción con modelos locales
"""
import ollama
from typing import List, Dict, Any, Optional, Generator


class LLMService:
    """Servicio para interactuar con LLMs vía Ollama"""
    
    def __init__(
        self,
        model: str = "qwen2.5:7b",
        temperature: float = 0.3,
        max_tokens: int = 1000,
        context_window: int = 4096
    ):
        """
        Inicializa el servicio LLM
        
        Args:
            model: Nombre del modelo en Ollama
            temperature: Temperatura para generación (0-1, menor = más determinista)
            max_tokens: Máximo de tokens a generar
            context_window: Ventana de contexto del modelo
        """
        self.model = model
        self.temperature = temperature
        self.max_tokens = max_tokens
        self.context_window = context_window
        
        # Verificar que el modelo existe
        self._verify_model()
    
    def _verify_model(self):
        """Verifica que el modelo esté disponible en Ollama"""
        try:
            models = ollama.list()
            # El formato puede variar, intentar diferentes formas
            available_models = []
            if 'models' in models:
                for m in models['models']:
                    if isinstance(m, dict) and 'name' in m:
                        available_models.append(m['name'])
                    elif isinstance(m, dict) and 'model' in m:
                        available_models.append(m['model'])
            
            # Si no encontramos modelos, asumir que existe
            if not available_models:
                print(f"⚠️  No se pudo verificar modelos, asumiendo que {self.model} está disponible")
                return
            
            if self.model not in available_models:
                raise ValueError(
                    f"Modelo '{self.model}' no encontrado en Ollama.\n"
                    f"Modelos disponibles: {available_models}\n"
                    f"Descarga el modelo con: ollama pull {self.model}"
                )
        except Exception as e:
            # Solo avisar, no fallar
            print(f"⚠️  No se pudo verificar modelo: {e}")
            print(f"   Continuando con {self.model}...")
    
    def generate(
        self,
        prompt: str,
        system_prompt: Optional[str] = None,
        temperature: Optional[float] = None,
        max_tokens: Optional[int] = None
    ) -> str:
        """
        Genera respuesta del LLM
        
        Args:
            prompt: Prompt del usuario
            system_prompt: Prompt de sistema (opcional)
            temperature: Override de temperatura
            max_tokens: Override de max tokens
        
        Returns:
            Respuesta generada
        """
        # Usar parámetros por defecto si no se especifican
        temp = temperature if temperature is not None else self.temperature
        max_tok = max_tokens if max_tokens is not None else self.max_tokens
        
        # Construir mensajes
        messages = []
        if system_prompt:
            messages.append({
                "role": "system",
                "content": system_prompt
            })
        
        messages.append({
            "role": "user",
            "content": prompt
        })
        
        # Llamar a Ollama
        response = ollama.chat(
            model=self.model,
            messages=messages,
            options={
                "temperature": temp,
                "num_predict": max_tok
            }
        )
        
        return response['message']['content']
    
    def generate_stream(
        self,
        prompt: str,
        system_prompt: Optional[str] = None,
        temperature: Optional[float] = None
    ) -> Generator[str, None, None]:
        """
        Genera respuesta en streaming (palabra por palabra)
        
        Args:
            prompt: Prompt del usuario
            system_prompt: Prompt de sistema
            temperature: Override de temperatura
        
        Yields:
            Fragmentos de texto generados
        """
        temp = temperature if temperature is not None else self.temperature
        
        messages = []
        if system_prompt:
            messages.append({"role": "system", "content": system_prompt})
        messages.append({"role": "user", "content": prompt})
        
        stream = ollama.chat(
            model=self.model,
            messages=messages,
            stream=True,
            options={"temperature": temp}
        )
        
        for chunk in stream:
            if 'message' in chunk and 'content' in chunk['message']:
                yield chunk['message']['content']
    
    def generate_with_context(
        self,
        query: str,
        context: str,
        system_prompt: str,
        temperature: Optional[float] = None
    ) -> str:
        """
        Genera respuesta con contexto RAG
        
        Args:
            query: Pregunta del usuario
            context: Contexto recuperado de la DB vectorial
            system_prompt: Instrucciones del sistema
            temperature: Override de temperatura
        
        Returns:
            Respuesta generada
        """
        # Construir prompt con contexto
        full_prompt = system_prompt.replace("{context}", context).replace("{query}", query)
        
        # Si no hay placeholders, construir manualmente
        if "{context}" not in system_prompt:
            full_prompt = f"{system_prompt}\n\nCONTEXTO:\n{context}\n\nPREGUNTA: {query}"
        
        return self.generate(
            prompt=full_prompt,
            temperature=temperature
        )
    
    def get_model_info(self) -> Dict[str, Any]:
        """Retorna información del modelo"""
        try:
            show_result = ollama.show(self.model)
            return {
                "model": self.model,
                "parameters": show_result.get('parameters', {}),
                "template": show_result.get('template', ''),
                "temperature": self.temperature,
                "max_tokens": self.max_tokens,
                "context_window": self.context_window
            }
        except Exception as e:
            return {
                "model": self.model,
                "error": str(e)
            }
    
    @staticmethod
    def list_available_models() -> List[str]:
        """Lista todos los modelos disponibles en Ollama"""
        try:
            models = ollama.list()
            return [m['name'] for m in models.get('models', [])]
        except Exception as e:
            return []