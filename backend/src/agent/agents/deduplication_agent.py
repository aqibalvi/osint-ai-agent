# src/agent/agents/deduplication_agent.py

from sentence_transformers import SentenceTransformer, util

model = SentenceTransformer("all-MiniLM-L6-v2")

def deduplication_agent(retrievals: dict, similarity_threshold: float = 0.85) -> dict:
    tasks = list(retrievals.keys())
    texts = [retrievals[t]["data"] for t in tasks]

    embeddings = model.encode(texts, convert_to_tensor=True)
    similarity_matrix = util.pytorch_cos_sim(embeddings, embeddings)

    keep = set()
    remove = set()

    for i in range(len(tasks)):
        if tasks[i] in remove:
            continue
        keep.add(tasks[i])
        for j in range(i + 1, len(tasks)):
            if similarity_matrix[i][j] > similarity_threshold:
                remove.add(tasks[j])

    # Filter retrievals
    filtered = {k: v for k, v in retrievals.items() if k in keep}
    return filtered
