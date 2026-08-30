from rag.skin_rag import skin_rag


user_profile = {
    "skin_concern": "dry skin",
    "face_washing": "2 times a day",
    "diet": "mostly vegetarian",
    "sunscreen": "rarely",
    "cosmetics": "occasionally",
    "water_intake": "low",
    "sun_exposure": "high",
    "sleep": "6 hours",
    "stress": "moderate"
}


response = skin_rag(user_profile)

print("\n")
print("=" * 60)
print("COSMORA SKIN CARE RESPONSE")
print("=" * 60)
print("\n")
print(response)