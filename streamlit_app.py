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
    query_params = st.query_params
    show_hidden = query_params.get("briefing", [""])[0].lower() == "grupo"

    tab_apresentacao, tab_metricas, tab_clusters, tab_codigo = st.tabs(
        ["Apresentação", "Visão Geral", "Clusters", "Código"]
    )

    with tab_apresentacao:
        st.markdown(
            """
# 📘 DOCUMENTAÇÃO COMPLETA — DO DADO BRUTO À INTELIGÊNCIA EDUCACIONAL

Este conteúdo resume todo o fluxo aplicado: coleta, limpeza, cálculo de engajamento, clustering, recomendações e painel interativo. Utilize em apresentações, relatórios, TCC ou portfolio.
            """,
            unsafe_allow_html=True,
        )
        st.markdown("<hr>", unsafe_allow_html=True)
        st.markdown(
            """
## 🎯 1. Coleta e Diagnóstico
- Fonte única: `Base anonimizada - Eric - PUC-SP.xlsx`.
- Campos por aula: aluno, unidade, sala, data, Pre-Class, Presença, Lição, Participação, Comportamento.
- Problemas iniciais: símbolos (“√”, “+/-”), emojis, coluna `Aula` quebrada, datas PT-BR, coluna Comportamento quase vazia, ausência de ID único (nomes repetidos).
            """,
            unsafe_allow_html=True,
        )
        st.markdown("<div style='margin:18px 0;'></div>", unsafe_allow_html=True)
        st.markdown(
            """
## 🧼 2. Limpeza e Padronização
1. Padronização de símbolos/emojis (√→1, N→0, +/−→0.5, emojis → escala 0–3, P/A/F → 1/0).
2. Correção da coluna `Aula` (mantém apenas dígitos, converte para inteiro, marca inválidos como NaN).
3. Conversão de datas PT-BR para `datetime`.
4. Remoção de “Comportamento” por baixa cobertura.
5. Tratamento de missing (binários com 0, participação com 1).
6. Criação de `aluno_id = Aluno::Sala::Unidade` para garantir unicidade.
            """,
            unsafe_allow_html=True,
        )
        st.markdown("<div style='margin:18px 0;'></div>", unsafe_allow_html=True)
        st.markdown(
            """
## 🧮 3. Métricas de Engajamento
Pilares: Preparação, Presença, Lição e Interação (normalizada 0–1).

```
engajamento = 0.30 * preparação
            + 0.45 * presença
            + 0.20 * lição_de_casa
            + 0.15 * interação
```

Saída `engagement_scores.csv` inclui `prep_score`, `attendance_score`, `homework_score`, `interaction_score`, `engajamento`, `engajamento_pct` e recomendações automáticas.
            """,
            unsafe_allow_html=True,
        )
        st.markdown("<div style='margin:18px 0;'></div>", unsafe_allow_html=True)
        st.markdown(
            """
## 🔥 4. Visualizações e Tendências
- Heatline com engajamento médio por aula.
- Cards com registros processados, alunos únicos, engajamento médio e clusters ativos.
- Tabelas e gráficos demonstrando consistência da limpeza e distribuição dos clusters.
            """,
            unsafe_allow_html=True,
        )
        st.markdown("<div style='margin:18px 0;'></div>", unsafe_allow_html=True)
        st.markdown(
            """
## 🧠 5. Clusters (K-Means) e Estratégias
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

### Narrativas
- Cluster 1: intervenção imediata.
- Cluster 2: monitoramento leve e metas curtas.
- Cluster 0: reconhecimento.
- Cluster 3: reforço de preparação.
            """,
            unsafe_allow_html=True,
        )
        st.markdown("<div style='margin:18px 0;'></div>", unsafe_allow_html=True)
        st.markdown(
            """
## 🤖 6. Relatórios, Dashboard e Evolução
- Relatórios individuais e chatbots podem acessar os CSVs e funções auxiliares.
- Painel Streamlit possui abas para narrativa (esta), visão geral e análises por cluster.
- Execução:
```bash
python pipeline.py
streamlit run streamlit_app.py
```

## 📤 7. Artefatos e Conclusão
- `cleaned_records.csv`, `engagement_scores.csv`, `student_clusters.csv`, `cluster_profiles.csv`, `pipeline.py`, `streamlit_app.py`.
- Transformamos o Excel heterogêneo em um pipeline robusto, com métricas de engajamento, clustering, visualizações e base pronta para APIs, chatbots e pesquisas.
            """,
            unsafe_allow_html=True,
        )
        st.markdown("<hr>", unsafe_allow_html=True)
        st.subheader("Exemplos de Resultados")
        overview_cols = st.columns(4)
        overview_cols[0].metric("Registros processados", f"{len(scores_df):,}")
        overview_cols[1].metric("Alunos únicos", f"{clusters_df['aluno_id'].nunique():,}")
        overview_cols[2].metric("Engajamento médio geral", f"{scores_df['engajamento'].mean():.2f}")
        overview_cols[3].metric("Clusters ativos", clusters_df["cluster"].nunique())

        st.markdown("<div style='margin:18px 0;'></div>", unsafe_allow_html=True)
        st.markdown(
            "<div style='font-size:18px;'>A tabela abaixo mostra as primeiras linhas pós-limpeza. "
            "Nela conseguimos verificar se as métricas foram convertidas corretamente (0/1 ou escala 0-3) antes de avançar para análises.</div>",
            unsafe_allow_html=True,
        )
        st.dataframe(scores_df[
            ["Data", "Aluno", "Sala", "Unidade", "Aula", "prep_score", "attendance_score", "homework_score", "interaction_score", "engajamento"]
        ].head(15))

        st.markdown("<div style='margin:28px 0;'></div>", unsafe_allow_html=True)
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

        st.markdown("<div style='margin:28px 0;'></div>", unsafe_allow_html=True)
        st.markdown(
            "<div style='font-size:18px;'>O heatmap abaixo detalha como o engajamento médio evolui por unidade/ aula. "
            "Regiões em vermelho indicam necessidade de intervenção; verdes apontam salas com ótimo aproveitamento.</div>",
            unsafe_allow_html=True,
        )
        heatmap_df = (
            scores_df.groupby(["Unidade", "Aula"])["engajamento"]
            .mean()
            .reset_index()
        )
        heatmap_pivot = heatmap_df.pivot(index="Unidade", columns="Aula", values="engajamento")
        st.dataframe(heatmap_pivot.style.background_gradient(cmap="RdYlGn", axis=1).format("{:.2f}"))

        st.markdown("<div style='margin:28px 0;'></div>", unsafe_allow_html=True)
        st.markdown(
            "<div style='font-size:18px;'>Os clusters abaixo ilustram como os alunos se distribuem entre perfis de engajamento. "
            "Clusters 0 e 2 representam públicos mais engajados, enquanto o cluster 1 concentra alunos em risco crítico. "
            "Essa segmentação direciona ações como mentorias individuais ou reforços positivos.</div>",
            unsafe_allow_html=True,
        )
        cluster_counts = clusters_df["cluster"].value_counts().sort_index()
        st.bar_chart(cluster_counts)

        st.markdown("<div style='margin:28px 0;'></div>", unsafe_allow_html=True)
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

        if show_hidden:
            st.markdown("<div style='margin:25px 0;'></div>", unsafe_allow_html=True)
            st.subheader("Roteiro dividido para 4 apresentadores (acesso especial)")
            st.markdown(
                """
1. **Pessoa A – Contexto e Diagnóstico:** Apresenta a origem do Excel, os problemas encontrados e o conceito de `aluno_id`.
2. **Pessoa B – Limpeza e Métricas:** Demonstra como padronizamos símbolos e calcula o engajamento (use a tabela inicial como apoio).
3. **Pessoa C – Clusters e Recomendações:** Foca no heatmap, na distribuição de clusters e na matriz de perfis para prescrever ações.
4. **Pessoa D – Dashboard e Futuro:** Navega pelas abas “Visão Geral” e “Clusters”, propondo próximos passos (chatbot, APIs, modelos preditivos).

Use este roteiro somente ao acessar o app com `?briefing=grupo`.
                """,
                unsafe_allow_html=True,
            )

    with tab_metricas:
        st.subheader("Filtros")
        unidades = sorted(scores_df["Unidade"].dropna().unique())
        selected_unidades = st.multiselect("Unidades", unidades, default=unidades)

        if selected_unidades:
            salas = sorted(
                scores_df[scores_df["Unidade"].isin(selected_unidades)]["Sala"].dropna().unique()
            )
        else:
            salas = sorted(scores_df["Sala"].dropna().unique())

        selected_salas = st.multiselect("Salas", salas, default=salas)

        filtered_scores = scores_df[
            ((scores_df["Unidade"].isin(selected_unidades)) | (not selected_unidades))
            & ((scores_df["Sala"].isin(selected_salas)) | (not selected_salas))
        ]
        filtered_clusters = clusters_df[
            ((clusters_df["Unidade"].isin(selected_unidades)) | (not selected_unidades))
            & ((clusters_df["Sala"].isin(selected_salas)) | (not selected_salas))
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

    with tab_codigo:
        st.subheader("Trechos essenciais do pipeline")
        st.markdown(
            "Use esta aba para explicar como os dados são limpos e preparados antes das análises."
        )
        st.code(
            '''
def build_student_id(row: pd.Series) -> str:
    fields = [
        str(row.get("Aluno", "")).strip(),
        str(row.get("Sala", "")).strip(),
        str(row.get("Unidade", "")).strip(),
    ]
    return "::".join(fields)

def clean_dataset(long_df: pd.DataFrame) -> pd.DataFrame:
    df = long_df.rename(columns=METRIC_RENAME).copy()
    df["Aluno"] = df["NOME COMPLETO"].apply(extract_student_name)
    df["Unidade"] = df["Nome Planilha Feedback"].apply(extract_unit)
    df["Sala"] = df["Sala"].astype(str).str.strip()
    df["Data"] = pd.to_datetime(df["Data"], errors="coerce")

    df["Fez a atividade antes da aula"] = df["Fez a atividade antes da aula"].apply(mapear_binario)
    df["Fez lição de casa"] = df["Fez lição de casa"].apply(mapear_binario)
    df["Presença/Ausencia"] = df["Presença/Ausencia"].apply(mapear_presenca)
    df["Participação"] = df["Participação"].apply(mapear_participacao)

    numeric_cols = [
        "Fez a atividade antes da aula",
        "Fez lição de casa",
        "Participação",
        "Presença/Ausencia",
    ]
    df[numeric_cols] = df[numeric_cols].fillna(0)

    df["aluno_id"] = df.apply(build_student_id, axis=1)
    df = df.drop_duplicates(subset=["aluno_id", "Aula"] + numeric_cols)
    df = df[df["Aula"] <= 14]
    df = df.sort_values(["Unidade", "Sala", "Aluno", "Aula"]).reset_index(drop=True)
    return df[
        [
            "aluno_id",
            "Aluno",
            "Sala",
            "Unidade",
            "Aula",
            "Data",
            "Fez a atividade antes da aula",
            "Presença/Ausencia",
            "Fez lição de casa",
            "Participação",
        ]
    ]
            '''
        )

        st.code(
            '''
def calculate_scores(clean_df: pd.DataFrame) -> pd.DataFrame:
    scores = clean_df.copy()
    scores["atividade_antes"] = scores["Fez a atividade antes da aula"]
    scores["presenca"] = scores["Presença/Ausencia"]
    scores["licao_casa"] = scores["Fez lição de casa"]
    scores["participacao"] = scores["Participação"]
    scores["participacao_norm"] = scores["participacao"] / 3

    scores["prep_score"] = scores["atividade_antes"]
    scores["attendance_score"] = scores["presenca"]
    scores["homework_score"] = scores["licao_casa"]
    scores["interaction_score"] = scores["participacao_norm"]

    scores["engajamento"] = (
        0.30 * scores["atividade_antes"]
        + 0.45 * scores["presenca"]
        + 0.20 * scores["licao_casa"]
        + 0.15 * scores["participacao_norm"]
    )
    scores["engajamento_pct"] = (scores["engajamento"] * 100).round(2)
    scores["acao_recomendada"] = scores.apply(recomendar_acao, axis=1)
    return scores
            '''
        )

        st.code(
            '''
def run_clustering(scores: pd.DataFrame, n_clusters: int = 4) -> Tuple[pd.DataFrame, pd.DataFrame]:
    metrics = ["prep_score", "attendance_score", "homework_score", "interaction_score", "engajamento"]
    grouped = (
        scores.groupby(["aluno_id", "Aluno", "Sala", "Unidade"])[metrics]
        .mean()
        .reset_index()
    )

    scaler = StandardScaler()
    features = scaler.fit_transform(grouped[metrics])

    kmeans = KMeans(n_clusters=min(n_clusters, len(grouped)), n_init=10, random_state=42)
    grouped["cluster"] = kmeans.fit_predict(features)

    cluster_profile = grouped.groupby("cluster")[metrics].mean().reset_index()
    return grouped, cluster_profile
            '''
        )


if __name__ == "__main__":
    main()
