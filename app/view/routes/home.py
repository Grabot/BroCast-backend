from app.view.routes import app_view


@app_view.route('/', methods=['GET', 'POST'])
@app_view.route('/home', methods=['GET', 'POST'])
def home():
    return "You have found the BroCast backend api"

