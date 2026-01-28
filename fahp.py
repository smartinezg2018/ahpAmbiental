"""
Fuzzy AHP con múltiples stakeholders
Autor: ---
Descripción:
- Método Fuzzy AHP usando números triangulares difusos (TFN)
- Agregación de encuestas de stakeholders
- Media geométrica difusa
- Defuzzificación por centroide
"""

import numpy as np

# ======================================================
# 1. Funciones auxiliares para números fuzzy triangulares
# ======================================================

def geometric_mean_fuzzy(values):
    """
    Calcula la media geométrica difusa de una lista de TFN
    """
    n = len(values)
    l = np.prod([v[0] for v in values]) ** (1/n)
    m = np.prod([v[1] for v in values]) ** (1/n)
    u = np.prod([v[2] for v in values]) ** (1/n)
    return (l, m, u)


def defuzzify_centroid(tfn):
    """
    Defuzzificación por método del centroide
    """
    l, m, u = tfn
    return (l + m + u) / 3


# ======================================================
# 2. Agregación de matrices de stakeholders
# ======================================================

def aggregate_fuzzy_matrices(stakeholders):
    """
    Agrega matrices fuzzy de múltiples stakeholders
    usando media geométrica difusa
    """
    n = len(stakeholders[0])
    aggregated = [[None for _ in range(n)] for _ in range(n)]

    for i in range(n):
        for j in range(n):
            values = [s[i][j] for s in stakeholders]
            aggregated[i][j] = geometric_mean_fuzzy(values)

    return aggregated


# ======================================================
# 3. Cálculo de pesos fuzzy (Fuzzy AHP)
# ======================================================

def fuzzy_ahp_weights(fuzzy_matrix):
    """
    Calcula pesos fuzzy usando el método
    de la media geométrica
    """
    n = len(fuzzy_matrix)
    fuzzy_gm = []

    # Media geométrica por fila
    for i in range(n):
        l = np.prod([fuzzy_matrix[i][j][0] for j in range(n)]) ** (1/n)
        m = np.prod([fuzzy_matrix[i][j][1] for j in range(n)]) ** (1/n)
        u = np.prod([fuzzy_matrix[i][j][2] for j in range(n)]) ** (1/n)
        fuzzy_gm.append((l, m, u))

    # Sumas
    sum_l = sum(w[0] for w in fuzzy_gm)
    sum_m = sum(w[1] for w in fuzzy_gm)
    sum_u = sum(w[2] for w in fuzzy_gm)

    # Normalización fuzzy
    fuzzy_weights = [
        (w[0] / sum_u, w[1] / sum_m, w[2] / sum_l)
        for w in fuzzy_gm
    ]

    return fuzzy_weights


# ======================================================
# 4. Normalización crisp
# ======================================================

def normalize_weights(weights):
    total = sum(weights)
    return [w / total for w in weights]


# ======================================================
# 5. Ejemplo de entrada (encuestas)
# ======================================================

"""
Ejemplo:
3 criterios
3 stakeholders
Cada stakeholder llena una matriz fuzzy de comparación pareada
"""

stakeholders = [
    # Stakeholder 1
    [
        [(1,1,1), (2,3,4), (4,5,6)],
        [(1/4,1/3,1/2), (1,1,1), (2,3,4)],
        [(1/6,1/5,1/4), (1/4,1/3,1/2), (1,1,1)]
    ],
    # Stakeholder 2
    [
        [(1,1,1), (4,5,6), (6,7,8)],
        [(1/6,1/5,1/4), (1,1,1), (2,3,4)],
        [(1/8,1/7,1/6), (1/4,1/3,1/2), (1,1,1)]
    ],
    # Stakeholder 3
    [
        [(1,1,1), (2,3,4), (6,7,8)],
        [(1/4,1/3,1/2), (1,1,1), (4,5,6)],
        [(1/8,1/7,1/6), (1/6,1/5,1/4), (1,1,1)]
    ]
]

criteria = ["Costo", "Calidad", "Riesgo"]

# ======================================================
# 6. Ejecución del modelo
# ======================================================

# Agregación de stakeholders
fuzzy_matrix = aggregate_fuzzy_matrices(stakeholders)

# Pesos fuzzy
fuzzy_weights = fuzzy_ahp_weights(fuzzy_matrix)

# Defuzzificación
crisp_weights = [defuzzify_centroid(w) for w in fuzzy_weights]

# Normalización final
final_weights = normalize_weights(crisp_weights)

# ======================================================
# 7. Resultados
# ======================================================

print("\nPESOS FINALES (Fuzzy AHP):\n")

for c, w in zip(criteria, final_weights):
    print(f"{c}: {w:.4f}")

