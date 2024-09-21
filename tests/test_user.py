import pytest
from data.user import User
from datetime import datetime


# Convert datetime object to ISO 8601 format with a "Z" to indicate UTC
def datetime_to_str(dt: datetime):
    return dt.strftime("%Y-%m-%dT%H:%M:%SZ")


# Convert string to datetime object
def str_to_datetime(s: str):
    return datetime.strptime(s, "%Y-%m-%dT%H:%M:%SZ")


# Verifies the data in a user is as expected by `history`
def verify_points(user: User, balance: int, history: list):
    assert user.points_balance == balance

    assert len(history) == len(user.points_history)
    for i in range(len(user.points_history)):
        assert user.points_history[i][1] == history[i][0]
        assert user.points_mapping[user.points_history[i][1]] == history[i][1]


def compare_defaultdict_with_dict(default_dict, regular_dict):
    """Compares a defaultdict with a regular dictionary."""

    # Check if keys are the same
    if default_dict.keys() != regular_dict.keys():
        return False

    # Check if values are the same for each key
    for key in default_dict.keys():
        if default_dict[key] != regular_dict[key]:
            return False

    return True


def test_user_creation():
    """
    GIVEN a user
    WHEN a new user is created
    THEN check points are set to 0 and points and min heap of size 0 is created
    """

    user = User()
    assert user.points_balance == 0
    assert len(user.points_history) == 0


def test_basic_user_add():
    """
    GIVEN a user
    WHEN points are added to a user balance
    THEN check if points are place in an order from oldest to newest and data is all there
    """

    user = User()

    # not in correct order to points gained (good test)
    user.add_points("DANNON", 100, str_to_datetime("2020-11-02T14:00:00Z"))
    user.add_points("MILLER COORS", 300, str_to_datetime("2020-12-14T14:00:00Z"))
    user.add_points("UNILEVER", 200, str_to_datetime("2020-12-02T14:00:00Z"))

    assert user.points_balance == 600
    assert len(user.points_history) == 3

    assert user.points_history[0] == (
        str_to_datetime("2020-11-02T14:00:00Z"),
        "DANNON",
        100,
    )

    assert user.points_mapping["DANNON"] == 100

    assert user.points_history[1] == (
        str_to_datetime("2020-12-14T14:00:00Z"),
        "MILLER COORS",
        300,
    )

    assert user.points_mapping["MILLER COORS"] == 300

    assert user.points_history[2] == (
        str_to_datetime("2020-12-02T14:00:00Z"),
        "UNILEVER",
        200,
    )

    assert user.points_mapping["UNILEVER"] == 200


def test_user_add_negative_points():
    """
    GIVEN a user
    WHEN taking away points from user
    THEN check points if points left over is as expected
    """
    user = User()

    user.add_points("DANNON", 100, str_to_datetime("2020-11-02T14:00:00Z"))
    user.add_points("DANNON", -50, str_to_datetime("2020-12-02T14:00:00Z"))

    assert user.points_mapping["DANNON"] == 50


def test_user_payer_points_go_negative():
    """
    GIVEN a user
    WHEN taking away points from user would cause them to have negative points
    THEN an `ValueError` is raised
    """
    user = User()

    user.add_points("DANNON", 100, str_to_datetime("2020-11-02T14:00:00Z"))

    with pytest.raises(ValueError) as e:
        user.add_points("DANNON", -200, str_to_datetime("2020-12-02T14:00:00Z"))


def test_user_spend_over_one_carry_over():
    """
    GIVEN a user
    WHEN points are subtracted
    THEN check if correct payer points are subtracted and removed from the user data
    """

    user = User()

    # not in correct order to points gained (good test)
    user.add_points("DANNON", 100, str_to_datetime("2020-11-02T14:00:00Z"))
    user.add_points("MILLER COORS", 300, str_to_datetime("2020-12-14T14:00:00Z"))
    user.add_points("UNILEVER", 200, str_to_datetime("2020-12-02T14:00:00Z"))

    assert compare_defaultdict_with_dict(
        user.spend_points(150),
        {
            "DANNON": -100,
            "UNILEVER": -50,
        },
    )

    verify_points(user, 450, [("UNILEVER", 150), ("MILLER COORS", 300)])


