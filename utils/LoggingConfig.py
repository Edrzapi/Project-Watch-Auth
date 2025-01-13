import logging


class LoggerManager:

    @staticmethod
    def get_logger():
        logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
        logging.getLogger(__name__)
        return logging
