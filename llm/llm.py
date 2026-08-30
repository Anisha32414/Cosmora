import os

from dotenv import load_dotenv
from langchain_groq import ChatGroq


load_dotenv()


def get_llm():

    api_key = os.getenv("GROQ_API_KEY")

    if not api_key:
        raise ValueError(
            "GROQ_API_KEY is missing from the .env file."
        )

    return ChatGroq(
        model="openai/gpt-oss-20b",
        temperature=0.3,
        max_tokens=2500,
        api_key=api_key
    )