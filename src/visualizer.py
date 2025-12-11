from typing import Dict, List, Tuple
import os
import networkx as nx
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches

COLORS = {
    'proposal': '#1f77b4',
    'accepted': '#2ca02c',
    'rejected': '#d62728',
}


def visualize_iteration(students: Dict[int, any], projects: Dict[str, any], graph_state: Dict[str, List[Tuple[int, str]]], iteration_index: int, out_path: str) -> None:
    """Renderiza grafo bipartido para uma iteração."""
    active_students = set()
    active_projects = set()
    
    for sid, proj_code in graph_state.get('proposals', []):
        active_students.add(sid)
        active_projects.add(proj_code)
    for sid, proj_code in graph_state.get('accepted', []):
        active_students.add(sid)
        active_projects.add(proj_code)
    for sid, proj_code in graph_state.get('rejected', []):
        active_students.add(sid)
        active_projects.add(proj_code)
    
    if not active_students and not active_projects:
        fig, ax = plt.subplots(figsize=(10, 6))
        ax.text(0.5, 0.5, f'Iteração {iteration_index}\n\nNenhuma proposta nesta iteração\n(Algoritmo convergiu)', 
                ha='center', va='center', fontsize=14, transform=ax.transAxes)
        ax.set_xlim(0, 1)
        ax.set_ylim(0, 1)
        ax.axis('off')
        os.makedirs(os.path.dirname(out_path), exist_ok=True)
        plt.savefig(out_path, dpi=150, bbox_inches='tight')
        plt.close()
        return
    
    G = nx.Graph()
    student_nodes = sorted([f"A{sid}" for sid in active_students])
    project_nodes = sorted([f"{proj_code}" for proj_code in active_projects])
    
    G.add_nodes_from(student_nodes, bipartite=0)
    G.add_nodes_from(project_nodes, bipartite=1)

    edge_colors = []
    edge_list = []
    
    for sid, proj_code in graph_state.get('rejected', []):
        edge = (f"A{sid}", f"{proj_code}")
        if edge not in edge_list:
            G.add_edge(*edge)
            edge_list.append(edge)
            edge_colors.append(COLORS['rejected'])
    
    for sid, proj_code in graph_state.get('proposals', []):
        edge = (f"A{sid}", f"{proj_code}")
        if edge not in edge_list:
            G.add_edge(*edge)
            edge_list.append(edge)
            edge_colors.append(COLORS['proposal'])
    
    for sid, proj_code in graph_state.get('accepted', []):
        edge = (f"A{sid}", f"{proj_code}")
        if edge not in edge_list:
            G.add_edge(*edge)
            edge_list.append(edge)
            edge_colors.append(COLORS['accepted'])

    n_students = len(student_nodes)
    n_projects = len(project_nodes)
    height = max(n_students, n_projects) * 0.5
    fig_height = max(8, min(height, 20))
    
    pos = {}
    for i, node in enumerate(student_nodes):
        pos[node] = (0, i * (height / max(n_students, 1)))
    for j, node in enumerate(project_nodes):
        pos[node] = (4, j * (height / max(n_projects, 1)))

    fig, ax = plt.subplots(figsize=(12, fig_height))
    
    nx.draw_networkx_nodes(G, pos, nodelist=student_nodes, 
                           node_color='lightblue', node_size=800, 
                           node_shape='o', ax=ax)
    nx.draw_networkx_nodes(G, pos, nodelist=project_nodes, 
                           node_color='lightgreen', node_size=800, 
                           node_shape='s', ax=ax)
    
    if edge_list:
        nx.draw_networkx_edges(G, pos, edgelist=edge_list, 
                               edge_color=edge_colors, width=2, alpha=0.7, ax=ax)
    
    nx.draw_networkx_labels(G, pos, font_size=8, font_weight='bold', ax=ax)
    
    ax.set_title(f"Iteração {iteration_index}\n"
                 f"({len(graph_state.get('proposals', []))} propostas, "
                 f"{len(graph_state.get('accepted', []))} aceitos, "
                 f"{len(graph_state.get('rejected', []))} rejeitados)", 
                 fontsize=12, fontweight='bold')
    
    legend_patches = [
        mpatches.Patch(color=COLORS['proposal'], label='Proposta ativa'),
        mpatches.Patch(color=COLORS['accepted'], label='Emparelhamento temporário'),
        mpatches.Patch(color=COLORS['rejected'], label='Rejeição'),
        mpatches.Patch(color='lightblue', label='Aluno'),
        mpatches.Patch(color='lightgreen', label='Projeto'),
    ]
    ax.legend(handles=legend_patches, loc='upper right', fontsize=8)
    
    ax.axis('off')
    ax.margins(0.1)
    
    os.makedirs(os.path.dirname(out_path), exist_ok=True)
    plt.savefig(out_path, dpi=150, bbox_inches='tight')
    plt.close()
