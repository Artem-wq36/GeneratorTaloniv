from settings import ensure_storage
from interface import run_app


if __name__ == "__main__":
    ensure_storage()
    run_app()