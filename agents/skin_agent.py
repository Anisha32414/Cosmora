import json
import re

from tools.rupam import analyze_with_rupam
from tools.dermaiq import analyze_with_dermaiq
from rag.skin_rag import skin_analysis_rag


# ============================================================
# DERMIQ FINDING NAME NORMALIZATION
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


# ============================================================
# NORMALIZE DERMIQ FINDINGS
# ============================================================

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

    # ========================================================
    # RUPAM FINDINGS
    # ========================================================

    if rupam_result.get("success"):

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

    # ========================================================
    # DERMIQ FINDINGS
    # ========================================================

    if dermaiq_result.get("success"):

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
# FIND COMMON CONCERNS
# ============================================================

def find_common_concerns(combined_findings):

    concern_sources = {}

    for finding in combined_findings:

        condition = (
            finding.get("condition_name")
            or finding.get("condition_id")
        )

        if not condition:
            continue

        condition = str(condition).lower().strip()

        if condition not in concern_sources:

            concern_sources[condition] = set()

        concern_sources[condition].add(
            finding.get("source")
        )

    common_concerns = []

    for condition, sources in concern_sources.items():

        if "Rupam" in sources and "DermIQ" in sources:

            common_concerns.append({

                "concern": condition,

                "detected_by": [
                    "Rupam",
                    "DermIQ"
                ],

                "tool_count": 2

            })

    return common_concerns


# ============================================================
# BUILD FINDING SUMMARY
# ============================================================

def build_finding_summary(combined_findings):

    summary = {}

    for finding in combined_findings:

        condition = (
            finding.get("condition_name")
            or finding.get("condition_id")
        )

        if not condition:
            continue

        condition = str(condition).lower().strip()

        if condition not in summary:

            summary[condition] = {

                "concern": condition,

                "sources": [],

                "scores": [],

                "regions": []

            }

        source = finding.get("source")

        if source and source not in summary[condition]["sources"]:

            summary[condition]["sources"].append(
                source
            )

        score = finding.get("score")

        if isinstance(score, (int, float)):

            summary[condition]["scores"].append(
                score
            )

        region = finding.get("region")

        if region and region not in summary[condition]["regions"]:

            summary[condition]["regions"].append(
                region
            )

    # ========================================================
    # CALCULATE SUMMARY VALUES
    # ========================================================

    result = []

    for condition, data in summary.items():

        scores = data["scores"]

        if scores:

            average_score = round(
                sum(scores) / len(scores),
                2
            )

        else:

            average_score = None

        result.append({

            "concern":
                data["concern"],

            "sources":
                data["sources"],

            "tool_count":
                len(data["sources"]),

            "scores":
                scores,

            "average_score":
                average_score,

            "regions":
                data["regions"],

            "agreement":
                len(data["sources"]) >= 2

        })

    # Sort strongest concerns first

    result.sort(

        key=lambda x:
            x["average_score"]
            if isinstance(
                x["average_score"],
                (int, float)
            )
            else 0,

        reverse=True

    )

    return result


# ============================================================
# CALCULATE OVERALL SKIN SCORE
# ============================================================

def calculate_combined_score(tool_results):

    scores = []

    for result in tool_results:

        if not result.get("success"):

            continue

        score = result.get(
            "overall_skin_score"
        )

        if isinstance(score, (int, float)):

            scores.append(score)

    if not scores:

        return None

    return round(
        sum(scores) / len(scores),
        2
    )


# ============================================================
# PARSE STRUCTURED RAG RESPONSE
# ============================================================

