"""Tests for the logger module."""

import logging
import unittest

from feed_to_somewhere.logger import setup_logger


class TestLogger(unittest.TestCase):
    """Test cases for logger configuration."""

    def test_setup_logger_updates_existing_handler_level(self):
        """Test setup_logger updates the level of an existing handler."""
        logger_name = "feed_to_somewhere.tests.logger"
        logger = setup_logger(name=logger_name, level=logging.INFO)

        updated_logger = setup_logger(name=logger_name, level=logging.DEBUG)

        self.assertEqual(updated_logger.level, logging.DEBUG)
        self.assertEqual(updated_logger.handlers[0].level, logging.DEBUG)


if __name__ == "__main__":
    unittest.main()
