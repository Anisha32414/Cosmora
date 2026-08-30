from vectorstore import (
    get_skin_vectorstore,
    get_hair_vectorstore
)


def test_skin():

    print("\n--- SKIN RAG TEST ---")

    vectorstore = get_skin_vectorstore()

    results = vectorstore.similarity_search(
        "My skin is dry and I don't drink enough water",
        k=3
    )

    for i, document in enumerate(results, start=1):

        print(f"\nResult {i}")
        print(document.page_content[:500])


def test_hair():

    print("\n--- HAIR RAG TEST ---")

    vectorstore = get_hair_vectorstore()

    results = vectorstore.similarity_search(
        "I have hair fall and I don't get enough protein",
        k=3
    )

    for i, document in enumerate(results, start=1):

        print(f"\nResult {i}")
        print(document.page_content[:500])


if __name__ == "__main__":

    test_skin()
    test_hair()