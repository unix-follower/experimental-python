import logging
import math
import textwrap

import sympy as sp
from sympy import Symbol, init_printing, lambdify, symbols

from math_practice.algebra.org_example_math.config.logging_config import logger

init_printing(use_latex=True)


def x_square(x):
    """
    f(x) = x²

    f'(x) = 2x

    :return: Tuple of f(x), derivative, f'(x)
    """
    _x = Symbol("x")
    expr = _x**2
    derivative = expr.diff(_x)
    f1 = lambdify(_x, derivative)
    result = f1(x)

    y_result = lambdify(_x, expr)(x)

    if logger.isEnabledFor(logging.INFO):
        msg = textwrap.dedent(
            f"""
            f(x) = {expr} = {y_result}
            f'(x) = {derivative} = {result}
            """
        )
        logger.info(msg)

    return y_result, derivative, result


def ax_in_power_n(a, n, x):
    """
    y = axⁿ

    dy/dx = anxⁿ⁻¹

    :return: Tuple of f(x), derivative, f'(x)
    """
    _a, _n, _x = symbols("a n x")
    expr = _a * _x**_n
    derivative = expr.diff(_x)
    f1 = lambdify((_a, _n, _x), derivative)
    result = f1(a, n, x)

    powered_x = pow(x, n)
    y_result = a * powered_x

    if logger.isEnabledFor(logging.INFO):
        msg = textwrap.dedent(
            f"""
            y = axⁿ = {a} * {powered_x} = {y_result}
            dy
            -- = anxⁿ⁻¹ = {derivative} = {result}
            dx
            f(x) = {y_result}
            f'(x) = {result}
            """
        )
        logger.info(msg)

    return y_result, derivative, result


def sinusoid(x):
    """
    y = sin(x)

    dy/dx = cos(x)

    :return: Tuple of f(x), derivative, f'(x)
    """
    _x = Symbol("x")
    expr = sp.sin(_x)
    derivative = expr.diff(_x)
    f1 = lambdify(_x, derivative)
    result = f1(x)
    y_result = lambdify(_x, expr)(x)

    if logger.isEnabledFor(logging.INFO):
        msg = textwrap.dedent(
            f"""
            y = {expr} = {y_result}
            dy
            -- = {derivative} = {result}
            dx
            f(x) = {y_result}
            f'(x) = {result}
            """
        )
        logger.info(msg)

    return y_result, derivative, result


def enhanced_sin_bx(a, b, x):
    """
    y = a * sin(b * x)

    dy/dx = a * b * cos(b * x)

    :return: Tuple of f(x), derivative, f'(x)
    """
    _a, _b, _x = symbols("a b x")
    expr = _a * sp.sin(_b * _x)
    derivative = expr.diff(_x)
    f1 = lambdify((_a, _b, _x), derivative)
    result = f1(a, b, x)
    y_result = lambdify((_a, _b, _x), expr)(a, b, x)

    if logger.isEnabledFor(logging.INFO):
        msg = textwrap.dedent(
            f"""
            y = {expr} = {y_result}
            dy
            -- = {derivative} = {result}
            dx
            f(x) = {y_result}
            f'(x) = {result}
            """
        )
        logger.info(msg)

    return y_result, derivative, result


def cosinusoid(x):
    """
    y = cos(x)

    dy/dx = -sin(x)

    :return: Tuple of f(x), derivative, f'(x)
    """
    _x = Symbol("x")
    expr = sp.cos(_x)
    derivative = expr.diff(_x)
    f1 = lambdify(_x, derivative)
    result = f1(x)
    y_result = lambdify(_x, expr)(x)

    if logger.isEnabledFor(logging.INFO):
        msg = textwrap.dedent(
            f"""
            y = {expr} = {y_result}
            dy
            -- = {derivative} = {result}
            dx
            f(x) = {y_result}
            f'(x) = {result}
            """
        )
        logger.info(msg)

    return y_result, derivative, result


def enhanced_sin_bx_minus_enhanced_cos_dx(a, b, c, d, x):
    """
    y = a * sin(b * x) - c * cos(d * x)

    dy/dx = a * b * cos(b * x) + c * d * sin(d * x)

    :return: Tuple of f(x), derivative, f'(x)
    """
    _a, _b, _c, _d, _x = symbols("a b c d x")
    expr = _a * sp.sin(_b * _x) - _c * sp.cos(_d * _x)
    derivative = expr.diff(_x)
    f1 = lambdify((_a, _b, _c, _d, _x), derivative)
    result = f1(a, b, c, d, x)
    y_result = lambdify((_a, _b, _c, _d, _x), expr)(a, b, c, d, x)

    if logger.isEnabledFor(logging.INFO):
        msg = textwrap.dedent(
            f"""
            y = {expr} = {a} * sin({b} * {x}) - {c} * cos({d} * {x}) = {y_result}
            dy
            -- = {derivative} = {result}
            dx
            f(x) = {y_result}
            f'(x) = {result}
            """
        )
        logger.info(msg)

    return y_result, derivative, result


def enhanced_sin_b_pi_x_minus_c(a, b, c, x):
    """
    y = a * sin(b * 𝛑 * x - c)

    dy/dx = a * b * cos(b * 𝛑 * x - c)

    :return: Tuple of f(x), derivative, f'(x)
    """
    _a, _b, _c, _x = symbols("a b c x")
    expr = _a * sp.sin(_b * sp.pi * _x - _c)
    derivative = expr.diff(_x)
    f1 = lambdify((_a, _b, _c, _x), derivative)
    result = f1(a, b, c, x)
    y_result = lambdify((_a, _b, _c, _x), expr)(a, b, c, x)

    if logger.isEnabledFor(logging.INFO):
        msg = textwrap.dedent(
            f"""
            y = {expr} = {a} * sin({math.pi} * {b} * {x} - {c}) = {y_result}
            dy
            -- = {derivative} = {result}
            dx
            f(x) = {y_result}
            f'(x) = {result}
            """
        )
        logger.info(msg)

    return y_result, derivative, result


