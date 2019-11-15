from app.routes import app_home
from flask import jsonify
from flask import request


@app_home.route('/api/post_data', methods=['POST'])
def get_post_message():
    """
    gets a post message and it returns a pre determined json argument.
    """
    json = request.get_json()
    print(json)
    if len(json['text']) == 0:
        return jsonify({'error': 'invalid input'})

    return jsonify({'you sent this': json['text']})

