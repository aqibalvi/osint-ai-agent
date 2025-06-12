# src/agent/agents/graph_builder_agent.py

import spacy
import networkx as nx
from typing import Dict

nlp = spacy.load("en_core_web_sm")

def graph_builder_agent(retrievals: Dict[str, Dict]) -> Dict:
    G = nx.Graph()

    for task, result in retrievals.items():
        text = result.get("data", "")
        score = result.get("decayed_score", 0.0)
        doc = nlp(text)

        entities = [ent.text for ent in doc.ents if ent.label_ in ["PERSON", "ORG", "GPE"]]
        unique_entities = list(set(entities))

        # Create nodes
        for ent in unique_entities:
            G.add_node(ent, label="entity")

        # Create weighted edges
        for i in range(len(unique_entities)):
            for j in range(i+1, len(unique_entities)):
                e1, e2 = unique_entities[i], unique_entities[j]
                if G.has_edge(e1, e2):
                    G[e1][e2]['weight'] += score
                else:
                    G.add_edge(e1, e2, weight=score, task=task)

    # Return graph as dict (for frontend use or persistence)
    graph_data = {
        "nodes": [{"id": n, **G.nodes[n]} for n in G.nodes()],
        "edges": [{"source": u, "target": v, **G[u][v]} for u, v in G.edges()]
    }
    return graph_data