def e_in_power(x):
    """
    y = e^x

    dy/dx = e^x

    :return: Tuple of f(x), derivative, f'(x)
    """
    e, _x = symbols("e x")
    expr = e**_x
    derivative = expr.diff(_x)
    f1 = lambdify((e, _x), derivative)
    result = f1(math.e, x)
    y_result = lambdify((e, _x), expr)(math.e, x)

    if logger.isEnabledFor(logging.INFO):
        msg = textwrap.dedent(
            f"""
            y = {expr} = {math.e}^{x} = {y_result}
            dy
            -- = {derivative} = {result}
            dx
            f(x) = {y_result}
            f'(x) = {result}
            """
        )
        logger.info(msg)

    return y_result, derivative, result


def ln(x):
    """
    y = ln(x)

    dy/dx = 1 / x

    :return: Tuple of f(x), derivative, f'(x)
    """
    _x = Symbol("x")
    expr = sp.ln(_x)
    derivative = expr.diff(_x)
    f1 = lambdify(_x, derivative)
    result = f1(x)
    y_result = lambdify(_x, expr)(x)

    if logger.isEnabledFor(logging.INFO):
        msg = textwrap.dedent(
            f"""
            y = {expr} = {y_result}
            dy
            -- = {derivative} = {result}
            dx
            f(x) = {y_result}
            f'(x) = {result}
            """
        )
        logger.info(msg)

    return y_result, derivative, result


def ln_ax(a, x):
    """
    y = ln(a * x)

    dy/dx = 1 / x

    :return: Tuple of f(x), derivative, f'(x)
    """
    _a, _x = symbols("a x")
    expr = sp.ln(_a * _x)
    derivative = expr.diff(_x)
    f1 = lambdify((_a, _x), derivative)
    result = f1(a, x)
    ax_multiply_result = a * x
    y_result = math.log(ax_multiply_result)

    if logger.isEnabledFor(logging.INFO):
        msg = textwrap.dedent(
            f"""
            y = {expr} = ln({ax_multiply_result}) = {y_result}
            dy
            -- = {derivative} = {result}
            dx
            f(x) = {y_result}
            f'(x) = {result}
            """
        )
        logger.info(msg)

    return y_result, derivative, result


def enhanced_ln_ax(a, b, x):
    """
    y = a * ln(b * x)

    dy/dx = a / x

    :return: Tuple of f(x), derivative, f'(x)
    """
    _a, _b, _x = symbols("a b x")
    expr = _a * sp.ln(_b * _x)
    derivative = expr.diff(_x)
    f1 = lambdify((_a, _b, _x), derivative)
    result = f1(a, b, x)
    bx_multiply_result = b * x
    y_result = a * math.log(bx_multiply_result)

    if logger.isEnabledFor(logging.INFO):
        msg = textwrap.dedent(
            f"""
            y = {expr} = {a} * ln({bx_multiply_result}) = {y_result}
            dy
            -- = {derivative} = {result}
            dx
            f(x) = {y_result}
            f'(x) = {result}
            """
        )
        logger.info(msg)

    return y_result, derivative, result


def enhanced_e_in_power_ax(a, b, x):
    """
    y = a * e^(b * x)

    dy/dx = a * b * e^(b * x)

    :return: Tuple of f(x), derivative, f'(x)
    """
    _a, _b, _x = symbols("a b x")
    expr = _a * math.e ** (_b * _x)
    derivative = expr.diff(_x)
    f1 = lambdify((_a, _b, _x), derivative)
    result = f1(a, b, x)
    bx_multiply_result = b * x
    y_result = a * math.pow(math.e, bx_multiply_result)

    if logger.isEnabledFor(logging.INFO):
        msg = textwrap.dedent(
            f"""
            y = {expr} = {a} * e^({bx_multiply_result}) = {y_result}
            dy
            -- = {derivative} = {result}
            dx
            f(x) = {y_result}
            f'(x) = {result}
            """
        )
        logger.info(msg)

    return y_result, derivative, result


def of_constant(a, x):
    """
    y = a or y = a * x⁰

    dy/dx = a * 0 * x^(0-1) = 0

    :return: Tuple of f(x), derivative, f'(x)
    """
    _a, _x = symbols("a x")
    expr = _a * _x**0
    derivative = expr.diff(_x)
    f1 = lambdify((_a, _x), derivative)
    result = f1(a, x)

    powered_x = math.pow(x, 0)
    y_result = a * powered_x

    if logger.isEnabledFor(logging.INFO):
        msg = textwrap.dedent(
            f"""
            y = a * x⁰ = {a} * {powered_x} = {y_result}
            dy
            -- = {derivative} = {result}
            dx
            f(x) = {y_result}
            f'(x) = {result}
            """
        )
        logger.info(msg)

    return y_result, derivative, result


def ax(a, x):
    """
    y = a * x or y = a * x¹

    dy/dx = a

    :return: Tuple of f(x), derivative, f'(x)
    """
    _a, _x = symbols("a x")
    expr = _a * _x
    derivative = expr.diff(_x)
    f1 = lambdify((_a, _x), derivative)
    result = f1(a, x)

    y_result = lambdify((_a, _x), expr)(a, x)

    if logger.isEnabledFor(logging.INFO):
        msg = textwrap.dedent(
            f"""
            y = a * x¹ = {expr} = {y_result}
            dy
            -- = {derivative} = {result}
            dx
            f(x) = {y_result}
            f'(x) = {result}
            """
        )
        logger.info(msg)

    return y_result, derivative, result
