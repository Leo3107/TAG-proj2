from typing import Dict, List, Tuple

# Helper rankings and metrics

def build_project_prefs(projects: Dict[str, any], students: Dict[int, any]) -> None:
    """For each project, compute preference list of eligible students by score desc, tie by id asc."""
    for proj in projects.values():
        eligible = [s for s in students.values() if s.score >= proj.min_req and proj.code in s.prefs]
        eligible.sort(key=lambda s: (-s.score, s.id))
        proj.pref_list = [s.id for s in eligible]


def rank_in_project(project: any, student_id: int) -> int:
    """Return 1-based rank of student in project's preference list, or large number if not present."""
    try:
        return project.pref_list.index(student_id) + 1
    except ValueError:
        return 10**9


def rank_in_student(student: any, project_code: str) -> int:
    """Return 1-based rank of project in student's preference list, or large number if not present."""
    try:
        return student.prefs.index(project_code) + 1
    except ValueError:
        return 10**9


def is_stable(matching: Dict[int, str], projects: Dict[str, any], students: Dict[int, any]) -> bool:
    """Check stability: no student-project pair prefers each other over current matching."""
    # For each student and each project they prefer over their current match
    for sid, student in students.items():
        current = matching.get(sid)
        for proj_code in student.prefs:
            if proj_code == current:
                break  # prefs are ordered; stop at current
            proj = projects.get(proj_code)
            if not proj:
                continue
            # Would the project prefer this student over its worst currently allocated?
            alloc = proj.current_alloc
            if len(alloc) < proj.vacancies:
                return False  # blocking pair (project has vacancy and student prefers it)
            worst = max(alloc, key=lambda s: rank_in_project(proj, s))
            if rank_in_project(proj, sid) < rank_in_project(proj, worst):
                return False
    return True


def student_satisfaction(matching: Dict[int, str], students: Dict[int, any]) -> Dict[str, float]:
    counts = {1:0, 2:0, 3:0, 'other':0}
    total = len(students)
    for sid, student in students.items():
        proj = matching.get(sid)
        r = rank_in_student(student, proj) if proj else 10**9
        if r in (1,2,3):
            counts[r] += 1
        else:
            counts['other'] += 1
    return {
        'choice1_pct': (counts[1]/total*100.0) if total else 0.0,
        'choice2_pct': (counts[2]/total*100.0) if total else 0.0,
        'choice3_pct': (counts[3]/total*100.0) if total else 0.0,
        'other_pct': (counts['other']/total*100.0) if total else 0.0,
    }


def project_satisfaction(projects: Dict[str, any]) -> float:
    """Average rank of allocated students (lower is better). Treat unranked as worst+1 instead of huge sentinel."""
    ranks: List[int] = []
    for proj in projects.values():
        if proj.current_alloc:
            worst_plus_one = len(proj.pref_list) + 1 if proj.pref_list else 1
            for sid in proj.current_alloc:
                r = rank_in_project(proj, sid)
                if r >= 10**8:  # sentinel for not present
                    r = worst_plus_one
                ranks.append(r)
    return (sum(ranks)/len(ranks)) if ranks else 0.0


def ensure_non_empty_projects(projects: Dict[str, any], students: Dict[int, any], matching: Dict[int, str]) -> None:
    """Post-process: if any project is empty, reassign an eligible student with minimal loss."""
    empty = [p for p in projects.values() if not p.current_alloc]
    for proj in empty:
        # Find eligible unmatched students first
        candidates = [s for s in students.values() if s.score >= proj.min_req and matching.get(s.id) is None]
        if not candidates:
            # Consider matched students where moving causes minimal increase in rank_in_student
            candidates = [s for s in students.values() if s.score >= proj.min_req]
        # Sort by loss: rank in proj + delta from current choice rank
        def loss(s):
            current = matching.get(s.id)
            current_rank = rank_in_student(s, current) if current else 10**9
            return rank_in_student(s, proj.code) - current_rank
        candidates.sort(key=lambda s: (loss(s), s.id))
        if candidates:
            chosen = candidates[0]
            prev_proj_code = matching.get(chosen.id)
            if prev_proj_code:
                prev_proj = projects[prev_proj_code]
                if chosen.id in prev_proj.current_alloc:
                    prev_proj.current_alloc.remove(chosen.id)
            proj.current_alloc.append(chosen.id)
            matching[chosen.id] = proj.code
