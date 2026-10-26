import logging

streamHandler = logging.StreamHandler()
streamHandler.setLevel(logging.INFO)

formatter = logging.Formatter(
    "%(asctime)s %(levelname)s [%(threadName)s] %(filename)s: %(message)s"
)
streamHandler.setFormatter(formatter)

logger = logging.getLogger("main")
logger.setLevel(logging.INFO)
logger.addHandler(streamHandler)
