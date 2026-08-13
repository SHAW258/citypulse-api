"""WSGI entrypoint for PythonAnywhere and WSGI application servers."""

from a2wsgi import ASGIMiddleware

from app.main import app

# PythonAnywhere looks for the 'application' callable
application = ASGIMiddleware(app)
