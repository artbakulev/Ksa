import logging


class MockLogger:
    def info(self, *args):
        pass

    def warning(self, *args):
        pass

    def error(self, *args):
        pass


def make_logger(debug_mode=False):
    if debug_mode:
        logger = logging.getLogger(__name__)
        logger.setLevel(logging.INFO)

        formatter = logging.Formatter('%(asctime)s %(levelname)-5s %(message)s')

        console = logging.StreamHandler()
        console.setLevel(logging.INFO)
        console.setFormatter(formatter)

        logger.addHandler(console)
    else:
        logger = MockLogger()
    return logger
