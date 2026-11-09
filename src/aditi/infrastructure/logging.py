
import logging
from dataclasses import dataclass
from pathlib import Path

LOGGER_NAME = "aditi"

DEFAULT_FORMAT = (
    "%(asctime)s | %(levelname)s | %(name)s | %(message)s"
)

DEFAULT_DATE_FORMAT = "%Y-%m-%d %H:%M:%S"


@dataclass(frozen=True, slots=True)
class LoggingConfig:
    """Configuration for the Aditi logging infrastructure."""

    level: int | str = logging.INFO
    log_file: Path | None = None

    format_string: str = DEFAULT_FORMAT
    date_format: str = DEFAULT_DATE_FORMAT


def configure_logging(
    config: LoggingConfig | None = None,
) -> logging.Logger:
    """
    Configure the application-wide Aditi logger.

    Replaces previously managed handlers to prevent duplicate
    output when configuration is applied multiple times.
    """

    if config is None:
        config = LoggingConfig()

    logger = logging.getLogger(LOGGER_NAME)

    logger.setLevel(config.level)
    logger.propagate = False

    # Remove handlers previously managed by this infrastructure.
    for handler in logger.handlers[:]:
        logger.removeHandler(handler)
        handler.close()

    formatter = logging.Formatter(
        fmt=config.format_string,
        datefmt=config.date_format,
    )

    console_handler = logging.StreamHandler()
    console_handler.setFormatter(formatter)
    # console_handler._aditi_managed = True

    logger.addHandler(console_handler)

    if config.log_file is not None:
        config.log_file.parent.mkdir(
            parents=True,
            exist_ok=True,
        )

        file_handler = logging.FileHandler(
            config.log_file,
            encoding="utf-8",
        )

        file_handler.setFormatter(formatter)
        # file_handler._aditi_managed = True

        logger.addHandler(file_handler)

    return logger


def get_logger(name: str | None = None) -> logging.Logger:
    """
    Retrieve a logger within the Aditi logger hierarchy.

    Examples:
        get_logger() -> aditi
        get_logger("modules.pathways") -> aditi.modules.pathways
        get_logger("data.parsers") -> aditi.data.parsers
    """

    if name is None or not name.strip():
        return logging.getLogger(LOGGER_NAME)

    if name == LOGGER_NAME or name.startswith(f"{LOGGER_NAME}."):
        logger_name = name
    else:
        logger_name = f"{LOGGER_NAME}.{name}"

    return logging.getLogger(logger_name)
