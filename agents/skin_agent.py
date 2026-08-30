import json

from tools.rupam import analyze_with_rupam
from tools.dermaiq import analyze_with_dermaiq
from rag.skin_rag import skin_analysis_rag


# ============================================================
# NORMALIZE DERMIQ FINDINGS
# ============================================================

DERMIQ_NAME_MAP = {
    "hd_acne": "acne",
    "hd_wrinkle": "wrinkles",
    "hd_pore": "pores",
    "hd_redness": "redness",
    "hd_oiliness": "oiliness",
    "hd_texture": "texture",
    "hd_firmness": "firmness",
    "hd_moisture": "moisture",
    "hd_radiance": "radiance",
    "hd_eye_bag": "eye_bags",
    "hd_dark_circle": "dark_circles",
    "hd_age_spot": "age_spots",
}


def normalize_dermiq_findings(dermiq_result):

    normalized = []

    for finding in dermiq_result.get("findings", []):

        condition_id = finding.get("condition_id")

        condition_name = DERMIQ_NAME_MAP.get(
            condition_id,
            condition_id
        )

        normalized.append({

            "condition_id": condition_name,

            "condition_name": condition_name,

            "score": finding.get("score"),

            "raw_score": finding.get("raw_score"),

            "region": finding.get("region"),

            "reliability": finding.get("reliability")

        })

    return normalized


# ============================================================
# BUILD COMBINED FINDINGS
# ============================================================

def build_combined_findings(rupam_result, dermaiq_result):

    combined = []

    # --------------------------------------------------------
    # RUPAM FINDINGS
    # --------------------------------------------------------

    for finding in rupam_result.get("findings", []):

        combined.append({

            "source": "Rupam",

            "condition_id":
                finding.get("condition_id"),

            "condition_name":
                finding.get("condition_name"),

            "severity":
                finding.get("severity"),

            "score":
                finding.get("score")

        })

    # --------------------------------------------------------
    # DERMIQ FINDINGS
    # --------------------------------------------------------

    dermaiq_findings = normalize_dermiq_findings(
        dermaiq_result
    )

    for finding in dermaiq_findings:

        combined.append({

            "source": "DermIQ",

            "condition_id":
                finding.get("condition_id"),

            "condition_name":
                finding.get("condition_name"),

            "score":
                finding.get("score"),

            "raw_score":
                finding.get("raw_score"),

            "region":
                finding.get("region"),

            "reliability":
                finding.get("reliability")

        })

    return combined


# ============================================================
# RUN SKIN ANALYSIS AGENT
# ============================================================

def run_skin_agent(image_path, user_concern):

    print("\n")
    print("=" * 60)
    print("COSMORA SKIN ANALYSIS AGENT")
    print("=" * 60)

    # ========================================================
    # 1. RUPAM
    # ========================================================

    print("\nRunning Rupam.ai...")

    try:

        rupam_result = analyze_with_rupam(
            image_path
        )

    except Exception as e:

        rupam_result = {
            "tool": "Rupam",
            "success": False,
            "error": str(e)
        }

    print(
        "Rupam success:",
        rupam_result.get("success")
    )

    # ========================================================
    # 2. DERMIQ
    # ========================================================

    print("\nRunning DermIQ...")

    try:

        dermaiq_result = analyze_with_dermaiq(
            image_path
        )

    except Exception as e:

        dermaiq_result = {
            "tool": "DermIQ",
            "success": False,
            "error": str(e)
        }

    print(
        "DermIQ success:",
        dermaiq_result.get("success")
    )

    # ========================================================
    # 3. COLLECT RESULTS
    # ========================================================

    tool_results = [

        rupam_result,

        dermaiq_result

    ]

    # ========================================================
    # 4. COMBINE FINDINGS
    # ========================================================

    combined_findings = build_combined_findings(
        rupam_result,
        dermaiq_result
    )

    # ========================================================
    # 5. OVERALL SCORES
    # ========================================================

    scores = []

    for result in tool_results:

        if result.get("success"):

            score = result.get(
                "overall_skin_score"
            )

            if isinstance(score, (int, float)):

                scores.append(score)

    if scores:

        combined_score = round(
            sum(scores) / len(scores),
            2
        )

    else:

        combined_score = None

    # ========================================================
    # 6. PREPARE DATA FOR RAG + LLM
    # ========================================================

    agent_context = {

        "user_concern":
            user_concern,

        "overall_skin_score":
            combined_score,

        "tool_results":
            tool_results,

        "combined_findings":
            combined_findings

    }

    # Convert to JSON-safe structure
    agent_context_json = json.dumps(
        agent_context,
        indent=2,
        default=str
    )

    # ========================================================
    # 7. SEND RESULTS TO SKIN RAG + LLM
    # ========================================================

    print("\n")
    print("=" * 60)
    print("SENDING ANALYSIS RESULTS TO SKIN RAG + LLM")
    print("=" * 60)

    try:

        final_guidance = skin_analysis_rag(
            tool_results=tool_results,
            user_concern=user_concern
        )

        print("\nSkin RAG + LLM completed successfully.")

    except Exception as e:

        print(
            "\nSkin RAG + LLM error:",
            e
        )

        final_guidance = (
            "Unable to generate personalized "
            "skincare guidance."
        )

    # ========================================================
    # 8. RETURN COMPLETE RESULT TO FLASK
    # ========================================================

        # ========================================================
    # 8. RETURN COMPLETE RESULT TO FLASK
    # ========================================================

    return {

        "success":
            any(
                result.get("success")
                for result in tool_results
            ),

        "tool_results":
            tool_results,

        "combined_findings":
            combined_findings,

        "overall_skin_score":
            combined_score,

        "final_guidance":
            final_guidance,

        "final_assessment":
            final_guidance,

        "agent_context":
            agent_context_json
    }