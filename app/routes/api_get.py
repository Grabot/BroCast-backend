from app.routes import app_home


@app_home.route('/users/<user>', methods=['GET'])
def hello_user(user):
    """
    a simple get call where a username is passed as argument.
    """
    return "Hello %s!" % user

