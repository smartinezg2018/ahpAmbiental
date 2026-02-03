import numpy as np
import pandas as pd
import random

class Transformer:

    def calculate_weights(self, matrices):
        matrix = self.geomean(matrices)
        norm_matrix = self.normalize_matrix(matrix)
        return self.define_weights(norm_matrix)

    # geometrical mean
    def geomean(self, matrices):
        base = np.ones((len(matrices[0]),len(matrices[0][0])))
        for matrix in matrices:
            base*=matrix
        base = base**(1/len(matrices[0]))
        return base

    #normalización de las matrices
    def normalize_matrix(self, matrix):
        norm_matrix = matrix.transpose().copy()
        for i in range(len(norm_matrix)):
            sum = norm_matrix[i].sum()
            for j in range(len(norm_matrix[i])):
                norm_matrix[i][j] = norm_matrix[i][j]/sum 
        return norm_matrix.transpose()

    #calculo de los pesos dentro de la matriz
    def define_weights(self, matrix):
        weights = []
        for i in range(len(matrix)):
            weights.append(matrix[i].mean())
        return weights
    
    def consistency_rate(self, matrices):
        RI = {
            1: 0.00, 2: 0.00, 3: 0.58,
            4: 0.90, 5: 1.12, 6: 1.24,
            7: 1.32, 8: 1.41, 9: 1.45,
            10: 1.49, 11: 1.51, 12: 1.48,
            13: 1.56,14: 1.57,15: 1.59, 16:1.62
        }

        scores = []

        for i,matrix in enumerate(matrices):
            weights = self.define_weights(self.normalize_matrix(matrix))
            eigvals, eigvecs = np.linalg.eig(matrix)
            n = len(matrix)
            nmax = max(eigvals.real)
            CI = (nmax-n)/(n-1)
            CR = CI/RI[n]
            scores.append(CR)
            print(f"matrix {i+1} score: ",nmax," ", CR )
        return scores

    def simulate_matrices(self, dm_number = 3,criteria_number = 4):
        matrices = []
        for _ in range(dm_number):
            matrix = np.ones((criteria_number,criteria_number))
            for i in range(0,len(matrix)):
                for j in range(i+1,len(matrix[0])):
                    matrix[i][j] = random.randint(1,9)
                    matrix[j][i] = 1/matrix[i][j]

            matrices.append(matrix)
        return np.array(matrices)
