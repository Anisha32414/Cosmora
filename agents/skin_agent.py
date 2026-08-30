import json

from tools.rupam import analyze_with_rupam

# Import your other skin-analysis tools here
# Change these imports to match your actual filenames/functions.
#
# from tools.tool2 import analyze_with_tool2
# from tools.tool3 import analyze_with_tool3


# ============================================================
# RUN SKIN ANALYSIS AGENT
# ============================================================

def run_skin_agent(image_path, user_concern):

    print("\n")
    print("=" * 60)
    print("COSMORA SKIN ANALYSIS AGENT")
    print("=" * 60)


    # ========================================================
    # 1. RUN RUPAM
    # ========================================================

    print("\nRunning Rupam.ai...")

    rupam_result = analyze_with_rupam(
        image_path
    )

    print(
        "Rupam success:",
        rupam_result.get("success")
    )


    # ========================================================
    # 2. COLLECT TOOL RESULTS
    # ========================================================

    tool_results = [

        rupam_result

    ]


    # ========================================================
    # 3. DISPLAY TOOL RESULTS IN TERMINAL
    # ========================================================

    print("\n")
    print("=" * 60)
    print("INDIVIDUAL TOOL RESULTS")
    print("=" * 60)


    for tool in tool_results:

        print("\nTool:")
        print(
            tool.get(
                "tool",
                "Unknown Tool"
            )
        )

        print(
            "Success:",
            tool.get("success")
        )

        print(
            "Overall Score:",
            tool.get(
                "overall_skin_score"
            )
        )

        print("\nFindings:")

        for finding in tool.get(
            "findings",
            []
        ):

            print(
                f"  - "
                f"{finding.get('condition_name')}: "
                f"{finding.get('severity')} "
                f"(score={finding.get('score')})"
            )

        print("\nSuggestions:")

        for suggestion in tool.get(
            "suggestions",
            []
        ):

            print(
                f"  - "
                f"{suggestion.get('text')}"
            )


    # ========================================================
    # 4. PREPARE DATA FOR LLM
    # ========================================================

    tool_information = json.dumps(
        tool_results,
        indent=2
    )


    # ========================================================
    # 5. TEMPORARY FINAL ASSESSMENT
    # ========================================================
    #
    # For now we are NOT calling the LLM here.
    #
    # First we want to make sure that:
    #
    # Rupam
    #   ↓
    # Agent
    #   ↓
    # Frontend
    #
    # is working correctly.
    #
    # We will connect the Skin RAG + LLM after this test.
    # ========================================================

    final_assessment = (
        "Skin analysis completed successfully."
    )


    # ========================================================
    # 6. RETURN EVERYTHING TO FLASK
    # ========================================================

    return {

        "success": True,

        "tool_results":
            tool_results,

        "final_assessment":
            final_assessment

    }