import json
import re
import sys
from pathlib import Path

# ============================================================
# PROJECT PATH
# ============================================================

PROJECT_ROOT = Path(__file__).resolve().parent.parent

if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))


# ============================================================
# COSMORA IMPORTS
# ============================================================

from rag.vectorstore import get_hair_vectorstore
from rag.hair_rag import hair_rag


# ============================================================
# CONFIG
# ============================================================

DATASET_PATH = (
    PROJECT_ROOT
    / "evaluation"
    / "datasets"
    / "hair_rag_eval.json"
)

TOP_K = 5


# ============================================================
# HELPERS
# ============================================================

def normalize(text):

    text = str(text).lower()

    text = re.sub(
        r"[^a-z0-9\s]",
        " ",
        text
    )

    text = re.sub(
        r"\s+",
        " ",
        text
    )

    return text.strip()


def document_text(doc):

    if hasattr(doc, "page_content"):
        return doc.page_content

    return str(doc)


def load_dataset():

    with open(
        DATASET_PATH,
        "r",
        encoding="utf-8"
    ) as f:

        return json.load(f)


# ============================================================
# QUERY
# ============================================================

def create_query(profile, question):

    parts = []

    for key, value in profile.items():

        if isinstance(value, list):
            value = ", ".join(
                map(str, value)
            )

        parts.append(
            f"{key}: {value}"
        )

    parts.append(
        f"question: {question}"
    )

    return " ".join(parts)


# ============================================================
# RETRIEVAL
# ============================================================

def retrieve_documents(
    vectorstore,
    query
):

    return vectorstore.similarity_search(
        query,
        k=TOP_K
    )


# ============================================================
# RETRIEVAL METRICS
# ============================================================

def retrieval_metrics(
    documents,
    expected_topics
):

    docs = [
        normalize(
            document_text(doc)
        )
        for doc in documents
    ]

    topics = [
        normalize(topic)
        for topic in expected_topics
    ]

    matched_topics = 0

    first_ranks = []

    for topic in topics:

        rank_found = None

        for rank, doc in enumerate(
            docs,
            start=1
        ):

            if topic in doc:

                rank_found = rank
                break

        if rank_found is not None:

            matched_topics += 1
            first_ranks.append(
                rank_found
            )

    recall = (
        matched_topics / len(topics)
        if topics
        else 0
    )

    relevant_docs = 0

    for doc in docs:

        if any(
            topic in doc
            for topic in topics
        ):

            relevant_docs += 1

    precision = (
        relevant_docs / len(docs)
        if docs
        else 0
    )

    hit_rate = (
        1.0
        if matched_topics > 0
        else 0.0
    )

    if first_ranks:

        mrr = 1 / min(first_ranks)

    else:

        mrr = 0.0

    return {

        "precision_at_5":
            precision,

        "recall_at_5":
            recall,

        "hit_rate_at_5":
            hit_rate,

        "mrr":
            mrr
    }


# ============================================================
# GENERATION METRICS
# ============================================================

def topic_coverage(
    answer,
    topics
):

    answer = normalize(answer)

    if not topics:
        return 0.0

    matched = 0

    for topic in topics:

        if normalize(topic) in answer:
            matched += 1

    return matched / len(topics)


def reference_overlap(
    answer,
    reference
):

    answer_words = set(
        normalize(answer).split()
    )

    reference_words = set(
        normalize(reference).split()
    )

    if not reference_words:
        return 0.0

    overlap = (
        answer_words &
        reference_words
    )

    return (
        len(overlap) /
        len(reference_words)
    )


def context_support(
    answer,
    documents
):

    context = normalize(
        " ".join(
            document_text(doc)
            for doc in documents
        )
    )

    sentences = re.split(
        r"[.!?]+",
        answer
    )

    sentences = [
        normalize(sentence)
        for sentence in sentences
        if len(sentence.strip()) > 10
    ]

    if not sentences:
        return 0.0

    supported = 0

    for sentence in sentences:

        words = sentence.split()

        if not words:
            continue

        matching = sum(
            1
            for word in words
            if word in context
        )

        ratio = (
            matching /
            len(words)
        )

        if ratio >= 0.30:
            supported += 1

    return (
        supported /
        len(sentences)
    )


# ============================================================
# HAIR RAG
# ============================================================

def generate_answer(profile):

    result = hair_rag(profile)

    if isinstance(result, str):
        return result

    if isinstance(result, dict):

        for key in [
            "answer",
            "response",
            "result"
        ]:

            if key in result:
                return str(
                    result[key]
                )

    return str(result)


# ============================================================
# MAIN
# ============================================================

