import json
from pprint import pprint, PrettyPrinter
from functools import lru_cache
from typing import List, Dict, Tuple, Any

from presidio_analyzer import RecognizerResult
from presidio_anonymizer import AnonymizerEngine
from presidio_anonymizer.entities import OperatorConfig
from presidio_anonymizer.entities import OperatorConfig
from presidio_anonymizer.operators import Decrypt

from transformers import AutoTokenizer

from fakers import *
import config

import logging
logger = logging.getLogger(__name__)


def length_factory(tokenizer: Any = None):
    @lru_cache(maxsize=5000, typed=True)
    def _len(text: str) -> int:
        return len(tokenizer.encode(text))
    if tokenizer:
        return _len
    else:
        return len

def anonimizer_factory():
    from sentence_splitter import chunk_sentences
    from nltk.tokenize import sent_tokenize

    from analyzer_engine_provider import analyzer_engine
    from recognizers.regex_recognisers import RU_ENTITIES

    analyzer = analyzer_engine("gliner", "gliner-community/gliner_large-v2.5")
    tokenizer =  AutoTokenizer.from_pretrained("gliner-community/gliner_large-v2.5")
    calc_len = length_factory(tokenizer)
    supported = analyzer.get_supported_entities() + RU_ENTITIES
    supported.remove("IN_PAN")
    engine = AnonymizerEngine()
    cr_key = config.CRYPRO_KEY

    
    def analyze(text, analizer_entities=supported):
        sentences = sent_tokenize(text, language='russian')
        texts = chunk_sentences(sentences, max_chunk_size=768, overlap_size=0, _len=calc_len)    
        analyzer_results = []
        shift = 0
        final_text = ""
        logger.debug(f"\n\n=============================ANALISYS================================")
        for chunk in texts:
            analized = analyzer.analyze(text=chunk, entities=analizer_entities, language='en', return_decision_process=False)
            logger.debug(f"\n\n=============================ANALISYS FOR CHUNK================================:\n{chunk}\n\n")
            for r in analized:
                logger.debug(f"\t\t{r.entity_type}: `{chunk[r.start:r.end]}` (score={r.score:.2f})) , Recognizer:{r.recognition_metadata['recognizer_name']}")
            #pprint(pii_data)
            analized = [
                RecognizerResult(r.entity_type, r.start + shift, r.end + shift, r.score, r.analysis_explanation, r.recognition_metadata)
                for r in analized
            ]
            analyzer_results.extend(analized)
            final_text = final_text + chunk + "\n"
            shift = len(final_text)#shift + len(chunk) + 2

        logger.debug(f"\n=============================ANALISYS DONE================================\n")
        return final_text, analyzer_results
    def anonimizer(text):
        faked_values.clear()
        true_values.clear()
        final_text, analyzer_results = analyze(text)

        #pii_data = [(final_text[res.start:res.end], res.start, res.end, res.entity_type, res.score, res.recognition_metadata['recognizer_name']) 
        #    for res in analyzer_results]
        #print("========Finally recognised entities========")
        #pprint(pii_data)

        result = engine.anonymize(
            text=final_text,
            analyzer_results=analyzer_results,
            operators={"DEFAULT": OperatorConfig("encrypt", {"key": cr_key}),
                    "RU_ORGANIZATION": OperatorConfig("custom", {"lambda": fake_organization}),
                    "RU_CITY": OperatorConfig("keep"),
                    "RU_PERSON": OperatorConfig("custom", {"lambda": fake_name}),
                    "RU_ADDRESS": OperatorConfig("custom", {"lambda": fake_house}),
                    "CREDIT_CARD": OperatorConfig("custom", {"lambda": fake_card}),
                    "PHONE_NUMBER": OperatorConfig("custom", {"lambda": fake_phone}),
                    "IP_ADDRESS": OperatorConfig("custom", {"lambda": fake_ip}),
                    "URL": OperatorConfig("custom", {"lambda": fake_url}),
                    "RU_PASSPORT": OperatorConfig("custom", {"lambda": fake_passport}),
                    "SNILS": OperatorConfig("custom", {"lambda": fake_snils}),
                    "INN": OperatorConfig("custom", {"lambda": fake_inn}),
                    "RU_BANK_ACC": OperatorConfig("custom", {"lambda": fake_account}),
                    })

        logger.debug(f"\n=============================ANONIMIZATION COMPLETE================================")
        return result.text, result.items
    
    def deanonimizer_simple(text, entities):
        def deanonimize(item):
            if item.operator=="encrypt":
                return Decrypt().operate(text=item.text, params={"key": cr_key})
            elif item.operator=="custom":
                return defake(item.text)
            else:
                return item.text
        deanonimized_entities = [
            {**item.to_dict(), 'restored': deanonimize(item)}
            for item in entities]
        for item in deanonimized_entities:
            text  = text.replace(item["text"], item["restored"])
        
        return text
    
    def deanonimizer(text, entities):
        def deanonimize(item): 
            if item.operator=="encrypt":
                return Decrypt().operate(text=item.text, params={"key": cr_key})
            #elif item.operator=="custom":
            #    return defake(item.text)
            else:
                return item.text


        analized_anon_text, analized_anon_results = analyze(text)#, ["person", "house_address"])
        logger.debug(f"\n=============================DEANONIMIZATION ANALISYS================================")
        for r in analized_anon_results:
            logger.debug(f"{r.entity_type}: `{analized_anon_text[r.start:r.end]}` (score={r.score:.2f})) , Recognizer:{r.recognition_metadata['recognizer_name']}")
        logger.debug(f"\n=============================DEANONIMIZATION ANALISYS================================")
        
        result = engine.anonymize(
            text=analized_anon_text,
            analyzer_results=analized_anon_results,

            operators={"DEFAULT": OperatorConfig("keep"),
                    "RU_ORGANIZATION": OperatorConfig("custom", {"lambda": defake_fuzzy}),
                    "RU_CITY": OperatorConfig("keep"),
                    "RU_PERSON": OperatorConfig("custom", {"lambda": defake_fuzzy}),
                    "RU_ADDRESS": OperatorConfig("custom", {"lambda": defake_fuzzy}),
                    "CREDIT_CARD": OperatorConfig("custom", {"lambda": defake}),
                    "PHONE_NUMBER": OperatorConfig("custom", {"lambda": defake_fuzzy}),
                    "IP_ADDRESS": OperatorConfig("custom", {"lambda": defake}),
                    "URL": OperatorConfig("custom", {"lambda": defake_fuzzy}),
                    "RU_PASSPORT": OperatorConfig("custom", {"lambda": defake}),
                    "SNILS": OperatorConfig("custom", {"lambda": defake}),
                    "INN": OperatorConfig("custom", {"lambda": defake}),
                    "RU_BANK_ACC": OperatorConfig("custom", {"lambda": defake}),
                    })

            #operators={"DEFAULT": OperatorConfig("keep"),
            #        "person": OperatorConfig("custom", {"lambda": defake}),
            #        "house_address": OperatorConfig("custom", {"lambda": defake}),
            #        })        
        deanonimized_text = result.text
        logger.debug(f"Count of entities: {len(entities)}: {len(faked_values)}: {len(true_values)}")    
        deanonimized_entities = [
            {**item.to_dict(), 'restored': deanonimize(item)}
            for item in entities]
        #for r in deanonimized_entities:
        #    print(f"{r['entity_type']}: `{analized_anon_text[r['start']:r['end']]}` (text={r['text']})) , restored:{r['restored']}")
        for item in deanonimized_entities:
            deanonimized_text  = deanonimized_text.replace(item["text"], item["restored"])


        return deanonimized_text, result.items

    return anonimizer, deanonimizer, analyze

