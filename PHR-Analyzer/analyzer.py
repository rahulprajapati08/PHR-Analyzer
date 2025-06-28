


from llm_config import get_mistral_model
from prompt_templates import analyze_prompt

def analyze_report(report_text: str) -> str:
    """
    Analyzes the patient report using Mistral LLM and returns the summarized result.
    """
    llm = get_mistral_model()
    chain = analyze_prompt | llm
    response = chain.invoke(report_text)
    return response
