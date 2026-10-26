"""
References
----------
[1] Jim Hefferon, Mathematics and Statistics,
    Saint Michael's College Colchester, Vermont USA 05439
    2020-Apr-26.

[2] https://hefferon.net/linearalgebra/
"""

import numpy as np
import org_example_linearalg.gauss_method as gauss


def test_example1_3():
    """
    References
    ----------
    [1] Page 3.
    """

    # given
    coefficient_matrix = np.array(
        [
            [3, 2],
            [-1, 1],
        ]
    )

    constant_vector = np.array([7, 6])

    # when
    result_vector = np.linalg.solve(coefficient_matrix, constant_vector)

    # then
    x1, x2 = result_vector
    assert -1 == x1
    assert 5 == x2


def test_example1_4_with_custom_gauss_method():
    """
    References
    ----------
    [1] Page 3.
    [2] gauss_method_example1_4.tex
    """

    # given
    coefficient_matrix = np.array([[0, 0, 3], [1, 5, -2], [1 / 3, 2, 0]])

    constant_vector = np.array([9, 2, 3])

    # when
    result_vector = gauss.solve(coefficient_matrix, constant_vector)

    # then
    x1, x2, x3 = result_vector
    assert 3 == x1
    assert 1 == x2
    assert 3 == x3


def test_example1_4():
    """
    References
    ----------
    [1] Page 3.
    [2] gauss_method_example1_4.tex
    """

    # given
    coefficient_matrix = np.array([[0, 0, 3], [1, 5, -2], [1 / 3, 2, 0]])

    constant_vector = np.array([9, 2, 3])

    # when
    result_vector = np.linalg.solve(coefficient_matrix, constant_vector)

    # then
    x1, x2, x3 = result_vector
    assert 3 == x1
    assert 1 == x2
    assert 3 == x3


def test_example1_7():
    """
    References
    ----------
    [1] Page 5.
    """

    # given
    coefficient_matrix = np.array([[1, 1, 0], [2, -1, 3], [1, -2, -1]])

    constant_vector = np.array([0, 3, 3])

    # when
    result_vector = np.linalg.solve(coefficient_matrix, constant_vector)

    # then
    x, y, z = result_vector
    assert 1 == x
    assert -1 == y
    assert 0 == z


def test_example1_8():
    """
    References
    ----------
    [1] Page 5.
    """

    # given
    coefficient_matrix = np.array(
        [
            [40, 15],
            [-50, 25],
        ]
    )

    constant_vector = np.array([100, 50])

    # when
    result_vector = np.linalg.solve(coefficient_matrix, constant_vector)

    # then
    h, c = result_vector
    assert 1 == h
    assert 4 == c
