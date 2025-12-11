from typing import Dict, List, Tuple, Set, Optional
from .utils import build_project_prefs, rank_in_project, rank_in_student


def run_gale_shapley(students: Dict[int, any], projects: Dict[str, any], max_iter: int = 1000, log_iter: int = 10, fixed_iterations: int = 10) -> Tuple[Dict[int, Optional[str]], Dict[int, Dict[str, List[Tuple[int, str]]]]]:
    """Gale-Shapley com proposta dos alunos para projetos multi-capacidade."""
    for student in students.values():
        student.next_proposal_index = 0
    for proj in projects.values():
        proj.current_alloc = []
    
    build_project_prefs(projects, students)
    held_by: Dict[int, Optional[str]] = {s.id: None for s in students.values()}
    logs: Dict[int, Dict[str, List[Tuple[int, str]]]] = {}

    for iteration in range(1, fixed_iterations + 1):
        proposals: List[Tuple[int, str]] = []
        accepted: List[Tuple[int, str]] = []
        rejected: List[Tuple[int, str]] = []

        free_students = [
            s for s in students.values() 
            if held_by[s.id] is None and s.next_proposal_index < len(s.prefs)
        ]
            
        for student in sorted(free_students, key=lambda s: s.id):
            target_proj_code = student.prefs[student.next_proposal_index]
            student.next_proposal_index += 1
            proposals.append((student.id, target_proj_code))

            proj = projects[target_proj_code]
            
            if student.score < proj.min_req:
                rejected.append((student.id, target_proj_code))
                continue
            
            proj.current_alloc.append(student.id)
            held_by[student.id] = target_proj_code
            
            while len(proj.current_alloc) > proj.vacancies:
                worst_sid = max(proj.current_alloc, key=lambda sid: rank_in_project(proj, sid))
                proj.current_alloc.remove(worst_sid)
                held_by[worst_sid] = None
                rejected.append((worst_sid, proj.code))

        for proj in projects.values():
            for sid in proj.current_alloc:
                accepted.append((sid, proj.code))

        logs[iteration] = {
            'proposals': proposals,
            'accepted': accepted,  # Current temporary matchings
            'rejected': rejected,
        }

    # Continuar até convergência
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
