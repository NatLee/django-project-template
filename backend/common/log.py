"""Logging handler that writes through loguru into rotated, per-level files."""

import logging
import os

from loguru import logger

# loguru unit names for the `when` values accepted by logging.handlers.TimedRotatingFileHandler.
_UNITS = {"s": "second", "m": "minute", "h": "hour", "d": "day", "w": "week"}
_TIME_FORMATS = {
    "s": "{time:%Y-%m-%d_%H-%M-%S}",
    "m": "{time:%Y-%m-%d_%H-%M}",
    "h": "{time:%Y-%m-%d_%H}",
    "d": "{time:%Y-%m-%d}",
    "w": "{time:%Y-%m-%d}",
}
_LEVELS = ("debug", "info", "warning", "error")

# Sink file pattern -> loguru sink id. Django may configure logging more than once
# per process (e.g. the autoreloader), and each file must only get one sink.
_SINKS: dict[str, int] = {}


class InterceptTimedRotatingFileHandler(logging.Handler):
    """Send standard `logging` records to loguru.

    Each level goes to its own file next to `filename`, for example
    `logs/auth/auth_2026-11-04_13_info.log`, rotated every `interval` x `when`
    and compressed to tar.gz once `backupCount` periods old.
    """

    def __init__(
        self,
        filename,
        when="d",
        interval=1,
        backupCount=15,
        encoding="utf-8",
        delay=False,
        utc=False,
        atTime=None,
        logging_levels="all",
    ):
        super().__init__()
        self.filename = os.path.abspath(filename)
        os.makedirs(os.path.dirname(self.filename), exist_ok=True)
        when = when.lower()
        unit = _UNITS[when]
        self.logger_ = logger.bind(sink_file=self.filename)

        if logging_levels == "all":
            levels = _LEVELS
        elif isinstance(logging_levels, str):
            levels = (logging_levels.lower(),)
        else:
            levels = tuple(level.lower() for level in logging_levels)

        for level in levels:
            sink = self.filename.replace(".log", f"_{_TIME_FORMATS[when]}_{level}.log")
            if sink in _SINKS:
                continue
            _SINKS[sink] = self.logger_.add(
                sink,
                rotation=f"{interval} {unit}",
                retention=f"{backupCount} {unit}s",
                encoding=encoding,
                compression="tar.gz",
                delay=delay,
                enqueue=True,
                filter=self._filter(level.upper()),
            )

    def _filter(self, level_name):
        filename = self.filename

        def accept(record):
            return record["level"].name == level_name and record["extra"].get("sink_file") == filename

        return accept

    def emit(self, record):
        try:
            level = self.logger_.level(record.levelname).name
        except ValueError:
            level = record.levelno

        # Point loguru at the caller, not at the logging module internals.
        frame, depth = logging.currentframe(), 2
        while frame and frame.f_code.co_filename == logging.__file__:
            frame = frame.f_back
            depth += 1
        self.logger_.opt(depth=depth, exception=record.exc_info).log(level, record.getMessage())
