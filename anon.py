def anonimize(text: str) -> str:
    """
    Dummy anonymization: replace digits with 'X'.
    Plug in your real logic here.
    """
    return ''.join('X' if c.isdigit() else c for c in text)