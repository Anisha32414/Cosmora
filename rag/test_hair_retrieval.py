from rag.vectorstore import get_hair_vectorstore


vectorstore = get_hair_vectorstore()

query = """
hair fall, dry scalp, frequent shampooing, pollution exposure,
heat styling, low hydration, poor sleep and moderate stress
"""

documents = vectorstore.similarity_search(query, k=5)

print("\n")
print("=" * 60)
print("HAIR RETRIEVAL TEST")
print("=" * 60)

print(f"\nDocuments retrieved: {len(documents)}\n")

for i, document in enumerate(documents, start=1):

    print(f"\n--- Document {i} ---")
    print(document.page_content[:1000])