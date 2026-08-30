from agents.skin_agent import run_skin_agent


# ============================================================
# TEST IMAGE
# ============================================================

IMAGE_PATH = "test.jpg"

USER_CONCERN = "I want to understand my skin condition and improve my skincare routine."


# ============================================================
# RUN TEST
# ============================================================

print("\n")
print("=" * 60)
print("COSMORA SKIN AGENT TEST")
print("=" * 60)


result = run_skin_agent(
    IMAGE_PATH,
    USER_CONCERN
)


# ============================================================
# AGENT RESULT
# ============================================================

print("\n")
print("=" * 60)
print("SKIN AGENT RESULT")
print("=" * 60)

print("\nSuccess:")
print(result.get("success"))

print("\nFinal Guidance:")
print(result.get("final_guidance"))


# ============================================================
# TOOL SUMMARY
# ============================================================

print("\n")
print("=" * 60)
print("TOOL RESULTS SUMMARY")
print("=" * 60)


for tool in result.get("tool_results", []):

    print("\nTool:", tool.get("tool"))

    print(
        "Success:",
        tool.get("success")
    )

    print(
        "Overall Skin Score:",
        tool.get("overall_skin_score")
    )

    findings = tool.get(
        "findings",
        []
    )

    print(
        "Number of Findings:",
        len(findings)
    )


# ============================================================
# COMBINED FINDINGS
# ============================================================

print("\n")
print("=" * 60)
print("COMBINED FINDINGS")
print("=" * 60)


combined_findings = result.get(
    "combined_findings",
    []
)


for finding in combined_findings:

    source = finding.get(
        "source",
        "Unknown"
    )

    condition = finding.get(
        "condition_name",
        finding.get(
            "condition_id",
            "Unknown"
        )
    )

    score = finding.get(
        "score"
    )

    reliability = finding.get(
        "reliability"
    )

    print(
        f"- [{source}] "
        f"{condition}: "
        f"score={score}"
        + (
            f", reliability={reliability}"
            if reliability
            else ""
        )
    )


# ============================================================
# OVERALL SCORE
# ============================================================

print("\n")
print("=" * 60)
print("COMBINED SKIN SCORE")
print("=" * 60)

print(
    result.get(
        "overall_skin_score"
    )
)


print("\n")
print("=" * 60)
print("SKIN AGENT TEST COMPLETED")
print("=" * 60)