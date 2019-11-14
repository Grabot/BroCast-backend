from flask import Flask, request, jsonify

app = Flask(__name__)


@app.route("/")
def index():
    """
    The index page.
    """
    return "Hello World"


@app.route('/users/<user>', methods=['GET'])
def hello_user(user):
    """
    a simple get call where a username is passed as argument.
    """
    return "Hello %s!" % user


@app.route('/api/post_some_data', methods=['POST'])
def get_post_message():
    """
    gets a post message with a json argument that will be returned.
    """
    json = request.get_json()
    print(json)
    if len(json['text']) == 0:
        return jsonify({'error': 'invalid input'})

    return jsonify({'you sent this': json['text']})


if __name__ == '__main__':
    app.run()

