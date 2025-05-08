from typing import Tuple
from langchain_mistralai import ChatMistralAI
from langchain_community.chat_models import ChatYandexGPT
from langchain_openai import ChatOpenAI
import config

#llm = ChatMistralAI(model="mistral-small-latest", temperature=1, frequency_penalty=0.3)

model_name=f'gpt://{config.YA_FOLDER_ID}/yandexgpt-32k/rc'
"""
llm = ChatYandexGPT(
    #iam_token = None,
    api_key = config.YA_API_KEY, 
    folder_id=config.YA_FOLDER_ID, 
    model_uri=model_name,
    temperature=0.4
    )
"""
llm = ChatOpenAI(model="gpt-4.1-mini", temperature=0.4, frequency_penalty=0.3)


def generate_answer(system_prompt: str, user_request: str) -> Tuple[str, str]:
    """
    Dummy LLM call. Replace with real API integration.
    Returns (llm_response, deanonymized_response).
    """
    messages = [
    {"role": "system", "content": system_prompt},
    {"role": "user", "content": user_request}
    ]
    response = llm.invoke(messages)
    llm_resp = response.content
    #dean_resp = deanonimizer(llm_resp, entities)
    return llm_resp#, dean_resp