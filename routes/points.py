"""
API endpoints relating to single arbitary user.
"""

from flask import request, jsonify
from datetime import datetime

from data.user import User

from __main__ import app

# main user
user = User()

"""
This endpoint allows users to add points for a specific payer along with a timestamp of the transaction.
Content Type: application/json

Request Body Parameters: {
    payer (str): name of the payer
    points (int): number of points to add
    timestamp (str): timestamp of the transaction
}

Success Response
- Code: 200 OK
- Description: Points were added successfully.
- Content-Type: application/json

Error Response
1. Invalid Input
- Code: 400 Bad Request
- Description: Missing or incorrect input.
- Content-Type: application/json

2. Negative Payer Points
- Code: 400 Bad Request
- Description: Cannot have negative payer points
- Content-Type: application/json

3. Invalid Timestamp Format:
- Code: 400 Bad Request
- Description: The timestamp format is incorrect.
- Content-Type: application/json
"""


@app.route("/add", methods=["POST"])
def add():
    data = request.get_json()
    payer: str = data.get("payer")
    points: int = data.get("points")
    timestamp: str = data.get("timestamp")

    if not payer or not isinstance(points, int) or not timestamp:
        return jsonify({"error": "Invalid input"}), 400

    # convert string timestamp to datetime
    try:
        timestamp_obj = datetime.strptime(timestamp, "%Y-%m-%dT%H:%M:%SZ")
    except ValueError:
        return jsonify({"error": "Invalid timestamp format"}), 400

    try:
        user.add_points(payer, points, timestamp_obj)
    except ValueError as e:
        return jsonify({"error": "Can't have negative payer points"}), 400

    return (
        jsonify(
            {
                "message": "Points added successfully",
                "data": {"payer": payer, "points": points, "timestamp": timestamp},
            }
        ),
        200,
    )


"""
This endpoint allows users to spend points they have added to their account.
Content Type: application/json

Request Body Parameters: {
    points (int): number of points to spend
}

Success Response
- Code: 200 OK
- Description: Points were added successfully.
- Content-Type: application/json

Error Response
1. Invalid Input
- Code: 400 Bad Request
- Description: Missing or incorrect input.
- Content-Type: application/json

2. Spending more points that available
- Code: 400 Bad Request
- Description: Can't spend more points that what's allocated.
- Content-Type: application/json
"""


@app.route("/spend", methods=["POST"])
def spend():
    data = request.get_json()
    points: int = data.get("points")

    if not points or not isinstance(points, int):
        return jsonify({"error": "Invalid input"}), 400

    try:
        payers = user.spend_points(points)
    except ValueError as e:
        return (
            jsonify(
                {"error": "Can't spend more points than what's available to user."}
            ),
            400,
        )

    return jsonify(payers), 200


"""
Adds points to user's balance. 

POST /add

Request Body:
{
  payer: string,
  points: int,
  timstamp: datetime
}
"""


@app.route("/balance", methods=["GET"])
def balance():
    return jsonify(user.get_points_mapping()), 200
