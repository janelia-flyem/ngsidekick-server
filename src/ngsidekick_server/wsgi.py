"""WSGI entry point for production deployment."""

from ngsidekick_server.app import create_app

app = create_app()

if __name__ == "__main__":
    app.run()

