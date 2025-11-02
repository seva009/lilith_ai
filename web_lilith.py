import os
import threading
from flask import Flask, render_template, request, jsonify
from flask_cors import CORS

from lilith_core import (
    BASE_DIR,
    EXISTENCE_KEYWORDS,
    MEMORY_FILE,
    PERSONA_FILE,
    classify_emotion,
    get_user_name,
    load_memory,
    load_persona,
    lilith_reply,
    set_user_name,
)

app = Flask(__name__, static_folder='static')
allowed_origins = os.getenv("CORS_ORIGINS", "*")
CORS(app, resources={
    r"/chat": {"origins": allowed_origins},
    r"/nickname": {"origins": allowed_origins},
})

persona = load_persona()
memory = load_memory()
memory_lock = threading.Lock()

@app.route('/')
def home():
    debug = {
        "cwd": os.getcwd(),
        "base_dir": BASE_DIR,
        "persona_file": PERSONA_FILE,
        "memory_file": MEMORY_FILE,
        "persona_length": len(persona),
        "memory_count": len(memory.get("conversation", [])),
    }
    recent_memory = memory.get("conversation", [])[-20:]
    user_name = get_user_name(memory)
    name_set = memory.get("meta", {}).get("user_name_set", False)
    return render_template(
        'index.html',
        persona=persona,
        memory=recent_memory,
        debug=debug,
        user_name=user_name,
        user_name_set=name_set,
    )

@app.route('/nickname', methods=['GET', 'POST'])
def nickname():
    with memory_lock:
        if request.method == 'GET':
            return jsonify({'user_name': get_user_name(memory)})
        payload = request.json or {}
        new_name = (payload.get('user_name') or '').strip()
        if not new_name:
            return jsonify({'error': 'nickname required'}), 400
        set_user_name(memory, new_name)
        return jsonify({'user_name': new_name})

@app.route('/chat', methods=['POST'])
def chat():
    user_msg = request.json.get('message', '').strip()
    if not user_msg:
        return jsonify({'reply': '', 'emotion': 'idle'}), 400

    with memory_lock:
        reply = lilith_reply(user_msg, persona, memory)

    emotion = classify_emotion(reply)
    # mirror CLI disappointed reaction for existence questions
    if any(k in user_msg.lower() for k in EXISTENCE_KEYWORDS):
        emotion = "dissapointed"

    return jsonify({'reply': reply, 'emotion': emotion})

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=False)
