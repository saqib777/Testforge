"""
Sample test suite — tests/sample/test_calculator.py
Demonstrates pytest-style tests that TestForge orchestrates.
"""

import pytest


# ───────────── module under test (inline for demo) ──────────────

class Calculator:
    def add(self, a, b):       return a + b
    def subtract(self, a, b):  return a - b
    def multiply(self, a, b):  return a * b
    def divide(self, a, b):
        if b == 0:
            raise ZeroDivisionError("Cannot divide by zero")
        return a / b
    def power(self, base, exp): return base ** exp


# ───────────── fixtures ──────────────────────────────────────────

@pytest.fixture
def calc():
    return Calculator()


# ───────────── basic arithmetic ──────────────────────────────────

class TestBasicArithmetic:

    def test_add_positive(self, calc):
        assert calc.add(3, 4) == 7

    def test_add_negative(self, calc):
        assert calc.add(-1, -2) == -3

    def test_add_zero(self, calc):
        assert calc.add(5, 0) == 5

    def test_subtract(self, calc):
        assert calc.subtract(10, 4) == 6

    def test_subtract_negative_result(self, calc):
        assert calc.subtract(3, 7) == -4

    def test_multiply(self, calc):
        assert calc.multiply(4, 5) == 20

    def test_multiply_by_zero(self, calc):
        assert calc.multiply(9999, 0) == 0

    def test_divide_exact(self, calc):
        assert calc.divide(10, 2) == 5.0

    def test_divide_float_result(self, calc):
        assert calc.divide(7, 2) == pytest.approx(3.5)


# ───────────── edge cases ────────────────────────────────────────

class TestEdgeCases:

    def test_divide_by_zero_raises(self, calc):
        with pytest.raises(ZeroDivisionError):
            calc.divide(5, 0)

    def test_large_numbers(self, calc):
        assert calc.add(10**9, 10**9) == 2 * 10**9

    def test_float_addition(self, calc):
        assert calc.add(0.1, 0.2) == pytest.approx(0.3)

    @pytest.mark.parametrize("a,b,expected", [
        (2, 3, 8),
        (3, 2, 9),
        (10, 0, 1),
        (5, 1, 5),
    ])
    def test_power_parametrized(self, calc, a, b, expected):
        assert calc.power(a, b) == expected


# ───────────── type handling ─────────────────────────────────────

class TestTypeHandling:

    def test_add_returns_int_for_ints(self, calc):
        result = calc.add(1, 2)
        assert isinstance(result, int)

    def test_divide_returns_float(self, calc):
        result = calc.divide(6, 2)
        assert isinstance(result, float)

