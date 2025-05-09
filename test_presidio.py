import json
from pprint import pprint, PrettyPrinter

from presidio_anonymizer import AnonymizerEngine
from presidio_anonymizer.entities import OperatorConfig
from presidio_anonymizer.entities import OperatorConfig
from presidio_anonymizer.operators import Decrypt

from fakers import *
from analyzer_engine_provider import analyzer_engine

from text_transformation import transform_text
from recognizers.regex_recognisers import RU_ENTITIES

text_to_anonymize = """Клиент Степан Степанов (4519 227557; 112-233-445 95) по поручению Ивана Иванова обратился в компанию Интерлизинг с предложением купить трактор. 
Для оплаты используется его карта 4095260993934932 или счёт 40817810806266001241. 
Позвоните ему 9867777777 или 9857777237.
Или можно по адресу г. Санкт-Петербург, Сенная Площадь, 1/2кв17
Посмотреть его данные можно https://client.ileasing.ru/name=stapanov:3000 или зайти на 182.34.35.12/
"""
#print(get_supported_entities("huggingface", "51la5/roberta-large-NER", None, None)) #flair/ner-english-large

print("========Initial text========")
print(text_to_anonymize)

#analyzer = analyzer_engine("flair", "flair/ner-english-large")
#analyzer = analyzer_engine("huggingface", "51la5/roberta-large-NER")
#analyzer = analyzer_engine("huggingface", "Gherman/bert-base-NER-Russian")
#analyzer = analyzer_engine("natasha", None)
analyzer = analyzer_engine("gliner", "gliner-community/gliner_large-v2.5")
#analyzer.registry.add_recognizer(NatashaSlovnetRecognizer())
recognizers = analyzer.get_recognizers()

entities = analyzer.get_supported_entities() + ["GENERIC_PII"] + RU_ENTITIES
entities.remove("IN_PAN")

#analyzer = analyzer_engine("flair", "flair/ner-english-large")
analyzer_results = analyzer.analyze(text=text_to_anonymize, entities=entities, language='en', return_decision_process=False)

#print(analyzer_results), Recognizer:{r.recognition_metadata['recognizer_name']}
pii_data = [(text_to_anonymize[res.start:res.end], res.start, res.end, res.entity_type, res.score, res.recognition_metadata['recognizer_name']) 
            for res in analyzer_results]

print("========Recognised entities========")
pprint(pii_data)


#decision_process = analyzer_results[0].analysis_explanation
#pp = PrettyPrinter()
#print("Decision process output:\n")
#pp.pprint(decision_process.__dict__)

# Initialize the engine:
engine = AnonymizerEngine()

#supported_entities = analyzer.get_supported_entities() + ["GENERIC_PII"]

result = engine.anonymize(
    text=text_to_anonymize,
    analyzer_results=analyzer_results,
    #operators={"PERSON": OperatorConfig("replace", {"new_value": "BIP"})},
    operators={"DEFAULT": OperatorConfig("encrypt", {"key": "WmZq4t7w!z%C&F)J"}),
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

anonimized_text = result.text

print("========Anonimized text========") 
print(anonimized_text)

print("========Anonimized entities========")
pprint(result.items)

def deanonimize(item): 
    if item.operator=="encrypt":
        return Decrypt().operate(text=item.text, params={"key": "WmZq4t7w!z%C&F)J"})
    elif item.operator=="custom":
        return defake(item.text)
    else:
        return item.text

#Deanonimizing entities
deanonimized_entities = [
    {**item.to_dict(), 'restored': deanonimize(item)}
    for item in result.items]

print("========DeAnonimized entities========")
pprint(deanonimized_entities)


#Restore deanonimized entities within text
llm_answer = transform_text(anonimized_text)
print("========LLM answer========")
print(llm_answer)

for item in deanonimized_entities:
    llm_answer  = llm_answer.replace(item["text"], item["restored"])

print("========Restored llm resoponse========")
print(llm_answer)

deanonimized_text = anonimized_text
for item in deanonimized_entities:
    deanonimized_text  = deanonimized_text.replace(item["text"], item["restored"])
print("========Restored text========")
print(deanonimized_text)
