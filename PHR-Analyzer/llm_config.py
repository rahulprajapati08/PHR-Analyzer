# llm_config.py

from langchain_ollama import OllamaLLM

def get_mistral_model(temperature: float = 0.3):
    """
    Returns a configured Mistral model running via Ollama.
    """
    return OllamaLLM(model="mistral" , temperature=temperature)
