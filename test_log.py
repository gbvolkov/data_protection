import logging
logger = logging.getLogger(__name__)

def do_something():
    logger.debug("🐛 debug from utils.do_something()")
    logger.info ("ℹ️  info from utils.do_something()")
    logger.warning("⚠️  warning from utils.do_something()")
