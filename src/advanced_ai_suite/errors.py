"""Errors raised when talking to the local model runtime."""


class ModelError(Exception):
    status_code: int = 500
    category: str = "model_error"

    def __init__(self, message: str) -> None: #__init__ method is a special method in Python classes that is called when an instance of the class Model Error is created. It initializes the instance with the provided message.
        super().__init__(message)
        self.message = message


class ModelUnavailableError(ModelError):
    """Ollama is not reachable (not running, wrong URL, overloaded)."""

    status_code = 503
    category = "model_unavailable"


class ModelTimeoutError(ModelError):
    """Ollama accepted the request but did not answer in time."""

    status_code = 504
    category = "model_timeout"


class ModelNotFoundError(ModelError):
    """The requested model is not installed in Ollama."""

    status_code = 404
    category = "model_not_found"


class ModelResponseError(ModelError):
    """Ollama answered with an error or an unexpected body."""

    status_code = 502
    category = "model_bad_response"