import logging


def setup(level: int = logging.INFO):
    """Set up the root logger"""
    logging.basicConfig(
        level=level,  # log messages with severity INFO and above
        format="%(asctime)s - %(name)s.%(funcName)s - %(threadName)s - %(levelname)s - %(message)s",
        datefmt='%Y-%m-%d %H:%M:%S',
        handlers=[logging.StreamHandler(), logging.FileHandler("app.log")],
    )
    logger = logging.getLogger()  # get the root logger
    return logger
