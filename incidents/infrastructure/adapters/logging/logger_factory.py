"""Logging configuration and factory."""

import logging
import sys


class LoggerFactory:
    """Factory for creating configured loggers."""

    _configured = False

    @classmethod
    def configure(cls, level: str = "INFO"):
        """
        Configure root logger.

        Args:
            level: Logging level (INFO, DEBUG, WARNING, ERROR)
        """
        if cls._configured:
            return

        # Create formatter
        formatter = logging.Formatter(
            fmt="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
            datefmt="%Y-%m-%d %H:%M:%S",
        )

        # Configure root logger
        root_logger = logging.getLogger()
        root_logger.setLevel(getattr(logging, level.upper()))

        # Add console handler
        console_handler = logging.StreamHandler(sys.stdout)
        console_handler.setFormatter(formatter)
        root_logger.addHandler(console_handler)

        cls._configured = True

    @classmethod
    def get_logger(cls, name: str) -> logging.Logger:
        """
        Get configured logger for module.

        Args:
            name: Module name (usually __name__)

        Returns:
            Configured logger instance
        """
        if not cls._configured:
            cls.configure()

        return logging.getLogger(name)


# Global instance
logger_factory = LoggerFactory()
