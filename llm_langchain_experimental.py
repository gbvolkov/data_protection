## IT DOES NOT WORK WITH LONG TEXTS. TO INVESTIGATE MORE!!!

from typing import Tuple, Any
from functools import lru_cache

import config

from langchain_core.prompts import ChatPromptTemplate
from langchain_mistralai import ChatMistralAI
from langchain_community.chat_models import ChatYandexGPT
from langchain_openai import ChatOpenAI
from transformers import AutoTokenizer

from langchain_experimental.data_anonymizer import PresidioReversibleAnonymizer
from langchain_experimental.data_anonymizer.deanonymizer_matching_strategies import (
    fuzzy_matching_strategy,
    combined_exact_fuzzy_matching_strategy,
)
from recognizers.gliner_recogniser import GlinerRecognizer
from recognizers.regex_recognisers import (
    ru_internal_passport_recognizer, 
    SNILSRecognizer,
    INNRecognizer,
    RUBankAccountRecognizer
)
from presidio_anonymizer.entities import OperatorConfig
from langchain_core.prompts.prompt import PromptTemplate
from langchain_openai import ChatOpenAI

from fakers import *
from sentence_splitter import chunk_sentences
from nltk.tokenize import sent_tokenize


## Configure anonimization engine
analyzed_fields = ["RU_ORGANIZATION", "RU_CITY", "RU_PERSON", "RU_ADDRESS", "CREDIT_CARD", "PHONE_NUMBER", "IP_ADDRESS", "URL", "SNILS", "INN", "RU_BANK_ACC"]

nlp_config = {
    "nlp_engine_name": "spacy",
    "models": [
        {"lang_code": "en", "model_name": "en_core_web_md"},
        {"lang_code": "ru", "model_name": "ru_core_news_sm"},
    ],
}

anonymizer = PresidioReversibleAnonymizer(analyzed_fields=analyzed_fields,
                                          add_default_faker_operators=True,
                                          languages_config=nlp_config)


anonymizer.add_recognizer(ru_internal_passport_recognizer)
anonymizer.add_recognizer(SNILSRecognizer())
anonymizer.add_recognizer(INNRecognizer())
anonymizer.add_recognizer(RUBankAccountRecognizer())
anonymizer.add_recognizer(GlinerRecognizer())

ru_operators={
        "RU_ORGANIZATION": OperatorConfig("keep"),
        "RU_CITY": OperatorConfig("keep"),
        "RU_PERSON": OperatorConfig("custom", {"lambda": fake_name}),
        "RU_ADDRESS": OperatorConfig("custom", {"lambda": fake_house}),
        "CREDIT_CARD": OperatorConfig("custom", {"lambda": fake_card}),
        "PHONE_NUMBER": OperatorConfig("custom", {"lambda": fake_phone}),
        "RU_PASSPORT": OperatorConfig("custom", {"lambda": fake_passport}),
        "SNILS": OperatorConfig("custom", {"lambda": fake_snils}),
        "INN": OperatorConfig("custom", {"lambda": fake_inn}),
        "RU_BANK_ACC": OperatorConfig("custom", {"lambda": fake_account}),
}
anonymizer.add_operators(ru_operators)

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

# Will need to split text to chunks. GliNER uses max 768 tokens
def length_factory(tokenizer: Any = None):
    @lru_cache(maxsize=5000, typed=True)
    def _len(text: str) -> int:
        return len(tokenizer.encode(text))
    if tokenizer:
        return _len
    else:
        return len
tokenizer =  AutoTokenizer.from_pretrained("gliner-community/gliner_large-v2.5")
calc_len = length_factory(tokenizer)


def anonymize(text, language = "en"):
    sentences = sent_tokenize(text, language='russian')
    texts = chunk_sentences(sentences, max_chunk_size=768, overlap_size=0, _len=calc_len)
    resulting_text = ""
    for text in texts:
        resulting_text = resulting_text + "\n" + anonymizer.anonymize(text, language=language)
    return resulting_text

def generate_answer(system_prompt: str, user_request: str) -> Tuple[str, str]:
    """
    Dummy LLM call. Replace with real API integration.
    Returns (llm_response, deanonymized_response).
    """
    anonymizer.reset_deanonymizer_mapping()
    prompt = ChatPromptTemplate.from_messages(
        [
            ("system", system_prompt),
            ("user", "{user_request}"),
        ]
    )

    chain = {"user_request": lambda txt: anonymize(txt, language="en")} | prompt | llm | (lambda ai_message: anonymizer.deanonymize(ai_message.content, deanonymizer_matching_strategy=combined_exact_fuzzy_matching_strategy,))
    response = chain.invoke(user_request)

    #results = chain.apply([{"user_request": user_request}])
    llm_resp = response
    #import pprint
    #pprint.pprint(anonymizer.deanonymizer_mapping)
    #dean_resp = deanonimizer(llm_resp, entities)
    return llm_resp#, dean_resp

if __name__ == "__main__":
    text = """Клиент Степан Степанов (4519227557) по поручению Ивана Иванова обратился в "Интерлизинг" с предложением купить трактор. 
    Для оплаты используется его карта 4095260993934932. 
    Позвоните ему 9867777777 или 9857777237.
    Или можно по адресу г. Санкт-Петербург, Сенная Площадь, д1/2кв17
    Посмотреть его данные можно https://client.ileasing.ru/name=stapanov:3000 или зайти на 182.34.35.12/
    """    
    system_prompt = """Преобразуй текст в записку для записи в CRM. Текст должен быть хорошо структурирован и понятен с первого взгляда"""
    print(generate_answer(system_prompt, text))