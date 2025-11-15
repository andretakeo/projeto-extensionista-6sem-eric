"""End-to-end data pipeline for Eric engagement analysis.

The script replicates the notebook workflow with clearer structure so it can be
executed headlessly. It loads the Excel workbook, reshapes class metrics into a
long format, cleans and scores engagement metrics, and finally performs
clustering with deterministic IDs built from student + room + unit.
"""
from __future__ import annotations

import re
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Tuple

import numpy as np
import pandas as pd
from sklearn.cluster import KMeans
from sklearn.preprocessing import StandardScaler

RAW_WORKBOOK = Path("Base anonimizada - Eric - PUC-SP.xlsx")
CLASS_METRICS = ["Pre-Class", "P", "Hw", "CP", "Bh"]
ID_COLUMNS = ["Nome Planilha Feedback", "Sala", "Num", "NOME COMPLETO"]

METRIC_RENAME = {
    "Pre-Class": "Fez a atividade antes da aula",
    "P": "Presença/Ausencia",
    "Hw": "Fez lição de casa",
    "CP": "Participação",
    "Bh": "Comportamento",
}

MONTH_MAP = {
    "jan.": "Jan",
    "fev.": "Feb",
    "mar.": "Mar",
    "abr.": "Apr",
    "mai.": "May",
    "jun.": "Jun",
    "jul.": "Jul",
    "ago.": "Aug",
    "set.": "Sep",
    "out.": "Oct",
    "nov.": "Nov",
    "dez.": "Dec",
}


@dataclass(frozen=True)
class PipelineArtifacts:
    cleaned: Path
    scores: Path
    clusters: Path
    cluster_profiles: Path


def parse_pt_br_date(value) -> pd.Timestamp:
    """Convert Portuguese short dates into pandas timestamps."""
    if pd.isna(value):
        return pd.NaT
    if isinstance(value, (pd.Timestamp, np.datetime64)):
        return pd.to_datetime(value)

    text = str(value).strip().lower()
    for pt, en in MONTH_MAP.items():
        text = text.replace(pt, en)
    cleaned = text.replace("-", " ").title()
    for pattern in ("%d %b %Y", "%d %B %Y"):
        try:
            parsed = datetime.strptime(cleaned, pattern)
            return pd.Timestamp(parsed)
        except ValueError:
            continue
    fallback = pd.to_datetime(cleaned, errors="coerce")
    return pd.Timestamp(fallback) if not pd.isna(fallback) else pd.NaT


def build_class_date_lookup(path: Path) -> Dict[int, pd.Timestamp]:
    raw_dates = pd.read_excel(path)
    header_row = raw_dates.drop(columns=[c for c in raw_dates.columns if "Unnamed:" in c]).iloc[0]
    lookup: Dict[int, pd.Timestamp] = {}
    for label, value in header_row.items():
        match = re.search(r"(\d+)", str(label))
        if not match:
            continue
        aula = int(match.group())
        lookup[aula] = parse_pt_br_date(value)
    return lookup


def parse_metric_column(col: str) -> Tuple[str, int] | None:
    if col in CLASS_METRICS:
        return col, 0
    if "." in col:
        base, idx = col.split(".", 1)
        if base in CLASS_METRICS and idx.isdigit():
            return base, int(idx)
    return None


def reshape_classes(raw_df: pd.DataFrame, date_lookup: Dict[int, pd.Timestamp]) -> pd.DataFrame:
    class_indices = sorted({parsed[1] for parsed in map(parse_metric_column, raw_df.columns) if parsed})
    frames: List[pd.DataFrame] = []

    for idx in class_indices:
        class_cols = {metric: (metric if idx == 0 else f"{metric}.{idx}") for metric in CLASS_METRICS}
        available = [col for col in class_cols.values() if col in raw_df.columns]
        if not available:
            continue
        frame = raw_df[ID_COLUMNS + available].copy()
        rename_map = {col: metric for metric, col in class_cols.items() if col in frame.columns}
        frame.rename(columns=rename_map, inplace=True)
        frame["Aula"] = idx + 1
        frame["Data"] = date_lookup.get(idx + 1, pd.NaT)
        frames.append(frame)

    if not frames:
        raise ValueError("Nenhuma coluna de aula encontrada no workbook")

    long_df = pd.concat(frames, ignore_index=True)
    return long_df


def extract_student_name(raw_name: str) -> str:
    if pd.isna(raw_name):
        return ""
    return str(raw_name).split(" - ")[0].strip()


def extract_unit(planilha_name: str) -> str:
    if pd.isna(planilha_name):
        return ""
    partes = str(planilha_name).split(" - ")
    return partes[2].strip() if len(partes) > 2 else ""


def build_student_id(row: pd.Series) -> str:
    fields = [str(row.get("Aluno", "")).strip(), str(row.get("Sala", "")).strip(), str(row.get("Unidade", "")).strip()]
    return "::".join(fields)


def mapear_binario(valor):
    if pd.isna(valor):
        return 0.0
    valor = str(valor).strip()
    if "ERROR" in valor.upper():
        return np.nan
    if valor == "√":
        return 1.0
    if valor in {"+/-", "+ –"}:
        return 0.5
    if valor in {"N", "n", "0"}:
        return 0.0
    try:
        return float(valor.replace(",", "."))
    except ValueError:
        return 0.0


