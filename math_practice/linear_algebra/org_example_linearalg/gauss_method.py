import numpy as np


def _find_pivot_row(augmented_matrix, i):
    return np.argmax(np.abs(augmented_matrix[i:, i])) + i


def _eliminate_rows(augmented_matrix, i, rows):
    for j in range(i + 1, rows):
        augmented_matrix[j] -= augmented_matrix[j, i] * augmented_matrix[i]


def _back_substitution(augmented_matrix, cols, rows):
    solution = np.zeros(cols - 1)
    for i in range(rows - 1, -1, -1):
        dot_product = np.dot(augmented_matrix[i, i + 1 : -1], solution[i + 1 :])
        last_number = augmented_matrix[i, -1]
        solution[i] = last_number - dot_product
    return solution


def solve(coefficient_matrix: np.ndarray, constant_vector: np.ndarray):
    augmented_matrix = np.column_stack((coefficient_matrix, constant_vector))

    rows, cols = augmented_matrix.shape

    for i in range(min(rows, cols - 1)):
        pivot_row = _find_pivot_row(augmented_matrix, i)

        # Swap rows if necessary
        augmented_matrix[[i, pivot_row]] = augmented_matrix[[pivot_row, i]]

        # Normalize the pivot row
        augmented_matrix[i] /= augmented_matrix[i, i]

        _eliminate_rows(augmented_matrix, i, rows)

    return _back_substitution(augmented_matrix, cols, rows)
