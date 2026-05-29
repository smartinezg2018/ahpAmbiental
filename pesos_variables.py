from ahp import Transformer
import numpy as np
import pandas as pd

transformer = Transformer()

# --- 1. Especies Bióticas ---
# Orden: Endémicas, IUCN, Migratorias, Pastos marinos, Zona reprod. aves, Aves playeras
labels_bioticas = [
    "Especies endémicas",
    "Especies IUCN",
    "Especies migratorias",
    "Pastos marinos",
    "Zona reprod. aves",
    "Aves playeras",
]

matrix_bioticas = np.array([
    [1,   1,   3,   2,   4,   5],
    [1,   1,   3,   2,   4,   5],
    [1/3, 1/3, 1,   1/2, 2,   3],
    [1/2, 1/2, 2,   1,   3,   4],
    [1/4, 1/4, 1/2, 1/3, 1,   2],
    [1/5, 1/5, 1/3, 1/4, 1/2, 1],
])

# --- 2. Áreas Protegidas ---
# Orden: Humedales RAMSAR, Áreas KBA, Áreas coralinas, Playas tortugas
labels_protegidas = [
    "Humedales RAMSAR",
    "Áreas KBA",
    "Áreas coralinas",
    "Playas tortugas",
]

matrix_protegidas = np.array([
    [1,   2,   1/2, 2],
    [1/2, 1,   1/4, 1],
    [2,   4,   1,   3],
    [1/2, 1,   1/3, 1],
])

# --- 3. Amenazas ---
# Orden: Riesgo físico (inundación/deslizamiento), Amenaza volcánica
labels_amenazas = [
    "Riesgo físico (inundación/deslizamiento)",
    "Amenaza volcánica",
]

matrix_amenazas = np.array([
    [1,   1.5],
    [2/3, 1  ],  # 1/1.5 ≈ 0.67
])

# --- 4. Condiciones Geológicas y Geotécnicas ---
# Orden: Uso del suelo, Elevación, Pendiente, Batimetría, Fallas/Sismicidad, Litología/Fondos
labels_geologia = [
    "Uso del suelo",
    "Elevación",
    "Pendiente",
    "Batimetría",
    "Fallas/Sismicidad",
    "Litología/Fondos",
]

matrix_geologia = np.array([
    [1,   3,   2,   2,   1/3, 4],
    [1/3, 1,   1/2, 1/2, 1/5, 2],
    [1/2, 2,   1,   1,   1/4, 3],
    [1/2, 2,   1,   1,   1/4, 3],
    [3,   5,   4,   4,   1,   6],
    [1/4, 1/2, 1/3, 1/3, 1/6, 1],
])

MATRICES_COLOMBIA = {
    "Especies Bióticas": (matrix_bioticas, labels_bioticas),
    "Áreas Protegidas": (matrix_protegidas, labels_protegidas),
    "Amenazas": (matrix_amenazas, labels_amenazas),
    "Geología/Geotecnia": (matrix_geologia, labels_geologia),
}


def report_ahp(category, matrix, labels):
    """Imprime consistencia y tabla de pesos locales (%)."""
    print(f"\n{'=' * 60}\n{category}\n{'=' * 60}")
    transformer.consistency_rate([matrix])
    weights = transformer.calculate_weights([matrix])
    df = pd.DataFrame({
        "Sub-criterio": labels,
        "Peso local (%)": [round(w * 100, 1) for w in weights],
    })
    print(df.to_string(index=False))
    return df


for category, (matrix, labels) in MATRICES_COLOMBIA.items():
    report_ahp(category, matrix, labels)