from typing import Dict, List, Tuple, Set, Optional
from .utils import build_project_prefs, rank_in_project, rank_in_student


def run_gale_shapley(students: Dict[int, any], projects: Dict[str, any], max_iter: int = 1000, log_iter: int = 10, fixed_iterations: int = 10) -> Tuple[Dict[int, Optional[str]], Dict[int, Dict[str, List[Tuple[int, str]]]]]:
    """
    Student-proposing GS adapted for multi-capacity projects (Hospital-Residents variant).
    
    Conforme especificação:
    - Executa exatamente `fixed_iterations` iterações para visualização
    - Em cada iteração, alunos livres propõem ao próximo projeto da sua lista
    - Projetos mantêm os melhores alunos até sua capacidade
    - Alunos rejeitados ficam livres e propõem na próxima iteração
    
    Args:
        students: Dicionário de alunos
        projects: Dicionário de projetos
        max_iter: Máximo de iterações internas do algoritmo
        log_iter: Quantas iterações registrar no log
        fixed_iterations: Número fixo de iterações para visualização (padrão: 10)
    """
    # Reset state from any previous runs
    for student in students.values():
        student.next_proposal_index = 0
    for proj in projects.values():
        proj.current_alloc = []
    
    build_project_prefs(projects, students)

    # Track which students are currently held by which project
    # None means the student is free (not held by any project)
    held_by: Dict[int, Optional[str]] = {s.id: None for s in students.values()}
    
    logs: Dict[int, Dict[str, List[Tuple[int, str]]]] = {}

    # Execute exactly fixed_iterations iterations for visualization purposes
    for iteration in range(1, fixed_iterations + 1):
        proposals: List[Tuple[int, str]] = []
        accepted: List[Tuple[int, str]] = []
        rejected: List[Tuple[int, str]] = []

        # Find all free students who still have preferences to propose to
        free_students = [
            s for s in students.values() 
            if held_by[s.id] is None and s.next_proposal_index < len(s.prefs)
        ]
            
        # Each free student proposes to their next choice
        for student in sorted(free_students, key=lambda s: s.id):
            target_proj_code = student.prefs[student.next_proposal_index]
            student.next_proposal_index += 1
            proposals.append((student.id, target_proj_code))

            proj = projects[target_proj_code]
            
            # Check if student meets minimum requirements
            if student.score < proj.min_req:
                # Student doesn't qualify, they remain free
                rejected.append((student.id, target_proj_code))
                continue
            
            # Tentatively accept this student
            proj.current_alloc.append(student.id)
            held_by[student.id] = target_proj_code
            
            # If over capacity, reject the worst student according to project prefs
            while len(proj.current_alloc) > proj.vacancies:
                # Find the worst student (highest rank = least preferred)
                worst_sid = max(proj.current_alloc, key=lambda sid: rank_in_project(proj, sid))
                proj.current_alloc.remove(worst_sid)
                held_by[worst_sid] = None  # This student is now free again
                rejected.append((worst_sid, proj.code))

        # Record accepted students (those currently held after this iteration)
        # "accepted" = all current temporary matchings
        for proj in projects.values():
            for sid in proj.current_alloc:
                accepted.append((sid, proj.code))

        # Log this iteration
        logs[iteration] = {
            'proposals': proposals,
            'accepted': accepted,  # Current temporary matchings
            'rejected': rejected,
        }

    # Continue algorithm until convergence (beyond the 10 visualization iterations)
    iteration = fixed_iterations
    changed = True
    while iteration < max_iter and changed:
        iteration += 1
        changed = False

        free_students = [
            s for s in students.values() 
            if held_by[s.id] is None and s.next_proposal_index < len(s.prefs)
        ]
        
        if not free_students:
            break
            
        for student in sorted(free_students, key=lambda s: s.id):
            target_proj_code = student.prefs[student.next_proposal_index]
            student.next_proposal_index += 1
            changed = True

            proj = projects[target_proj_code]
            
            if student.score < proj.min_req:
                continue
            
            proj.current_alloc.append(student.id)
            held_by[student.id] = target_proj_code
            
            while len(proj.current_alloc) > proj.vacancies:
                worst_sid = max(proj.current_alloc, key=lambda sid: rank_in_project(proj, sid))
                proj.current_alloc.remove(worst_sid)
                held_by[worst_sid] = None

    # Build final matching from held_by
    matching: Dict[int, Optional[str]] = {sid: proj_code for sid, proj_code in held_by.items()}

    return matching, logs
