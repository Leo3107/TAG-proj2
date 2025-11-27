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
    """
    Load and validate input from a TXT file with a simple JSON-like format or CSV-like.
    Expected keys: projects and students blocks.
    Robustly parse lines of the form:
      PROJECT;code;vacancies;min_req
      STUDENT;id;score;prefs(comma-separated project codes)
    """
    projects: Dict[str, Project] = {}
    students: Dict[int, Student] = {}

    with open(path, 'r', encoding='utf-8') as f:
        for raw in f:
            line = raw.strip()
            if not line or line.startswith('#'):
                continue
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
            else:
                raise ValueError(f"Unknown line tag: {parts[0]}")

    # Validate that preferences refer to known projects; allow unknown but drop
    for s in students.values():
        s.prefs = [p for p in s.prefs if p in projects]

    return projects, students