def mapear_presenca(valor):
    if pd.isna(valor):
        return np.nan
    valor = str(valor).strip().upper()
    if valor == "P":
        return 1.0
    if valor in {"A", "F"}:
        return 0.0
    return np.nan


def mapear_participacao(valor):
    if pd.isna(valor):
        return 1.0
    valor = str(valor).strip()
    mapping = {":-D": 3.0, ":-)": 2.0, ":-|": 1.0, ":-/": 1.0, ":-&": 0.0, ":-(": 0.0}
    return mapping.get(valor, 1.0)


def clean_dataset(long_df: pd.DataFrame) -> pd.DataFrame:
    df = long_df.rename(columns=METRIC_RENAME).copy()
    df["Aluno"] = df["NOME COMPLETO"].apply(extract_student_name)
    df["Unidade"] = df["Nome Planilha Feedback"].apply(extract_unit)
    df["Sala"] = df["Sala"].astype(str).str.strip()
    df["Data"] = pd.to_datetime(df["Data"], errors="coerce")

    df = df.dropna(subset=["Aluno", "Sala", "Unidade"])

    df["Fez a atividade antes da aula"] = df["Fez a atividade antes da aula"].apply(mapear_binario)
    df["Fez lição de casa"] = df["Fez lição de casa"].apply(mapear_binario)
    df["Presença/Ausencia"] = df["Presença/Ausencia"].apply(mapear_presenca)
    df["Participação"] = df["Participação"].apply(mapear_participacao)

    numeric_cols = ["Fez a atividade antes da aula", "Fez lição de casa", "Participação", "Presença/Ausencia"]
    df[numeric_cols] = df[numeric_cols].fillna(0)

    if "Comportamento" in df.columns:
        df = df.drop(columns=["Comportamento"])

    df["aluno_id"] = df.apply(build_student_id, axis=1)
    df = df.drop_duplicates(subset=["aluno_id", "Aula"] + numeric_cols)
    df = df.sort_values(["Unidade", "Sala", "Aluno", "Aula"]).reset_index(drop=True)

    desired_cols = [
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
    return df[desired_cols]


def recomendar_acao(row: pd.Series) -> str:
    if row["attendance_score"] < 0.6:
        return "Contato individual / planos de presença"
    if row["homework_score"] < 0.4 and row["prep_score"] < 0.4:
        return "Reforço assíncrono + tutoria"
    if row["interaction_score"] < 0.4:
        return "Ações de engajamento em sala"
    if row["engajamento"] > 0.8:
        return "Reforço positivo"
    return "Acompanhamento padrão"


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


def run_clustering(scores: pd.DataFrame, n_clusters: int = 4) -> Tuple[pd.DataFrame, pd.DataFrame]:
    metrics = ["prep_score", "attendance_score", "homework_score", "interaction_score", "engajamento"]
    grouped = scores.groupby(["aluno_id", "Aluno", "Sala", "Unidade"])[metrics].mean().reset_index()

    if grouped.empty:
        raise ValueError("Sem registros para clustering")

    target_clusters = min(n_clusters, len(grouped))
    if target_clusters < 1:
        raise ValueError("Não há alunos suficientes para clustering")

    scaler = StandardScaler()
    features = scaler.fit_transform(grouped[metrics])

    kmeans = KMeans(n_clusters=target_clusters, n_init=10, random_state=42)
    grouped["cluster"] = kmeans.fit_predict(features)

    cluster_profile = grouped.groupby("cluster")[metrics].mean().reset_index()
    return grouped, cluster_profile


def run_pipeline(raw_path: Path = RAW_WORKBOOK) -> PipelineArtifacts:
    if not raw_path.exists():
        raise FileNotFoundError(f"Arquivo não encontrado: {raw_path}")

    print("▶️ Carregando dados brutos...")
    raw_df = pd.read_excel(raw_path, skiprows=2)
    date_lookup = build_class_date_lookup(raw_path)

    print("▶️ Reestruturando aulas...")
    long_df = reshape_classes(raw_df, date_lookup)

    print("▶️ Limpando e padronizando valores...")
    clean_df = clean_dataset(long_df)
    clean_path = Path("eric-dados-compilados-LIMPO.csv")
    clean_df.to_csv(clean_path, index=False)

    print("▶️ Calculando scores...")
    scores_df = calculate_scores(clean_df)
    scores_path = Path("eric-dados-engajamento.csv")
    scores_df.to_csv(scores_path, index=False)

    print("▶️ Executando clustering...")
    clusters_df, profile_df = run_clustering(scores_df)
    clusters_path = Path("clusters_alunos.csv")
    profiles_path = Path("perfil_clusters.csv")
    clusters_df.to_csv(clusters_path, index=False)
    profile_df.to_csv(profiles_path, index=False)

    print("✅ Pipeline concluído")
    return PipelineArtifacts(clean_path, scores_path, clusters_path, profiles_path)


if __name__ == "__main__":
    run_pipeline()
