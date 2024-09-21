"""
Matthew Chen's submission for Fetch Backend internship.
"""

from flask import Flask

app = Flask(__name__)

import routes.points


@app.route("/")
def main():
    return "<p>Matthew Chen's submission for Fetch Backend Internship.</p>"


if __name__ == "__main__":
    app.run(host="localhost", port=8000)
