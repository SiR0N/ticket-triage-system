# Proyecto de Triage Asistido por LLM

## Descripción
Este proyecto es una solución para procesar y clasificar reportes de incidencias utilizando un motor de triaje asistido por LLMs. La solución incluye una API REST desarrollada con FastAPI y un dashboard interactivo creado con Streamlit.

## Requisitos
- Python 3.8+
- FastAPI
- Uvicorn
- Pydantic
- Streamlit
- Requests
- Ollama

## Instalación
1. Clona el repositorio:
    ```bash
    git clone https://github.com/tu-repo/proyecto_triage.git
    cd proyecto_triage
    ```

2. Instala las dependencias:
    ```bash
    pip install -r requirements.txt
    ```

## Ejecución
1. Inicia el servidor FastAPI:
    ```bash
    uvicorn src.main:app --reload
    ```

2. Inicia el dashboard Streamlit:
    ```bash
    streamlit run dashboard/app.py
    ```

## Pruebas
Ejecuta las pruebas unitarias:
```bash
pytest
```

## Contribución
Contribuciones son bienvenidas. Por favor, crea un pull request con tus cambios.
```

### 2. API y Type-Safety

#### src/models.py

```python models.py
from pydantic import BaseModel, Field
from typing import Optional

class Incident(BaseModel):
    description: str = Field(..., description="Descripción de la incidencia")
    provider: str = Field(..., description="Proveedor: 'local' o 'externo'")

class IncidentResponse(BaseModel):
    category: str = Field(..., description="Categoría de la incidencia")
    urgency: str = Field(..., description="Nivel de urgencia")
    summary: str = Field(..., description="Resumen de 10 palabras")
    department: str = Field(..., description="Departamento asignado")
    reasoning: str = Field(..., description="Razonamiento del LLM")
```

#### src/main.py

```python src/main.py
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from src.models import Incident, IncidentResponse
from src.services import local_llm, external_llm
import time

app = FastAPI()

@app.post("/triage", response_model=IncidentResponse)
async def triage_incident(incident: Incident):
    start_time = time.time()
    try:
        if incident.provider == "local":
            response = local_llm.process(incident.description)
        elif incident.provider == "externo":
            response = external_llm.process(incident.description)
        else:
            raise HTTPException(status_code=400, detail="Proveedor inválido")

        end_time = time.time()
        latency = end_time - start_time

        return IncidentResponse(
            category=response["category"],
            urgency=response["urgency"],
            summary=response["summary"],
            department=response["department"],
            reasoning=response["reasoning"]
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
```

#### src/services/local_llm.py

```python local_llm.py
import ollama

def process(description: str) -> dict:
    # Implementar lógica para interactuar con el modelo local de Ollama
    response = ollama.generate(prompt=description)
    return parse_response(response)

def parse_response(response: str) -> dict:
    # Implementar lógica para parsear la respuesta y validarla con Pydantic
    try:
        # Ejemplo de respuesta:
        # {"category": "Accidente", "urgency": "Alta", "summary": "Choque en Av. Principal", "department": "Transito", "reasoning": "La descripción indica un choque con varios vehículos involucrados."}
        return {
            "category": response["category"],
            "urgency": response["urgency"],
            "summary": response["summary"],
            "department": response["department"],
            "reasoning": response["reasoning"]
        }
    except Exception as e:
        raise ValueError(f"Error en el formato de la respuesta: {str(e)}")
```

#### src/services/external_llm.py

```python external_llm.py
import requests

def process(description: str) -> dict:
    # Implementar lógica para interactuar con el modelo externo (ej. GPT/Gemini/Claude)
    response = requests.post("https://api.provider.com/llm", json={"description": description})
    response.raise_for_status()
    return parse_response(response.json())

def parse_response(response: dict) -> dict:
    # Implementar lógica para parsear la respuesta y validarla con Pydantic
    try:
        # Ejemplo de respuesta:
        # {"category": "Accidente", "urgency": "Alta", "summary": "Choque en Av. Principal", "department": "Transito", "reasoning": "La descripción indica un choque con varios vehículos involucrados."}
        return {
            "category": response["category"],
            "urgency": response["urgency"],
            "summary": response["summary"],
            "department": response["department"],
            "reasoning": response["reasoning"]
        }
    except Exception as e:
        raise ValueError(f"Error en el formato de la respuesta: {str(e)}")
```

### 3. Prompt Engineering y Modelado de Salida

#### src/prompts.py

```python prompts.py
def generate_prompt(description: str) -> str:
    system_prompt = """
    Eres un asistente que clasifica incidencias urbanas y razona sobre su urgencia utilizando el framework ReAct. 
    Para cada incidencia, primero razona paso a paso (Chain-of-Thought) sobre la clasificación y luego proporciona una respuesta en formato JSON.
    Instrucciones:
    - Ignora el género, origen, raza o barrio inferido en el texto de la incidencia.
    - Genera una categoría, un nivel de urgencia, un resumen de 10 palabras y el departamento asignado.
    - Proporciona un razonamiento detallado.
    """
    user_prompt = f"Incidencia: {description}"
    return f"{system_prompt}\n{user_prompt}"
```

### 4. Interfaz Visual (Dashboard)

#### dashboard/app.py

```python app.py
import streamlit as st
import requests
from src.models import Incident

st.title("Dashboard de Triage de Incidencias")

description = st.text_area("Descripción de la incidencia", height=150)
provider = st.selectbox("Proveedor", ["local", "externo"])

if st.button("Procesar"):
    if description:
        incident = Incident(description=description, provider=provider)
        response = requests.post("http://localhost:8000/triage", json=incident.dict())
        if response.status_code == 200:
            data = response.json()
            st.write("Categoría:", data["category"])
            st.write("Urgencia:", data["urgency"])
            st.write("Resumen:", data["summary"])
            st.write("Departamento:", data["department"])
            st.write("Razonamiento:", data["reasoning"])
        else:
            st.error(f"Error: {response.text}")
    else:
        st.error("Por favor, ingresa una descripción de la incidencia.")
```

### 5. Testing

#### tests/test_main.py

```python test_main.py
from fastapi.testclient import TestClient
from src.main import app
from src.models import Incident

client = TestClient(app)

def test_read_main():
    response = client.post("/triage", json={"description": "Choque en Av. Principal", "provider": "local"})
    assert response.status_code == 200
    data = response.json()
    assert "category" in data
    assert "urgency" in data
    assert "summary" in data
    assert "department" in data
    assert "reasoning" in data

def test_invalid_provider():
    response = client.post("/triage", json={"description": "Choque en Av. Principal", "provider": "invalid"})
    assert response.status_code == 400
```

#### tests/test_models.py

```python test_models.py
from src.models import Incident

def test_valid_incident():
    incident = Incident(description="Choque en Av. Principal", provider="local")
    assert incident.description == "Choque en Av. Principal"
    assert incident.provider == "local"

def test_invalid_incident():
    try:
        Incident(description="Choque en Av. Principal", provider="invalid")
    except ValueError as e:
        assert str(e) == "1 validation error for Incident\nprovider\n  unexpected value; permitted: 'local', 'externo' (type=value_error.const; given=invalid; permitted=['local', 'externo'])"