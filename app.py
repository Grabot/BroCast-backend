from flask import Flask
from flask_restful import Api, Resource

app = Flask(__name__, static_url_path="")
api = Api(app)


class Bro(Resource):
    def __init__(self):
        print("broer")

    def get(self):
        print("getting")
        return {'bro': 'get'}

    def post(self):
        print("posting")
        return {'bro': 'post'}


api.add_resource(Bro, '/bro', endpoint='bros')


if __name__ == '__main__':
    app.run(debug=True)
