
from tools.rupam import analyze_with_rupam


# ============================================================
# TEST IMAGE
# ============================================================

IMAGE_PATH = "test.jpg"


print()
print("=" * 60)
print("RUPAM AI TEST")
print("=" * 60)


# ============================================================
# RUN ANALYSIS
# ============================================================

result = analyze_with_rupam(
    IMAGE_PATH
)


# ============================================================
# DISPLAY RESULT
# ============================================================

print()
print("=" * 60)
print("RUPAM NORMALIZED RESULT")
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
    result.get("overall_skin_score")
)

print()

print("Skin Profile:")

print(
    result.get("skin_profile")
)

print()

print("Image Quality:")

print(
    result.get("image_quality")
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

        f"severity="
        f"{finding.get('severity')}, "

        f"score="
        f"{finding.get('score')}, "

        f"grade="
        f"{finding.get('grade')}, "

        f"confidence="
        f"{finding.get('confidence')}"

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

if result.get("error"):

    print("ERROR:")

    print(
        result.get("error")
    )


print("=" * 60)
