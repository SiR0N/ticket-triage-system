# src/services/triage_service.py
import time
from pydantic import ValidationError
from fastapi import HTTPException
from src.models.schemas import TicketRequest, TicketTriageOutput, ProviderEnum
from src.utils.prompts import generate_prompt
from src.services import local_llm, external_llm
from src.core.logging_config import logger

def process_triage_with_llm(ticket_request: TicketRequest):
    original_description = ticket_request.description
    current_prompt = generate_prompt(original_description)
    provider_str = ticket_request.provider.value
    
    validation_error = None
    retries = 0
    total_latency = 0.0
    total_tokens = 0
    triage_output = None

    valid_external_providers = [
        ProviderEnum.GEMINI.value, 
        ProviderEnum.HF_API.value, 
        ProviderEnum.HF_TRANSFORMERS.value
    ]

    while retries < 2:
        start_time = time.time()
        
        if provider_str == ProviderEnum.LOCAL.value:
            response, latency, tokens = local_llm.process(current_prompt, validation_error=validation_error)
        elif provider_str in valid_external_providers:
            response, latency, tokens = external_llm.process(prompt=current_prompt, provider=provider_str, validation_error=validation_error)
        else:
            raise HTTPException(status_code=400, detail=f"Proveedor inválido: '{provider_str}'")

        total_latency += latency
        total_tokens += tokens

        try:
            triage_output = TicketTriageOutput.model_validate_json(response)
            break
        except ValidationError as e:
            validation_error = str(e)
            retries += 1
            logger.warning(f"Error de validación en intento {retries}: {validation_error}")
            current_prompt = generate_prompt(original_description, validation_error)

    if not triage_output:
        raise HTTPException(
            status_code=422, 
            detail=f"No se pudo obtener un JSON válido tras reintentos. Último error: {validation_error}"
        )

    return triage_output, total_latency, total_tokens