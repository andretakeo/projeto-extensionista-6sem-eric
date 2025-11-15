# Pipeline de Engajamento dos Alunos

Este repositório centraliza o pipeline de limpeza, cálculo de engajamento e clustering aplicado aos dados acadêmicos anonimizados do projeto extensionista do sexto semestre do curso CDIA/PUC-SP. Tudo começa na planilha `Base anonimizada - Eric - PUC-SP.xlsx`, que consolida cada aula em colunas múltiplas; o script `pipeline.py` é responsável por transformar esse arquivo único em conjuntos reutilizáveis para análises, dashboards ou relatórios operacionais.

## Estrutura do Projeto
- `Base anonimizada - Eric - PUC-SP.xlsx`: insumo bruto com indicadores por aula (Pre-Class, Presença, Homework, Participação, Comportamento). **Não existe outra fonte: qualquer versão revisada precisa documentar a proveniência.**
- `pipeline.py`: implementação profissionalizada do pipeline (reshape → limpeza → scores → clustering).
- `consolidado.ipynb`: notebook histórico que inspirou o script atual; serve como referência exploratória.
- Saídas geradas automaticamente:
  - `cleaned_records.csv`: dados normalizados em formato long.
  - `engagement_scores.csv`: scores calculados por aula com recomendações de ação.
  - `student_clusters.csv`: médias por aluno e cluster atribuído.
  - `cluster_profiles.csv`: perfil médio de cada cluster.
- `AGENTS.md` e `CLAUDE.md`: guias rápidos para agentes/automações colaborarem no repositório.

## Origem e Identidade dos Dados
- `Base anonimizada - Eric - PUC-SP.xlsx` é o único ponto de verdade; ela traz linhas por aluno e colunas repetidas para cada aula (ex.: `Pre-Class`, `Pre-Class.1`, ...).
- `pipeline.py` cria `aluno_id` concatenando `Aluno::Sala::Unidade`, garantindo unicidade mesmo que “Estudante 1” apareça em várias unidades.
- Não mantenha cópias divergentes do Excel. Caso precise atualizar os dados, substitua o arquivo apenas após documentar a origem e garantir que continua anonimizado.
- As datas das aulas são lidas da própria planilha (linha de cabeçalho “Aula 1”, “Aula 2”); não edite manualmente esses campos para evitar desalinhamento.

## Execução do Pipeline
1. Crie um ambiente isolado e instale dependências:
   ```bash
   python -m venv .venv && source .venv/bin/activate
   pip install pandas numpy scikit-learn openpyxl
   ```
2. Execute o pipeline:
   ```bash
   python pipeline.py
   ```
3. O script realiza as etapas abaixo:
   - **Carregamento e reshape:** lê o Excel, sincroniza datas («Aula 1», «Aula 2», …) e expande cada aula para uma linha individual.
   - **Limpeza:** extrai `Aluno`, `Sala`, `Unidade`, monta `aluno_id = Aluno::Sala::Unidade`, converte símbolos (√, +/-) em valores numéricos e normaliza datas PT-BR.
   - **Scores:** aplica pesos (30% preparação, 45% presença, 20% lição, 15% interação) e gera recomendações automáticas.
   - **Clustering:** agrega médias por `aluno_id`, padroniza com `StandardScaler` e roda `KMeans` (até 4 clusters) salvando o perfil médio.

## Boas Práticas de Dados
- Considere **Aluno + Sala + Unidade** como chave primária; nomes como “Estudante 1” podem repetir em unidades diferentes.
- Mantenha os arquivos sensíveis apenas localmente; não faça commit de novas bases sem validar a anonimização.
- Sempre versionar artefatos derivados (CSV/plots) que impactem análises downstream e registrar no commit/PR quais foram regenerados.

## Desenvolvimento e Validação
- Use `consolidado.ipynb` para testes exploratórios ou validação visual de etapas específicas; após ajustes, replique a lógica em `pipeline.py`.
- Ao evoluir o pipeline, adicione asserts simples (p.ex., `assert df['Presença/Ausencia'].between(0,1).all()`) para garantir consistência.
- Recomenda-se configurar um job simples (GitHub Actions ou cron) chamando `python pipeline.py` e anexando os CSVs produzidos para auditoria.

## Próximos Passos Sugeridos
1. Automatizar geração de gráficos (heatmaps e distribuição de clusters) diretamente no script ou em um notebook dedicado.
2. Documentar métricas de qualidade por unidade/sala (faltas, homework, preparação) para alimentar relatórios executivos.
3. Adicionar testes unitários leves para as funções de mapeamento (`mapear_binario`, `mapear_presenca`, etc.) garantindo estabilidade em novas bases.
