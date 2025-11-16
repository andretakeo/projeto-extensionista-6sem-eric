# Apresentação do Pipeline de Engajamento

## 1. Contexto e Origem dos Dados
- Projeto extensionista CDIA/PUC-SP focado em engajamento estudantil.
- Fonte única: `Base anonimizada - Eric - PUC-SP.xlsx`, contendo registros por aluno e múltiplas aulas (colunas `Pre-Class`, `P`, `Hw`, `CP`, `Bh` com sufixos).
- Identidade real do aluno = combinação **Aluno + Sala + Unidade**. `pipeline.py` cria `aluno_id` concatenando esses campos para evitar colisões.

## 2. Objetivo do Pipeline
1. Reestruturar o Excel (de formato wide para long) preservando datas de cada aula.
2. Mapear símbolos e emojis para valores numéricos e normalizar dados (0/1, escala 0-3).
3. Calcular scores ponderados de engajamento e recomendações automáticas.
4. Agregar médias por aluno e executar clustering para identificar perfis (alto risco, intermediário, super engajados).

## 3. Preparação do Ambiente
```bash
python -m venv .venv && source .venv/bin/activate
pip install pandas numpy scikit-learn openpyxl streamlit altair
```

## 4. Execução do Pipeline
```bash
python pipeline.py
```
- **Saídas geradas:**
  - `cleaned_records.csv`: base normalizada (29k+ linhas) com métricas por aula.
  - `engagement_scores.csv`: adiciona `prep_score`, `attendance_score`, `homework_score`, `interaction_score`, `engajamento`, `acao_recomendada`.
  - `student_clusters.csv`: médias por `aluno_id` com cluster aplicado.
  - `cluster_profiles.csv`: perfil médio de cada cluster.
- Logs exibem cada fase (carregamento, reshape, limpeza, scores, clustering) e notificam sucesso.

## 5. Checagem Rápida dos Dados (Notebook opcional)
```bash
jupyter notebook consolidado.ipynb
```
- Utilizar para auditoria visual ou criação de gráficos exploratórios.
- Após qualquer ajuste na lógica, sincronizar com `pipeline.py`.

## 6. Dashboard Interativo (Streamlit)
```bash
streamlit run streamlit_app.py
```
- Sidebar permite filtrar unidades e salas.
- Componentes principais:
  - Indicadores agregados (engajamento, presença, preparação, interação).
  - Evolução média por aula (linha temporal).
  - Distribuição de clusters e perfis médios.
  - Ranking dos 10 alunos com maior engajamento no filtro.
  - Amostra tabular para inspeção rápida.

## 7. Interpretação dos Clusters
- **Cluster 0 – Super engajados:** médias ~0.8+; manter estímulo e desafios.
- **Cluster 2 – Bom nível, precisa consistência:** engajamento ~0.68; reforçar rotinas.
- **Cluster 3 – Médio/baixo:** ~0.50; apoio direcionado em preparação e interação.
- **Cluster 1 – Alto risco:** engajamento ~0.15; contato individual urgente.

## 8. Boas Práticas e Próximos Passos
- Regenerar os CSVs sempre que a planilha Excel for atualizada.
- Documentar qualquer substituição de `Base anonimizada - Eric - PUC-SP.xlsx` (origem, data, anonimização confirmada).
- Considerar automações (GitHub Actions/Cron) para rodar `python pipeline.py` e anexar outputs.
- Estender o Streamlit com gráficos adicionais (heatmaps, comparação entre unidades) conforme necessidades de apresentação.
