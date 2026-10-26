import textwrap
import unittest

import matplotlib.pyplot as plt
import numpy as np

from math_practice.algebra.org_example_math import derivative
from math_practice.algebra.org_example_math.config.logging_config import logger


class DerivativeTest(unittest.TestCase):
    def test_x_square(self):
        # f(2) = 2²
        result = derivative.x_square(2)
        logger.info(result)
        f_result, dx, f1_result = result
        self.assertEqual("2*x", str(dx))
        self.assertEqual(4, f_result)
        self.assertEqual(4, f1_result)
        return result

    def show_x_square(self):
        x = 2
        f_result, _dx, f1_result = self.test_x_square()
        x_axis = np.arange(-10, 10, 0.001)
        x_at_2_item = np.where((x_axis >= x) & (x_axis <= 2.1))
        markers = [x_at_2_item[0][0]]

        y = np.power(x_axis, 2)
        plt.plot(
            x_axis,
            y,
            label="f(x)",
            markevery=markers,
            marker="o",
            markerfacecolor="black",
        )
        plt.annotate(
            f"f(x) = {f_result}\nf'(x) = {f1_result}",
            xy=(x, f_result),
            xytext=(x + 0.1, f_result),
        )

        y1 = x * x_axis
        plt.plot(
            x_axis,
            y1,
            label="f'(x)",
            markevery=markers,
            marker="o",
            markerfacecolor="black",
        )

        plt.ylabel("y")
        plt.xlabel("x")
        title = textwrap.dedent(
            """
            y = x²
            dy/dx = 2x
            """
        )
        plt.title(title)
        plt.legend()
        plt.grid(True)
        plt.xlim(-np.pi, np.pi)
        plt.ylim(-1, f_result * 1.5)
        plt.show()

    def test_ax_in_power_n(self):
        # y = 5 * 2^7
        result = derivative.ax_in_power_n(a=5, n=7, x=2)
        logger.info(result)
        f_result, dx, f1_result = result
        self.assertEqual("a*n*x**n/x", str(dx))
        self.assertEqual(640, f_result)
        self.assertEqual(2240, f1_result)

        # y = 3 * 5²
        result = derivative.ax_in_power_n(a=3, n=2, x=5)
        logger.info(result)
        f_result, dx, f1_result = result
        self.assertEqual("a*n*x**n/x", str(dx))
        self.assertEqual(75, f_result)
        self.assertEqual(30, f1_result)

        #      4
        # y = --- = 4 * 6⁻²
        #     6²
        result = derivative.ax_in_power_n(a=4, n=-2, x=6)
        logger.info(result)
        f_result, dx, f1_result = result
        self.assertEqual("a*n*x**n/x", str(dx))
        self.assertEqual(0.111, round(f_result, 3))
        self.assertEqual(-0.037, round(f1_result, 3))

        # y = 3√5 = 3 * 5^½ = 3 * 5^0.5
        result = derivative.ax_in_power_n(a=3, n=0.5, x=5)
        logger.info(result)
        f_result, dx, f1_result = result
        self.assertEqual("a*n*x**n/x", str(dx))
        self.assertEqual(6.708, round(f_result, 3))
        self.assertEqual(0.671, round(f1_result, 3))
        return result

    def show_ax_in_power_n(self):
        a = 3
        n = 0.5
        x = 5
        f_result, _dx, f1_result = self.test_ax_in_power_n()
        x_axis = np.arange(0, 10, 0.001)
        x_at_2_item = np.where((x_axis >= x) & (x_axis <= 5.1))
        markers = [x_at_2_item[0][0]]

        y = a * np.power(x_axis, n)
        plt.plot(
            x_axis,
            y,
            label="f(x)",
            markevery=markers,
            marker="o",
            markerfacecolor="black",
        )
        plt.annotate(
            f"f(x) = {round(f_result, 3)}",
            xy=(x, f_result - 0.1),
            xytext=(x + 0.2, f_result),
        )

        y1 = (a * n * np.power(x_axis, n)) / x_axis
        plt.plot(
            x_axis,
            y1,
            label="f'(x)",
            markevery=markers,
            marker="o",
            markerfacecolor="black",
        )
        plt.annotate(
            f"f'(x) = {round(f1_result, 3)}",
            xy=(x, f1_result - 0.1),
            xytext=(x + 0.2, f1_result),
        )

        plt.ylabel("y")
        plt.xlabel("x")
        title = textwrap.dedent(
            """
            y = axⁿ
            dy/dx = anxⁿ⁻¹ =  a*n*x**n/x
            """
        )
        plt.title(title)
        plt.legend()
        plt.grid(True)
        plt.xlim(-0.5, 2 * np.pi)
        plt.ylim(-0.5, f_result * 1.5)
        plt.show()

    def test_sinusoid(self):
        # y = sin(2)
        result = derivative.sinusoid(2)
        logger.info(result)
        f_result, dx, f1_result = result
        self.assertEqual("cos(x)", str(dx))
        self.assertEqual(0.909, round(f_result, 3))
        self.assertEqual(-0.416, round(f1_result, 3))
        return result

    def show_sinusoid(self):
        f_result, _dx, f1_result = self.test_sinusoid()
        x = 2
        x_axis = np.arange(0, 2 * np.pi, 0.1)
        x_at_2_item = np.where(x_axis == x)
        markers = [x_at_2_item[0][0]]

        y = np.sin(x_axis)
        plt.plot(x_axis, y, markevery=markers, marker="o", markerfacecolor="black")
        plt.annotate(
            f"f(x) = {round(f_result, 3)}",
            xy=(x, f_result - 0.1),
            xytext=(x + 0.2, f_result),
        )

        y1 = np.cos(x_axis)
        plt.plot(x_axis, y1, markevery=markers, marker="o", markerfacecolor="black")
        plt.annotate(
            f"f'(x) = {round(f1_result, 3)}",
            xy=(x, f1_result - 0.1),
            xytext=(x + 0.2, f1_result),
        )

        plt.ylabel("y")
        plt.xlabel("x")
        title = textwrap.dedent(
            """
            y = sin(x)
            d/dx = sin(x) = cos(x)
            """
        )
        plt.title(title)
        plt.legend(["sin(x)", "cos(x)"])
        plt.grid(True)
        plt.show()

    def show_sinusoid_with_subplots(self):
        f_result, _dx, f1_result = self.test_sinusoid()
        x = 2
        x_axis = np.arange(0, 2 * np.pi, 0.1)
        x_at_2_item = np.where(x_axis == x)
        markers = [x_at_2_item[0][0]]

        y = np.sin(x_axis)
        plt.subplot(211)
        plt.plot(x_axis, y, markevery=markers, marker="o", markerfacecolor="black")
        plt.annotate(
            f"f(x) = {round(f_result, 3)}",
            xy=(x, f_result - 0.1),
            xytext=(x + 0.2, f_result),
        )
        plt.title("y = sin(x)")
        plt.grid(True)

        y1 = np.cos(x_axis)
        plt.subplot(212)
        plt.plot(x_axis, y1, markevery=markers, marker="o", markerfacecolor="black")
        plt.annotate(
            f"f'(x) = {round(f1_result, 3)}",
            xy=(x, f1_result - 0.1),
            xytext=(x + 0.2, f1_result),
        )
        plt.title("d/dx = sin(x) = cos(x)")
        plt.grid(True)
        plt.show()

    def test_cosinusoid(self):
        # y = cos(2)
        result = derivative.cosinusoid(2)
        logger.info(result)
        f_result, dx, f1_result = result
        self.assertEqual("-sin(x)", str(dx))
        self.assertEqual(-0.416, round(f_result, 3))
        self.assertEqual(-0.909, round(f1_result, 3))
        return result

    def show_cosinusoid(self):
        f_result, _dx, f1_result = self.test_cosinusoid()
        x = 2
        x_axis = np.arange(0, 2 * np.pi, 0.1)
        x_at_2_item = np.where(x_axis >= x)
        markers = [x_at_2_item[0][0]]

        y = np.cos(x_axis)
        plt.plot(x_axis, y, markevery=markers, marker="o", markerfacecolor="black")
        plt.annotate(
            f"f(x) = {round(f_result, 3)}",
            xy=(x, f_result),
            xytext=(x + 0.2, f_result),
        )

        y1 = -np.sin(x_axis)
        plt.plot(x_axis, y1, markevery=markers, marker="o", markerfacecolor="black")
        plt.annotate(
            f"f'(x) = {round(f1_result, 3)}",
            xy=(x, f1_result),
            xytext=(x + 0.2, f1_result),
        )

        plt.ylabel("y")
        plt.xlabel("from 0 to 2π")
        title = textwrap.dedent(
            """
            y = cos(x)
            d/dx = cos(x) = -sin(x)
            """
        )
        plt.title(title)
        plt.legend(["cos(x)", "-sin(x)"])
        plt.grid(True)
        plt.show()

    def test_enhanced_sin_bx_minus_enhanced_cos_dx(self):
        # y = 7 * sin(2 * 2) - 3 * cos(4 * 2)
        result = derivative.enhanced_sin_bx_minus_enhanced_cos_dx(
            a=7, b=2, c=3, d=4, x=2
        )
        logger.info(result)
        f_result, dx, f1_result = result
        self.assertEqual("a*b*cos(b*x) + c*d*sin(d*x)", str(dx))
        self.assertEqual(-4.861, round(f_result, 3))
        self.assertEqual(2.721, round(f1_result, 3))
        return result

    def show_enhanced_sin_bx_minus_enhanced_cos_dx(self):
        a = 7
        b = 2
        c = 3
        d = 4
        x = 2
        f_result, _dx, f1_result = self.test_enhanced_sin_bx_minus_enhanced_cos_dx()
        x_axis = np.arange(0, 2 * np.pi, 0.001)
        x_at_2_item = np.where(x_axis == x)
        markers = [x_at_2_item[0][0]]

        y_cos = a * np.sin(b * x_axis) - c * np.cos(d * x_axis)
        plt.plot(x_axis, y_cos, markevery=markers, marker="o", markerfacecolor="black")
        plt.annotate(
            f"f(x) = {round(f_result, 3)}",
            xy=(x, f_result),
            xytext=(x + 0.2, f_result),
        )

        y_sin = a * b * np.cos(b * x_axis) + c * d * np.sin(d * x_axis)
        plt.plot(x_axis, y_sin, markevery=markers, marker="o", markerfacecolor="black")
        plt.annotate(
            f"f'(x) = {round(f1_result, 3)}",
            xy=(x, f1_result),
            xytext=(x + 0.1, f1_result),
        )

        plt.ylabel("y")
        plt.xlabel("x")
        title = textwrap.dedent(
            """
            y = a * sin(b * x) - c * cos(d * x)
            dy/dx = a * b * cos(b * x) + c * d * sin(d * x)
            """
        )
        plt.title(title)
        plt.legend(["f(x)", "f'(x)"])
        plt.grid(True)
        plt.xlim(-1, 2 * np.pi + 1)
        plt.ylim(-25, 25)
        plt.show()

    def test_enhanced_sin_b_pi_x_minus_c(self):
        # y = 5 * sin(100 * 𝛑 * 2 - 0.40)
        result = derivative.enhanced_sin_b_pi_x_minus_c(a=5, b=100, c=0.40, x=2)
        logger.info(result)
        f_result, dx, f1_result = result
        self.assertEqual("pi*a*b*cos(pi*b*x - c)", str(dx))
        self.assertEqual(-1.947, round(f_result, 3))
        self.assertEqual(1446.799, round(f1_result, 3))
        return result

    def show_enhanced_sin_b_pi_x_minus_c(self):
        a = 5
        b = 100
        c = 0.40
        x = 2
        f_result, _dx, f1_result = self.test_enhanced_sin_b_pi_x_minus_c()
        x_axis = np.arange(0, a * b, 0.001)
        x_at_2_item = np.where(x_axis == x)
        markers = [x_at_2_item[0][0]]

        y_cos = a * np.sin(b * np.pi * x_axis - c)
        plt.plot(x_axis, y_cos, markevery=markers, marker="o", markerfacecolor="black")
        plt.annotate(
            f"f(x) = {round(f_result, 3)}",
            xy=(x, f_result),
            xytext=(x + 0.2, f_result),
        )

        y_sin = np.pi * a * b * np.cos(np.pi * b * x_axis - c)
        plt.plot(x_axis, y_sin, markevery=markers, marker="o", markerfacecolor="black")
        plt.annotate(
            f"f'(x) = {round(f1_result, 3)}",
            xy=(x, f1_result),
            xytext=(x + 0.1, f1_result),
        )

        plt.ylabel("y")
        plt.xlabel("x")
        title = textwrap.dedent(
            """
            y = a * sin(b * PI * x - c)
            dy/dx = PI * a * b * cos(PI * b * x - c)
            """
        )
        plt.title(title)
        plt.legend(["f(x)", "f'(x)"])
        plt.grid(True)
        plt.xlim(-50, a * b + 50)
        plt.ylim(-2000, 2000)
        plt.show()

    def test_e_in_power(self):
        # y = e³ = 2.718281828459045^3
        result = derivative.e_in_power(x=3)
        logger.info(result)
        f_result, dx, f1_result = result
        self.assertEqual("e**x*log(e)", str(dx))
        self.assertEqual(20.086, round(f_result, 3))
        self.assertEqual(20.086, round(f1_result, 3))
        return result

    def show_e_in_power(self):
        x = 3
        f_result, _dx, _f1_result = self.test_e_in_power()

        _fig, ax = plt.subplots()
        ax.spines[["left", "bottom"]].set_position(("data", 0))
        ax.spines[["top", "right"]].set_visible(False)
        ax.plot(1, 0, ">k", transform=ax.get_yaxis_transform(), clip_on=False)
        ax.plot(0, 1, "^k", transform=ax.get_xaxis_transform(), clip_on=False)

        x_axis = np.arange(0, 100, 0.001)
        x_at_2_item = np.where(x_axis == x)
        markers = [x_at_2_item[0][0]]

        y = np.exp(x_axis)
        ax.plot(
            x_axis,
            y,
            label="f(x)",
            markevery=markers,
            marker="o",
            markerfacecolor="black",
        )
        ax.annotate(
            "f(x) = {0}\nf'(x) = {0}".format(round(f_result, 3)),
            xy=(x, f_result),
            xytext=(x + 0.2, f_result + 1.5),
        )

        y1 = np.exp(x_axis)
        ax.plot(
            x_axis,
            y1,
            label="f'(x)",
            markevery=markers,
            marker="o",
            markerfacecolor="black",
        )

        plt.ylabel("y")
        plt.xlabel("x")
        title = textwrap.dedent(
            """
            y = e³
            dy/dx = e³
            """
        )
        ax.grid(True)
        plt.title(title)
        plt.legend()
        plt.xlim(-2, 2 * np.pi)
        plt.ylim(-1, 100)
        plt.show()

    def test_ln(self):
        # y = ln(1)
        result = derivative.ln(x=1)
        logger.info(result)
        f_result, dx, f1_result = result
        self.assertEqual("1/x", str(dx))
        self.assertEqual(0, f_result)
        self.assertEqual(1, f1_result)

        # y = ln(2)
        result = derivative.ln(x=2)
        logger.info(result)
        f_result, dx, f1_result = result
        self.assertEqual("1/x", str(dx))
        self.assertEqual(0.693, round(f_result, 3))
        self.assertEqual(0.5, f1_result)
        return result

    def show_ln(self):
        x = 2
        f_result, _dx, f1_result = self.test_ln()
        x_axis = np.arange(0, 10, 0.001)
        x_at_2_item = np.where(x_axis == x)
        markers = [x_at_2_item[0][0]]

        y = np.log(x_axis)
        plt.plot(x_axis, y, markevery=markers, marker="o", markerfacecolor="black")
        plt.annotate(
            f"f(x) = {round(f_result, 3)}",
            xy=(x, f_result),
            xytext=(x + 0.1, f_result + 0.4),
        )

        y1 = 1 / x_axis
        plt.plot(x_axis, y1, markevery=markers, marker="o", markerfacecolor="black")
        plt.annotate(
            f"f'(x) = {round(f1_result, 3)}",
            xy=(x, f1_result),
            xytext=(x + 0.1, f1_result),
        )

        plt.ylabel("y")
        plt.xlabel("x")
        title = textwrap.dedent(
            """
            y = ln(x)
            dy/dx = 1 / x
            """
        )
        plt.title(title)
        plt.legend(["f(x)", "f'(x)"])
        plt.grid(True)
        plt.xlim(-0.5, 2 * np.pi)
        plt.ylim(-1, np.pi * 1.5)
        plt.show()

    def test_ln_ax(self):
        # y = ln(2 * 2)
        result = derivative.ln_ax(a=2, x=2)
        logger.info(result)
        f_result, dx, f1_result = result
        self.assertEqual("1/x", str(dx))
        self.assertEqual(1.386, round(f_result, 3))
        self.assertEqual(0.5, f1_result)
        return result

    def show_ln_ax(self):
        a = 2
        x = 2
        f_result, _dx, f1_result = self.test_ln_ax()
        x_axis = np.arange(0, 10, 0.001)
        x_at_2_item = np.where(x_axis == x)
        markers = [x_at_2_item[0][0]]

        y = np.log(a * x_axis)
        plt.plot(x_axis, y, markevery=markers, marker="o", markerfacecolor="black")
        plt.annotate(
            f"f(x) = {round(f_result, 3)}",
            xy=(x, f_result),
            xytext=(x + 0.2, f_result),
        )

        y1 = 1 / x_axis
        plt.plot(x_axis, y1, markevery=markers, marker="o", markerfacecolor="black")
        plt.annotate(
            f"f'(x) = {round(f1_result, 3)}",
            xy=(x, f1_result),
            xytext=(x + 0.1, f1_result),
        )

        plt.ylabel("y")
        plt.xlabel("x")
        title = textwrap.dedent(
            """
            y = ln(a * x)
            dy/dx = 1 / x
            """
        )
        plt.title(title)
        plt.legend(["f(x)", "f'(x)"])
        plt.grid(True)
        plt.xlim(-0.5, 2 * np.pi)
        plt.ylim(-1, 3.8)
        plt.show()

    def test_enhanced_ln_ax(self):
        # y = 3 * ln(4 * 2)
        result = derivative.enhanced_ln_ax(a=3, b=4, x=2)
        logger.info(result)
        f_result, dx, f1_result = result
        self.assertEqual("a/x", str(dx))
        self.assertEqual(6.238, round(f_result, 3))
        self.assertEqual(1.5, f1_result)
        return result

    def show_enhanced_ln_ax(self):
        a = 3
        b = 4
        x = 2
        f_result, _dx, f1_result = self.test_enhanced_ln_ax()
        x_axis = np.arange(0, 10, 0.001)
        x_at_2_item = np.where(x_axis == x)
        markers = [x_at_2_item[0][0]]

        y = a * np.log(b * x_axis)
        plt.plot(
            x_axis,
            y,
            label="f(x)",
            markevery=markers,
            marker="o",
            markerfacecolor="black",
        )
        plt.annotate(
            f"f(x) = {round(f_result, 3)}",
            xy=(x, f_result),
            xytext=(x + 0.1, f_result),
        )

        y1 = a / x_axis
        plt.plot(
            x_axis,
            y1,
            label="f'(x)",
            markevery=markers,
            marker="o",
            markerfacecolor="black",
        )
        plt.annotate(
            f"f'(x) = {round(f1_result, 3)}",
            xy=(x, f1_result),
            xytext=(x + 0.1, f1_result),
        )

        plt.ylabel("y")
        plt.xlabel("x")
        title = textwrap.dedent(
            """
            y = a * ln(b * x)
            dy/dx = a / x
            """
        )
        plt.title(title)
        plt.legend()
        plt.grid(True)
        plt.xlim(-0.5, 2 * np.pi)
        plt.ylim(-1, f_result * 1.5)
        plt.show()

    def test_enhanced_e_in_power_ax(self):
        # y = 2e^(6 * 2)
        result = derivative.enhanced_e_in_power_ax(a=2, b=6, x=2)
        logger.info(result)
        f_result, dx, f1_result = result
        self.assertEqual("1.0*2.71828182845905**(b*x)*a*b", str(dx))
        self.assertEqual(325509.583, round(f_result, 3))
        self.assertEqual(1953057.497, round(f1_result, 3))
        return result

    def show_enhanced_e_in_power_ax(self):
        a = 2
        b = 6
        x = 2
        f_result, _dx, _f1_result = self.test_enhanced_e_in_power_ax()
        x_axis = np.arange(0, 10, 0.001)
        x_at_2_item = np.where(x_axis == x)
        markers = [x_at_2_item[0][0]]

        y = a * np.power(np.e, b * x * x_axis)
        plt.plot(
            x_axis,
            y,
            label="f(x)",
            markevery=markers,
            marker="o",
            markerfacecolor="black",
        )

        y1 = a * b * np.power(np.e, b * x * x_axis)
        plt.plot(
            x_axis,
            y1,
            label="f'(x)",
            markevery=markers,
            marker="o",
            markerfacecolor="black",
        )

        plt.ylabel("y")
        plt.xlabel("x")
        title = textwrap.dedent(
            """
            y = a * e^(b * x)
            dy/dx = a * b * e^(b * x)
            """
        )
        plt.title(title)
        plt.legend()
        plt.grid(True)
        plt.figtext(
            0.05,
            0.0,
            "f(x) = {0} f'(x) = {0}".format(round(f_result, 3), ),
        )
        plt.xlim(-1, x * 1.5)
        plt.ylim(-1, f_result * 1.5)
        plt.show()

    def test_of_constant(self):
        # y = 6 = 6 * 0 * 1^(0 - 1)
        result = derivative.of_constant(a=6, x=1)
        logger.info(result)
        f_result, dx, f1_result = result
        self.assertEqual("0", str(dx))
        self.assertEqual(6, f_result)
        self.assertEqual(0, f1_result)

        # y = 6 = 6 * 0 * 2^(0 - 1)
        result = derivative.of_constant(a=6, x=2)
        logger.info(result)
        f_result, dx, f1_result = result
        self.assertEqual("0", str(dx))
        self.assertEqual(6, f_result)
        self.assertEqual(0, f1_result)
        return result

    def show_of_constant(self):
        a = 6
        x = 2
        f_result, _dx, f1_result = self.test_of_constant()
        x_axis = np.arange(0, 10, 0.001)
        x_at_2_item = np.where(x_axis == x)
        markers = [x_at_2_item[0][0]]

        y = a * np.power(x_axis, 0)
        plt.plot(
            x_axis,
            y,
            label="f(x)",
            markevery=markers,
            marker="o",
            markerfacecolor="black",
        )
        plt.annotate(
            f"f(x) = {f_result}", xy=(x, f_result), xytext=(x + 0.1, f_result)
        )

        y1 = a * 0 * np.power(x_axis, 0 - 1)
        plt.plot(
            x_axis,
            y1,
            label="f'(x)",
            markevery=markers,
            marker="o",
            markerfacecolor="black",
        )
        plt.annotate(
            f"f'(x) = {f1_result}",
            xy=(x, f1_result),
            xytext=(x + 0.1, f1_result),
        )

        plt.ylabel("y")
        plt.xlabel("x")
        title = textwrap.dedent(
            """
            y = a or y = a * x⁰
            dy/dx = a * 0 * x^(0-1)
            """
        )
        plt.title(title)
        plt.legend()
        plt.grid(True)
        plt.xlim(-0.5, 2 * np.pi)
        plt.ylim(-1, f_result * 1.5)
        plt.show()

    def test_ax(self):
        # y = 6 * 1 = 6 * 1¹
        result = derivative.ax(a=6, x=1)
        logger.info(result)
        f_result, dx, f1_result = result
        self.assertEqual("a", str(dx))
        self.assertEqual(6, f_result)
        self.assertEqual(6, f1_result)

        # y = 6 * 2 = 6 * 2¹
        result = derivative.ax(a=6, x=2)
        logger.info(result)
        f_result, dx, f1_result = result
        self.assertEqual("a", str(dx))
        self.assertEqual(12, f_result)
        self.assertEqual(6, f1_result)
        return result

    def show_ax(self):
        a = 6
        x = 2
        f_result, _dx, f1_result = self.test_ax()
        x_axis = np.arange(0, 10, 0.001)
        x_at_2_item = np.where(x_axis == x)
        markers = [x_at_2_item[0][0]]

        y = a * x_axis
        plt.plot(
            x_axis,
            y,
            label="f(x)",
            markevery=markers,
            marker="o",
            markerfacecolor="black",
        )
        plt.annotate(
            f"f(x) = {f_result}", xy=(x, f_result), xytext=(x + 0.1, f_result)
        )

        y1 = a * np.power(x_axis, 0)
        plt.plot(
            x_axis,
            y1,
            label="f'(x)",
            markevery=markers,
            marker="o",
            markerfacecolor="black",
        )
        plt.annotate(
            f"f'(x) = {f1_result}",
            xy=(x, f1_result),
            xytext=(x + 0.1, f1_result),
        )

        plt.ylabel("y")
        plt.xlabel("x")
        title = textwrap.dedent(
            """
            y = ax or y = a * x¹
            dy/dx = a
            """
        )
        plt.title(title)
        plt.legend()
        plt.grid(True)
        plt.xlim(-0.5, 2 * np.pi)
        plt.ylim(-1, f_result * 1.5)
        plt.show()

    def test_enhanced_sin_bx(self):
        # y = 3 sin (4 * 2)
        result = derivative.enhanced_sin_bx(a=3, b=4, x=2)
        logger.info(result)
        f_result, dx, f1_result = result
        self.assertEqual("a*b*cos(b*x)", str(dx))
        self.assertEqual(2.968, round(f_result, 3))
        self.assertEqual(-1.746, round(f1_result, 3))
        return result

    def show_enhanced_sin_bx(self):
        a = 3
        b = 4
        x = 2
        f_result, _dx, f1_result = self.test_enhanced_sin_bx()
        x_axis = np.arange(0, 10, 0.001)
        x_at_2_item = np.where(x_axis == x)
        markers = [x_at_2_item[0][0]]

        y = a * np.sin(b * x_axis)
        plt.plot(
            x_axis,
            y,
            label="f(x)",
            markevery=markers,
            marker="o",
            markerfacecolor="black",
        )
        plt.annotate(
            f"f(x) = {round(f_result, 3)}",
            xy=(x, f_result),
            xytext=(x + 0.1, f_result),
        )

        y1 = a * b * np.cos(b * x_axis)
        plt.plot(
            x_axis,
            y1,
            label="f'(x)",
            markevery=markers,
            marker="o",
            markerfacecolor="black",
        )
        plt.annotate(
            f"f'(x) = {round(f1_result, 3)}",
            xy=(x, f1_result),
            xytext=(x + 0.1, f1_result),
        )

        plt.ylabel("y")
        plt.xlabel("x")
        title = textwrap.dedent(
            """
            y = a * sin(b * x)
            dy/dx = a * b * cos(b * x)
            """
        )
        plt.title(title)
        plt.legend()
        plt.grid(True)
        plt.xlim(-0.5, 2 * np.pi)
        plt.ylim(-2, 2 * np.pi)
        plt.show()


if __name__ == "__main__":
    unittest.main()