def parse_rag_response(response):

    if not response:

        return {

            "summary": "",

            "key_concerns": [],

            "contributing_factors": [],

            "lifestyle_plan": [],

            "morning_routine": [],

            "evening_routine": [],

            "weekly_routine": [],

            "avoid": [],

            "dermatologist": []

        }

    text = str(response).strip()

    # --------------------------------------------------------
    # Normalize markdown headings
    # --------------------------------------------------------

    text = text.replace("\r\n", "\n")

    # --------------------------------------------------------
    # Find sections
    # --------------------------------------------------------

    section_patterns = {

        "summary":
            r"(?:1\.\s*)?(?:SKIN ANALYSIS SUMMARY)(.*?)(?=(?:2\.\s*)?KEY SKIN CONCERNS)",

        "key_concerns":
            r"(?:2\.\s*)?(?:KEY SKIN CONCERNS)(.*?)(?=(?:3\.\s*)?POSSIBLE CONTRIBUTING FACTORS)",

        "contributing_factors":
            r"(?:3\.\s*)?(?:POSSIBLE CONTRIBUTING FACTORS)(.*?)(?=(?:4\.\s*)?NATURAL SKINCARE & LIFESTYLE PLAN)",

        "lifestyle_plan":
            r"(?:4\.\s*)?(?:NATURAL SKINCARE & LIFESTYLE PLAN)(.*?)(?=(?:5\.\s*)?DAILY ROUTINE)",

        "daily_routine":
            r"(?:5\.\s*)?(?:DAILY ROUTINE)(.*?)(?=(?:6\.\s*)?WHAT TO AVOID)",

        "avoid":
            r"(?:6\.\s*)?(?:WHAT TO AVOID)(.*?)(?=(?:7\.\s*)?WHEN TO SEE A DERMATOLOGIST)",

        "dermatologist":
            r"(?:7\.\s*)?(?:WHEN TO SEE A DERMATOLOGIST)(.*?)(?=(?:DISCLAIMER|$))"

    }

    sections = {}

    for key, pattern in section_patterns.items():

        match = re.search(
            pattern,
            text,
            flags=re.IGNORECASE | re.DOTALL
        )

        if match:

            sections[key] = match.group(1).strip()

        else:

            sections[key] = ""

    # ========================================================
    # SUMMARY
    # ========================================================

    summary = clean_text(
        sections.get("summary", "")
    )

    # ========================================================
    # LIST SECTIONS
    # ========================================================

    key_concerns = extract_bullets(
        sections.get("key_concerns", "")
    )

    contributing_factors = extract_bullets(
        sections.get("contributing_factors", "")
    )

    lifestyle_plan = extract_bullets(
        sections.get("lifestyle_plan", "")
    )

    avoid = extract_bullets(
        sections.get("avoid", "")
    )

    dermatologist = extract_bullets(
        sections.get("dermatologist", "")
    )

    # ========================================================
    # DAILY ROUTINE
    # ========================================================

    daily_routine = sections.get(
        "daily_routine",
        ""
    )

    morning_routine = extract_subsection(
        daily_routine,
        "MORNING"
    )

    evening_routine = extract_subsection(
        daily_routine,
        "EVENING"
    )

    weekly_routine = extract_subsection(
        daily_routine,
        "WEEKLY"
    )

    return {

        "summary":
            summary,

        "key_concerns":
            key_concerns,

        "contributing_factors":
            contributing_factors,

        "lifestyle_plan":
            lifestyle_plan,

        "morning_routine":
            morning_routine,

        "evening_routine":
            evening_routine,

        "weekly_routine":
            weekly_routine,

        "avoid":
            avoid,

        "dermatologist":
            dermatologist

    }


# ============================================================
# CLEAN TEXT
# ============================================================

def clean_text(text):

    if not text:

        return ""

    text = re.sub(
        r"\*\*(.*?)\*\*",
        r"\1",
        text
    )

    text = re.sub(
        r"#+\s*",
        "",
        text
    )

    return text.strip()


# ============================================================
# EXTRACT BULLETS
# ============================================================

def extract_bullets(text):

    if not text:

        return []

    lines = text.split("\n")

    bullets = []

    for line in lines:

        line = line.strip()

        if not line:

            continue

        # Remove markdown bullets / numbering

        line = re.sub(
            r"^[-*•]\s*",
            "",
            line
        )

        line = re.sub(
            r"^\d+[\.\)]\s*",
            "",
            line
        )

        line = clean_text(line)

        if line:

            bullets.append(line)

    return bullets


# ============================================================
# EXTRACT ROUTINE SUBSECTION
# ============================================================

def extract_subsection(text, heading):

    if not text:

        return []

    pattern = (
        rf"{heading}"
        r"\s*:?"
        r"(.*?)"
        r"(?=(?:MORNING|EVENING|WEEKLY)\s*:|$)"
    )

    match = re.search(
        pattern,
        text,
        flags=re.IGNORECASE | re.DOTALL
    )

    if not match:

        return []

    return extract_bullets(
        match.group(1)
    )


# ============================================================
# RUN SKIN ANALYSIS AGENT
# ============================================================

