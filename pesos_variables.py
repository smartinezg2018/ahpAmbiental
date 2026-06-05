from pathlib import Path

from ahp import Ahp_calc
import numpy as np
import pandas as pd

ahp_calc = Ahp_calc()

TIPOS_PATH = Path(__file__).resolve().parent / "codigo_tipos(in).csv"
_tipos_df = pd.read_csv(TIPOS_PATH, sep=";", encoding="latin-1")
_tipos_df["Codigo"] = _tipos_df["Codigo"].astype(str).str.strip()
_tipos_df["Variable"] = _tipos_df["Variable"].astype(str).str.strip()
VARIABLES_POR_CODIGO = _tipos_df.drop_duplicates(subset="Codigo", keep="first").set_index("Codigo")["Variable"].to_dict()
# AMB-040-A aparece dos veces en el CSV; la fila de inundaciones es la de Amenazas físicas.
VARIABLES_POR_CODIGO["AMB-040-A"] = "inundaciones"


def _variable(codigo: str) -> str:
    return VARIABLES_POR_CODIGO[codigo]


# --- 1. Especies Bióticas ---
# Orden: Endémicas, IUCN (terrestre + marina), Migratorias, Pastos marinos, Reprod. aves, Aves playeras
CODIGOS_BIOTICAS = [
    ["AMB-003-A"],
    ["AMB-005-A"],
    ["AMB-017-A"],
    ["AMB-019-A"],
    ["AMB-020-A"],
    ["AMB-034-A"],
    ["AMB-038-A"],
]

matrix_bioticas = np.array([
    [1,   1,   3,   2,   4,   5, 1],
    [1,   1,   3,   2,   4,   5, 1],
    [1/3, 1/3, 1,   1/2, 2,   3, 1],
    [1/2, 1/2, 2,   1,   3,   4, 1],
    [1/4, 1/4, 1/2, 1/3, 1,   2, 1],
    [1/5, 1/5, 1/3, 1/4, 1/2, 1, 1],
    [1/5, 1/5, 1/3, 1/4, 1/2, 1, 1],
])

# --- 2. Áreas Protegidas ---
# Orden: Humedales RAMSAR, KBAs, Áreas coralinas, Playas tortugas
CODIGOS_PROTEGIDAS = [
    ["AMB-012-A"],
    ["AMB-033-A"],
    ["AMB-021-A"],
    ["AMB-036-A"],
]

matrix_protegidas = np.array([
    [1,   2,   1/2, 2],
    [1/2, 1,   1/4, 1],
    [2,   4,   1,   3],
    [1/2, 1,   1/3, 1],
])

# --- 3. Amenazas ---
# Orden: inundaciones/deslizamiento, catástrofes naturales (volcánica)
CODIGOS_AMENAZAS = [
    ["AMB-031-A"],
    ["AMB-041-A"],
]

matrix_amenazas = np.array([
    [1,   1.5],
    [2/3, 1  ],  # 1/1.5 ≈ 0.67
])

# --- 4. Condiciones Geológicas y Geotécnicas ---
# Orden: Cobertura suelos, Elevación, Pendiente, Batimetría, Fallas/Sismicidad, Litología/Fondos
CODIGOS_GEOLOGIA = [
    ["AMB-006-A"],
    ["AMB-007-AT"],
    ["AMB-008-AT"],
    ["AMB-029-AT"],
    ["AMB-030-AT"],
]

matrix_geologia = np.array([
    [1,   3,   2,   2,   1/3],
    [1/3, 1,   1/2, 1/2, 1/5],
    [1/2, 2,   1,   1,   1/4],
    [1/2, 2,   1,   1,   1/4],
    [3,   5,   4,   4,   1, ],
])

MATRICES_COLOMBIA = {
    "Especies Bióticas": (matrix_bioticas, CODIGOS_BIOTICAS),
    "Áreas Protegidas": (matrix_protegidas, CODIGOS_PROTEGIDAS),
    "Amenazas": (matrix_amenazas, CODIGOS_AMENAZAS),
    "Geología/Geotecnia": (matrix_geologia, CODIGOS_GEOLOGIA),
}


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
    """Devuelve {codigo: peso local} como fracción 0-1."""
    pesos: dict[str, float] = {}
    for matrix, codigos in MATRICES_COLOMBIA.values():
        weights = ahp_calc.calculate_weights([matrix])
        print(weights)
        print(codigos)
        for codigos_col, weight in zip(codigos, weights):
            for codigo in codigos_col:
                pesos[codigo] = weight
    return pesos


if __name__ == "__main__":
    for category, (matrix, codigos) in MATRICES_COLOMBIA.items():
        report_ahp(category, matrix, codigos)
