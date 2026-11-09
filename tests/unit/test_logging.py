
import logging

from aditi.infrastructure.logging import (
    LoggingConfig,
    configure_logging,
    get_logger,
)


def test_configure_logging_returns_application_logger():
    logger = configure_logging()

    assert logger.name == "aditi"


def test_get_logger_returns_application_logger():
    logger = get_logger()

    assert logger.name == "aditi"


def test_get_logger_creates_module_logger():
    logger = get_logger("modules.pathways")

    assert logger.name == "aditi.modules.pathways"


def test_get_logger_accepts_fully_qualified_name():
    logger = get_logger("aditi.data.parsers")

    assert logger.name == "aditi.data.parsers"


def test_configure_logging_sets_level():
    logger = configure_logging(
        LoggingConfig(level=logging.DEBUG)
    )

    assert logger.level == logging.DEBUG


def test_configure_logging_does_not_duplicate_handlers():
    logger = configure_logging()

    initial_count = len(logger.handlers)

    configure_logging()

    assert len(logger.handlers) == initial_count
    assert initial_count == 1


def test_configure_logging_writes_to_file(tmp_path):
    log_file = tmp_path / "logs" / "aditi.log"

    configure_logging(
        LoggingConfig(
            level=logging.INFO,
            log_file=log_file,
        )
    )

    logger = get_logger("modules.pathways")
    logger.info("Pathway module initialized.")

    assert log_file.exists()
    assert "Pathway module initialized." in log_file.read_text(
        encoding="utf-8"
    )


def test_configure_logging_uses_custom_format(capsys):
    configure_logging(
        LoggingConfig(
            level=logging.INFO,
            format_string="%(levelname)s: %(message)s",
        )
    )

    logger = get_logger("runtime")
    logger.info("Runtime initialized.")

    captured = capsys.readouterr()

    assert "INFO: Runtime initialized." in captured.err


def test_module_logger_inherits_application_level():
    configure_logging(
        LoggingConfig(level=logging.WARNING)
    )

    logger = get_logger("modules.pathways")

    assert logger.getEffectiveLevel() == logging.WARNING
