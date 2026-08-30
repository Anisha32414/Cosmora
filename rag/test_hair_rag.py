from rag.hair_rag import hair_rag


user_profile = {
    "hair_problems": "hair fall and dry scalp",

    "hair_washing": "3 times a week",

    "shampoo": "3 times a week",

    "conditioner": "sometimes",

    "oiling": "once a week",

    "pollution": "high",

    "hair_treatments": "none",

    "heat_styling": "2 times a week",

    "pillow_cover": "cotton",

    "diet": "mostly vegetarian",

    "hydration": "low",

    "sleep": "6 hours",

    "stress": "moderate"
}


response = hair_rag(user_profile)


print("\n")
print("=" * 60)
print("COSMORA HAIR CARE RESPONSE")
print("=" * 60)
print("\n")
print(response)