from pathlib import Path

try:
    from utils.ahp import Ahp_calc
except ImportError:
    from ahp import Ahp_calc
import numpy as np
import pandas as pd

ahp_calc = Ahp_calc()

TIPOS_PATH = Path(__file__).resolve().parent.parent / "seeds" / "codigo_tipos(in).csv"
_tipos_df = pd.read_csv(TIPOS_PATH, sep=";", encoding="latin-1")
_tipos_df["Codigo"] = _tipos_df["Codigo"].astype(str).str.strip()
_tipos_df["Variable"] = _tipos_df["Variable"].astype(str).str.strip()
VARIABLES_POR_CODIGO = _tipos_df.drop_duplicates(subset="Codigo", keep="first").set_index("Codigo")["Variable"].to_dict()
# AMB-040-A aparece dos veces en el CSV; la fila de inundaciones es la de Amenazas físicas.
VARIABLES_POR_CODIGO["AMB-040-A"] = "inundaciones"


def _variable(codigo: str) -> str:
    return VARIABLES_POR_CODIGO[codigo]




# --- 1. Especies Bióticas (n=8) ---
# Orden columnas/filas: Endémicas, Migratorias, Marinas IUCN, Aves IUCN,
#                       Murciélagos IUCN, Pastos marinos, Aves playeras, Reproducción aves
CODIGOS_BIOTICAS = [
    ["AMB-005-A"],   # AMB-005 Especies endémicas
    ["AMB-003-A"],   # AMB-003 Especies migratorias
    ["AMB-019-A"],   # AMB-019 Especies marinas listadas en la IUCN
    ["AMB-017-A"],   # AMB-017 Especies aves IUCN
    ["AMB-042-A"],   # AMB-042 Especies murciélagos IUCN
    ["AMB-020-A"],   # AMB-020 Pastos marinos
    ["AMB-038-A"],   # AMB-038 Congregación de aves playeras
    ["AMB-034-A"],   # AMB-034 Zona reproducción aves
]

matrix_bioticas = np.array([
    [1,    5,    2,    2,    2,    3,    4,    4],
    [1/5,  1,    1/3,  1/3,  1/3,  1/2,  1,    1],
    [1/2,  3,    1,    1,    1,    2,    3,    3],
    [1/2,  3,    1,    1,    1,    2,    3,    3],
    [1/2,  3,    1,    1,    1,    2,    3,    3],
    [1/3,  2,    1/2,  1/2,  1/2,  1,    2,    2],
    [1/4,  1,    1/3,  1/3,  1/3,  1/2,  1,    1],
    [1/4,  1,    1/3,  1/3,  1/3,  1/2,  1,    1],
])

# --- 2. Áreas Protegidas (n=4) ---
# Orden: KBAs, Humedales RAMSAR, Áreas coralinas, Playas anidación tortugas
CODIGOS_PROTEGIDAS = [
    ["AMB-033-A"],   # AMB-033 KBAs / áreas clave de biodiversidad
    ["AMB-012-A"],   # AMB-012 Humedales RAMSAR
    ["AMB-021-A"],   # AMB-021 Áreas coralinas
    ["AMB-036-A"],   # AMB-036 Playas de anidación de tortugas
]

matrix_protegidas = np.array([
    [1,    1/3,  1/5,  1/2],
    [3,    1,    1/3,  2],
    [5,    3,    1,    4],
    [2,    1/2,  1/4,  1],
])

# --- 3. Amenazas (n=2) ---
# Orden: Riesgo físico relativo (TEC-015), Amenaza volcánica (TEC-016).
# TEC-015 -> AMB-040-A (Amenazas múltiples / riesgo físico combinado),
# TEC-016 -> AMB-009-A (Zonas de riesgo catástrofes naturales / volcánica).
CODIGOS_AMENAZAS = [
    ["AMB-040-A"],   # TEC-015 Riesgo físico relativo
    ["AMB-009-A"],   # TEC-016 Amenaza volcánica
]

matrix_amenazas = np.array([
    [1,   3],
    [1/3, 1],
])

