from flask import Flask, request
from flask_restful import Api, Resource, abort
import json
import os

app = Flask("banAPI")
api = Api(app)
with open("keys.json", "r") as file:
    keys = json.load(file)

version = "pre-alpha"


def abortResponse(condition: bool, errorCode: int, message: str = "no message given"):
    if condition:
        abort(errorCode, message=message)


def checkKey(key):
    if key:
        if not key in keys:
            abort(401, message="invalid or no api key")


class getUser(Resource):
    @staticmethod
    def get(_id: int):
        with open("data.json", "r") as data:
            cases = json.load(data)["cases"]
            if _id == 0:
                return cases, 200
            test = cases.get(str(_id))
            print(test)
            abortResponse(not test, 404, "user not banned or isn't recorded to be banned")
            return {_id: cases[str(_id)]}, 201


class banUser(Resource):
    @staticmethod
    def post(_id: int, reason: str):
        checkKey(request.headers.get("X-Api-Key"))
        with open("data.json", "r") as data:
            cases = json.load(data)
        abortResponse(cases["cases"].get(str(_id)), 409, "user already banned")
        cases["cases"][_id] = reason
        with open("data.json", "w") as data:
            json.dump(cases, data)
            return {"success": 201}


class unbanUser(Resource):
    @staticmethod
    def post(_id: int):
        checkKey(request.headers.get("X-Api-Key"))
        with open("data.json", "r") as data:
            cases = json.load(data)
            abortResponse(not cases["cases"].get(str(_id)), 409, "user not banned or isn't recorded to be banned")
            del cases["cases"][str(_id)]
        with open("data.json", "w") as data:
            json.dump(cases, data)
            return {"success": 201}


api.add_resource(getUser, "/bans/<int:_id>")
api.add_resource(banUser, "/banuser/<int:_id>/<string:reason>")
api.add_resource(unbanUser, "/unbanuser/<int:_id>/")


@app.route("/")
def main():
    return {"name": app.name, "version": version, "endpoints": "".join("/" + i + "/" for i in api.endpoints)}


app.debug = False
if __name__ == "__main__":
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)