class TextProcessor():
    def __init__(self, verbose=False):
        self._anonimizer, self._deanonimizer, _ = anonimizer_factory()
        self._entities = None
        self._anonimized_text = ""
        self._verbose = verbose
    def anonimize(self, text: str) -> str:
        logger.debug(f"\n\n=============================ANONIMIZATION================================")
        logger.debug(    f"\n==================================================================INITIAL TEXT:\n{text}\n\n")
        self._anonimized_text, self._entities = self._anonimizer(text)
        if self._verbose:
            logger.debug(f"\n===========================ANONIMIZED RESULTS================================")
            logger.debug(  f"\n===========================================================ANONIMIZED_TEXT:\n{self._anonimized_text}\n\n")
            logger.debug(  f"\n===========================================================FAKED_VALUES:")
            for hash in faked_values:
                logger.debug(f"\thash: {hash};  true: {faked_values[hash]['true']};  fake: {faked_values[hash]['fake']}")
            logger.debug(  f"\n===========================================================TRUE_VALUES:")
            for hash in true_values:
                logger.debug(f"\thash: {hash};  true: {true_values[hash]['true']};  fake: {true_values[hash]['fake']}")
            logger.debug(  f"\n===========================================================ENTITIES:")
            for e in self._entities:
                logger.debug(f"\ttype: {e.entity_type};  value: {e.text};  operator: {e.operator}")

        
        return self._anonimized_text
    def deanonimize(self, anonimized_text: str) -> str:
        if self._entities:
            logger.debug(f"\n\n===========================DEANONIMIZATION================================")
            logger.debug(  f"===========================================================ANONIMIZED_TEXT:\n{anonimized_text}\n\n")
            deanonimized_text, deanon_entities = self._deanonimizer(anonimized_text, self._entities)
        
            if self._verbose:
                logger.debug(f"\n===========================DEANONIMIZED RESULTS================================")
                logger.debug(  f"\n===========================================================DEANONIMIZED_TEXT:\n{deanonimized_text}\n\n")
                logger.debug(  f"\n===========================================================DEANON_ENTITIES:")
                for e in deanon_entities:
                    logger.debug(f"\ttype: {e.entity_type};  value: {e.text};  operator: {e.operator}")
        
            return deanonimized_text
        else:
            return ""


