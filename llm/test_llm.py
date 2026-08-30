from llm import get_llm


llm = get_llm()

response = llm.invoke(
    "Give me one simple natural habit for maintaining healthy skin."
)

print(response.content)