from app import db
from app.view.routes import app_view
from flask import render_template
from app.view.models.bro import Bro


@app_view.route('/test_functions', methods=['GET', 'POST'])
def test_functions():
    bros = Bro.query.all()
    for bro in bros:
        print("bro: " + bro.bro_name)
        print("has " + str(bro.bros.count()) + " bros right now")
        print("______________________________________________________")

    return "check logs"