def test_user_spend_all():
    """
    GIVEN a user
    WHEN user wants to use all points
    THEN no points left over
    """
    user = User()
    user.add_points("DANNON", 100, str_to_datetime("2020-11-02T14:00:00Z"))
    user.add_points("MILLER COORS", 300, str_to_datetime("2020-12-14T14:00:00Z"))
    user.add_points("UNILEVER", 200, str_to_datetime("2020-12-02T14:00:00Z"))

    assert compare_defaultdict_with_dict(
        user.spend_points(600),
        {
            "DANNON": -100,
            "UNILEVER": -200,
            "MILLER COORS": -300,
        },
    )

    verify_points(user, 0, [])


def test_user_spend_one():
    """
    GIVEN a user
    WHEN user spends exactly one payer's entire allocated points
    THEN that payer's points is completely removed
    """
    user = User()
    user.add_points("DANNON", 100, str_to_datetime("2020-11-02T14:00:00Z"))
    user.add_points("MILLER COORS", 300, str_to_datetime("2020-12-14T14:00:00Z"))
    user.add_points("UNILEVER", 200, str_to_datetime("2020-12-02T14:00:00Z"))

    assert compare_defaultdict_with_dict(user.spend_points(100), {"DANNON": -100})
    verify_points(user, 500, [("UNILEVER", 200), ("MILLER COORS", 300)])


def test_order_of_spending():
    """
    GIVEN a user
    WHEN adding points in a different order from timestamps
    THEN spend the points of the oldest first
    """
    user = User()
    user.add_points("DANNON", 100, str_to_datetime("2020-06-02T14:00:00Z"))
    user.add_points("MILLER COORS", 300, str_to_datetime("2020-03-14T14:00:00Z"))
    user.add_points("UNILEVER", 200, str_to_datetime("2020-01-02T14:00:00Z"))

    assert compare_defaultdict_with_dict(
        user.spend_points(300),
        {
            "UNILEVER": -200,
            "MILLER COORS": -100,
        },
    )
    verify_points(user, 300, [("MILLER COORS", 200), ("DANNON", 100)])


def test_not_enough_points():
    """
    GIVEN a user
    WHEN not enough points are available to spend
    THEN raise a `ValueError` exception
    """
    user = User()

    user.add_points("DANNON", 100, str_to_datetime("2020-06-02T14:00:00Z"))
    user.add_points("MILLER COORS", 300, str_to_datetime("2020-03-14T14:00:00Z"))

    with pytest.raises(ValueError) as e:
        user.spend_points(1000)


def test_same_payer_but_with_break():
    """
    GIVEN a user
    WHEN user spends points for a payer they got at different times (after another pay gave them points)
    THEN spend the first payer's points first and continue spending it after the second payer's points wasn't enough
    """
    user = User()

    user.add_points("DANNON", 100, str_to_datetime("2020-06-02T14:00:00Z"))
    user.add_points("MILLER COORS", 300, str_to_datetime("2020-08-14T14:00:00Z"))
    user.add_points("DANNON", 200, str_to_datetime("2020-09-02T14:00:00Z"))

    assert compare_defaultdict_with_dict(
        user.spend_points(450), {"DANNON": -150, "MILLER COORS": -300}
    )


def test_final_boss():
    user = User()

    user.add_points("DANNON", 300, str_to_datetime("2022-10-31T10:00:00Z"))
    user.add_points("UNILEVER", 200, str_to_datetime("2022-10-31T11:00:00Z"))
    user.add_points("DANNON", -200, str_to_datetime("2022-10-31T15:00:00Z"))
    user.add_points("MILLER COORS", 10000, str_to_datetime("2022-11-01T14:00:00Z"))
    user.add_points("DANNON", 1000, str_to_datetime("2022-11-02T14:00:00Z"))

    user.spend_points(5000)

    verify_points(user, 6300, [("MILLER COORS", 5300), ("DANNON", 1000)])

    assert user.points_mapping["DANNON"] == 1000
    assert user.points_mapping["MILLER COORS"] == 5300
    assert user.points_mapping["UNILEVER"] == 0
