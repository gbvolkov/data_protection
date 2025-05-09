from typing import Tuple, Any
from functools import lru_cache

import config

from langchain_mistralai import ChatMistralAI
from langchain_community.chat_models import ChatYandexGPT
from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate

from fakers import *

from anonimizer import TextProcessor

import logging
logger = logging.getLogger(__name__)

# Setting up LLM
#llm = ChatMistralAI(model="mistral-small-latest", temperature=1, frequency_penalty=0.3)
"""
model_name=f'gpt://{config.YA_FOLDER_ID}/yandexgpt-32k/rc'
llm = ChatYandexGPT(
    #iam_token = None,
    api_key = config.YA_API_KEY, 
    folder_id=config.YA_FOLDER_ID, 
    model_uri=model_name,
    temperature=0.4
    )
"""
llm = ChatOpenAI(model="gpt-4.1-mini", temperature=0.4, frequency_penalty=0.3)

processor = TextProcessor()

def anonymize(text: str, language = "en") -> str:
    resulting_text = processor.anonimize(text)
    return resulting_text

def deanonymize(text: str, language = "en") -> str:
    resulting_text = processor.deanonimize(text)
    return resulting_text


def generate_answer(system_prompt: str, user_request: str) -> Tuple[str, str]:
    """
    Dummy LLM call. Replace with real API integration.
    Returns (llm_response, deanonymized_response).
    """
    prompt = ChatPromptTemplate.from_messages(
        [
            ("system", system_prompt),
            ("user", "{user_request}"),
        ]
    )

    chain = {"user_request": lambda txt: anonymize(txt, language="en")} | prompt | llm | (lambda ai_message: deanonymize(ai_message.content))
    response = chain.invoke(user_request)

    llm_resp = response
    return llm_resp

if __name__ == "__main__":
    from logger_factory import setup_logging


    setup_logging("anonimizer_web", other_console_level=logging.DEBUG, project_console_level=logging.DEBUG)

    text = """Клиент Степан Степанов (4519227557) по поручению Ивана Иванова обратился в "Интерлизинг" с предложением купить трактор. 
    Для оплаты используется его карта 4095260993934932. 
    Позвоните ему 9867777777 или 9857777237.
    Или можно по адресу г. Санкт-Петербург, Сенная Площадь, д1/2кв17
    Посмотреть его данные можно https://client.ileasing.ru/name=stapanov:3000 или зайти на 182.34.35.12/
    """    
    system_prompt = """Преобразуй текст в записку для записи в CRM. Текст должен быть хорошо структурирован и понятен с первого взгляда"""
    print(generate_answer(system_prompt, text))