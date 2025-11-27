# Projeto 2 — Teoria e Aplicação de Grafos (2025/2)

Sistema de alocação aluno–projeto com variação do algoritmo Gale–Shapley (Student-Proposing) para projetos com capacidade múltipla.

## Variação do algoritmo

- Student-Proposing: em cada iteração, cada aluno propõe a um único projeto (seguindo sua lista). Projetos mantêm até `vacancies` melhores candidatos conforme sua lista de preferência (ordenada por `score` desc e desempate por `id` asc).
- Elegibilidade: aluno é elegível se `student.score >= project.min_req`. Projetos ignoram candidatos inelegíveis.
- Desempates:
  - Entre alunos na lista de projeto: maior `score`, em caso de empate menor `id` primeiro.
  - Entre projetos nas preferências do aluno: ordem dada no arquivo de entrada.

## Visualizações

- Cores:
  - Proposta ativa: azul (`#1f77b4`)
  - Emparelhamento temporário: verde (`#2ca02c`)
  - Rejeição: vermelho (`#d62728`)

## Saídas

- `notebooks/figs/iter_01.png` ... `iter_10.png` com evolução.
- `results/final_matching.csv` com colunas: `student_id, project_id, project_rank_of_student, student_choice_rank`.
- `notebooks/main.ipynb` com execução passo-a-passo.
- Mini-relatório gerado via nbconvert (`mini-relatorio.pdf`).

## Como executar (local)

```powershell
python -m venv .venv; .\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
python scripts/run_all.py
```

## Como executar (Colab)

1. Faça upload dos arquivos `src/`, `data/entradaProj2.25TAG.txt` e `notebooks/main.ipynb`.
2. Instale dependências: `pip install networkx matplotlib pandas`.
3. Execute as células do notebook.

## Referência

Abraham, D.J.; Irving, R.W.; Manlove, D.F. (2007). Two algorithms for the student-project allocation problem. Journal of Discrete Algorithms 5(1): pp. 73–90.
