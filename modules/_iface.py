import importlib
import configparser

config = configparser.ConfigParser()
config.read('config.ini')

_iface = None
iface_type = config['server']['server_ai']

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

    def get_response(self, prompt):
        return self.imp.get_response(prompt)