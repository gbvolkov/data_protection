from fuzzysearch import find_near_matches
from rapidfuzz import fuzz, process

with open("data/test_text_test.txt", encoding="utf-8") as f:
    text = f.read()

pattern = "ул. Линейная, д. 2, квартира 723"
text = "Линейная улица, 2-723"


#text = "Мы живём по адресу Линейная улица, дом 2, кв. 723 совершенно одни"
#pattern = "123 Main Street, Springfeld IL"
#text = "шоссе Ермака, д. 6"
#pattern = "ш. Ермака, д. 6"
matches = find_near_matches(pattern, text, max_l_dist=1)#, max_substitutions=5, max_deletions=3, max_insertions=12)
for m in matches:
    print(f"Matched '{m.matched}' at [{m.start}:{m.end}], distance={m.dist}")

text = "шоссе Ермака, д. 6"
choices = ["ш. Ермакова, дом 1/6", "Георгий Волков", "шоссе Ермолова д.6", "535474758"]

text = "Линейная улица, 2-723"
choices = ["ш. Ермака, д. 6", "Георгий Волков", "ул. Линейная, д. 2, квартира 723", "штрассе Ермолова", "535474758", "Волконский"]

#fuzz.token_set_ratio
best = process.extractOne(text, choices, scorer=fuzz.partial_token_sort_ratio, score_cutoff=60)
print(best)