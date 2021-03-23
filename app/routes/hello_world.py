from app.routes import app_view


@app_view.route('/', methods=['GET', 'POST'])
def home():
    return {"hello": "world"}
