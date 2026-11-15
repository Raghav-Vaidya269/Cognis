"""Structured logging configuration."""

import logging

import structlog #Structured logging can produce logs in various formats, including JSON, which can be easily parsed and analyzed by log management systems.
from structlog.types import Processor


def configure_logging(level: str = "INFO", json_logs: bool = False) -> None: #level parameter specifies the logging level (e.g., "DEBUG", "INFO", "WARNING", "ERROR"), and json_logs parameter determines whether the logs should be formatted as JSON or plain text.
    #-> None indicates that this function does not return any value.
    level_no = logging.getLevelNamesMapping()[level.upper()] #logging.getLevelNamesMapping() retrieves a mapping of logging level names to their corresponding numeric values. The level.upper() converts the provided level string to uppercase to ensure case-insensitive matching. 
    #The resulting numeric value is stored in the level_no variable.

    processors: list[Processor] = [ #A processor is a function that modifies or adds information to a log message.
        structlog.contextvars.merge_contextvars,  # adds request_id etc.
        structlog.processors.add_log_level, # adds the log level (e.g., "INFO", "ERROR") to the log message.
        structlog.processors.TimeStamper(fmt="iso", utc=True), # adds a timestamp to the log message in ISO 8601 format (e.g., "2023-03-15T12:34:56Z") and ensures that the timestamp is in Coordinated Universal Time (UTC).
    ]
    if json_logs: #if json_logs is True, the log messages will be formatted as JSON. This is useful for structured logging and integration with log management systems that can parse JSON logs.
        processors += [structlog.processors.format_exc_info, structlog.processors.JSONRenderer()]
    else:
        processors.append(structlog.dev.ConsoleRenderer())

    structlog.configure( #configure the structlog library with the specified processors, a wrapper class for filtering log messages based on the logging level, a logger factory for creating loggers, and caching behavior for loggers.
        processors=processors,
        wrapper_class=structlog.make_filtering_bound_logger(level_no),
        logger_factory=structlog.PrintLoggerFactory(),
        cache_logger_on_first_use=False,
    )