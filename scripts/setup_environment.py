#!/usr/bin/env python3
"""
Script de inicialización para verificar y descargar los modelos
locales (Ollama y HF Local) y comprobar las credenciales de API.
"""

import os
import sys
import subprocess
from pathlib import Path
from dotenv import load_dotenv

# Cargar variables de entorno desde .env
root_dir = Path(__file__).resolve().parent.parent
load_dotenv(root_dir / ".env")

MODEL_OLLAMA = os.getenv("MODEL_OLLAMA", "qwen2.5-coder:1.5b")
MODEL_HF_LOCAL = os.getenv("MODEL_HF_LOCAL", "Qwen/Qwen2.5-0.5B-Instruct")
MODEL_HF_API = os.getenv("MODEL_HF_API", "Qwen/Qwen2.5-Coder-32B-Instruct")
MODEL_GEMINI = os.getenv("MODEL_GEMINI", "gemini-2.5-flash")


def check_ollama():
    print(f"\n🦙 [1/3] Verificando Ollama para el modelo: {MODEL_OLLAMA}...")
    try:
        # Comprobar si ollama está disponible en el PATH
        subprocess.run(["ollama", "--version"], check=True, capture_output=True)
    except (subprocess.CalledProcessError, FileNotFoundError):
        print("❌ Ollama no está instalado o no se encuentra en el PATH.")
        print("   Por favor instálalo desde https://ollama.com antes de continuar.")
        return False

    print(f"📥 Ejecutando `ollama pull {MODEL_OLLAMA}`...")
    try:
        subprocess.run(["ollama", "pull", MODEL_OLLAMA], check=True)
        print(f"✅ Modelo de Ollama '{MODEL_OLLAMA}' listo.")
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ Error al descargar el modelo de Ollama: {e}")
        return False


def check_hf_local():
    print(f"\n🤗 [2/3] Descargando/Precargando modelo HF Local: {MODEL_HF_LOCAL}...")
    try:
        from transformers import AutoTokenizer, AutoModelForCausalLM

        print("   Descargando Tokenizer...")
        AutoTokenizer.from_pretrained(MODEL_HF_LOCAL)
        print("   Descargando Weights del Modelo...")
        AutoModelForCausalLM.from_pretrained(MODEL_HF_LOCAL)
        print(f"✅ Modelo HF Local '{MODEL_HF_LOCAL}' precargado en caché de HuggingFace.")
        return True
    except Exception as e:
        print(f"⚠️ No se pudo precargar el modelo local de HF: {e}")
        print("   (Se descargará automáticamente en el primer uso si tienes conexión).")
        return False


def check_api_keys():
    print("\n🔑 [3/3] Comprobando configuración de API Keys...")
    
    hf_token = os.getenv("HF_TOKEN")
    if not hf_token or hf_token.startswith("hf_xxx"):
        print("⚠️ HF_TOKEN no está configurado en .env (requerido para HF API).")
    else:
        print(f"✅ HF_TOKEN detectado para modelo: {MODEL_HF_API}")

    gemini_key = os.getenv("GEMINI_API_KEY")
    if not gemini_key or gemini_key.startswith("AIzaSyxxx"):
        print("⚠️ GEMINI_API_KEY no está configurado en .env (requerido para Gemini).")
    else:
        print(f"✅ GEMINI_API_KEY detectada para modelo: {MODEL_GEMINI}")


def main():
    print("==================================================")
    print("🚀 Verificación y Preparación del Entorno de IA")
    print("==================================================")
    
    check_ollama()
    check_hf_local()
    check_api_keys()
    
    print("\n==================================================")
    print("🎉 Proceso de verificación finalizado.")
    print("   Usa `python -m scripts.setup_environment` para volver a verificar.")
    print("==================================================\n")


if __name__ == "__main__":
    main()