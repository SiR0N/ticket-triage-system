import re
import time
import ollama
from src.core.config import MODEL_HF_LOCAL, MODEL_OLLAMA,OLLAMA_BASE_URL

_hf_local_pipeline = None
# Inicializamos el cliente de Ollama apuntando a la URL del config (que leerá el .env)
ollama_client = ollama.Client(host=OLLAMA_BASE_URL)

def process_ollama(prompt: str, model_name: str = MODEL_OLLAMA) -> tuple[str, int]:
    response = ollama_client.generate(
        model=model_name,
        prompt=prompt,
        format="json"
    )
    
    prompt_tokens = response.get("prompt_eval_count", 0) or 0
    completion_tokens = response.get("eval_count", 0) or 0
    tokens_consumed = prompt_tokens + completion_tokens
    
    return response["response"], tokens_consumed


def process_hf_local(prompt: str, model_id: str = MODEL_HF_LOCAL) -> tuple[str, int]:
    global _hf_local_pipeline

    import torch
    from transformers import pipeline

    if _hf_local_pipeline is None:
        _hf_local_pipeline = pipeline(
            "text-generation",
            model=model_id,
            torch_dtype=torch.float16 if torch.cuda.is_available() else torch.float32,
            device_map="auto"
        )

    messages = [
        {"role": "system", "content": "Eres un asistente de triaje. Responde EXCLUSIVAMENTE en formato JSON estricto."},
        {"role": "user", "content": prompt}
    ]

    outputs = _hf_local_pipeline(
        messages,
        max_new_tokens=300,
        temperature=0.1,
        return_full_text=False
    )
    
    raw_response = outputs[0]["generated_text"]

    json_match = re.search(r'\{.*\}', raw_response, re.DOTALL)
    response_text = json_match.group(0) if json_match else raw_response

    tokenizer = _hf_local_pipeline.tokenizer
    prompt_tokens = len(tokenizer.apply_chat_template(messages, tokenize=True))
    completion_tokens = len(tokenizer.encode(response_text))
    tokens_consumed = prompt_tokens + completion_tokens

    return response_text, tokens_consumed


def process(prompt: str, provider: str = "local", validation_error: str = None) -> tuple[str, float, int]:
    start_time = time.time()

    provider_clean = provider.lower()
    if provider_clean == "local":
        response_text, tokens = process_ollama(prompt)
    elif provider_clean == "hf_local":
        response_text, tokens = process_hf_local(prompt)
    else:
        raise ValueError(f"Proveedor local '{provider}' no soportado.")

    latency = time.time() - start_time
    return response_text, latency, tokens