import os
import threading
from flask import Flask, render_template, request, jsonify
from flask_cors import CORS

from lilith import (
    BASE_DIR,
    EXISTENCE_KEYWORDS,
    Lilith_AI,
)

app = Flask(__name__, static_folder='static')
allowed_origins = os.getenv("CORS_ORIGINS", "*")
CORS(app, resources={
    r"/chat": {"origins": allowed_origins},
    r"/nickname": {"origins": allowed_origins},
})

persona = Lilith_AI.persona
memory = Lilith_AI.memory
memory_lock = threading.Lock()

@app.route('/')
def home():
    debug = {
        "cwd": os.getcwd(),
        "base_dir": BASE_DIR,
        "persona_length": len(persona),
        "memory_count": len(memory.get("conversation", [])),
    }
    recent_memory = memory.get("conversation", [])[-20:]
    user_name = Lilith_AI.get_user_name()
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
            return jsonify({'user_name': Lilith_AI.get_user_name()})
        payload = request.json or {}
        new_name = (payload.get('user_name') or '').strip()
        if not new_name:
            return jsonify({'error': 'nickname required'}), 400
        Lilith_AI.set_user_name(new_name)
        return jsonify({'user_name': new_name})

@app.route('/chat', methods=['POST'])
def chat():
    user_msg = request.json.get('message', '').strip()
    if not user_msg:
        return jsonify({'reply': '', 'emotion': 'idle'}), 400

    with memory_lock:
        reply = Lilith_AI.lilith_reply(user_msg)

    emotion = Lilith_AI.get_current_emotion()
    # mirror CLI disappointed reaction for existence questions
    if any(k in user_msg.lower() for k in EXISTENCE_KEYWORDS):
        emotion = "dissapointed"

    return jsonify({'reply': reply, 'emotion': emotion})

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=False)