if __name__ == '__main__':
    import time
    import threading

    from logger_factory import setup_logging

    thread_id = threading.get_ident()
    timestamp = time.strftime("%Y%m%d_%H%M%S", time.localtime())
    log_name = f"anonimizer_{timestamp}_{thread_id}"

    #logging.basicConfig(level=logging.WARNING)
    setup_logging("anonimizer")
    logger = logging.getLogger(__name__)
    #timestamp=time.time()
    #logger = logging.getLogger(log_name)
    #logger.info("Started")

#    with open("data/anonimized.txt", encoding="utf-8") as f:
#        text = f.read()
#
#    _, _, analyze = anonimizer_factory()
#    analized_anon_text, analized_anon_results = analyze(text)
#    for r in analized_anon_results:
#        print(f"{r.entity_type}: `{analized_anon_text[r.start:r.end]}` (score={r.score:.2f})) , Recognizer:{r.recognition_metadata['recognizer_name']}")
    from llm_simplistic import generate_answer
    text = """Клиент Степан Степанов (4519227557) по поручению Ивана Иванова обратился в "Интерлизинг" с предложением купить трактор. 
    Для оплаты используется его карта 4095260993934932. 
    Позвоните ему 9867777777 или 9857777237.
    Или можно по адресу г. Санкт-Петербург, Сенная Площадь, д1/2кв17
    Посмотреть его данные можно https://client.ileasing.ru/name=stapanov:3000 или зайти на 182.34.35.12/
    """    
    #with open("data/test_text.txt", encoding="utf-8") as f:
    #    text = f.read()

    system_prompt = """Ты очень опытный секретарь, который умеет готовить идеальные протоколы встреч.
Подготовь детальный протокол по транскрипту встречи.
Обязательно отрази основные тезисы докладов, высказанные возражения, зафиксируй решения и поставленные задачи со сроками и ответственными"""
    system_prompt = """Преобразуй текст в записку для записи в CRM. Текст должен быть хорошо структурирован и понятен с первого взгляда"""

    processor = TextProcessor(verbose=True)
    for i in range(0,31):
        anon = processor.anonimize(text)
        logger.info("Anonimized")
        answer = generate_answer(system_prompt, anon)
        logger.info("LLM response recevied")
        deanon = processor.deanonimize(answer)
        logger.info("DONE")
        with open(f"data/result_{i:2}.txt", "w", encoding="utf-8") as f:
            f.write(deanon)
