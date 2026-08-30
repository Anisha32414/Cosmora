from rag.vectorstore import get_skin_vectorstore
from llm.llm import get_llm
from llm.prompts import SKIN_SYSTEM_PROMPT


# ============================================================
# QUESTIONNAIRE-BASED SKIN RAG
# ============================================================

def skin_rag(user_profile):
    """
    Generate personalized skin-care wellness guidance
    using questionnaire/profile information + ChromaDB + LLM.
    """

    # --------------------------------------------------------
    # 1. Load Skin Knowledge Base
    # --------------------------------------------------------

    vectorstore = get_skin_vectorstore()

    # --------------------------------------------------------
    # 2. Build Retrieval Query
    # --------------------------------------------------------

    query = f"""
    Skin concern: {user_profile.get("skin_concern", "")}
    Skin concerns: {user_profile.get("skin_concerns", "")}

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

    # --------------------------------------------------------
    # 3. Combine Retrieved Knowledge
    # --------------------------------------------------------

    retrieved_context = "\n\n".join(
        document.page_content
        for document in documents
    )

    # --------------------------------------------------------
    # 4. Create LLM Prompt
    # --------------------------------------------------------

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

    # --------------------------------------------------------
    # 5. Call LLM
    # --------------------------------------------------------

    llm = get_llm()

    response = llm.invoke(
        [
            ("system", SKIN_SYSTEM_PROMPT),
            ("human", user_prompt)
        ]
    )

    return response.content


# ============================================================
# IMAGE-ANALYSIS SKIN RAG
# ============================================================

def skin_analysis_rag(tool_results, user_concern=""):
    """
    Generate personalized skincare guidance using:

    - Rupam.ai image-analysis results
    - DermIQ image-analysis results
    - User concern
    - ChromaDB skin knowledge base
    - Groq LLM
    """

    print("\n")
    print("=" * 60)
    print("SKIN ANALYSIS RAG")
    print("=" * 60)

    # --------------------------------------------------------
    # 1. Load Skin Knowledge Base
    # --------------------------------------------------------

    print("\nLoading skin knowledge base...")

    vectorstore = get_skin_vectorstore()

    print("Skin knowledge base loaded.")

    # --------------------------------------------------------
    # 2. Extract Findings From Both Tools
    # --------------------------------------------------------

    findings = []

    for tool in tool_results:

        if not tool.get("success"):
            continue

        tool_name = tool.get(
            "tool",
            "Unknown Tool"
        )

        for finding in tool.get("findings", []):

            condition = (
                finding.get("condition_name")
                or finding.get("condition_id")
                or "Unknown"
            )

            score = finding.get("score")

            region = finding.get("region")

            findings.append({

                "tool": tool_name,

                "condition": condition,

                "score": score,

                "region": region

            })

    # --------------------------------------------------------
    # 3. Check Findings
    # --------------------------------------------------------

    print("\nNumber of detected findings:", len(findings))

    if not findings:

        print("WARNING: No successful findings were received.")

    # --------------------------------------------------------
    # 4. Convert Findings Into Text
    # --------------------------------------------------------

    findings_text = "\n".join(

        f"- {item['tool']}: "
        f"{item['condition']} "
        f"(score={item['score']}, "
        f"region={item['region']})"

        for item in findings

    )

    print("\nDetected findings:")
    print(findings_text)

    # --------------------------------------------------------
    # 5. Build Retrieval Query
    # --------------------------------------------------------

    query = f"""
    User's skin concern:
    {user_concern}

    Skin concerns detected from image analysis:

    {findings_text}

    Retrieve skincare knowledge specifically relevant
    to the detected concerns.

    Focus on:

    - possible contributing factors
    - natural skincare practices
    - lifestyle habits
    - hydration
    - sleep
    - diet
    - sun protection
    - stress management
    - safe home-care practices
    - precautions
    - situations where professional dermatological
      advice may be appropriate
    """

    # --------------------------------------------------------
    # 6. Retrieve Knowledge From ChromaDB
    # --------------------------------------------------------

    print("\nSearching ChromaDB...")

    documents = vectorstore.similarity_search(
        query,
        k=5
    )

    print(
        "Retrieved documents:",
        len(documents)
    )

    # --------------------------------------------------------
    # 7. Combine Retrieved Knowledge
    # --------------------------------------------------------

    retrieved_context = "\n\n".join(

        document.page_content

        for document in documents

    )

    print("\nRetrieved knowledge successfully.")

    # --------------------------------------------------------
    # 8. Prepare Tool Summary
    # --------------------------------------------------------

    tool_summary = []

    for tool in tool_results:

        if not tool.get("success"):
            continue

        tool_summary.append({

            "tool":
                tool.get("tool"),

            "overall_skin_score":
                tool.get("overall_skin_score"),

            "findings":
                tool.get(
                    "findings",
                    []
                )

        })

    # --------------------------------------------------------
    # 9. Create LLM Prompt
    # --------------------------------------------------------

    user_prompt = f"""
