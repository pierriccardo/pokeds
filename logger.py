import logging


def setup():
    """Set up the root logger"""
    logging.basicConfig(
        level=logging.INFO,  # log messages with severity INFO and above
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
        handlers=[logging.StreamHandler(), logging.FileHandler("app.log")],
    )
    logger = logging.getLogger()  # get the root logger
    return logger
