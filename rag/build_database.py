from vectorstore import (
    create_skin_vectorstore,
    create_hair_vectorstore
)


def main():

    print("\nBuilding Skin Care knowledge base...")
    create_skin_vectorstore()
    print("Skin Care knowledge base created successfully.")

    print("\nBuilding Hair Care knowledge base...")
    create_hair_vectorstore()
    print("Hair Care knowledge base created successfully.")

    print("\nAll knowledge bases are ready.")


if __name__ == "__main__":
    main()