def validate_card(card_no: str) -> bool:
    # remove spaces or hyphens
    digits = [int(ch) for ch in card_no if ch.isdigit()]
    checksum = 0
    # process from rightmost, i=0
    for i, d in enumerate(reversed(digits)):
        if i % 2 == 1:
            d *= 2
            if d > 9:
                d -= 9
        checksum += d
    return checksum % 10 == 0



print(validate_card("2200150222538735"))