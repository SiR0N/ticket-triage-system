import os
import time
from google import genai
from google.genai import types
from dotenv import load_dotenv
from huggingface_hub import InferenceClient
from src.utils.prompts import generate_prompt
import re

load_dotenv()

# Variable global para cachear el pipeline local de transformers cuando se use
_hf_local_pipeline = None


# ==========================================
# OPCIÓN A: GEMINI (Nube vía SDK Oficial)
# ==========================================
def process_gemini(prompt: str, model_name: str = "gemini-2.5-flash") -> tuple[str, int]:
    api_key = os.getenv("GEMINI_API_KEY")
    if not api_key:
        raise ValueError("GEMINI_API_KEY no está configurada en el archivo .env")

    client = genai.Client(api_key=api_key)

    response = client.models.generate_content(
        model=model_name,
        contents=prompt,
        config=types.GenerateContentConfig(
            response_mime_type="application/json",
            temperature=0.1
        )
    )

    tokens = 0
    if hasattr(response, "usage_metadata") and response.usage_metadata:
        prompt_tokens = response.usage_metadata.prompt_token_count or 0
        candidates_tokens = response.usage_metadata.candidates_token_count or 0
        tokens = prompt_tokens + candidates_tokens

    return response.text, tokens


# ==========================================
# OPCIÓN B: HUGGING FACE NUBE (vía SDK huggingface_hub)
# ==========================================
def process_hf_api(prompt: str, model_id: str = "Qwen/Qwen2.5-Coder-32B-Instruct") -> tuple[str, int]:
    hf_token = os.getenv("HF_TOKEN")
    if not hf_token:
        raise ValueError("HF_TOKEN no está configurado en el archivo .env")

    # Usamos la clase InferenceClient en lugar de requests manuales
    client = InferenceClient(token=hf_token)

    response = client.chat_completion(
        model=model_id,
        messages=[{"role": "user", "content": prompt}],
        temperature=0.1,
        response_format={"type": "json_object"}
    )

    response_text = response.choices[0].message.content
    
    # Extracción de uso de tokens desde el objeto ChatCompletionOutput
    tokens = 0
    if hasattr(response, "usage") and response.usage:
        tokens = getattr(response.usage, "total_tokens", 0)

    return response_text, tokens


# ==========================================
# OPCIÓN C: HUGGING FACE LOCAL (vía Transformers)
# ==========================================
def process_hf_local(prompt: str, model_id: str = "Qwen/Qwen2.5-0.5B-Instruct") -> tuple[str, int]:
    """
    Ejecuta un modelo de lenguaje localmente usando la librería Transformers.
    Devuelve la respuesta limpia (JSON) y el total estimado de tokens procesados.
    """
    # Permite modificar la variable global declarada fuera de la función
    global _hf_local_pipeline

    import torch
    from transformers import pipeline

    # CARGA DIFERIDA (Lazy Loading): Solo carga el modelo la primera vez que se ejecuta la función
    if _hf_local_pipeline is None:
        _hf_local_pipeline = pipeline(
            "text-generation",  # Tarea: Generación de texto autorregresiva (Causal LM)
            model=model_id,     # Repositorio/Modelo a cargar desde Hugging Face Hub
            # Si hay GPU (CUDA), usa precisión fp16 para reducir uso de VRAM y acelerar la inferencia; si no, usa fp32 para CPU
            torch_dtype=torch.float16 if torch.cuda.is_available() else torch.float32,
            device_map="auto"   # Asigna automáticamente las capas del modelo al hardware disponible (GPU/CPU)
        )

    # ESTRUCTURA DE DIÁLOGO (Chat Template)
    # Define los roles esperados por el modelo Instruct para formatear el prompt correctamente
    messages = [
        {"role": "system", "content": "Eres un asistente de triaje. Responde EXCLUSIVAMENTE en formato JSON estricto."},
        {"role": "user", "content": prompt}
    ]

    # INFERENCIA DEL MODELO
    outputs = _hf_local_pipeline(
        messages, #aqui se puede utilizar promt tambien pero puede reducir la precision
        max_new_tokens=300,  # Límite máximo de tokens que el modelo puede generar como respuesta
        temperature=0.1,     # Configuración baja para reducir la creatividad y forzar respuestas deterministas
        return_full_text=False  # Oculta el prompt de entrada en el resultado, devuelve solo el texto nuevo
    )
    
    # Extrae la cadena de texto generada por el pipeline
    raw_response = outputs[0]["generated_text"]

    # EXTRACCIÓN Y LIMPIEZA DE JSON
    # Expresión regular que busca desde el primer '{' hasta el último '}'
    # re.DOTALL permite que el punto '.' coincida también con saltos de línea
    json_match = re.search(r'\{.*\}', raw_response, re.DOTALL)
    if json_match:
        response_text = json_match.group(0)  # Extrae únicamente el bloque JSON hallado
    else:
        response_text = raw_response         # Si no detecta la estructura, conserva el texto original

    # CÁLCULO DE TOKENS
    tokenizer = _hf_local_pipeline.tokenizer

    # 1. Contamos los tokens reales del prompt de entrada
    prompt_tokens = len(tokenizer.apply_chat_template(messages, tokenize=True))

    # 2. Contamos los tokens reales de la respuesta generada
    completion_tokens = len(tokenizer.encode(response_text))

    # Total real de tokens consumidos
    tokens_consumed = prompt_tokens + completion_tokens
    # Devuelve la respuesta procesada y el total de tokens estimados
    return response_text, tokens_consumed


# ==========================================
# ENTRADA PRINCIPAL PARA EL SERVICIO
# ==========================================
def process(prompt: str, provider: str = "gemini", validation_error: str = None) -> tuple[str, float, int]:
    start_time = time.time()

    if provider in ["gemini", "externo"]:
        response_text, tokens = process_gemini(prompt)
    elif provider == "hf_api":
        response_text, tokens = process_hf_api(prompt)
    elif provider == "hf_local":
        response_text, tokens = process_hf_local(prompt)
    else:
        raise ValueError(f"Proveedor '{provider}' no soportado.")

    latency = time.time() - start_time
    return response_text, latency, tokens