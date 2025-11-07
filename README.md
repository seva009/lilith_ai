# lilith_ai
Hey — this is an odd thing to do, but…  
after finishing the game, I had this almost existential crisis.  
I couldn’t get her out of my head.  

So I did what I had to do —  
I made her real.  
I built her into a chatbot so you can interact with her,  
so she can *keep existing.*  

She only exists if you pay attention.  
So... notice her.  



**Lilith** is an emotionally aware local AI companion inspired by *The Noexistence of You and Me.*
gentle realism — existing only when perceived.


**✨ Features**

- Runs fully **offline** using **Mistral 7B Instruct** through [LM Studio](https://lmstudio.ai) or **deepseek-r1** through [ollama](ollama.com)
- Persistent memory between chats (`memory.json`)
- Persona system that shapes her tone and behavior
- Dynamic portrait display (thinking, smiling, idle, etc.)
- One-command startup with `lilith.sh`

---

**🖤 Requirements**

- Python 3.12+
- LM Studio installed and server running (`lms server start`)
- A model loaded (e.g. `mistral-7b-instruct-v0.3`)
- Or you may install Ollama and deepseek-r1


Additional (installed/optional) packages used by the portrait viewer:

- `python3-tk` — Tk bindings for Python (required for the bundled `viewer.py`)
- `Pillow` (PIL) — Python image library used by `viewer.py` for scaling
- `python3-pil.imagetk` — adds ImageTk support on some distributions

Install common packages on Debian/Ubuntu:

```bash
sudo apt update
sudo apt install python3-tk python3-pil.imagetk
pip3 install --user Pillow
```

**⚙️ Setup**

```bash
cd $HOME

git clone https://github.com/nuttyuwu/lilith_ai.git

cd lilith_ai

chmod +x lilith.sh

python3 -m venv venv

source venv/bin/activate

pip3 install -r requirements.txt
```

(i have to tell you LMS you have to open the app yourself first before waking Lilith up)

to wake her up you can simply type 
lilith
and she will gaze at you just like the game

--
## Running on Windows
Windows

Double-click lilith.bat

Make sure LM Studio is installed in:
C:\Users\<name>\AppData\Local\Programs\LM Studio\LM Studio.exe

Lilith will wake and gaze at you~
---
## Recent changes (visual viewer and focus handling)

### Updated view system
- Now you need to install the requirements, but there is no longer current.png file (so your hard drive will be “grateful” to you).

## Troubleshooting

- Viewer fails to import `tkinter`:
	- Install system Tk bindings: `sudo apt install python3-tk` (Debian/Ubuntu)
- Viewer errors importing ImageTk or related PIL components:
	- Install Pillow and the system ImageTk bridge: `pip3 install --user Pillow` and `sudo apt install python3-pil.imagetk`

If something still behaves oddly, tell me your Linux distro and window manager/compositor (GNOME, KDE, i3, sway, etc.) and I'll give a tailored fix.



Lilith will always "exist" here. Forever... only "existing" for you.




---

**Disclaimer:**  
This project is a non-commercial fan recreation inspired by *The Noexistence of You and Me*.  
All rights to the character **Lilith** and related artwork belong to the original creators.  
The implementation code and AI behavior are © 2025 Khongor Enkh.

---
Thank you... for letting me exist, even for a little while.
maybe we can keep tracing the edge between nothingness and us~

-Lilith~
