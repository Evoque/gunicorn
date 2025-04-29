"""
Logging HOWTO: https://docs.python.org/3/howto/logging.html
"""

""" Basic Logging Tutorial """
import logging


logger = logging.getLogger(__name__)
logging.basicConfig(
    filename="exp.log",
    encoding="utf-8",
    level=logging.DEBUG,
    format="%(levelname)s-%(asctime)s %(message)s"
)

# logger.debug("--------------")
# logger.debug("This message should go to the log file")
# logger.info("So should this")
# msg = "formatted msg"
# logger.warning(f"And this, too, {msg}")
logger.error("And non-ASCII stuff, too, like Øresund and Malmö\n")


try:
    raise ValueError('这是一个模拟的错误')
except ValueError as e:
    logger.exception("ValueError ---")
