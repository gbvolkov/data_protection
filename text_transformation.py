from langchain_mistralai import ChatMistralAI
import config

llm = ChatMistralAI(model="mistral-small-latest", temperature=1, frequency_penalty=0.3)

def transform_text(text):
    result = llm.invoke(f"Изложи текст красиво, в виде официальнеого питсьма руководству\n\n#TEXT\n{text}")
    return result.content
