from faker import Faker
fake = Faker(locale="ru-RU")

faked_values = {}

def fake_name(x):
    faked = fake.first_name() + " " + fake.last_name()
    faked_values[faked] = x
    return faked
def fake_first_name(x):
    faked = fake.first_name()
    faked_values[faked] = x
    return faked
def fake_middle_name(x):
    faked = fake.middle_name()
    faked_values[faked] = x
    return faked
def fake_last_name(x):
    faked = fake.last_name()
    faked_values[faked] = x
    return faked
def fake_city(x):
    faked = fake.city()
    faked_values[faked] = x
    return faked
def fake_street(x):
    faked = fake.street_name()
    faked_values[faked] = x
    return faked
def fake_district(x):
    faked = fake.district()
    faked_values[faked] = x
    return faked
def fake_region(x):
    faked = fake.region_code()
    faked_values[faked] = x
    return faked
def fake_house(x):
    faked = fake.street_address()
    faked_values[faked] = x
    return faked
def fake_city(x):
    faked = fake.city()
    faked_values[faked] = x
    return faked
def fake_location(x):
    faked = fake.address()
    faked_values[faked] = x
    return faked
def fake_email(x):
    faked = fake.safe_email()
    faked_values[faked] = x
    return faked
def fake_phone(x):
    faked = fake.phone_number()
    faked_values[faked] = x
    return faked
def fake_card(x):
    faked = fake.credit_card_number()
    faked_values[faked] = x
    return faked
def fake_ip(x):
    faked = fake.ipv4_public()
    faked_values[faked] = x
    return faked
def fake_url(x):
    faked = fake.url()
    faked_values[faked] = x
    return faked
