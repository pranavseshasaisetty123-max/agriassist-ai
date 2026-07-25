import contextvars

request_language = contextvars.ContextVar("request_language", default="en")
