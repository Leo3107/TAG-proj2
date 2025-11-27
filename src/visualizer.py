from typing import Dict, List, Tuple
import os
import networkx as nx
import matplotlib.pyplot as plt

COLORS = {
    'proposal': '#1f77b4',  # blue
    'accepted': '#2ca02c',  # green
    'rejected': '#d62728',  # red
}


def visualize_iteration(students: Dict[int, any], projects: Dict[str, any], graph_state: Dict[str, List[Tuple[int, str]]], iteration_index: int, out_path: str) -> None:
    """Render bipartite graph for an iteration and save PNG."""
    G = nx.Graph()
    student_nodes = [f"A{sid}" for sid in students.keys()]
    project_nodes = [f"P{code}" for code in projects.keys()]
    G.add_nodes_from(student_nodes, bipartite=0)
    G.add_nodes_from(project_nodes, bipartite=1)

    # Add edges for proposals
    for sid, proj_code in graph_state.get('proposals', []):
        G.add_edge(f"A{sid}", f"P{proj_code}", color=COLORS['proposal'])
    for sid, proj_code in graph_state.get('accepted', []):
        G.add_edge(f"A{sid}", f"P{proj_code}", color=COLORS['accepted'])
    for sid, proj_code in graph_state.get('rejected', []):
        G.add_edge(f"A{sid}", f"P{proj_code}", color=COLORS['rejected'])

    pos = {}
    # Left side: students
    for i, sid in enumerate(sorted(students.keys())):
        pos[f"A{sid}"] = (0, i)
    # Right side: projects
    for j, code in enumerate(sorted(projects.keys())):
        pos[f"P{code}"] = (10, j)

    colors = [G[u][v]['color'] for u, v in G.edges()]
    plt.figure(figsize=(8, 6))
    nx.draw(G, pos, with_labels=True, node_size=500, edge_color=colors)
    plt.title(f"Iteração {iteration_index}")
    os.makedirs(os.path.dirname(out_path), exist_ok=True)
    plt.tight_layout()
    plt.savefig(out_path)
    plt.close()
