"""FastAPI backend entrypoint for the project.

This keeps the backend interface separate from the Streamlit frontend while
reusing the existing implementation under the app/ package.
"""

from app.api.main import app

__all__ = ["app"]
