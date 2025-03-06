import time
import logging

from ansi_colors import * 

class LogCenter(logging.Logger):
    def __init__(self, name, level=logging.NOTSET):
        super().__init__(name, level)
        console_handler = logging.StreamHandler()
        text = " %(levelname)s ~ [Time]: %(asctime)s \
                ~ [Function Name]: %(funcName)s \t [Filename]: %(filename)s \
                ~ [Created]: %(relativeCreated)s \
                ~ [ProcessID]: %(process)s \
                ~ [Message]: %(message)s"
        formatter = ColorFormatter(text.replace("~", "\n"))
        console_handler.setFormatter(formatter)
        self.addHandler(console_handler)
   

    def time_event(self, func):
        def wrapper(*args, **kwargs):
            func.__name__ = BRIGHT_YELLOW + func.__name__ + END_COLOR
            self.info("Starting ~{}~> function".format(func.__name__))
            start_time = time.time()
            result = func(*args, **kwargs)
            self.info("Function ~{}~> finished.".format(func.__name__))
            self.info("Execution took: ~{%.6f}~> seconds.", time.time() - start_time)
            return result
        return wrapper


class ColorFormatter(logging.Formatter):
    LEVEL_COLORS = {
        "DEBUG": BRIGHT_GREEN ,
        "INFO": BRIGHT_BLUE,
        "WARNING": BRIGHT_YELLOW,
        "ERROR": RED,
        "CRITICAL": BLINK + BRIGHT_RED,
    }

    RECORD_COLORS = {
        "name": BRIGHT_BLUE,
        'exc_info': BRIGHT_GREEN,
        'exc_text': GREEN,
        'filename': GREEN,
        'funcName': GREEN,
        'module': GREEN,
        'msg': BRIGHT_YELLOW,
        'pathname': GREEN,
        'process': GREEN,
        'stack_info': GREEN,
        'relativeCreated': GREEN,
    }


    def format(self, record):
        levelname = record.levelname
        color = self.LEVEL_COLORS.get(levelname, "")
        record.levelname = f"{color}{levelname}{END_COLOR}"
        for attribute, colors in self.RECORD_COLORS.items():
            gets = getattr(record, attribute)
            setattr(record, attribute, f"{colors}{gets}{END_COLOR}")
        return super().format(record)
