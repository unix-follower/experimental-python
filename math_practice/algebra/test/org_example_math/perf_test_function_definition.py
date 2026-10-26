import cProfile
import timeit
import unittest

# noinspection PyUnresolvedReferences
from math_practice.algebra.org_example_math.config.logging_config import logger


class FunctionDefinitionPerformanceTest(unittest.TestCase):
    @staticmethod
    def test_execute_profiler():
        cProfile.runctx("f_def.example1(0)", globals(), locals())

    def test_benchmark(self):
        result = timeit.timeit("f_def.example1(0)", globals=globals())
        logger.info(f"benchmark result: {result}")
        self.assertTrue(result < 1)


if __name__ == "__main__":
    unittest.main()