# --- 4. Condiciones Geológicas y Geotécnicas (n=5) ---
# Orden: Uso/cobertura suelo, Fallas/Sismicidad (TEC-013), Litología y fondos (TEC-021),
#        Pendiente, Elevación.
# TEC-013 -> AMB-039-A (Fallas activas y zonas de fractura),
# TEC-021 -> AMB-028-AT + AMB-029-AT (Suelos/litología + Fondos marinos).
# Definición de códigos actualizados con la separación de Litología y Fondos Marinos
CODIGOS_GEOLOGIA = [
    ["AMB-031-A"],    # Sismicidad / Fallas (Factor crítico en Colombia)
    ["AMB-028-AT"],   # Litología (Capacidad de carga de la cimentación)
    ["AMB-030-AT"],   # Batimetría (Profundidad y selección tecnológica)
    ["AMB-029-AT"],   # Fondos marinos (Estabilidad superficial)
    ["AMB-006-A"],    # Uso / cobertura de suelo (Compatibilidad territorial)
    ["AMB-007-AT"],   # Pendiente del terreno (Riesgo de remoción en masa)
    ["AMB-008-AT"],   # Elevación (Accesibilidad y costos logísticos)
]

# Matriz AHP (7x7) basada en la escala de Saaty [4, 6]
# Representa la importancia relativa de las filas sobre las columnas
matrix_geologia = np.array([
    [1,3,4,5,6,7, 8],      # AMB-039-A
    [1/3,    1,      2,      3,      4,      5,      6],      # AMB-028-AT
    [1/4,    1/2,    1,      2,      3,      4,      5],      # AMB-030-AT
    [1/5,    1/3,    1/2,    1,      2,      3,      4],      # AMB-029-AT
    [1/6,    1/4,    1/3,    1/2,    1,      2,      3],      # AMB-006-A
    [1/7,    1/5,    1/4,    1/3,    1/2,    1,      2],      # AMB-007-AT
    [1/8,    1/6,    1/5,    1/4,    1/3,    1/2,    1],      # AMB-008-AT
])

MATRICES_COLOMBIA = {
    "Especies Bióticas": (matrix_bioticas, CODIGOS_BIOTICAS),
    "Áreas Protegidas": (matrix_protegidas, CODIGOS_PROTEGIDAS),
    "Amenazas": (matrix_amenazas, CODIGOS_AMENAZAS),
    "Geología/Geotecnia": (matrix_geologia, CODIGOS_GEOLOGIA),
}

# Subcriterios bióticos: especies vs áreas protegidas.
GRUPOS_SUB_BIOTICAS = [
    "Especies Bióticas",
    "Áreas Protegidas",
]

matrix_sub_bioticas = np.array([
    [1,   1/3],
    [3,   1],
])

# Subcriterios abióticos: amenazas vs geología/geotecnia.
GRUPOS_SUB_ABIOTICAS = [
    "Amenazas",
    "Geología/Geotecnia",
]

matrix_sub_abioticas = np.array([
    [1,   2],
    [1/2, 1],
])

MATRICES_JERARQUIA = {
    "Subcriterios Bióticos": (matrix_sub_bioticas, GRUPOS_SUB_BIOTICAS),
    "Subcriterios Abióticos": (matrix_sub_abioticas, GRUPOS_SUB_ABIOTICAS),
}

# Subcriterios del CSV (Amenazas, Especies, Condiciones, Areas) → categoría AHP hoja.
SUBCRITERIO_A_CATEGORIA = {
    "Especies": "Especies Bióticas",
    "Areas": "Áreas Protegidas",
    "Condiciones": "Geología/Geotecnia",
    "Amenazas": "Amenazas",
}

SUBCRITERIOS = tuple(SUBCRITERIO_A_CATEGORIA.keys())

SUBCRITERIOS_BIOTICAS = ("Especies", "Areas")
SUBCRITERIOS_ABIOTICAS = ("Condiciones", "Amenazas")

PESO_RAMA_BIOTICAS = 0.5
PESO_RAMA_ABIOTICAS = 0.5


