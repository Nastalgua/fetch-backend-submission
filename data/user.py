"""
User model for maintaing information about user. This information includes:
- points_balance (int)
- points_history (heap)
- points_mapping (dict): payer, total
- debt (dict): payer, (balance, timestamp)
"""

"""
Comments:
- The way I handle negative points 
"""

import heapq
from collections import defaultdict
from datetime import datetime


class User:
    def __init__(self):
        self.points_balance = 0

        # this should be a minHeap that is ordered by the timestamp
        self.points_history = []
        self.points_mapping = defaultdict(int)  # payer, total
        self.debt = defaultdict(list)  # payer, [(int, timestamp)]

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
            heapq.heappush(self.debt[payer], (timestamp, abs(points)))

        self.points_balance += points
        self.points_mapping[payer] += points

        return self.points_balance

    """
    Spends points from the user's balance and get a list of payers to charge. 
    Payers of users oldest points (determined by timestamp) will be used first.

    If a user has some kind of debt of points, but they already spent points before the debt was added to their account, just ignored the
    debt amount. Don't think we would be asking user for points back.

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

            # check if we removed points in the future and update the actual amount of points we have at this transaction
            while payer in self.debt and self.debt[payer] and amount >= 0:
                # debt timestamp is before any of the new transactions current; must mean the user already spent the points and there are no
                # points to actually use to account for the debt after this point remove the debt because the customer is always right
                # i.e. 200 (D, 1) -> 200 (5) -> spend 200 (6) -> -50 (D, 2), there would be no points to take 50 from; just forget about the debt
                debt_timestamp, debt_amt = heapq.heappop(self.debt[payer])
                if debt_timestamp > timestamp:
                    amount -= debt_amt
                    if amount < 0:  # user still owes points
                        heapq.heappush(self.debt[payer], (debt_timestamp, abs(amount)))

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

    """
    Gets the amount of points from each payer

    Returns:
        dict: The current distributions of points from each payer for this user.
    """

    def get_points_mapping(self):
        return self.points_mapping
