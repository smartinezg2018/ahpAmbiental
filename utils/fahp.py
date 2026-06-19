import numpy as np
import random

class Transformer:
        #normalización de las matrices
    def normalize_matrix(self, matrix):
        norm_matrix = matrix.transpose().copy()
        for i in range(len(norm_matrix)):
            sum = norm_matrix[i].sum()
            for j in range(len(norm_matrix[i])):
                norm_matrix[i][j] = norm_matrix[i][j]/sum 
        return norm_matrix.transpose()
    
    #calculo de los pesos dentro de la matriz
    def define_weights_ahp(self, matrix):
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
            weights = self.define_weights_ahp(self.normalize_matrix(matrix))
            eigvals, eigvecs = np.linalg.eig(matrix)
            n = len(matrix)
            nmax = max(eigvals.real)
            CI = (nmax-n)/(n-1)
            CR = CI/RI[n]
            scores.append(CR)
            print(f"matrix {i+1} CR:", CR )
        return scores
    
    def calculate_weights(self, matrices):
        fuzzy_matrices = np.array([self.create_fuzzy_matrix(matrix) for matrix in matrices])
        fuzzy_matrix = self.geomean_fuzzy_matrices(fuzzy_matrices)
        matrix = self.geomean_fuzzy_matrix(fuzzy_matrix)
        weights = self.define_weights(matrix)
        return weights

    def geomean_matrices(self,matrices):
        base = np.ones((len(matrices[0]),len(matrices[0][0])))
        for matrix in matrices:
            base*=matrix
        base = base**(1/len(matrices[0]))
        return base
    
    def geomean_fuzzy_matrices(self,matrices):
        n = len(matrices[0])
        base = np.ones((n,n,3))
        for i in range(n):
            for j in range(n):
                j
                for i_matrix in range(len(matrices)):
                    base[i][j]*=matrices[i_matrix][i][j]
                base[i][j]**=(1/len(matrices))
        return base

    def create_fuzzy_matrix(self,matrix):
        n = len(matrix)
        fuzzy_matrix = np.empty((n,n,3))
        for i in range(n):
            for j in range(n):
                value = matrix[i][j]
                if(value<1): 
                    continue
                fuzzy_matrix[i][j] = np.array([value]*3)
                if value!= 9 and value != 1:
                    fuzzy_matrix[i][j][0]-=1
                    fuzzy_matrix[i][j][2]+=1

                fuzzy_matrix[j][i] = 1/fuzzy_matrix[i][j]
        return fuzzy_matrix
    
    def geomean_fuzzy_matrix(self,matrix):
        n = len(matrix)
        geo_mean = []
        for i in range(n):
            base = np.ones((3))
            for j in range(n):
                base *= matrix[i][j]
            geo_mean.append(base**(1/n))
        
        return geo_mean
    
    def define_weights(self, geo_mean, u = 0.5):
        ans = []
        for l , m, h in geo_mean:
            ans.append(u*l+(1-u)*h)
            # ans.append((l+m+h)/3)
        ans = np.array(ans)
        return np.array(ans/sum(ans))
    
    
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
    