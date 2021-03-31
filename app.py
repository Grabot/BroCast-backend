from app import create_app
from app import socks

app = create_app()


if __name__ == "__main__":
    socks.run(app, host="0.0.0.0", debug=True)
