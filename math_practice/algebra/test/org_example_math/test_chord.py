import unittest

import matplotlib.pyplot as plt

from math_practice.algebra.org_example_math import chord


class ChordTest(unittest.TestCase):
    def test_slope_angle(self):
        # f(x) = x²
        ab = chord.slope_angle(1, 3)
        self.assertEqual(4, ab)

        ac = chord.slope_angle(1, 2)
        self.assertEqual(3, ac)

        ad = chord.slope_angle(1, 1.5)
        self.assertEqual(2.5, ad)

        ae = chord.slope_angle(1, 1.1)
        self.assertEqual(2.1, ae)

        af = chord.slope_angle(1, 1.01)
        self.assertEqual(2.01, round(af, 3))

    def show_slope_angle_of_chord(self):
        # f(x) = x²
        a = 1
        b = 3
        c = 2
        d = 1.5
        chord.slope_angle(a, b)
        chord.slope_angle(a, c)
        chord.slope_angle(a, d)

        a_square = pow(a, 2)
        b_square = pow(b, 2)
        c_square = pow(c, 2)
        d_square = pow(d, 2)
        plt.plot([a, d, c, b], [a_square, d_square, c_square, b_square], "-o")
        plt.axis([0, b + 1, 0, b_square + 1])
        plt.annotate("A", xy=(a, a_square), xytext=(a, a_square + 0.2))
        plt.annotate("B", xy=(b, b_square), xytext=(b, b_square + 0.2))
        plt.annotate(
            "f(x) = x²",
            xy=(b + 0.01, b_square),
            xytext=(b + 0.3, b_square),
            arrowprops={"facecolor": "black", "shrink": 0.02, "width": 1, "headwidth": 6},
        )
        plt.annotate("C", xy=(c, c_square), xytext=(c, c_square + 0.2))
        plt.annotate("D", xy=(d, d_square), xytext=(d, d_square + 0.2))
        plt.grid(True)
        plt.show()


if __name__ == "__main__":
    unittest.main()
