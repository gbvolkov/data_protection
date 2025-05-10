import config
from pprint import pprint

#from langchain_experimental.data_anonymizer import PresidioAnonymizer
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

from  fakers import *
from typing import cast

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

# Will need to split text to chunks. GliNER uses max 768 tokens
from transformers import AutoTokenizer
from functools import lru_cache
from typing import Any
from sentence_splitter import chunk_sentences
from nltk.tokenize import sent_tokenize

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
        pprint(anonymizer.deanonymizer_mapping)
    return resulting_text


text = """Клиент Степан Степанов (4519227557) по поручению Ивана Иванова обратился в "Интерлизинг" с предложением купить трактор. 
Для оплаты используется его карта 4095260993934932. 
Позвоните ему 9867777777 или 9857777237.
Или можно по адресу г. Санкт-Петербург, Сенная Площадь, д1/2кв17
Посмотреть его данные можно https://client.ileasing.ru/name=stapanov:3000 или зайти на 182.34.35.12/
"""

cr_key = config.CRYPRO_KEY
ru_operators={#"DEFAULT": OperatorConfig("encrypt", {"key": cr_key}),
        #"FIRST_NAME": OperatorConfig("custom", {"lambda": fake_first_name}),
        #"MIDDLE_NAME": OperatorConfig("custom", {"lambda": fake_middle_name}),
        #"LAST_NAME": OperatorConfig("custom", {"lambda": fake_last_name}),
        "RU_ORGANIZATION": OperatorConfig("keep"),
        "RU_CITY": OperatorConfig("keep"),
        "RU_PERSON": OperatorConfig("custom", {"lambda": fake_name}),
        #"PERSON": OperatorConfig("custom", {"lambda": fake_name}),
        #"STREET": OperatorConfig("custom", {"lambda": fake_street}),
        "RU_ADDRESS": OperatorConfig("custom", {"lambda": fake_house}),
        #"LOCATION": OperatorConfig("custom", {"lambda": fake_location}),
        "CREDIT_CARD": OperatorConfig("custom", {"lambda": fake_card}),
        "PHONE_NUMBER": OperatorConfig("custom", {"lambda": fake_phone}),
        #"IP_ADDRESS": OperatorConfig("custom", {"lambda": fake_ip}),
        #"URL": OperatorConfig("custom", {"lambda": fake_url}),
        "RU_PASSPORT": OperatorConfig("custom", {"lambda": fake_passport}),
        "SNILS": OperatorConfig("custom", {"lambda": fake_snils}),
        "INN": OperatorConfig("custom", {"lambda": fake_inn}),
        "RU_BANK_ACC": OperatorConfig("custom", {"lambda": fake_account}),
}

anonymizer.add_operators(ru_operators)
#print(anonymizer.anonymize(text, language="ru"))

with open("data/test_text.txt", encoding="utf-8") as f:
    text = f.read()

system_prompt = """Ты очень опытный секретарь, который умеет готовить идеальные протоколы встреч.
Подготовь детальный протокол по транскрипту встречи.
Обязательно отрази основные тезисы докладов, высказанные возражения, зафиксируй решения и поставленные задачи со сроками и ответственными

{text}
"""


#system_prompt = """Преобразуй текст в записку для записи в CRM. Текст должен быть хорошо структурирован и понятен с первого взгляда.
#{text}
#"""

prompt = PromptTemplate.from_template(system_prompt)
#llm = ChatOpenAI(temperature=0)
llm = ChatOpenAI(model="gpt-4.1-mini", temperature=0.4, frequency_penalty=0.3)

chain = {"text": lambda txt: anonymize(txt, language="en")} | prompt | llm | (lambda ai_message: anonymizer.deanonymize(ai_message.content, deanonymizer_matching_strategy=fuzzy_matching_strategy,))

response = chain.invoke(text)
print(response)

pprint(anonymizer.deanonymizer_mapping)