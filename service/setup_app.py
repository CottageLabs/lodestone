import logging
import logging.config
from octopus.lib import paths

def setup_app(app):
    logging.config.fileConfig(paths.rel2abs(__file__, "..", "sword2_logging.conf"))
    logger = logging.getLogger('setup_app')
    logger.info("Logging configured")