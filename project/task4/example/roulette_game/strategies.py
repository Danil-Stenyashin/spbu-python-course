from abc import ABC, abstractmethod
from random import randint, choice

from project.task4.example.roulette_game.bets import Bet
from project.task4.example.roulette_game.enums import (
    BetType,
    Color,
    EvenOdd,
    Dozen,
    Half,
)


class Strategy(ABC):
    """Abstract base class for betting strategies"""

    def __init__(self):
        self._last_result: bool = True

    @abstractmethod
    def make_bet(self, player_balance: int, game_history: list) -> Bet:
        """Creates a bet based on player balance and game history"""
        pass

    def update_result(self, won: bool) -> None:
        """Update strategy with result of last bet"""
        self._last_result = won

    def get_last_result(self) -> bool:
        """Get result of last bet"""
        return self._last_result


class ConservativeStrategy(Strategy):
    """Conservative strategy - uses safer bets with lower risk"""

    def __init__(self):
        super().__init__()
        self.bet_cycle = [BetType.COLOR, BetType.EVEN_ODD, BetType.DOZEN, BetType.HALF]
        self.cycle_index = 0

    def make_bet(self, player_balance: int, game_history: list) -> Bet:
        bet_type = self.bet_cycle[self.cycle_index]
        self.cycle_index = (self.cycle_index + 1) % len(self.bet_cycle)

        amount = max(1, int(player_balance * 0.1))

        if bet_type == BetType.COLOR:
            color = Color.RED if len(game_history) % 2 == 0 else Color.BLACK
            return Bet(bet_type, color, amount)
        elif bet_type == BetType.EVEN_ODD:
            even_odd = EvenOdd.EVEN if len(game_history) % 2 == 0 else EvenOdd.ODD
            return Bet(bet_type, even_odd, amount)
        elif bet_type == BetType.DOZEN:
            dozens = [Dozen.FIRST, Dozen.SECOND, Dozen.THIRD]
            dozen = dozens[len(game_history) % 3]
            return Bet(bet_type, dozen, amount)
        elif bet_type == BetType.HALF:
            half = Half.FIRST_18 if len(game_history) % 2 == 0 else Half.LAST_18
            return Bet(bet_type, half, amount)


class RiskStrategy(Strategy):
    """Risky strategy - uses all bet types including numbers"""

    def __init__(self):
        super().__init__()

    def make_bet(self, player_balance: int, game_history: list) -> Bet:
        bet_type = choice(
            [
                BetType.NUMBER,
                BetType.COLOR,
                BetType.EVEN_ODD,
                BetType.DOZEN,
                BetType.COLUMN,
                BetType.HALF,
            ]
        )

        amount = max(1, int(player_balance * 0.1))

        if bet_type == BetType.NUMBER:
            return Bet(bet_type, randint(0, 36), amount)
        elif bet_type == BetType.COLOR:
            return Bet(bet_type, choice([Color.RED, Color.BLACK]), amount)
        elif bet_type == BetType.EVEN_ODD:
            return Bet(bet_type, choice([EvenOdd.EVEN, EvenOdd.ODD]), amount)
        elif bet_type == BetType.DOZEN:
            return Bet(
                bet_type, choice([Dozen.FIRST, Dozen.SECOND, Dozen.THIRD]), amount
            )
        elif bet_type == BetType.COLUMN:
            return Bet(bet_type, randint(1, 3), amount)
        elif bet_type == BetType.HALF:
            return Bet(bet_type, choice([Half.FIRST_18, Half.LAST_18]), amount)


class MegaRiskStrategy(Strategy):
    """Very risky strategy - focuses on high-risk high-reward bets"""

    def __init__(self):
        super().__init__()
        self.risk_modes = [BetType.NUMBER, BetType.COLUMN]
        self.mode_index = 0

    def make_bet(self, player_balance: int, game_history: list) -> Bet:
        if len(game_history) % 2 == 0:
            self.mode_index = (self.mode_index + 1) % len(self.risk_modes)

        bet_type = self.risk_modes[self.mode_index]
        amount = max(1, int(player_balance * 0.5))

        if bet_type == BetType.NUMBER:
            number = choice([0, 0, 0, 1, 2, 34, 35, 36] + list(range(3, 34)))
            return Bet(bet_type, number, amount)
        elif bet_type == BetType.COLUMN:
            return Bet(bet_type, randint(1, 3), amount)


class MathematicalStrategy(Strategy):
    """Mathematical strategy using Martingale system"""

    def __init__(self):
        super().__init__()
        self.last_bet_amount = 1
        self.consecutive_losses = 0
        self.bet_rotation = [
            BetType.COLOR,
            BetType.EVEN_ODD,
            BetType.DOZEN,
            BetType.HALF,
        ]
        self.rotation_index = 0

    def make_bet(self, player_balance: int, game_history: list) -> Bet:
        bet_type = self.bet_rotation[self.rotation_index]
        self.rotation_index = (self.rotation_index + 1) % len(self.bet_rotation)

        new_bet_amount = 1 * (2**self.consecutive_losses)
        new_bet_amount = min(new_bet_amount, player_balance)
        if new_bet_amount == 0 and player_balance > 0:
            new_bet_amount = 1

        self.last_bet_amount = new_bet_amount

        if bet_type == BetType.COLOR:
            color = Color.RED if len(game_history) % 2 == 0 else Color.BLACK
            return Bet(bet_type, color, new_bet_amount)
        elif bet_type == BetType.EVEN_ODD:
            even_odd = EvenOdd.EVEN if len(game_history) % 2 == 0 else EvenOdd.ODD
            return Bet(bet_type, even_odd, new_bet_amount)
        elif bet_type == BetType.DOZEN:
            dozens = [Dozen.FIRST, Dozen.SECOND, Dozen.THIRD]
            dozen = dozens[len(game_history) % 3]
            return Bet(bet_type, dozen, new_bet_amount)
        elif bet_type == BetType.HALF:
            half = Half.FIRST_18 if len(game_history) % 2 == 0 else Half.LAST_18
            return Bet(bet_type, half, new_bet_amount)

    def update_result(self, won: bool) -> None:
        super().update_result(won)
        if won:
            self.consecutive_losses = 0
        else:
            self.consecutive_losses += 1

    def get_previous_bet_amount(self) -> int:
        return self.last_bet_amount
