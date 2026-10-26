from math_practice.algebra.org_example_math.config.logging_config import logger


def f_definition(number):
    """
    :return: f(x) = 3x² + 2x -5
    """

    def f(x):
        return 3 * pow(x, 2) + 2 * x - 5

    result = f(number)
    logger.info(f"f({number}) = {result}")
    return result
