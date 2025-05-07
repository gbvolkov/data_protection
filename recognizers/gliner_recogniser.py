from typing import Optional, List, Tuple, Set

from presidio_analyzer import AnalyzerEngine, EntityRecognizer, RecognizerResult

from gliner import GLiNER

class GlinerRecognizer(EntityRecognizer):
    def __init__(
        self,
        supported_language: str = "en",
        supported_entities: Optional[List[str]] = None,
        check_label_groups: Optional[Tuple[Set, Set]] = None,
        model_path: Optional[str] = "gliner-community/gliner_large-v2.5",
    ):
        supported_entities = ["person", "organization", "city", "house_address"]
        super().__init__(
            supported_entities=supported_entities,
            name="GlinerRecognizer",
        )
        self._model = GLiNER.from_pretrained(model_path)

    def is_language_supported(self, language: str) -> bool:
        # Принудительно говорим Presidio: "вызывайте меня всегда"
        return True

    def analyze(self, text: str, entities=None, **kwargs):
        # запускаем Natasha NER
        spans = self._model.predict_entities(text=text, labels = self.supported_entities, flat_ner=True, threshold=0.35, multi_label=False)

        results = []
        for span in spans:
            # Переводим PER/LOC/ORG → Presidio-тизеры
            label = span.get("label")  # "PER", "LOC", "ORG"
            # фильтруем, если у нас есть entities-фильтр
            if entities and label not in entities:
                continue
            results.append(
                RecognizerResult(
                    entity_type=label,
                    start=span.get("start"),
                    end=span.get("end"),
                    score=span.get("score"),
                )
            )
        return results


if __name__ == "__main__":
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

    print("\n=== Russian call ===")
    result = engine.analyze(text=text_ru, language="en", return_decision_process=True)
    for r in result:
        print(f"{r.entity_type}: `{text_ru[r.start:r.end]}` (score={r.score:.2f})) , Recognizer:{r.recognition_metadata['recognizer_name']}")
