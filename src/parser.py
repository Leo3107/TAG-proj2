from typing import Dict, List, Tuple
import json

class Project:
    def __init__(self, code: str, vacancies: int, min_req: int):
        self.code = code
        self.vacancies = vacancies
        self.min_req = min_req
        self.pref_list: List[int] = []
        self.current_alloc: List[int] = []

class Student:
    def __init__(self, student_id: int, prefs: List[str], score: int):
        self.id = student_id
        self.prefs = prefs[:3] if prefs else []
        self.score = score
        self.next_proposal_index = 0


def load_input(path: str) -> Tuple[Dict[str, Project], Dict[int, Student]]:
    """Carrega arquivo de entrada com projetos e alunos."""
    projects: Dict[str, Project] = {}
    students: Dict[int, Student] = {}

    with open(path, 'r', encoding='utf-8') as f:
        for raw in f:
            line = raw.strip()
            if not line or line.startswith('#') or line.startswith('//'):
                continue
            # Support tuple-like formats too
            if line.upper().startswith('PROJECT') or line.upper().startswith('STUDENT'):
                parts = [p.strip() for p in line.split(';')]
                tag = parts[0].upper()
                if tag == 'PROJECT':
                    if len(parts) < 4:
                        raise ValueError(f"Invalid PROJECT line: {line}")
                    code = parts[1]
                    vacancies = int(parts[2])
                    min_req = int(parts[3])
                    if vacancies < 1:
                        raise ValueError(f"Project {code} must have at least 1 vacancy")
                    projects[code] = Project(code, vacancies, min_req)
                elif tag == 'STUDENT':
                    if len(parts) < 3:
                        raise ValueError(f"Invalid STUDENT line: {line}")
                    sid = int(parts[1])
                    score = int(parts[2])
                    if score not in (3,4,5):
                        raise ValueError(f"Student {sid} score must be 3/4/5")
                    prefs: List[str] = []
                    if len(parts) >= 4 and parts[3]:
                        prefs = [p.strip() for p in parts[3].split(',') if p.strip()]
                    students[sid] = Student(sid, prefs, score)
                continue
            # Parse project tuple line: (P1, 2, 5)
            if line.startswith('(') and ')' in line and ':' not in line:
                content = line.strip()[1:line.rfind(')')]
                fields = [p.strip() for p in content.split(',')]
                if len(fields) >= 3:
                    code = fields[0]
                    vacancies = int(fields[1])
                    min_req = int(fields[2])
                    if vacancies < 1:
                        raise ValueError(f"Project {code} must have at least 1 vacancy")
                    projects[code] = Project(code, vacancies, min_req)
                continue
            # Parse student line: (A1):(P1, P30, P50) (5)
            if ':' in line:
                try:
                    left, rest = line.split(':', 1)
                    sid_str = left.strip()
                    if sid_str.startswith('(') and sid_str.endswith(')'):
                        sid_str = sid_str[1:-1]
                    if sid_str.upper().startswith('A'):
                        sid = int(sid_str[1:])
                    else:
                        sid = int(sid_str)
                    # Extract prefs in parentheses
                    prefs_part_start = rest.find('(')
                    prefs_part_end = rest.find(')', prefs_part_start+1)
                    prefs_list: List[str] = []
                    if prefs_part_start != -1 and prefs_part_end != -1:
                        prefs_str = rest[prefs_part_start+1:prefs_part_end]
                        prefs_list = [p.strip() for p in prefs_str.split(',') if p.strip()]
                    # Extract score: last parentheses
                    score = None
                    last_open = rest.rfind('(')
                    last_close = rest.rfind(')')
                    if last_open != -1 and last_close != -1 and last_close > last_open:
                        score_str = rest[last_open+1:last_close].strip()
                        score = int(score_str)
                    if score is None or score not in (3,4,5):
                        raise ValueError(f"Student {sid} score must be 3/4/5")
                    students[sid] = Student(sid, prefs_list, score)
                except Exception as e:
                    raise ValueError(f"Invalid STUDENT line: {line}. Error: {e}")
                continue

    for s in students.values():
        s.prefs = [p for p in s.prefs if p in projects]

    return projects, students
