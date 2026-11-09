
from aditi.application.modules.manager import ModuleManager
from aditi.application.runtime.application import Application
from aditi.application.runtime.context import ApplicationContext
from aditi.application.runtime.module_runtime import RuntimeState
from aditi.infrastructure.logging import get_logger

logger = get_logger("bootstrap")


def create_application() -> Application:
    """
    Construct the Aditi application.

    Application modules will be registered here as they
    are implemented.
    """

    module_manager = ModuleManager()

    context = ApplicationContext(
        application_name="Aditi",
    )

    return Application(
        module_manager=module_manager,
        context=context,
        target_update_rate_hz=60.0,
    )


def main() -> int:
    """Execute the Aditi application bootstrap sequence."""

    application = create_application()
    exit_code = 0

    try:
        application.initialize()
        application.start()

        logger.info("Aditi application started successfully.")

        application.run()

    except KeyboardInterrupt:
        logger.info("Aditi application interrupted by user.")
        exit_code = 130

    except Exception:
        logger.exception("Aditi application execution failed.")
        exit_code = 1

    finally:
        if application.state not in (
            RuntimeState.NEW,
            RuntimeState.SHUTDOWN,
        ):
            try:
                application.shutdown()

            except KeyboardInterrupt:
                logger.warning(
                    "Aditi application shutdown interrupted by user."
                )

                if exit_code == 0:
                    exit_code = 130

            except Exception:
                logger.exception(
                    "Aditi application shutdown failed."
                )
                exit_code = 1

    return exit_code


if __name__ == "__main__":
    raise SystemExit(main())
