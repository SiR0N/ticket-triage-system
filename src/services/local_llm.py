import time
import ollama
from src.utils.prompts import generate_prompt
#"""
def process(prompt: str, validation_error: str = None):

    
    start_time = time.time()
    response = ollama.generate(
        model="qwen2.5-coder:1.5b",
        prompt=prompt,
        format="json"
    )
    latency = time.time() - start_time
    
    prompt_tokens = response.get("prompt_eval_count", 0) or 0
    completion_tokens = response.get("eval_count", 0) or 0
    tokens_consumed = prompt_tokens + completion_tokens
    
    return response["response"], latency, tokens_consumed
"""
import requests
OLLAMA_URL = "http://localhost:11434/api/generate"

def process(description: str, validation_error: str = None):
    # Generar prompt con o sin error previo
    prompt = generate_prompt(description, validation_error=validation_error)
    
    # Construir el payload HTTP para Ollama REST API
    payload = {
        "model": "qwen2.5-coder:1.5b",
        "prompt": prompt,
        "format": "json",
        "stream": False  # Importante: para recibir la respuesta de una sola vez
    }
    
    start_time = time.time()
    
    # Petición HTTP POST al servidor local de Ollama
    response = requests.post(OLLAMA_URL, json=payload, timeout=60)
    response.raise_for_status()
    
    latency = time.time() - start_time
    
    res_json = response.json()
    
    # Extraer el texto generado
    response_text = res_json.get("response", "")
    
    # Extraer tokens desde la respuesta REST de Ollama
    prompt_tokens = res_json.get("prompt_eval_count", 0) or 0
    completion_tokens = res_json.get("eval_count", 0) or 0
    tokens_consumed = prompt_tokens + completion_tokens
    
    return response_text, latency, tokens_consumed
#"""