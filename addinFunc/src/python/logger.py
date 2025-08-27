import logging
import os
import traceback

##CLASE DEL LOGGER
class Logger():

    def __set_logger(self):
        log_directory = 'utils/logs'
        log_filename = 'app.log'
        log_path = os.path.join(log_directory, log_filename)

        logger = logging.getLogger(__name__)
        if not logger.hasHandlers():
            logger.setLevel(logging.DEBUG)

            file_handler = logging.FileHandler(log_path, mode="w", encoding='utf-8')
            file_handler.setLevel(logging.DEBUG)

            formatter = logging.Formatter(
                '%(asctime)s | %(levelname)s | %(message)s', "%Y-%m-%d %H:%M:%S")
            file_handler.setFormatter(formatter)

            if (logger.hasHandlers()):
                logger.handlers.clear()

            logger.addHandler(file_handler)

        return logger

    @classmethod
    def add_to_log(cls, level, message):
        try:
            logger = cls.__set_logger(cls)

            if (level == "critical"):
                logger.critical(message)
            elif (level == "debug"):
                logger.debug(message)
            elif (level == "error"):
                logger.error(message)
            elif (level == "info"):
                logger.info(message)
            elif (level == "llamada"):
                logger.warn(message)
        except Exception as ex:
            print(traceback.format_exc())
            print(ex)