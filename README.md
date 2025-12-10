# Projeto 2 — Teoria e Aplicação de Grafos (2025/2)

Sistema de alocação aluno–projeto com variação do algoritmo Gale–Shapley (Student-Proposing) para projetos com capacidade múltipla.

## Variação do Algoritmo Gale-Shapley

### Algoritmo Clássico vs. Implementação

O algoritmo clássico de Gale-Shapley foi projetado para o problema do **casamento estável** (Stable Marriage Problem), onde:
- Há dois conjuntos de igual tamanho (homens e mulheres)
- Cada participante tem preferências sobre todos do outro conjunto
- Cada participante pode ser emparelhado com exatamente uma pessoa

### Modificações Implementadas

Nossa implementação adapta o algoritmo para o problema **Student-Project Allocation** (também conhecido como **Hospital-Residents Problem**), com as seguintes modificações:

#### 1. **Capacidade Múltipla (Multi-Capacity)**
- **Clássico**: Cada "projeto" (hospital) aceita exatamente 1 "aluno" (residente)
- **Modificado**: Cada projeto tem `vacancies` vagas e pode aceitar múltiplos alunos
- **Implementação**: Projetos mantêm uma lista `current_alloc` com até `vacancies` alunos

#### 2. **Listas de Preferência Parciais**
- **Clássico**: Cada participante lista todos do outro conjunto
- **Modificado**: Alunos listam no máximo 3 preferências; projetos só consideram alunos elegíveis
- **Implementação**: Aluno propõe apenas aos projetos da sua lista (`student.prefs[:3]`)

#### 3. **Requisitos de Elegibilidade**
- **Clássico**: Qualquer par pode ser emparelhado
- **Modificado**: Aluno só é elegível para projeto se `student.score >= project.min_req`
- **Implementação**: Proposta é rejeitada imediatamente se aluno não atende requisito mínimo

#### 4. **Construção da Lista de Preferência dos Projetos**
- **Clássico**: Lista de preferência é fornecida como entrada
- **Modificado**: Lista é construída automaticamente baseada em critérios objetivos
- **Implementação**: `build_project_prefs()` ordena alunos elegíveis por:
  1. Maior `score` (nota) primeiro
  2. Desempate: menor `id` (aluno) primeiro

#### 5. **Iterações Fixas para Visualização**
- **Clássico**: Algoritmo executa até convergência
- **Modificado**: Executa exatamente 10 iterações para visualização, depois continua até convergir
- **Implementação**: Loop fixo de 10 iterações com logging, seguido de loop até estabilização

### Pseudocódigo da Variação

```
ENTRADA: students (com prefs e score), projects (com vacancies e min_req)
SAÍDA: matching estável

1. Para cada projeto, construir pref_list ordenando alunos elegíveis por (score desc, id asc)
2. held_by[s] ← None para todo aluno s
3. Para iteração = 1 até 10:
   a. free_students ← {s : held_by[s] = None e s ainda tem preferências}
   b. Para cada s em free_students (ordem crescente de id):
      i.   p ← próximo projeto na lista de preferências de s
      ii.  Se score[s] < min_req[p]: rejeitar s, continuar
      iii. Adicionar s a current_alloc[p]
      iv.  held_by[s] ← p
      v.   Enquanto |current_alloc[p]| > vacancies[p]:
           - worst ← aluno com pior rank em pref_list[p]
           - Remover worst de current_alloc[p]
           - held_by[worst] ← None
   c. Registrar estado para visualização
4. Continuar iterações até não haver mais mudanças
5. Retornar matching = {s: held_by[s] para todo s}
```

### Garantias de Estabilidade

O matching resultante é **estável** no sentido de que não existe par bloqueador (blocking pair):
- Não há aluno `s` e projeto `p` tal que:
  - `s` prefere `p` ao seu match atual
  - `s` é elegível para `p` (`score[s] >= min_req[p]`)
  - `p` tem vaga OU `p` prefere `s` ao seu pior aluno alocado

### Limitações

- Se há mais vagas exigindo nota 5 do que alunos com nota 5, alguns projetos ficarão vazios
- Alunos com listas de preferência curtas (3 opções) podem ficar sem alocação se todas forem rejeitadas

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
