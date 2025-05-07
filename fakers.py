from faker import Faker
import functools
import spacy
import re

fake = Faker(locale="ru-RU")

faked_values = {}
nlp = spacy.load("ru_core_news_sm")

def calc_hash(text):
    VOWELS = set("АЕЁИОУЫЭЮЯаеёиоуыэюя")
    def alnum(s: str) -> str:
        def strip_vowels(word: str) -> str:
            while word and word[-1] in VOWELS:
                word = word[:-1]
            return word
        alfanum = ''.join(ch if (ch.isalnum() or ch.isspace()) else " " for ch in s)   

        words = alfanum.split()
        stripped = [strip_vowels(w) for w in words]
        return " ".join(stripped)
    
    tockens = nlp(text)
    hash = alnum("".join([token.lemma_ for token in tockens]))
    return hash

def defake(fake):
    hash = calc_hash(fake)
    return faked_values[hash].get('true')

def record_replacement(func):

    @functools.wraps(func)
    def wrapper(x):
        if x == "PII":
            return x
        fake = func(x)
        hash = calc_hash(fake)
        faked_values[hash] = {"true": x, "fake": fake}
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
    return fake.first_name() + " " + fake.last_name()
@record_replacement
def fake_first_name(x):
    return fake.first_name()
@record_replacement
def fake_middle_name(x):
    return fake.middle_name()
@record_replacement
def fake_last_name(x):
    return fake.last_name()
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
