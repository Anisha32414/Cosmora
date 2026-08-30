from tools.dermaiq import analyze_with_dermiq


# ============================================================
# TEST IMAGE
# ============================================================

IMAGE_PATH = "test.jpg"


print()
print("=" * 60)
print("DERMIQ AI TEST")
print("=" * 60)


# ============================================================
# RUN ANALYSIS
# ============================================================

result = analyze_with_dermiq(
    IMAGE_PATH
)


# ============================================================
# DISPLAY RESULT
# ============================================================

print()
print("=" * 60)
print("DERMIQ NORMALIZED RESULT")
print("=" * 60)


print()

print("Tool:")
print(
    result.get("tool")
)


print()

print("Success:")
print(
    result.get("success")
)


print()

print("Overall Skin Score:")
print(
    result.get(
        "overall_skin_score"
    )
)


print()

print("Skin Profile:")
print(
    result.get(
        "skin_profile"
    )
)


print()

print("Findings:")
print("-" * 60)


for finding in result.get(
    "findings",
    []
):

    print(

        f"{finding.get('condition_name')}: "

        f"region="
        f"{finding.get('region')}, "

        f"score="
        f"{finding.get('score')}, "

        f"raw_score="
        f"{finding.get('raw_score')}"

    )


print()

print("Suggestions:")
print("-" * 60)


for suggestion in result.get(
    "suggestions",
    []
):

    print(
        f"- {suggestion.get('text')}"
    )


print()


# ============================================================
# ERROR
# ============================================================

if result.get("error"):

    print("ERROR:")

    print(
        result.get("error")
    )


print(
    "=" * 60
)