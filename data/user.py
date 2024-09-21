"""
User model for maintaing information about user. This information includes:
- points_balance
- points_history
"""

import heapq
from collections import defaultdict
from datetime import datetime


class User:
    def __init__(self):
        self.points_balance = 0
        # this should be a minHeap that is ordered by the timestamp
        self.points_history = []
        self.points_mapping = defaultdict(int)
        self.debt = {}  # payer, (int, timestamp)

    """
    Adds points to the user's balance and records the transaction in the history.
    If points are being taken away, no transaction will be recorded, just updates the total amount of points.

    Args:
        payer (str): The user who added the points.
        points (int): The number of points added. This could be negative to take away points
        timestamp (datetime): The timestamp of the transaction.
    Raises:
        ValueError: If a payer's points go negative.
    Returns:
        int: The updated points balance.
    """

    def add_points(self, payer: str, points: int, timestamp: datetime):
        if self.points_mapping[payer] + points < 0:
            raise ValueError(f"Points for {payer} cannot go negative")

        if points > 0:
            heapq.heappush(self.points_history, (timestamp, payer, points))
        else:
            self.debt[payer] = (
                self.debt.get(payer, (0, 0))[0] + abs(points),
                timestamp,
            )

        self.points_balance += points
        self.points_mapping[payer] += points

        # update the amount
        return self.points_balance

    """
    Spends points from the user's balance and get a list of payers to charge. 
    Payers of users oldest points (determined by timestamp) will be used first.

    Args:
        points (int): The number of points to be spent.
    Raises:
        ValueError: If the user does not have enough points to spend.
    Returns:
        defaultdict: The payers (key) and amount of points subtracted from payers (value). Amount
              is negative or 0.
    """

    def spend_points(self, points):
        if points > self.points_balance:
            raise ValueError("Not enough points")
        self.points_balance -= points

        removed = defaultdict(int)
        while points > 0:
            timestamp, payer, amount = heapq.heappop(self.points_history)

            if (
                payer in self.debt
                and self.debt[payer][0] > 0
                and self.debt[payer][1] > timestamp
            ):  # there is a debt
                amount -= self.debt[payer][0]

                if amount > 0:
                    del self.debt[payer]
                else:
                    self.debt[payer] = (
                        amount,
                        self.debt[payer][1],
                    )  # clear the debt

            if amount <= 0:
                continue

            if amount <= points:  # completely spend all of this payer's points
                points -= amount
                self.points_mapping[payer] -= amount
                removed[payer] -= amount
            else:  # will have some points leftover
                heapq.heappush(self.points_history, (timestamp, payer, amount - points))
                self.points_mapping[payer] -= points
                removed[payer] -= points
                points = 0

        return removed

    """
    Gets the amount of points left in this user.

    Returns:
        int: The current points balance.
    """

    def get_total_balance(self):
        return self.points_balance

    def get_points_mapping(self):
        return self.points_mapping
