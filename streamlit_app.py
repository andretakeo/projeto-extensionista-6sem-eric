"""
Interactive dashboard built with Streamlit to explore engagement outputs.

The app assumes that `pipeline.py` has been executed and that the CSV artifacts
are available in the repository root. Use this interface to filter by unidade,
sala e cluster e visualizar métricas-chave sem abrir notebooks.
"""

from __future__ import annotations

from pathlib import Path

import pandas as pd
import streamlit as st

DATA_DIR = Path(__file__).parent

CLUSTER_NOTES = {
    0: "Cluster 0 reúne os **super engajados**: presença e preparação quase constantes. "
       "São candidatos a atividades avançadas e podem atuar como multiplicadores com os colegas.",
    1: "Cluster 1 representa o grupo **crítico/alto risco**. Engajamento baixíssimo exige contato individual imediato, "
       "investigando faltas e falta de preparação.",
    2: "Cluster 2 indica um grupo **bom, porém instável**. Oscilam entre aulas com alta participação e quedas repentinas; "
       "feedback contínuo ajuda a mantê-los no rumo.",
    3: "Cluster 3 corresponde a um **nível intermediário**. Precisam de reforço em preparação e lição de casa para não regredirem.",
}


def load_csv(filename: str, parse_dates: list[str] | None = None) -> pd.DataFrame:
    """Read a CSV from the repository root and fail fast if it is missing."""
    path = DATA_DIR / filename
    if not path.exists():
        st.error(f"Arquivo `{filename}` não encontrado. Execute `python pipeline.py` antes de abrir o app.")
        st.stop()
    return pd.read_csv(path, parse_dates=parse_dates)


@st.cache_data
def load_data() -> tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame]:
    scores = load_csv("engagement_scores.csv", parse_dates=["Data"])
    clusters = load_csv("student_clusters.csv")
    profiles = load_csv("cluster_profiles.csv")
    return scores, clusters, profiles


def format_pct(value: float) -> str:
    return f"{value * 100:,.1f}%"


