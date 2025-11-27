from typing import Dict, List, Tuple
from .utils import build_project_prefs, rank_in_project, rank_in_student


def run_gale_shapley(students: Dict[int, any], projects: Dict[str, any], max_iter: int = 1000, log_iter: int = 10) -> Tuple[Dict[int, str], Dict[int, Dict[str, List[Tuple[int, str]]]]]:
    """
    Student-proposing GS adapted for multi-capacity projects.
    Each iteration: each free student proposes once to next project in prefs.
    Projects keep up to vacancies best according to project prefs and reject the worst when overfull.
    Logs store proposals, accepted (allocations), rejected per iteration.
    """
    build_project_prefs(projects, students)

    matching: Dict[int, str] = {s.id: None for s in students.values()}
    logs: Dict[int, Dict[str, List[Tuple[int, str]]]] = {}

    free_students = {s.id for s in students.values() if s.prefs}

    iteration = 0
    while iteration < max_iter and free_students:
        iteration += 1
        proposals: List[Tuple[int, str]] = []
        accepted: List[Tuple[int, str]] = []
        rejected: List[Tuple[int, str]] = []

        # Each free student proposes once per iteration
        to_remove = set()
        for sid in sorted(list(free_students)):
            student = students[sid]
            if student.next_proposal_index >= len(student.prefs):
                to_remove.add(sid)
                continue
            target_proj = student.prefs[student.next_proposal_index]
            student.next_proposal_index += 1
            proposals.append((sid, target_proj))

            proj = projects[target_proj]
            # Tentatively accept
            proj.current_alloc.append(sid)
            # If over capacity, reject the worst according to project prefs
            if len(proj.current_alloc) > proj.vacancies:
                worst = max(proj.current_alloc, key=lambda s: rank_in_project(proj, s))
                proj.current_alloc.remove(worst)
                rejected.append((worst, proj.code))
                # If the rejected student still has prefs left, they remain free
                if rank_in_student(students[worst], proj.code) < 10**9:
                    pass
            # Accepted those currently in alloc
            accepted.append((sid, proj.code))

        for sid, proj_code in accepted:
            # mark matched only if actually in current_alloc
            if sid in projects[proj_code].current_alloc:
                matching[sid] = proj_code
                if matching[sid] is not None:
                    # student considered tentatively matched; but may still propose in future if rejected
                    pass
        # Remove students with no remaining prefs from free set
        for sid in to_remove:
            if sid in free_students:
                free_students.remove(sid)
        # Mark students still unmatched and with remaining prefs as free
        free_students = {s.id for s in students.values() if (matching.get(s.id) is None and s.next_proposal_index < len(s.prefs))}

        if iteration <= log_iter:
            logs[iteration] = {
                'proposals': proposals,
                'accepted': accepted,
                'rejected': rejected,
            }

        # Early exit if no changes and all projects at capacity
        if not free_students:
            all_full_or_no_candidates = all(len(p.current_alloc) >= min(p.vacancies, len(p.pref_list)) for p in projects.values())
            if all_full_or_no_candidates:
                break

    # Final matching map
    for proj in projects.values():
        for sid in proj.current_alloc:
            matching[sid] = proj.code

    return matching, logs
