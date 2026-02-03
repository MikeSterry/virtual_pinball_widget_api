"""Dev entrypoint for local `python -m app.main` runs."""
from app import create_app

app = create_app()

if __name__ == "__main__":
    # Flask dev server (do not use in prod)
    app.run(host="0.0.0.0", port=8000, debug=True)
