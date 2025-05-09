from faker import Faker
from faker.providers.person.en import Provider as BasePerson

import functools
import spacy
import pymorphy3

import re

from names_morph import get_morphs

import logging
logger = logging.getLogger(__name__)

class FilteredPerson(BasePerson):
    # drop your unwanted names here
    first_names = [n for n in BasePerson.first_names if n not in {"Алесандр", "Алесандра", "Юлия", "Юлия", "Добромысл", "Добромысла", "Эммануил", "Эммануила", "Мирослав", "Мирослава"}]

fake = Faker(locale="ru-RU")
morph = pymorphy3.MorphAnalyzer(lang='ru')

faked_values = {}
true_values = {}
nlp = spacy.load("ru_core_news_sm")

def validate_name(name):
    try:
        forms = get_morphs(name)
        hash_nom = calc_hash(name)
        for case, val in forms["singular"].items():
            hash_var = calc_hash(val)
            if hash_var != hash_nom:
                #print(f"{name} ({hash_nom}): {case}: {val} ({hash_var})")
                return False
        for case, val in forms["plural"].items():
            hash_var = calc_hash(val)
            if hash_var != hash_nom:
                #print(f"{name} ({hash_nom}): plural_{case}: {val} ({hash_var})")
                return False
        return True
    except:
        return False


def calc_hash(text):
    VOWELS = set("АЕЁИОУЫЭЮЯаеёиоуыэюя")
    def alnum(s: str) -> str:
        def strip_vowels(word: str) -> str:
            while word and word[-1] in VOWELS:
                word = word[:-1]
            return word
        alfanum = ''.join(ch if (ch.isalnum() or ch.isspace()) else " " for ch in s)   

        words = alfanum.split()
        #stripped = [strip_vowels(w) for w in words]
        stripped = [w for w in words]
        return " ".join(stripped)
    
    def normalyze_lemma(lemma):
        parse = morph.parse(lemma)[0]
        form = parse.inflect({"nomn", "sing", "masc"})
        return form.word if form else lemma

    tockens = nlp(text)
    hash = alnum("".join([normalyze_lemma(token.lemma_) for token in tockens]))
    return hash

def defake(fake):
    if fake == 'PII':
        return fake
    hash = calc_hash(fake)
    if hash in faked_values:
        logger.debug(f"FAKE FOUND: request: {fake}; hash: {hash}; true: {faked_values[hash].get('true')}; fake: {faked_values[hash].get('fake')}")
        return faked_values[hash].get('true')
    else:
        logger.debug(f"FAKE NOT FOUND: request: {fake}; hash: {hash}")
        return fake

def record_replacement(func):

    @functools.wraps(func)
    def wrapper(x):
        if x == "PII":
            return x
        hash = calc_hash(x)
        if hash in true_values:
            fake = true_values[hash].get('fake')
        else:
            fake = func(x)
            true_values[hash] = {"true": x, "fake": fake}
        faked_values[calc_hash(fake)] = {"true": x, "fake": fake}
        return fake
    return wrapper

@record_replacement
def fake_account(x):
    return fake.checking_account()
@record_replacement
def fake_snils(x):
    return fake.snils()
@record_replacement
def fake_inn(x):
    return  fake.businesses_inn()
@record_replacement
def fake_passport(x):
    return fake.passport_number()
@record_replacement
def fake_name(x):
    attempts = 10
    while attempts > 0:
        name = fake.first_name() + " " + fake.last_name()
        if validate_name(name):
            return name
        attempts -= 1
    logger.warning(f"NON_CASHABLE: {name}")
    return name
@record_replacement
def fake_first_name(x):
    attempts = 10
    while attempts > 0:
        name = fake.first_name()
        if validate_name(name):
            return name
        attempts -= 1
    logger.warning(f"NON_CASHABLE: {name}")
    return name
def fake_middle_name(x):
    return fake.middle_name()
@record_replacement
def fake_last_name(x):
    attempts = 10
    while attempts > 0:
        name = fake.last_name()
        if validate_name(name):
            return name
        attempts -= 1
    logger.warning(f"NON_CASHABLE: {name}")
    return name
@record_replacement
def fake_city(x):
    return fake.city()
@record_replacement
def fake_street(x):
    return fake.street_name()
@record_replacement
def fake_district(x):
    return fake.district()
@record_replacement
def fake_region(x):
    return fake.region_code()
@record_replacement
def fake_house(x):
    return fake.street_address()
@record_replacement
def fake_city(x):
    return fake.city()
@record_replacement
def fake_location(x):
    return fake.address()
@record_replacement
def fake_email(x):
    return fake.safe_email()
@record_replacement
def fake_phone(x):
    return fake.phone_number()
@record_replacement
def fake_card(x):
    return fake.credit_card_number()
@record_replacement
def fake_ip(x):
    return fake.ipv4_public()
@record_replacement
def fake_url(x):
    return fake.url()

if __name__ == '__main__':
    import time
    for i in range(0, 15):
        name = fake.name()
        print(name)
    hash = calc_hash('Юлия Валентиновича Блинова')
    print(hash)
    hash = calc_hash('Юлий Валентинович Блинов')
    print(hash)