You are Cosmora's personalized natural skincare
wellness assistant.

The user uploaded a face image for analysis.

The image was analyzed by TWO independent
AI skin-analysis tools.

USER'S MAIN CONCERN:

{user_concern}


IMAGE ANALYSIS RESULTS:

{tool_summary}


DETECTED FINDINGS:

{findings_text}


RETRIEVED SKINCARE KNOWLEDGE:

{retrieved_context}


============================================================
YOUR TASK
============================================================

Analyze the findings from BOTH Rupam.ai and DermIQ
together.

Do not blindly trust one tool or one numerical score.

Give greater importance to concerns that:

- appear in both tools,
- have relatively strong scores,
- or are clearly relevant to the user's stated concern.

The image analysis is NOT a medical diagnosis.


============================================================
YOUR RESPONSE MUST CONTAIN THESE SECTIONS
============================================================

1. SKIN ANALYSIS SUMMARY

Explain the main skin concerns detected from the
image analysis.

Clearly distinguish between observations from the
AI tools and medical diagnosis.

Mention when both tools indicate a similar concern.


2. KEY SKIN CONCERNS

List the most important concerns.

For every concern:

- name the concern
- briefly explain what it means
- explain why it is relevant based on the analysis


3. POSSIBLE CONTRIBUTING FACTORS

Explain possible lifestyle or environmental factors
that may contribute to the detected concerns.

Examples may include:

- poor sleep
- stress
- dehydration
- excessive sun exposure
- diet
- excessive face washing
- unsuitable skincare habits

IMPORTANT:

These are possible contributing factors only.
Do not claim that they are confirmed causes.


4. NATURAL SKINCARE & LIFESTYLE PLAN

Provide practical and affordable recommendations.

Focus on:

- gentle face washing
- hydration
- adequate sleep
- balanced diet
- sun protection
- stress management
- simple natural skincare habits
- safe home-care practices

Do not recommend expensive products.


5. DAILY ROUTINE

Create a simple routine.

MORNING:
- Step 1
- Step 2
- Step 3

EVENING:
- Step 1
- Step 2
- Step 3

WEEKLY:
- useful simple habits


6. WHAT TO AVOID

List habits or practices that could potentially
worsen the user's detected concerns.


7. WHEN TO SEE A DERMATOLOGIST

Explain when professional dermatological advice
would be appropriate.

Examples include:

- severe or persistent acne
- painful or rapidly worsening skin problems
- sudden unexplained changes
- persistent irritation
- concerns that do not improve with basic care


============================================================
IMPORTANT RULES
============================================================

- Do not diagnose diseases.
- Do not claim the image analysis is a diagnosis.
- Do not blindly trust one AI tool.
- Consider BOTH Rupam.ai and DermIQ.
- Do not recommend brands.
- Do not recommend expensive skincare products.
- Do not advertise.
- Do not upsell.
- Prioritize affordable lifestyle practices.
- Prefer safe, evidence-informed general skincare advice.
- Do not invent information.
- Base recommendations on the retrieved knowledge.
- Do not expose API IDs or technical implementation details.
- Do not expose raw API responses.
- Keep the response understandable to a normal user.
"""

    # --------------------------------------------------------
    # 10. Call Groq LLM
    # --------------------------------------------------------

    print("\nSending data to Groq LLM...")

    llm = get_llm()

    response = llm.invoke(
        [
            ("system", SKIN_SYSTEM_PROMPT),
            ("human", user_prompt)
        ]
    )

    # --------------------------------------------------------
    # 11. Extract LLM Response
    # --------------------------------------------------------

    final_guidance = response.content

    print("\n")
    print("=" * 60)
    print("LLM RESPONSE RECEIVED")
    print("=" * 60)

    print(final_guidance)

    print("=" * 60)

    # --------------------------------------------------------
    # 12. Return Final Guidance
    # --------------------------------------------------------

    return final_guidance