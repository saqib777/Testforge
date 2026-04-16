"""
tests/sample/test_bank_account.py

More advanced pytest patterns:
  - class-level fixtures with setup/teardown
  - custom exceptions
  - property-based edge cases
  - marks (slow, smoke)
"""

import pytest
from decimal import Decimal


# ── domain model (inline for demo) ──────────────────────────────

class InsufficientFundsError(Exception):
    def __init__(self, balance, amount):
        super().__init__(f"Cannot withdraw {amount:.2f}; balance is {balance:.2f}")
        self.balance = balance
        self.amount  = amount


class BankAccount:
    def __init__(self, owner: str, initial: float = 0.0):
        if initial < 0:
            raise ValueError("Initial balance cannot be negative")
        self.owner   = owner
        self._balance = Decimal(str(initial))
        self._history: list[str] = []

    @property
    def balance(self) -> float:
        return float(self._balance)

    def deposit(self, amount: float) -> float:
        if amount <= 0:
            raise ValueError("Deposit amount must be positive")
        self._balance += Decimal(str(amount))
        self._history.append(f"deposit:{amount}")
        return self.balance

    def withdraw(self, amount: float) -> float:
        if amount <= 0:
            raise ValueError("Withdrawal amount must be positive")
        if Decimal(str(amount)) > self._balance:
            raise InsufficientFundsError(self.balance, amount)
        self._balance -= Decimal(str(amount))
        self._history.append(f"withdraw:{amount}")
        return self.balance

    def transfer(self, target: "BankAccount", amount: float):
        self.withdraw(amount)
        target.deposit(amount)

    def history(self) -> list[str]:
        return list(self._history)


# ── fixtures ─────────────────────────────────────────────────────

@pytest.fixture
def empty_account():
    return BankAccount("Alice")


@pytest.fixture
def funded_account():
    acc = BankAccount("Bob", initial=1000.0)
    return acc


@pytest.fixture
def two_accounts():
    src = BankAccount("Carol",  initial=500.0)
    dst = BankAccount("Dave",   initial=100.0)
    return src, dst


# ── creation ─────────────────────────────────────────────────────

class TestAccountCreation:

    def test_default_balance_is_zero(self, empty_account):
        assert empty_account.balance == 0.0

    def test_initial_balance_set_correctly(self, funded_account):
        assert funded_account.balance == 1000.0

    def test_owner_name_stored(self, empty_account):
        assert empty_account.owner == "Alice"

    def test_negative_initial_balance_raises(self):
        with pytest.raises(ValueError, match="cannot be negative"):
            BankAccount("Eve", initial=-50.0)

    def test_history_starts_empty(self, empty_account):
        assert empty_account.history() == []


# ── deposits ─────────────────────────────────────────────────────

class TestDeposits:

    def test_deposit_increases_balance(self, empty_account):
        empty_account.deposit(250.0)
        assert empty_account.balance == 250.0

    def test_deposit_returns_new_balance(self, empty_account):
        result = empty_account.deposit(100.0)
        assert result == 100.0

    def test_multiple_deposits_accumulate(self, empty_account):
        empty_account.deposit(100.0)
        empty_account.deposit(200.0)
        assert empty_account.balance == 300.0

    def test_deposit_zero_raises(self, empty_account):
        with pytest.raises(ValueError):
            empty_account.deposit(0)

    def test_deposit_negative_raises(self, empty_account):
        with pytest.raises(ValueError):
            empty_account.deposit(-10)

    def test_deposit_recorded_in_history(self, empty_account):
        empty_account.deposit(50.0)
        assert "deposit:50.0" in empty_account.history()

    @pytest.mark.parametrize("amount", [0.01, 1.0, 1000.0, 999999.99])
    def test_deposit_various_amounts(self, empty_account, amount):
        empty_account.deposit(amount)
        assert empty_account.balance == pytest.approx(amount)


# ── withdrawals ──────────────────────────────────────────────────

class TestWithdrawals:

    def test_withdraw_decreases_balance(self, funded_account):
        funded_account.withdraw(300.0)
        assert funded_account.balance == 700.0

    def test_withdraw_exact_balance(self, funded_account):
        funded_account.withdraw(1000.0)
        assert funded_account.balance == 0.0

    def test_overdraft_raises_insufficient_funds(self, funded_account):
        with pytest.raises(InsufficientFundsError):
            funded_account.withdraw(1001.0)

    def test_insufficient_funds_error_has_balance(self, funded_account):
        try:
            funded_account.withdraw(9999.0)
        except InsufficientFundsError as e:
            assert e.balance == 1000.0
            assert e.amount  == 9999.0

    def test_withdraw_zero_raises(self, funded_account):
        with pytest.raises(ValueError):
            funded_account.withdraw(0)

    def test_withdraw_recorded_in_history(self, funded_account):
        funded_account.withdraw(200.0)
        assert "withdraw:200.0" in funded_account.history()

    def test_failed_withdraw_does_not_change_balance(self, funded_account):
        try:
            funded_account.withdraw(9999.0)
        except InsufficientFundsError:
            pass
        assert funded_account.balance == 1000.0


# ── transfers ────────────────────────────────────────────────────

class TestTransfers:

    def test_transfer_debits_source(self, two_accounts):
        src, dst = two_accounts
        src.transfer(dst, 200.0)
        assert src.balance == 300.0

    def test_transfer_credits_destination(self, two_accounts):
        src, dst = two_accounts
        src.transfer(dst, 200.0)
        assert dst.balance == 300.0

    def test_transfer_total_money_conserved(self, two_accounts):
        src, dst = two_accounts
        total_before = src.balance + dst.balance
        src.transfer(dst, 150.0)
        assert src.balance + dst.balance == pytest.approx(total_before)

    def test_transfer_insufficient_funds_raises(self, two_accounts):
        src, dst = two_accounts
        with pytest.raises(InsufficientFundsError):
            src.transfer(dst, 9999.0)

    def test_transfer_failure_leaves_balances_unchanged(self, two_accounts):
        src, dst = two_accounts
        src_before, dst_before = src.balance, dst.balance
        try:
            src.transfer(dst, 9999.0)
        except InsufficientFundsError:
            pass
        assert src.balance == src_before
        assert dst.balance == dst_before


# ── history audit ────────────────────────────────────────────────

class TestAuditHistory:

    def test_history_records_all_operations(self, empty_account):
        empty_account.deposit(100)
        empty_account.deposit(50)
        empty_account.withdraw(30)
        assert len(empty_account.history()) == 3

    def test_history_returns_copy(self, funded_account):
        h = funded_account.history()
        h.append("tampered")
        assert "tampered" not in funded_account.history()

