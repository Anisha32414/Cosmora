from rag.vectorstore import get_hair_vectorstore
from llm.llm import get_llm
from llm.prompts import HAIR_SYSTEM_PROMPT


def hair_rag(user_profile):
    """
    Generate personalized hair-care wellness guidance
    using ChromaDB + Groq LLM.
    """

    # -----------------------------------------
    # 1. Load Hair Knowledge Base
    # -----------------------------------------

    vectorstore = get_hair_vectorstore()

    # -----------------------------------------
    # 2. Create Retrieval Query
    # -----------------------------------------

    query = f"""
    Hair problems:
    {user_profile.get("hair_problems", "")}

    Hair washing:
    {user_profile.get("hair_washing", "")}

    Shampoo usage:
    {user_profile.get("shampoo", "")}

    Conditioner usage:
    {user_profile.get("conditioner", "")}

    Oiling:
    {user_profile.get("oiling", "")}

    Pollution exposure:
    {user_profile.get("pollution", "")}

    Hair treatments:
    {user_profile.get("hair_treatments", "")}

    Heat styling:
    {user_profile.get("heat_styling", "")}

    Pillow cover:
    {user_profile.get("pillow_cover", "")}

    Diet:
    {user_profile.get("diet", "")}

    Hydration:
    {user_profile.get("hydration", "")}

    Sleep:
    {user_profile.get("sleep", "")}

    Stress:
    {user_profile.get("stress", "")}
    """

    # -----------------------------------------
    # 3. Retrieve Relevant Hair Knowledge
    # -----------------------------------------

    documents = vectorstore.similarity_search(
        query,
        k=5
    )

    # -----------------------------------------
    # 4. Combine Retrieved Documents
    # -----------------------------------------

    retrieved_context = "\n\n".join(
        document.page_content
        for document in documents
    )

    # -----------------------------------------
    # 5. Create User Prompt
    # -----------------------------------------

    user_prompt = f"""
USER HAIR PROFILE
=================

{user_profile}


RETRIEVED KNOWLEDGE
===================

{retrieved_context}


TASK
====

Using the user's hair profile and the retrieved knowledge,
provide personalized natural hair-care wellness guidance.

RESPONSE LENGTH
===============

- Keep the complete response between 400 and 500 words.
- Do not exceed 500 words.
- Use concise sentences.
- Use bullet points where appropriate.
- Do not repeat the same recommendation.

RESPONSE STRUCTURE
==================

1. Understanding the concern
   - 2-3 sentences.

2. Natural remedies
   - Maximum 3 remedies.

3. Lifestyle improvements
   - Maximum 4 bullet points.

4. Diet and hydration
   - Maximum 4 bullet points.

5. Preventive habits
   - Maximum 4 bullet points.

6. When to consult a professional
   - Maximum 3 bullet points.

Finish the complete response with the required disclaimer.

Do not provide a medical diagnosis.
Do not claim that a remedy will cure a condition.
Do not recommend expensive products, brands,
advertisements, affiliate products, or upselling.
"""

    # -----------------------------------------
    # 6. Call Groq LLM
    # -----------------------------------------

    llm = get_llm()

    response = llm.invoke(
        [
            ("system", HAIR_SYSTEM_PROMPT),
            ("human", user_prompt)
        ]
    )

    return response.content