def run_skin_agent(image_path, user_concern):

    print("\n")
    print("=" * 60)
    print("COSMORA SKIN ANALYSIS AGENT")
    print("=" * 60)

    # ========================================================
    # 1. RUPAM.AI
    # ========================================================

    print("\nRunning Rupam.ai...")

    try:

        rupam_result = analyze_with_rupam(
            image_path
        )

    except Exception as e:

        rupam_result = {

            "tool": "Rupam.ai",

            "success": False,

            "error": str(e),

            "findings": []

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

            "error": str(e),

            "findings": []

        }

    print(
        "DermIQ success:",
        dermaiq_result.get("success")
    )

    # ========================================================
    # 3. COLLECT TOOL RESULTS
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
    # 5. FIND COMMON CONCERNS
    # ========================================================

    common_concerns = find_common_concerns(

        combined_findings

    )

    # ========================================================
    # 6. BUILD FINDING SUMMARY
    # ========================================================

    finding_summary = build_finding_summary(

        combined_findings

    )

    # ========================================================
    # 7. CALCULATE COMBINED SCORE
    # ========================================================

    combined_score = calculate_combined_score(

        tool_results

    )

    print(
        "\nCombined Skin Score:",
        combined_score
    )

    print(
        "Common Concerns:",
        len(common_concerns)
    )

    # ========================================================
    # 8. PREPARE AGENT CONTEXT
    # ========================================================

    agent_context = {

        "user_concern":
            user_concern,

        "overall_skin_score":
            combined_score,

        "tool_results":
            tool_results,

        "combined_findings":
            combined_findings,

        "common_concerns":
            common_concerns,

        "finding_summary":
            finding_summary

    }

    agent_context_json = json.dumps(

        agent_context,

        indent=2,

        default=str

    )

    # ========================================================
    # 9. SEND RESULTS TO RAG + LLM
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

        print(
            "\nSkin RAG + LLM completed successfully."
        )

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
    # 10. PARSE RAG + LLM RESPONSE
    # ========================================================

    rag_sections = parse_rag_response(
        final_guidance
    )

    # ========================================================
    # 11. BUILD FRONTEND-FRIENDLY RESULT
    # ========================================================

    dashboard_data = {

        # ----------------------------------------------------
        # USER
        # ----------------------------------------------------

        "user_concern":
            user_concern,

        # ----------------------------------------------------
        # OVERALL SCORE
        # ----------------------------------------------------

        "overall_skin_score":
            combined_score,

        # ----------------------------------------------------
        # INDIVIDUAL TOOLS
        # ----------------------------------------------------

        "rupam":
            rupam_result,

        "dermaiq":
            dermaiq_result,

        # ----------------------------------------------------
        # COMBINED ANALYSIS
        # ----------------------------------------------------

        "combined_findings":
            combined_findings,

        "common_concerns":
            common_concerns,

        "finding_summary":
            finding_summary,

        # ----------------------------------------------------
        # RAG + LLM
        # ----------------------------------------------------

        "rag_guidance":
            final_guidance,

        "rag_sections":
            rag_sections

    }

    # ========================================================
    # 12. PRINT FINAL GUIDANCE
    # ========================================================

    print("\n")
    print("=" * 60)
    print("LLM RESPONSE RECEIVED")
    print("=" * 60)

    print(final_guidance)

    print("=" * 60)

    # ========================================================
    # 13. RETURN COMPLETE RESULT TO FLASK
    # ========================================================

    return {

        "success":
            any(
                result.get("success")
                for result in tool_results
            ),

        # ----------------------------------------------------
        # INDIVIDUAL TOOL RESULTS
        # ----------------------------------------------------

        "tool_results":
            tool_results,

        "rupam":
            rupam_result,

        "dermaiq":
            dermaiq_result,

        # ----------------------------------------------------
        # COMBINED RESULTS
        # ----------------------------------------------------

        "combined_findings":
            combined_findings,

        "common_concerns":
            common_concerns,

        "finding_summary":
            finding_summary,

        "overall_skin_score":
            combined_score,

        # ----------------------------------------------------
        # RAG + LLM
        # ----------------------------------------------------

        "final_guidance":
            final_guidance,

        "final_assessment":
            final_guidance,

        "rag_guidance":
            final_guidance,

        "rag_sections":
            rag_sections,

        # ----------------------------------------------------
        # COMPLETE CONTEXT
        # ----------------------------------------------------

        "dashboard_data":
            dashboard_data,

        "agent_context":
            agent_context_json

    }