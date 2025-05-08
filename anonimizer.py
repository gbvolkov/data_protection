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

    from analyser_engine import analyzer_engine
    from nltk.tokenize import sent_tokenize
    from recognizers.regex_recognisers import RU_ENTITIES

    analyzer = analyzer_engine("gliner", "gliner-community/gliner_large-v2.5")
    tokenizer =  AutoTokenizer.from_pretrained("gliner-community/gliner_large-v2.5")
    calc_len = length_factory(tokenizer)
    supported = analyzer.get_supported_entities() + ["GENERIC_PII"] + RU_ENTITIES
    supported.remove("IN_PAN")
    engine = AnonymizerEngine()
    cr_key = config.CRYPRO_KEY

    
    def analyze(text, analizer_entities=supported):
        sentences = sent_tokenize(text, language='russian')
        texts = chunk_sentences(sentences, max_chunk_size=768, overlap_size=0, _len=calc_len)    
        analyzer_results = []
        shift = 0
        final_text = ""
        for chunk in texts:
            analized = analyzer.analyze(text=chunk, entities=analizer_entities, language='en', return_decision_process=False)
            #pii_data = [(chunk[res.start:res.end], res.start, res.end, res.entity_type, res.score, res.recognition_metadata['recognizer_name']) for res in analized]
            #print(f"========Recognised entities of chunk {chunk}========")
            #pprint(pii_data)
            analized = [
                RecognizerResult(r.entity_type, r.start + shift, r.end + shift, r.score, r.analysis_explanation, r.recognition_metadata)
                for r in analized
            ]
            analyzer_results.extend(analized)
            final_text = final_text + chunk + "\n"
            shift = len(final_text)#shift + len(chunk) + 2

        return final_text, analyzer_results
    def anonimizer(text):
        faked_values.clear()
        final_text, analyzer_results = analyze(text)

        #pii_data = [(final_text[res.start:res.end], res.start, res.end, res.entity_type, res.score, res.recognition_metadata['recognizer_name']) 
        #    for res in analyzer_results]
        #print("========Finally recognised entities========")
        #pprint(pii_data)

        result = engine.anonymize(
            text=final_text,
            analyzer_results=analyzer_results,
            #operators={"PERSON": OperatorConfig("replace", {"new_value": "BIP"})},
            operators={"DEFAULT": OperatorConfig("encrypt", {"key": cr_key}),
                    #"FIRST_NAME": OperatorConfig("custom", {"lambda": fake_first_name}),
                    #"MIDDLE_NAME": OperatorConfig("custom", {"lambda": fake_middle_name}),
                    #"LAST_NAME": OperatorConfig("custom", {"lambda": fake_last_name}),
                    "organization": OperatorConfig("keep"),
                    "city": OperatorConfig("keep"),
                    "person": OperatorConfig("custom", {"lambda": fake_name}),
                    #"STREET": OperatorConfig("custom", {"lambda": fake_street}),
                    "house_address": OperatorConfig("custom", {"lambda": fake_house}),
                    #"LOCATION": OperatorConfig("custom", {"lambda": fake_location}),
                    "CREDIT_CARD": OperatorConfig("custom", {"lambda": fake_card}),
                    "PHONE_NUMBER": OperatorConfig("custom", {"lambda": fake_phone}),
                    "IP_ADDRESS": OperatorConfig("custom", {"lambda": fake_ip}),
                    "URL": OperatorConfig("custom", {"lambda": fake_url}),
                    "RU_PASSPORT": OperatorConfig("custom", {"lambda": fake_passport}),
                    "SNILS": OperatorConfig("custom", {"lambda": fake_snils}),
                    "INN": OperatorConfig("custom", {"lambda": fake_inn}),
                    "RU_BANK_ACC": OperatorConfig("custom", {"lambda": fake_account}),
                    })

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
            elif item.operator=="custom":
                return defake(item.text)
            else:
                return item.text
        
        deanonimized_entities = [
            {**item.to_dict(), 'restored': deanonimize(item)}
            for item in entities]
        for item in deanonimized_entities:
            text  = text.replace(item["text"], item["restored"])


        analized_anon_text, analized_anon_results = analyze(text, ["person", "house_address"])
        
        result = engine.anonymize(
            text=analized_anon_text,
            analyzer_results=analized_anon_results,
            operators={"DEFAULT": OperatorConfig("keep"),
                    "person": OperatorConfig("custom", {"lambda": defake}),
                    "house_address": OperatorConfig("custom", {"lambda": defake}),
                    })        

        return result.text

    return anonimizer, deanonimizer

if __name__ == '__main__':
    from llm import generate_answer
    
    anonimizer, deanonimizer = anonimizer_factory()
    with open("data/test_text.txt", encoding="utf-8") as f:
        text = f.read()
    
    crypted, entities = anonimizer(text)
    with open("data/crypted.txt", "w", encoding="utf-8") as f:
        f.write(crypted)
    #print("========================================================")
    #print(crypted)
    with open("data/faked_hash.txt", "w", encoding="utf-8") as f:
        for hash in faked_values:
            f.write(f"hash: {hash};  true: {faked_values[hash]['true']};  fake: {faked_values[hash]['fake']}\n")
    with open("data/true_hash.txt", "w", encoding="utf-8") as f:
        for hash in true_values:
            f.write(f"hash: {hash};  true: {true_values[hash]['true']};  fake: {true_values[hash]['fake']}\n")

    system_prompt = """Ты очень опытный секретарь, который умеет готовить идеальные протоколы встреч.
Подготовь детальный протокол по транскрипту встречи.
Обязательно отрази основные тезисы докладов, высказанные возражения, зафиксируй решения и поставленные задачи со сроками и ответственными"""

    llm_resp = generate_answer(system_prompt, crypted)
    with open("data/response.txt", "w", encoding="utf-8") as f:
        f.write(llm_resp)
    dean_resp = deanonimizer(llm_resp, entities)
    with open("data/decypted.txt", "w", encoding="utf-8") as f:
        f.write(dean_resp)
    print("READY")

