# -*- coding: utf-8 -*-
from logging import Logger, getLogger
from logging.config import dictConfig
from yaml import safe_load

def get_logger(conf_file:str, logger_name:str) -> Logger:
    """Responding logger instance

    Args:
        conf_file (str): Logger configuration file path.
        logger_name (str): Logger name.

    Returns:
        Logger: Logger instance.
    """
    
    with open(conf_file, "r") as f:
        dictConfig(safe_load(f.read()))
    return get_logger(logger_name)

if __name__ == "__main__":
    m_logger = get_logger("./logger_conf.yml", "main")
    f_logger = get_logger("./logger_conf.yml", "filer")
    m_logger.info("Main logger log")
    f_logger.info("Filer logger log")