def main():

    print("=" * 70)
    print("COSMORA - HAIR RAG EVALUATION")
    print("=" * 70)

    dataset = load_dataset()

    print(
        f"\nTest cases: {len(dataset)}"
    )

    print(
        f"Top-K: {TOP_K}"
    )

    print(
        "\nLoading Hair ChromaDB..."
    )

    vectorstore = get_hair_vectorstore()

    print(
        "Vectorstore loaded."
    )

    results = []

    for case_number, case in enumerate(
        dataset,
        start=1
    ):

        print(
            "\n" + "-" * 70
        )

        print(
            f"Case {case_number}/"
            f"{len(dataset)}"
        )

        profile = case["profile"]

        question = case["question"]

        topics = case["expected_topics"]

        reference = case["reference_answer"]

        # ----------------------------------------------------
        # Retrieval
        # ----------------------------------------------------

        query = create_query(
            profile,
            question
        )

        documents = retrieve_documents(
            vectorstore,
            query
        )

        retrieval = retrieval_metrics(
            documents,
            topics
        )

        # ----------------------------------------------------
        # Generation
        # ----------------------------------------------------

        print(
            "Generating answer..."
        )

        try:

            answer = generate_answer(
                profile
            )

        except Exception as e:

            print(
                f"Generation error: {e}"
            )

            answer = ""

        relevance = topic_coverage(
            answer,
            topics
        )

        correctness = reference_overlap(
            answer,
            reference
        )

        faithfulness = context_support(
            answer,
            documents
        )

        # ----------------------------------------------------
        # Store
        # ----------------------------------------------------

        result = {

            "id": case["id"],

            "retrieval": retrieval,

            "generation": {

                "answer_relevance":
                    relevance,

                "answer_correctness":
                    correctness,

                "context_support":
                    faithfulness
            },

            "answer": answer
        }

        results.append(result)

        # ----------------------------------------------------
        # Display
        # ----------------------------------------------------

        print(
            f"Precision@5 : "
            f"{retrieval['precision_at_5']:.3f}"
        )

        print(
            f"Recall@5    : "
            f"{retrieval['recall_at_5']:.3f}"
        )

        print(
            f"Hit Rate@5  : "
            f"{retrieval['hit_rate_at_5']:.3f}"
        )

        print(
            f"MRR         : "
            f"{retrieval['mrr']:.3f}"
        )

        print(
            f"Relevance   : "
            f"{relevance:.3f}"
        )

        print(
            f"Correctness : "
            f"{correctness:.3f}"
        )

        print(
            f"Faithfulness: "
            f"{faithfulness:.3f}"
        )

    # ========================================================
    # AVERAGES
    # ========================================================

    n = len(results)

    avg_precision = sum(
        r["retrieval"]["precision_at_5"]
        for r in results
    ) / n

    avg_recall = sum(
        r["retrieval"]["recall_at_5"]
        for r in results
    ) / n

    avg_hit_rate = sum(
        r["retrieval"]["hit_rate_at_5"]
        for r in results
    ) / n

    avg_mrr = sum(
        r["retrieval"]["mrr"]
        for r in results
    ) / n

    avg_relevance = sum(
        r["generation"]["answer_relevance"]
        for r in results
    ) / n

    avg_correctness = sum(
        r["generation"]["answer_correctness"]
        for r in results
    ) / n

    avg_faithfulness = sum(
        r["generation"]["context_support"]
        for r in results
    ) / n

    # ========================================================
    # FINAL RESULTS
    # ========================================================

    print("\n")

    print("=" * 70)
    print("FINAL HAIR RAG RESULTS")
    print("=" * 70)

    print("\nRETRIEVAL")

    print(
        f"Precision@5 : "
        f"{avg_precision:.3f}"
    )

    print(
        f"Recall@5    : "
        f"{avg_recall:.3f}"
    )

    print(
        f"Hit Rate@5  : "
        f"{avg_hit_rate:.3f}"
    )

    print(
        f"MRR         : "
        f"{avg_mrr:.3f}"
    )

    print("\nGENERATION")

    print(
        f"Answer Relevance : "
        f"{avg_relevance:.3f}"
    )

    print(
        f"Answer Correctness : "
        f"{avg_correctness:.3f}"
    )

    print(
        f"Context Support / Faithfulness : "
        f"{avg_faithfulness:.3f}"
    )

    # ========================================================
    # SAVE
    # ========================================================

    output_path = (
        PROJECT_ROOT
        / "evaluation"
        / "hair_rag_results.json"
    )

    output = {

        "test_cases": n,

        "top_k": TOP_K,

        "retrieval": {

            "precision_at_5":
                avg_precision,

            "recall_at_5":
                avg_recall,

            "hit_rate_at_5":
                avg_hit_rate,

            "mrr":
                avg_mrr
        },

        "generation": {

            "answer_relevance":
                avg_relevance,

            "answer_correctness":
                avg_correctness,

            "context_support":
                avg_faithfulness
        },

        "cases": results
    }

    with open(
        output_path,
        "w",
        encoding="utf-8"
    ) as f:

        json.dump(
            output,
            f,
            indent=4,
            ensure_ascii=False
        )

    print(
        f"\nDetailed results saved to:\n"
        f"{output_path}"
    )


if __name__ == "__main__":
    main()