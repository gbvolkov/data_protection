import json
from pprint import pprint, PrettyPrinter
from typing import Tuple, List, Optional

from presidio_analyzer import (
    AnalyzerEngine,
    RecognizerResult,
    RecognizerRegistry,
    PatternRecognizer,
    Pattern,
)
from presidio_anonymizer.entities import OperatorConfig
from presidio_anonymizer import AnonymizerEngine
from presidio_anonymizer.entities import OperatorConfig
from presidio_analyzer.nlp_engine import (
    NlpEngine,
    NlpEngineProvider,
)

import spacy

def create_nlp_engine_with_transformers(
    model_path: str,
) -> Tuple[NlpEngine, RecognizerRegistry]:
    """
    Instantiate an NlpEngine with a TransformersRecognizer and a small spaCy model.
    The TransformersRecognizer would return results from Transformers models, the spaCy model
    would return NlpArtifacts such as POS and lemmas.
    :param model_path: HuggingFace model path.
    """
    print(f"Loading Transformers model: {model_path} of type {type(model_path)}")

    nlp_configuration = {
        "nlp_engine_name": "transformers",
        "models": [
            {
                "lang_code": "en",
                "model_name": {"spacy": "en_core_web_sm", "transformers": model_path},
            }
        ],
        "ner_model_configuration": {
            "model_to_presidio_entity_mapping": {
                "PER": "PERSON",
                "PERSON": "PERSON",
                "LOC": "LOCATION",
                "LOCATION": "LOCATION",
                "GPE": "LOCATION",
                "ORG": "ORGANIZATION",
                "ORGANIZATION": "ORGANIZATION",
                "NORP": "NRP",
                "AGE": "AGE",
                "ID": "ID",
                "EMAIL": "EMAIL",
                "PATIENT": "PERSON",
                "STAFF": "PERSON",
                "HOSP": "ORGANIZATION",
                "PATORG": "ORGANIZATION",
                "DATE": "DATE_TIME",
                "TIME": "DATE_TIME",
                "PHONE": "PHONE_NUMBER",
                "HCW": "PERSON",
                "HOSPITAL": "ORGANIZATION",
                "FACILITY": "LOCATION",
            },
            "low_confidence_score_multiplier": 0.4,
            "low_score_entity_names": ["ID"],
            "labels_to_ignore": [
                "CARDINAL",
                "EVENT",
                "LANGUAGE",
                "LAW",
                "MONEY",
                "ORDINAL",
                "PERCENT",
                "PRODUCT",
                "QUANTITY",
                "WORK_OF_ART",
            ],
        },
    }

    nlp_engine = NlpEngineProvider(nlp_configuration=nlp_configuration).create_engine()

    registry = RecognizerRegistry()
    registry.load_predefined_recognizers(nlp_engine=nlp_engine)

    return nlp_engine, registry


def create_nlp_engine_with_flair(
    model_path: str,
) -> Tuple[NlpEngine, RecognizerRegistry]:
    """
    Instantiate an NlpEngine with a FlairRecognizer and a small spaCy model.
    The FlairRecognizer would return results from Flair models, the spaCy model
    would return NlpArtifacts such as POS and lemmas.
    :param model_path: Flair model path.
    """
    from flair_recognizer import FlairRecognizer

    registry = RecognizerRegistry()
    registry.load_predefined_recognizers()

    # there is no official Flair NlpEngine, hence we load it as an additional recognizer

    if not spacy.util.is_package("en_core_web_sm"):
        spacy.cli.download("en_core_web_sm")
    # Using a small spaCy model + a Flair NER model
    flair_recognizer = FlairRecognizer(model_path=model_path)
    nlp_configuration = {
        "nlp_engine_name": "spacy",
        "models": [{"lang_code": "en", "model_name": "en_core_web_sm"}],
    }
    registry.add_recognizer(flair_recognizer)
    registry.remove_recognizer("SpacyRecognizer")

    nlp_engine = NlpEngineProvider(nlp_configuration=nlp_configuration).create_engine()

    return nlp_engine, registry


