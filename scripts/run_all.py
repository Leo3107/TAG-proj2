import os
import sys
import pandas as pd

# Ensure root path on sys.path
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if ROOT not in sys.path:
    sys.path.append(ROOT)

from src.parser import load_input
from src.utils import build_project_prefs, rank_in_project, rank_in_student, is_stable, student_satisfaction, project_satisfaction, ensure_non_empty_projects
from src.allocator import run_gale_shapley
from src.visualizer import visualize_iteration

DATA = os.path.join(ROOT, 'data', 'entradaProj2.25TAG.txt')
FIGS = os.path.join(ROOT, 'notebooks', 'figs')
RESULTS = os.path.join(ROOT, 'results')

projects, students = load_input(DATA)
matching, logs = run_gale_shapley(students, projects, max_iter=1000, log_iter=10)

# Visualizations for first 10 iterations
for i in range(1, 11):
    state = logs.get(i, {'proposals': [], 'accepted': [], 'rejected': []})
    out = os.path.join(FIGS, f'iter_{i:02d}.png')
    visualize_iteration(students, projects, state, i, out)

# Continue to stability (already done in allocator loop); then post-process
ensure_non_empty_projects(projects, students, matching)

# Export final matching CSV
rows = []
for sid, proj_code in matching.items():
    if proj_code is None:
        continue
    proj = projects[proj_code]
    stu = students[sid]
    rows.append({
        'student_id': sid,
        'project_id': proj_code,
        'project_rank_of_student': rank_in_project(proj, sid),
        'student_choice_rank': rank_in_student(stu, proj_code),
    })

df = pd.DataFrame(rows)
os.makedirs(RESULTS, exist_ok=True)
df.to_csv(os.path.join(RESULTS, 'final_matching.csv'), index=False)

# Print metrics
print('Stable:', is_stable(matching, projects, students))
print('Student satisfaction:', student_satisfaction(matching, students))
print('Project satisfaction (avg rank):', project_satisfaction(projects))
