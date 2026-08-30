from rag.vectorstore import get_skin_vectorstore
from llm.llm import get_llm
from llm.prompts import SKIN_SYSTEM_PROMPT


def skin_rag(user_profile):
    """
    Generate personalized skin-care wellness guidance
    using ChromaDB + Groq LLM.
    """

    # -----------------------------------------
    # 1. Load Skin Knowledge Base
    # -----------------------------------------

    vectorstore = get_skin_vectorstore()

    # -----------------------------------------
    # 2. Retrieve Relevant Knowledge
    # -----------------------------------------

    query = f"""
    Skin concern: {user_profile.get("skin_concern", "")}

    Lifestyle:
    Face washing: {user_profile.get("face_washing", "")}
    Diet: {user_profile.get("diet", "")}
    Sunscreen usage: {user_profile.get("sunscreen", "")}
    Cosmetics usage: {user_profile.get("cosmetics", "")}
    Water intake: {user_profile.get("water_intake", "")}
    Sun exposure: {user_profile.get("sun_exposure", "")}
    Sleep: {user_profile.get("sleep", "")}
    Stress: {user_profile.get("stress", "")}
    """

    documents = vectorstore.similarity_search(
        query,
        k=5
    )

    # -----------------------------------------
    # 3. Combine Retrieved Knowledge
    # -----------------------------------------

    retrieved_context = "\n\n".join(
        document.page_content
        for document in documents
    )

    # -----------------------------------------
    # 4. Create Prompt
    # -----------------------------------------

    user_prompt = f"""
USER SKIN PROFILE:

{user_profile}


RETRIEVED KNOWLEDGE:

{retrieved_context}


TASK:

Using the user's profile and the retrieved knowledge,
provide personalized natural skincare wellness guidance.

Follow all rules in the system instructions.

Do not diagnose any medical condition.

Do not recommend brands, expensive products,
cosmetics, advertisements, or upselling.
"""

    # -----------------------------------------
    # 5. Call LLM
    # -----------------------------------------

    llm = get_llm()

    response = llm.invoke(
        [
            ("system", SKIN_SYSTEM_PROMPT),
            ("human", user_prompt)
        ]
    )

    return response.content