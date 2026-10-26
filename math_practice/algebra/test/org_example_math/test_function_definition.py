import unittest

import math_practice.algebra.org_example_math.function_definition as f_def


class FunctionDefinitionTest(unittest.TestCase):
    def test_numbers(self):
        # f(0) = 3 * 0² + 2 * 0 - 5
        self.assertEqual(-5, f_def.f_definition(0))

        # f(2) = 3 * 2² + 2 * 2 - 5
        self.assertEqual(11, f_def.f_definition(2))

        # f(-1) = 3 * -1² + 2 * -1 - 5
        self.assertEqual(-4, f_def.f_definition(-1))


if __name__ == "__main__":
    unittest.main()
