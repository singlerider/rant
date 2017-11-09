import logging


def set_up_logging():
    logging.addLevelName(
        logging.DEBUG, "\033[1;36m{0}\033[1;0m".format(
            logging.getLevelName(logging.DEBUG)))
    logging.addLevelName(
        logging.INFO, "\033[1;32m{0}\033[1;0m".format(
            logging.getLevelName(logging.INFO)))
    logging.addLevelName(
        logging.WARNING, "\033[1;31m{0}\033[1;0m".format(
            logging.getLevelName(logging.WARNING)))
    logging.addLevelName(
        logging.ERROR, "\033[1;41m{0}\033[1;0m".format(
            logging.getLevelName(logging.ERROR)))
    logger = logging.getLogger("rant")
    logging.Formatter(fmt="%(asctime)s.%(msecs)03d",
                      datefmt="%Y-%m-%d,%H:%M:%S")
    logger.setLevel(logging.DEBUG)  # change to INFO for explicit logs
    ch = logging.StreamHandler()
    formatter = logging.Formatter(
        "%(asctime)s.%(msecs)03d - %(name)s - %(levelname)s - %(message)s",
        "%Y-%m-%d %H:%M:%S"
    )
    ch.setFormatter(formatter)
    logger.addHandler(ch)
    logger.propagate = False