def pesos_grupo_subcriterio(grupo: str) -> dict[str, float]:
    """Pesos AHP dentro de la rama biótica o abiótica (suma 1)."""
    if grupo == "bioticas":
        weights = ahp_calc.calculate_weights([matrix_sub_bioticas])
        labels = SUBCRITERIOS_BIOTICAS
    elif grupo == "abioticas":
        weights = ahp_calc.calculate_weights([matrix_sub_abioticas])
        labels = SUBCRITERIOS_ABIOTICAS
    else:
        raise ValueError(f"Grupo desconocido: {grupo}")
    return dict(zip(labels, weights))


def combinar_score_grupo(
    scores_subcriterio: pd.DataFrame,
    grupo: str,
) -> pd.Series:
    """Combina Especies+Areas (bióticas) o Condiciones+Amenazas (abióticas)."""
    pesos = pesos_grupo_subcriterio(grupo)
    score = pd.Series(0.0, index=scores_subcriterio.index)
    for sub, peso in pesos.items():
        if sub in scores_subcriterio.columns:
            score += peso * scores_subcriterio[sub]
    return score


def cols_por_subcriterio(
    codigos: list[str],
    codigo_subcriterio: dict[str, str],
) -> dict[str, list[str]]:
    """Agrupa códigos AMB por subcriterio (Amenazas, Especies, Condiciones, Areas)."""
    cols: dict[str, list[str]] = {sub: [] for sub in SUBCRITERIOS}
    for codigo in codigos:
        sub = str(codigo_subcriterio.get(codigo, "")).strip()
        if sub in cols:
            cols[sub].append(codigo)
    return {sub: cols_sub for sub, cols_sub in cols.items() if cols_sub}


def pesos_subcriterio_label() -> dict[str, float]:
    """Pesos globales por subcriterio (Amenazas, Especies, Condiciones, Areas), suma 1."""
    pesos_cat = pesos_subcriterios_dict()
    pesos = {
        sub: pesos_cat[categoria]
        for sub, categoria in SUBCRITERIO_A_CATEGORIA.items()
    }
    total = sum(pesos.values())
    return {sub: w / total for sub, w in pesos.items()}


def combinar_scores_subcriterio(
    df: pd.DataFrame,
    codigo_subcriterio: dict[str, str],
    pesos_local: dict[str, float] | None = None,
) -> pd.DataFrame:
    """Combina columnas AMB en scores por subcriterio con pesos locales AHP."""
    if pesos_local is None:
        pesos_local = pesos_dict()

    amb_cols = [c for c in df.columns if str(c).startswith("AMB-")]
    cols_por_sub = cols_por_subcriterio(amb_cols, codigo_subcriterio)

    scores = pd.DataFrame(index=df.index)
    for sub, cols in cols_por_sub.items():
        cols_con_peso = [c for c in cols if c in pesos_local]
        if not cols_con_peso:
            continue
        pesos = np.array([pesos_local[c] for c in cols_con_peso], dtype=float)
        pesos = pesos / pesos.sum()
        scores[sub] = df[cols_con_peso].mul(pesos, axis=1).sum(axis=1)
    return scores


def combinar_score_ahp_global(scores_subcriterio: pd.DataFrame) -> pd.Series:
    """Combinación jerárquica AHP: rama biótica y abiótica con peso 50% cada una."""
    score_bioticas = combinar_score_grupo(scores_subcriterio, "bioticas")
    score_abioticas = combinar_score_grupo(scores_subcriterio, "abioticas")
    return (
        PESO_RAMA_BIOTICAS * score_bioticas
        + PESO_RAMA_ABIOTICAS * score_abioticas
    )


def pesos_subcriterios_dict() -> dict[str, float]:
    """Devuelve {categoría: peso} de subcriterios bióticos y abióticos (fracción 0-1)."""
    w_sub_bioticas = ahp_calc.calculate_weights([matrix_sub_bioticas])
    w_sub_abioticas = ahp_calc.calculate_weights([matrix_sub_abioticas])
    return {
        **dict(zip(GRUPOS_SUB_BIOTICAS, w_sub_bioticas)),
        **dict(zip(GRUPOS_SUB_ABIOTICAS, w_sub_abioticas)),
    }


def _weights_table_grupos(grupos: list[str], weights: list[float]) -> pd.DataFrame:
    return pd.DataFrame({
        "Grupo": grupos,
        "Peso (%)": [round(w * 100, 1) for w in weights],
    })


