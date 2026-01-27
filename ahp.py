import numpy as np

def normalizar_matriz(matriz):
    return matriz / np.sum(matriz, axis=0)

def vector_prioridades(matriz_normalizada):
    return np.mean(matriz_normalizada, axis=1)

def consistencia(matriz, pesos):
    n = matriz.shape[0]
    lambda_max = np.mean(np.dot(matriz, pesos) / pesos)
    CI = (lambda_max - n) / (n - 1)

    RI_dict = {1:0, 2:0, 3:0.58, 4:0.90, 5:1.12}
    RI = RI_dict[n]
    CR = CI / RI if RI != 0 else 0
    return CI, CR

def ahp(matriz):
    matriz_norm = normalizar_matriz(matriz)
    pesos = vector_prioridades(matriz_norm)
    CI, CR = consistencia(matriz, pesos)
    return pesos, CI, CR

def media_geometrica(matrices):
    producto = np.ones_like(matrices[0])
    for m in matrices:
        producto *= m
    return producto ** (1 / len(matrices))


# Stakeholder 1
criterios_s1 = np.array([
    [1,   3,   5],
    [1/3, 1,   2],
    [1/5, 1/2, 1]
])

# Stakeholder 2
criterios_s2 = np.array([
    [1,   4,   7],
    [1/4, 1,   3],
    [1/7, 1/3, 1]
])

# Stakeholder 3
criterios_s3 = np.array([
    [1,   2,   4],
    [1/2, 1,   3],
    [1/4, 1/3, 1]
])


criterios_agregados = media_geometrica(
    [criterios_s1, criterios_s2, criterios_s3]
)

pesos_criterios, CI_c, CR_c = ahp(criterios_agregados)


C1 = np.array([
    [1,   4,   7],
    [1/4, 1,   3],
    [1/7, 1/3, 1]
])

C2 = np.array([
    [1,   1/2, 4],
    [2,   1,   6],
    [1/4, 1/6, 1]
])

C3 = np.array([
    [1,   3,   5],
    [1/3, 1,   2],
    [1/5, 1/2, 1]
])

pesos_C1, CI1, CR1 = ahp(C1)
pesos_C2, CI2, CR2 = ahp(C2)
pesos_C3, CI3, CR3 = ahp(C3)


matriz_alternativas = np.vstack([pesos_C1, pesos_C2, pesos_C3])
resultado_final = np.dot(pesos_criterios, matriz_alternativas)


print("Matriz de criterios agregada:\n", criterios_agregados)
print("\nPesos de criterios:", pesos_criterios)
print("CR criterios:", CR_c)

print("\nPesos alternativas C1:", pesos_C1, "CR:", CR1)
print("Pesos alternativas C2:", pesos_C2, "CR:", CR2)
print("Pesos alternativas C3:", pesos_C3, "CR:", CR3)

print("\nRanking final de alternativas:")
print("A1:", resultado_final[0])
print("A2:", resultado_final[1])
print("A3:", resultado_final[2])