def main() -> None:
    st.set_page_config(page_title="Engajamento de Alunos", page_icon="📊", layout="wide")
    st.title("📊 Painel de Engajamento de Alunos")
    st.markdown(
        "Os dados abaixo são derivados diretamente de `Base anonimizada - Eric - PUC-SP.xlsx` "
        "via `pipeline.py`. Rode o pipeline sempre que um novo Excel for importado."
    )

    scores_df, clusters_df, profiles_df = load_data()

    tab_apresentacao, tab_metricas, tab_clusters = st.tabs(["Apresentação", "Visão Geral", "Clusters"])

    with tab_apresentacao:
        st.markdown(
            """
# 📘 DOCUMENTAÇÃO COMPLETA — DO DADO BRUTO À INTELIGÊNCIA EDUCACIONAL

Este conteúdo resume todo o fluxo aplicado: coleta, limpeza, cálculo de engajamento, clustering, recomendações e painel interativo. Utilize em apresentações, relatórios, TCC ou portfolio.

## 🎯 1. Coleta e Diagnóstico
- Fonte única: `Base anonimizada - Eric - PUC-SP.xlsx`.
- Campos por aula: aluno, unidade, sala, data, Pre-Class, Presença, Lição, Participação, Comportamento.
- Problemas iniciais: símbolos (“√”, “+/-”), emojis, coluna `Aula` quebrada, datas PT-BR, coluna Comportamento quase vazia, ausência de ID único (nomes repetidos).

## 🧼 2. Limpeza e Padronização
1. Padronização de símbolos/emojis (√→1, N→0, +/−→0.5, emojis → escala 0–3, P/A/F → 1/0).
2. Correção da coluna `Aula` (mantém apenas dígitos, converte para inteiro, marca inválidos como NaN).
3. Conversão de datas PT-BR para `datetime`.
4. Remoção de “Comportamento” por baixa cobertura.
5. Tratamento de missing (binários com 0, participação com 1).
6. Criação de `aluno_id = Aluno::Sala::Unidade` para garantir unicidade.

## 🧮 3. Métricas de Engajamento
Pilares: Preparação, Presença, Lição e Interação (normalizada 0–1).

```
engajamento = 0.30 * preparação
            + 0.45 * presença
            + 0.20 * lição_de_casa
            + 0.15 * interação
```

Saída `engagement_scores.csv` inclui `prep_score`, `attendance_score`, `homework_score`, `interaction_score`, `engajamento`, `engajamento_pct` e recomendações automáticas.

## 🔥 4. Visualizações
- Heatline com engajamento médio por aula.
- Cards com registros processados, alunos únicos, engajamento médio e clusters ativos.
- Tabelas e gráficos demonstrando consistência da limpeza e distribuição dos clusters.

## 🧠 5. Clusters (K-Means)
1. Média por `aluno_id`.
2. Padronização com `StandardScaler`.
3. K-Means (até 4 clusters).
4. Artefatos: `student_clusters.csv` e `cluster_profiles.csv`.

Perfis típicos:
| Cluster | Perfil | Estratégia |
| --- | --- | --- |
| 0 | Super engajados (≈0.82) | Desafios / liderança |
| 1 | Crítico (≈0.15) | Contato individual |
| 2 | Bom/instável (≈0.68) | Reforçar consistência |
| 3 | Intermediário (≈0.50) | Trabalhar preparação / lição |

## 🔍 6. Estratégias e Narrativas
- Cluster 1: intervenção imediata.
- Cluster 2: monitoramento leve e metas curtas.
- Cluster 0: reconhecimento.
- Cluster 3: reforço de preparação.

## 🤖 7. Relatórios e Chatbots
Com os CSVs gerados é possível criar relatórios por aluno, ferramentas para responder “Quem está em risco?” e integrar com FastAPI/LLMs para chatbots acadêmicos.

## 📊 8. Dashboard Streamlit
- **Apresentação**: esta documentação + exemplos reais.
- **Visão Geral**: filtros, métricas e gráficos interativos.
- **Clusters**: mergulho por cluster (descrição, distribuição por unidade, top/bottom alunos).

Execução:
```bash
python pipeline.py
streamlit run streamlit_app.py
```

## 📤 9. Artefatos
- `cleaned_records.csv`, `engagement_scores.csv`, `student_clusters.csv`, `cluster_profiles.csv`.
- Scripts: `pipeline.py`, `streamlit_app.py`.

## 🏁 Conclusão
Transformamos um Excel heterogêneo em:
- Pipeline reproducível.
- Índice de engajamento com recomendações.
- Segmentação comportamental via clustering.
- Painel interativo pronto para storytelling e tomada de decisão.
- Base pronta para APIs, chatbots, estudos acadêmicos e modelos preditivos.
            """,
            unsafe_allow_html=True,
        )
        st.subheader("Origem e Identidade dos Dados")
        st.markdown(
            "<div style='font-size:18px;'>Fonte única: <strong>Base anonimizada - Eric - PUC-SP.xlsx</strong>, com turmas de Campinas, Diadema, Rio, "
            "entre outras unidades. As datas das aulas são lidas diretamente da aba de cabeçalhos (Aula 1, Aula 2, ...), garantindo aderência ao calendário real. "
            "Cada estudante é identificado por <code>Aluno::Sala::Unidade</code>, pois nomes genéricos como “Estudante 1” se repetem em diferentes polos.</div>",
            unsafe_allow_html=True,
        )

        st.subheader("Pipeline Executado")
        st.markdown(
            "<div style='font-size:18px;'>"
            "1. <strong>Extração</strong> – leitura do Excel e sincronização das datas de aula.<br>"
            "2. <strong>Reestruturação</strong> – expansão das colunas <em>Pre-Class, P, Hw, CP, Bh</em> para formato long (uma linha por aluno/aula).<br>"
            "3. <strong>Limpeza</strong> – criação de <code>aluno_id</code>, mapeamento de símbolos/emojis (√, +/-) para valores numéricos e ajuste de datas PT-BR.<br>"
            "4. <strong>Scores</strong> – cálculo de preparação, presença, lição de casa e interação; fórmula final: "
            "<code>0.30 * prep + 0.45 * presença + 0.20 * lição + 0.15 * interação</code>, gerando recomendações automáticas.<br>"
            "5. <strong>Clustering</strong> – agregação média por aluno, padronização com StandardScaler e K-Means (4 clusters) para rotular perfis de engajamento."
            "</div>",
            unsafe_allow_html=True,
        )

        st.subheader("Artefatos Gerados")
        st.markdown(
            "<div style='font-size:18px;'>"
            "- <strong>cleaned_records.csv</strong>: base normalizada por aula (≈29 mil linhas).<br>"
            "- <strong>engagement_scores.csv</strong>: inclui scores, percentuais e ação recomendada por aula.<br>"
            "- <strong>student_clusters.csv</strong>: visão por aluno único com cluster aplicado.<br>"
            "- <strong>cluster_profiles.csv</strong>: médias de preparação/presença/lição/interação/engajamento por cluster."
            "</div>",
            unsafe_allow_html=True,
        )

        st.subheader("Exemplos de Resultados")
        overview_cols = st.columns(4)
        overview_cols[0].metric("Registros processados", f"{len(scores_df):,}")
        overview_cols[1].metric("Alunos únicos", f"{clusters_df['aluno_id'].nunique():,}")
        overview_cols[2].metric("Engajamento médio geral", f"{scores_df['engajamento'].mean():.2f}")
        overview_cols[3].metric("Clusters ativos", clusters_df["cluster"].nunique())

        st.markdown(
            "<div style='font-size:18px;'>A tabela abaixo mostra as primeiras linhas pós-limpeza. "
            "Nela conseguimos verificar se as métricas foram convertidas corretamente (0/1 ou escala 0-3) antes de avançar para análises.</div>",
            unsafe_allow_html=True,
        )
        st.dataframe(scores_df[
            ["Data", "Aluno", "Sala", "Unidade", "Aula", "prep_score", "attendance_score", "homework_score", "interaction_score", "engajamento"]
        ].head(15))

        st.markdown(
            "<div style='font-size:18px;'>Além da auditoria tabular, também observamos tendências globais. "
            "O gráfico seguinte evidencia como o engajamento médio oscila ao longo das aulas. "
            "Quedas acentuadas sinalizam momentos em que a equipe pedagógica pode reforçar comunicação ou atividades complementares.</div>",
            unsafe_allow_html=True,
        )
        overall_engagement = (
            scores_df.groupby("Aula")["engajamento"]
            .mean()
            .reset_index()
            .sort_values("Aula")
        )
        st.line_chart(overall_engagement.set_index("Aula"))

        st.markdown(
            "<div style='font-size:18px;'>Os clusters abaixo ilustram como os alunos se distribuem entre perfis de engajamento. "
            "Clusters 0 e 2 representam públicos mais engajados, enquanto o cluster 1 concentra alunos em risco crítico. "
            "Essa segmentação direciona ações como mentorias individuais ou reforços positivos.</div>",
            unsafe_allow_html=True,
        )
        cluster_counts = clusters_df["cluster"].value_counts().sort_index()
        st.bar_chart(cluster_counts)

        st.markdown(
            "<div style='font-size:18px;'>"
            "Para reforçar a interpretação, a matriz a seguir traz os valores médios por cluster. "
            "Note que o Cluster 0 mantém engajamento acima de 0.8, enquanto o Cluster 1 mal ultrapassa 0.15."
            "</div>",
            unsafe_allow_html=True,
        )
        st.dataframe(
            profiles_df.rename(
                columns={
                    "prep_score": "Preparação",
                    "attendance_score": "Presença",
                    "homework_score": "Lição",
                    "interaction_score": "Interação",
                    "engajamento": "Engajamento",
                }
            ).style.format("{:.2f}"),
            use_container_width=True,
        )

        st.subheader("Como utilizar")
        st.markdown(
            "<div style='font-size:18px;'>"
            "1. Execute <code>python pipeline.py</code> após atualizar o Excel.<br>"
            "2. Use esta aba para apresentar o contexto, os resultados-chave e o porquê de cada etapa do pipeline.<br>"
            "3. Vá para a aba <strong>Análises</strong> para filtrar unidades/salas específicas e tomar decisões operacionais."
            "</div>",
            unsafe_allow_html=True,
        )

    with tab_metricas:
        st.subheader("Filtros")
        unidades = sorted(scores_df["Unidade"].dropna().unique())
        salas = sorted(scores_df["Sala"].dropna().unique())

        filter_col1, filter_col2 = st.columns(2)
        unidade_filter = filter_col1.multiselect("Unidades", unidades, default=unidades)
        sala_filter = filter_col2.multiselect("Salas", salas, default=salas)

        filtered_scores = scores_df[
            scores_df["Unidade"].isin(unidade_filter) & scores_df["Sala"].isin(sala_filter)
        ]
        filtered_clusters = clusters_df[
            clusters_df["Unidade"].isin(unidade_filter) & clusters_df["Sala"].isin(sala_filter)
        ]

        if filtered_scores.empty:
            st.warning("Nenhum registro encontrado para os filtros selecionados.")
            st.stop()

        col1, col2, col3, col4 = st.columns(4)
        col1.metric("Engajamento médio", f"{filtered_scores['engajamento'].mean():.2f}")
        col2.metric("Presença média", f"{filtered_scores['attendance_score'].mean():.2f}")
        col3.metric("Preparação média", f"{filtered_scores['prep_score'].mean():.2f}")
        col4.metric("Interação média", f"{filtered_scores['interaction_score'].mean():.2f}")

        st.subheader("Evolução média por aula")
        engagement_by_aula = (
            filtered_scores.groupby("Aula")["engajamento"]
            .mean()
            .reset_index()
            .sort_values("Aula")
        )
        st.line_chart(engagement_by_aula.set_index("Aula"))

        st.subheader("Distribuição de clusters (alunos únicos)")
        if filtered_clusters.empty:
            st.info("Sem dados agregados para cluster no filtro atual.")
        else:
            counts = filtered_clusters["cluster"].value_counts().sort_index()
            st.bar_chart(counts)

        st.subheader("Perfis médios por cluster")
        st.dataframe(
            profiles_df.rename(
                columns={
                    "prep_score": "Preparação",
                    "attendance_score": "Presença",
                    "homework_score": "Lição",
                    "interaction_score": "Interação",
                    "engajamento": "Engajamento",
                }
            ).style.format("{:.2f}"),
            use_container_width=True,
        )

        st.subheader("Top 10 alunos por engajamento (filtro atual)")
        top_students = (
            filtered_scores.groupby(["aluno_id", "Aluno", "Sala", "Unidade"])["engajamento"]
            .mean()
            .reset_index()
            .sort_values("engajamento", ascending=False)
            .head(10)
        )
        st.dataframe(top_students.style.format({"engajamento": "{:.2f}"}), use_container_width=True)

        st.subheader("Amostra de registros por aula")
        st.dataframe(
            filtered_scores[
                [
                    "Data",
                    "Aluno",
                    "Sala",
                    "Unidade",
                    "Aula",
                    "prep_score",
                    "attendance_score",
                    "homework_score",
                    "interaction_score",
                    "engajamento",
                ]
            ]
            .sort_values(["Data", "Aluno"])
            .head(50)
        )

    with tab_clusters:
        st.subheader("Análises por Cluster")
        cluster_options = sorted(clusters_df["cluster"].unique())
        selected_cluster = st.selectbox(
            "Selecione o cluster para aprofundar",
            cluster_options,
            format_func=lambda c: f"Cluster {c}",
        )

        cluster_profile = profiles_df[profiles_df["cluster"] == selected_cluster].iloc[0]
        st.markdown(
            f"<div style='font-size:18px; margin-top:10px;'>{CLUSTER_NOTES.get(selected_cluster, '')}</div>",
            unsafe_allow_html=True,
        )

        metric_cols = st.columns(5)
        metric_cols[0].metric("Preparação média", f"{cluster_profile['prep_score']:.2f}")
        metric_cols[1].metric("Presença média", f"{cluster_profile['attendance_score']:.2f}")
        metric_cols[2].metric("Lição média", f"{cluster_profile['homework_score']:.2f}")
        metric_cols[3].metric("Interação média", f"{cluster_profile['interaction_score']:.2f}")
        metric_cols[4].metric("Engajamento", f"{cluster_profile['engajamento']:.2f}")

        cluster_members = clusters_df[clusters_df["cluster"] == selected_cluster]
        st.markdown(
            f"<div style='font-size:18px;'>Total de alunos no cluster: <strong>{len(cluster_members):,}</strong></div>",
            unsafe_allow_html=True,
        )

        unidade_breakdown = (
            cluster_members.groupby("Unidade")["aluno_id"]
            .nunique()
            .sort_values(ascending=False)
        )
        st.markdown("<div style='font-size:18px;'>Distribuição por unidade:</div>", unsafe_allow_html=True)
        st.bar_chart(unidade_breakdown)

        subset_scores = scores_df[scores_df["aluno_id"].isin(cluster_members["aluno_id"])]
        student_avg = (
            subset_scores.groupby(["aluno_id", "Aluno", "Sala", "Unidade"])["engajamento"]
            .mean()
            .reset_index()
        )

        st.markdown("<div style='font-size:18px;'>Top 10 alunos no cluster:</div>", unsafe_allow_html=True)
        top_cluster = student_avg.sort_values("engajamento", ascending=False).head(10)
        st.dataframe(top_cluster.style.format({"engajamento": "{:.2f}"}), use_container_width=True)

        st.markdown("<div style='font-size:18px;'>10 alunos com menor engajamento dentro do cluster:</div>", unsafe_allow_html=True)
        bottom_cluster = student_avg.sort_values("engajamento", ascending=True).head(10)
        st.dataframe(bottom_cluster.style.format({"engajamento": "{:.2f}"}), use_container_width=True)

        st.markdown(
            "<div style='font-size:18px;'>Use essas listas para priorizar ações: "
            "reforço positivo aos destaques e planos de recuperação aos últimos colocados.</div>",
            unsafe_allow_html=True,
        )


if __name__ == "__main__":
    main()