def report_ahp_grupos(category: str, matrix: np.ndarray, grupos: list[str]) -> pd.DataFrame:
    """Imprime consistencia y tabla de pesos (%) para matrices jerárquicas."""
    print(f"\n{'=' * 60}\n{category}\n{'=' * 60}")
    ahp_calc.consistency_rate([matrix])
    weights = ahp_calc.calculate_weights([matrix])
    df = _weights_table_grupos(grupos, weights)
    print(df.to_string(index=False))
    return df


def _weights_table(codigos_por_columna: list[list[str]], weights: list[float]) -> pd.DataFrame:
    rows = []
    for codigos, weight in zip(codigos_por_columna, weights):
        pct = round(weight * 100, 1)
        for codigo in codigos:
            rows.append({
                "Codigo": codigo,
                "Variable": _variable(codigo),
                "Peso local (%)": pct,
            })
    return pd.DataFrame(rows)


def report_ahp(category, matrix, codigos_por_columna):
    """Imprime consistencia y tabla de pesos locales (%) por código AMB."""
    print(f"\n{'=' * 60}\n{category}\n{'=' * 60}")
    ahp_calc.consistency_rate([matrix])
    weights = ahp_calc.calculate_weights([matrix])
    df = _weights_table(codigos_por_columna, weights)
    print(df.to_string(index=False))
    return df


def pesos_por_codigo() -> pd.DataFrame:
    """Devuelve pesos locales concatenados de todas las categorías AHP."""
    frames = []
    for category, (matrix, codigos) in MATRICES_COLOMBIA.items():
        print(category)
        print(matrix)
        print(codigos)
        weights = ahp_calc.calculate_weights([matrix])
        df = _weights_table(codigos, weights)
        df.insert(0, "Categoría AHP", category)
        frames.append(df)
    return pd.concat(frames, ignore_index=True)


def pesos_dict() -> dict[str, float]:
    """Devuelve {codigo: peso local} como fracción 0-1 dentro de su categoría hoja."""
    pesos: dict[str, float] = {}
    for matrix, codigos in MATRICES_COLOMBIA.values():
        weights = ahp_calc.calculate_weights([matrix])
        for codigos_col, weight in zip(codigos, weights):
            for codigo in codigos_col:
                pesos[codigo] = weight
    return pesos


def pesos_dict_global() -> dict[str, float]:
    """Devuelve {codigo: peso global} = peso categoría × peso local."""
    pesos_categoria = pesos_subcriterios_dict()
    pesos: dict[str, float] = {}
    for categoria, (matrix, codigos) in MATRICES_COLOMBIA.items():
        peso_categoria = pesos_categoria[categoria]
        weights = ahp_calc.calculate_weights([matrix])
        for codigos_col, weight in zip(codigos, weights):
            for codigo in codigos_col:
                pesos[codigo] = peso_categoria * weight
    return pesos


def pesos_globales_por_codigo() -> pd.DataFrame:
    """Tabla con peso de categoría, peso local y peso global por código AMB."""
    pesos_categoria = pesos_subcriterios_dict()
    rows = []
    for categoria, (matrix, codigos) in MATRICES_COLOMBIA.items():
        peso_cat = pesos_categoria[categoria]
        weights = ahp_calc.calculate_weights([matrix])
        for codigos_col, weight in zip(codigos, weights):
            for codigo in codigos_col:
                rows.append({
                    "Categoría AHP": categoria,
                    "Codigo": codigo,
                    "Variable": _variable(codigo),
                    "Peso categoría (%)": round(peso_cat * 100, 1),
                    "Peso local (%)": round(weight * 100, 1),
                    "Peso global (%)": round(peso_cat * weight * 100, 2),
                })
    return pd.DataFrame(rows)


if __name__ == "__main__":
    for category, (matrix, grupos) in MATRICES_JERARQUIA.items():
        report_ahp_grupos(category, matrix, grupos)

    for category, (matrix, codigos) in MATRICES_COLOMBIA.items():
        report_ahp(category, matrix, codigos)

    print(f"\n{'=' * 60}\nPesos globales por código\n{'=' * 60}")
    print(pesos_globales_por_codigo().to_string(index=False))
