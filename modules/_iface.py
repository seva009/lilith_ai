import importlib
import configparser
import logging

logger = logging.getLogger(__name__)

config = configparser.ConfigParser()
config.read('config.ini')

_iface = None
iface_type = config['server']['server_ai']

logger.info(f"Loading AI interface: {iface_type}")

if iface_type == 'ollama':
    try:
        _iface = importlib.import_module('modules._ollama_iface')
    except ImportError:
        raise ImportError("Ollama module not found. Please install the 'ollama' package to use this interface.")
elif iface_type == 'LM studio':
    try:
        _iface = importlib.import_module('modules._openai_iface')
    except ImportError:
        raise ImportError("openai module not found. Please install the 'openai' package to use this interface.")
elif iface_type == 'hf':
    try:
        _iface = importlib.import_module('modules._hf_iface')
    except ImportError:
        raise ImportError("Transformers module not found. Please install the 'transformers' package to use this interface.")
elif iface_type == 'llama':
    try:
        _iface = importlib.import_module('modules._llama_iface')
    except ImportError:
        raise ImportError("llama_cpp module not found. Please install the 'llama-cpp-python' package to use this interface.")
else:
    raise ValueError(f"Unsupported server type specified in config.ini. Supported types are 'ollama' and 'LM studio'. Got '{iface_type}'.")

class AIInterface:
    def __init__(self, *args, **kwargs):
        if _iface is None:
            raise RuntimeError("No AI interface module loaded.")
        if iface_type == 'ollama':
            self.imp = _iface.AIInterface_Ollama(*args, **kwargs)
        elif iface_type == 'LM studio':
            self.imp = _iface.AIInterface_OpenAI(*args, **kwargs)
        elif iface_type == 'hf':
            self.imp = _iface.AIInterface_HF(*args, **kwargs)
            self.imp.load()
        elif iface_type == 'llama':
            self.imp = _iface.AIInterface_Llama(*args, **kwargs)

    def get_response(self, messages):
        return self.imp.get_response(messages)