def nlp_engine_and_registry(
    model_family: str,
    model_path: str,
    ta_key: Optional[str] = None,
    ta_endpoint: Optional[str] = None,
) -> Tuple[NlpEngine, RecognizerRegistry]:
    """Create the NLP Engine instance based on the requested model.
    :param model_family: Which model package to use for NER.
    :param model_path: Which model to use for NER. E.g.,
        "StanfordAIMI/stanford-deidentifier-base",
        "obi/deid_roberta_i2b2",
        "en_core_web_lg"
    :param ta_key: Key to the Text Analytics endpoint (only if model_path = "Azure Text Analytics")
    :param ta_endpoint: Endpoint of the Text Analytics instance (only if model_path = "Azure Text Analytics")
    """

    # Set up NLP Engine according to the model of choice
    if "flair" in model_family.lower():
        return create_nlp_engine_with_flair(model_path)
    elif "huggingface" in model_family.lower():
        return create_nlp_engine_with_transformers(model_path)
    else:
        raise ValueError(f"Model family {model_family} not supported")


def analyzer_engine(
    model_family: str,
    model_path: str,
    ta_key: Optional[str] = None,
    ta_endpoint: Optional[str] = None,
) -> AnalyzerEngine:
    """Create the NLP Engine instance based on the requested model.
    :param model_family: Which model package to use for NER.
    :param model_path: Which model to use for NER:
        "StanfordAIMI/stanford-deidentifier-base",
        "obi/deid_roberta_i2b2",
        "en_core_web_lg"
    :param ta_key: Key to the Text Analytics endpoint (only if model_path = "Azure Text Analytics")
    :param ta_endpoint: Endpoint of the Text Analytics instance (only if model_path = "Azure Text Analytics")
    """
    nlp_engine, registry = nlp_engine_and_registry(
        model_family, model_path, ta_key, ta_endpoint
    )
    analyzer = AnalyzerEngine(nlp_engine=nlp_engine, registry=registry)
    return analyzer

def get_supported_entities(
    model_family: str, model_path: str, ta_key: str, ta_endpoint: str
):
    """Return supported entities from the Analyzer Engine."""
    return analyzer_engine(
        model_family, model_path, ta_key, ta_endpoint
    ).get_supported_entities() + ["GENERIC_PII"]

text_to_anonymize = """Клиент Степан Степанов обратился в компанию с предложением купить трактор. 
Для оплаты используется его карта 4095260993934932. 
Позвоните ему 9867777777 или 9857777237.
Или можно по адресу г. Санкт-Петербург, Сенная Площадь, 1/2кв17
Посмотреть его данные можно https://client.ileasing.ru/name=stapanov:3000 или зайти на 182.34.35.12/

"""
#print(get_supported_entities("huggingface", "51la5/roberta-large-NER", None, None)) #flair/ner-english-large

analyzer = analyzer_engine("huggingface", "51la5/roberta-large-NER")
#analyzer = analyzer_engine("flair", "flair/ner-english-large")
analyzer_results = analyzer.analyze(text=text_to_anonymize, language='en', return_decision_process=True)

#print(analyzer_results)
pii_data = [(text_to_anonymize[res.start:res.end], res.start, res.end, res.entity_type, res.score, res.analysis_explanation) 
            for res in analyzer_results]

pprint(pii_data)


#decision_process = analyzer_results[0].analysis_explanation
#pp = PrettyPrinter()
#print("Decision process output:\n")
#pp.pprint(decision_process.__dict__)

# Initialize the engine:
engine = AnonymizerEngine()

result = engine.anonymize(
    text=text_to_anonymize,
    analyzer_results=analyzer_results,
    #operators={"PERSON": OperatorConfig("replace", {"new_value": "BIP"})},
    operators={"PERSON": OperatorConfig("encrypt", {"key": "WmZq4t7w!z%C&F)J"})},
)

print(result)