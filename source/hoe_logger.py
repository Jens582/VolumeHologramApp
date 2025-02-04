import logging
import logging.handlers
import queue



log_queue = queue.Queue()
logger = logging.getLogger("Hologram_app_logger")
logger.setLevel(logging.DEBUG)

queue_handler = logging.handlers.QueueHandler(log_queue)
logger.addHandler(queue_handler)

formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
for handler in logger.handlers:
    handler.setFormatter(formatter)