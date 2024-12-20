import abc
import logging
import logfire

#logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
# Configuração Logfire
logfire.configure()
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s', handlers=[logfire.LogfireLoggingHandler()])

class Processor(abc.ABC):
    def __init__(self, api_connection, processor_name) -> None:
        self.api_connection = api_connection
        self.processor_name = processor_name
        self.logger = logging.getLogger(processor_name)

    
    @abc.abstractmethod
    def process(self) -> None:
        """Processing logic comes here"""
        pass