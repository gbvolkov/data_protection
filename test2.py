from presidio_analyzer import AnalyzerEngine, EntityRecognizer, RecognizerResult
from gliner import GLiNER
from recognizers.gliner_recogniser import GlinerRecognizer

if __name__ == "__main__":
    from sentence_splitter import chunk_sentences
    from nltk.tokenize import sent_tokenize
    from functools import lru_cache
    from typing import Any
    from transformers import AutoTokenizer

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

    # Собираем движок с дефолтными Pattern/Spacy-распознавателями
    engine = AnalyzerEngine()
    # Впихиваем наш Natasha-распознаватель
    #engine.registry.add_recognizer(GlinerRecognizer(model_path="urchade/gliner_multi-v2.1"))
    engine.registry.add_recognizer(GlinerRecognizer(model_path="gliner-community/gliner_large-v2.5"))
    engine.registry.remove_recognizer("SpacyRecognizer")

    # Тест на реальном русском
    text_ru = "Пётр Иванов из Санкт-Петербурга поехал в офис Яндекса."
    text_ru = """Клиент Степан Степанов (4519227557) по поручению Ивана Иванова обратился в "Интерлизинг" с предложением купить трактор. 
Для оплаты используется его карта 4095260993934932. 
Позвоните ему 9867777777 или 9857777237.
Или можно по адресу г. Санкт-Петербург, Сенная Площадь, д1/2кв17
Посмотреть его данные можно https://client.ileasing.ru/name=stapanov:3000 или зайти на 182.34.35.12/
"""
    with open("data/anonimized.txt", encoding="utf-8") as f:
        text_ru = f.read()
    sentences = sent_tokenize(text_ru, language='russian')
    texts = chunk_sentences(sentences, max_chunk_size=768, overlap_size=0, _len=calc_len)    
    for text in texts:
        print("\n=== Russian call ===")
        result = engine.analyze(text=text, language="en", return_decision_process=True)
        for r in result:
            print(f"{r.entity_type}: `{text[r.start:r.end]}` (score={r.score:.2f})) , Recognizer:{r.recognition_metadata['recognizer_name']}")
