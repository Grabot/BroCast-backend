import os

from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    API_V1_STR: str = "/api/v1.0"
    API_LOGIN_STR: str = "/login"

    POSTGRES_URL: str = os.environ["POSTGRES_URL"]
    POSTGRES_PORT: int = os.environ["POSTGRES_PORT"]
    POSTGRES_USER: str = os.environ["POSTGRES_USER"]
    POSTGRES_PASSWORD: str = os.environ["POSTGRES_PASSWORD"]
    POSTGRES_DB: str = os.environ["POSTGRES_DB"]

    REDIS_URL: str = os.environ["REDIS_URL"]
    REDIS_PORT: int = os.environ["REDIS_PORT"]

    ASYNC_DB_URL: str = "postgresql+asyncpg://{user}:{pw}@{url}:{port}/{db}".format(
        user=POSTGRES_USER,
        pw=POSTGRES_PASSWORD,
        url=POSTGRES_URL,
        port=POSTGRES_PORT,
        db=POSTGRES_DB,
    )

    SYNC_DB_URL: str = "postgresql://{user}:{pw}@{url}:{port}/{db}".format(
        user=POSTGRES_USER,
        pw=POSTGRES_PASSWORD,
        url=POSTGRES_URL,
        port=POSTGRES_PORT,
        db=POSTGRES_DB,
    )

    REDIS_URI: str = "redis://{url}:{port}".format(url=REDIS_URL, port=REDIS_PORT)

    SQLALCHEMY_TRACK_MODIFICATIONS: bool = False
    SECRET_KEY: str = os.environ.get("SECRET_KEY") or "you-will-never-guess"

    # Configuration
    GOOGLE_CLIENT_ID: str = os.environ.get("GOOGLE_CLIENT_ID", None)
    GOOGLE_CLIENT_SECRET: str = os.environ.get("GOOGLE_CLIENT_SECRET", None)
    GOOGLE_DISCOVERY_URL: str = "https://accounts.google.com/.well-known/openid-configuration"
    GOOGLE_ACCESS_TOKEN_URL: str = "https://www.googleapis.com/oauth2/v3/userinfo"

    GITHUB_AUTHORIZE: str = "https://github.com/login/oauth/authorize"
    GITHUB_ACCESS: str = "https://github.com/login/oauth/access_token"
    GITHUB_USER: str = "https://api.github.com/user"
    GITHUB_CLIENT_ID: str = os.environ.get("GITHUB_CLIENT_ID", None)
    GITHUB_CLIENT_SECRET: str = os.environ.get("GITHUB_CLIENT_SECRET", None)

    REDDIT_AUTHORIZE: str = "https://www.reddit.com/api/v1/authorize"
    REDDIT_ACCESS: str = "https://www.reddit.com/api/v1/access_token"
    REDDIT_USER: str = "https://oauth.reddit.com/api/v1/me"
    REDDIT_CLIENT_ID: str = os.environ.get("REDDIT_CLIENT_ID", None)
    REDDIT_CLIENT_SECRET: str = os.environ.get("REDDIT_CLIENT_SECRET", None)
    REDDIT_REDIRECT: str = "https://brocast.nl/login/reddit/callback"

    APPLE_AUTHORIZE: str = "https://appleid.apple.com/auth/token"
    APPLE_CLIENT_ID: str = os.environ.get("APPLE_CLIENT_ID", None)
    APPLE_AUD_URL: str = "https://appleid.apple.com"
    APPLE_KEY_ID: str = os.environ.get("APPLE_KEY_ID", None)
    APPLE_TEAM_ID: str = os.environ.get("APPLE_TEAM_ID", None)
    APPLE_AUTH_KEY: str = os.environ.get("APPLE_AUTH_KEY", None)
    APPLE_GRANT_TYPE: str = "authorization_code"
    APPLE_REDIRECT_URL: str = os.environ.get("APPLE_REDIRECT_URL", None)

    jwk: dict = {
        "alg": os.environ.get("JWT_ALG", ""),
        "crv": os.environ.get("JWT_CRV", ""),
        "d": os.environ.get("JWT_D", ""),
        "key_ops": ["sign", "verify"],
        "kty": os.environ.get("JWT_KTY", ""),
        "x": os.environ.get("JWT_X", ""),
        "y": os.environ.get("JWT_Y", ""),
        "use": os.environ.get("JWT_USE", ""),
        "kid": os.environ.get("JWT_KID", ""),
    }

    header: dict = {
        "alg": os.environ.get("JWT_ALG", ""),
        "kid": os.environ.get("JWT_KID", ""),
        "typ": os.environ.get("JWT_TYP", ""),
    }
    JWT_SUB: str = os.environ.get("JWT_SUB", "")
    JWT_ISS: str = os.environ.get("JWT_ISS", "")
    JWT_AUD: str = os.environ.get("JWT_AUD", "")
    API_SOCK_NAMESPACE: str = "/api/v1.0/sock"

    MAIL_SERVER: str = os.environ.get("MAIL_SERVER")
    MAIL_PORT: str = int(os.environ.get("MAIL_PORT") or 25)
    MAIL_USE_TLS: str = os.environ.get("MAIL_USE_TLS") is not None
    MAIL_USERNAME: str = os.environ.get("MAIL_USERNAME")
    MAIL_PASSWORD: str = os.environ.get("MAIL_PASSWORD")
    MAIL_SENDERNAME: str = os.environ.get("MAIL_SENDERNAME")
    BASE_URL: str = os.environ.get("BASE_URL")
    UPLOAD_FOLDER_AVATARS: str = "static/uploads/avatars"

    class Config:
        case_sensitive: bool = True


settings = Settings()
