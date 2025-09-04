"""
Logger configuration for the SaaS Billing Platform.
Logs messages to a file (sass_billing_logs.log) with timestamps, level, and message.
"""

import logging

logging.basicConfig(
     filename="sass_billing_logs.log",
     format="%(asctime)s - %(levelname)s - %(message)s",
     level=logging.INFO
)

logger = logging.getLogger(__name__)