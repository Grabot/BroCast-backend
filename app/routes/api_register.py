from app import db
from app.routes import app_home
from app.models.user import User
from flask import abort
from flask import jsonify
from flask import make_response


# @app_home.route('/brocast_api/register/<string:username>/<string:password>', methods=['GET', 'POST'])
# def api_register(username, password):
#     """
#     Here the registration is handled.
#     The username and password are validated and checked if they don't already exist
#     If the registration is successful the success message is shown and the data is included in the database.
#     """
#     user = User(username=username)
#     user.set_password(password)
#     db.session.add(user)
#     db.session.commit()


@app_home.route('/todo/brocast_api/v1.0/tasks', methods=['GET'])
def get_tasks():
    tasks = [
        {
            'id': 0,
            'title': u'Buy groceries',
            'description': u'Milk, Cheese, Pizza, Fruit, Tylenol',
            'done': False
        },
        {
            'id': 1,
            'title': u'Learn Python',
            'description': u'Need to find a good Python tutorial on the web',
            'done': False
        }
    ]
    return jsonify({'tasks': tasks})


@app_home.route('/brocast_api/register/todo/<int:task_id>', methods=['GET'])
def get_task(task_id):
    tasks = [
        {
            'id': 0,
            'title': u'Buy groceries',
            'description': u'Milk, Cheese, Pizza, Fruit, Tylenol',
            'done': False
        },
        {
            'id': 1,
            'title': u'Learn Python',
            'description': u'Need to find a good Python tutorial on the web',
            'done': False
        }
    ]
    task = [task for task in tasks if task['id'] == task_id]
    if len(task) == 0:
        abort(404)
    return jsonify({'task': task[0]})


@app_home.errorhandler(404)
def not_found(error):
    return make_response(jsonify({'error': 'Not found'}), 404)

