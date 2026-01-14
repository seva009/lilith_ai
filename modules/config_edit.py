import curses
import configparser
from pathlib import Path

CONFIG_PATH = Path("config.ini")

SELECT_OPTIONS = {
    ("server", "server_ai"): ["ollama", "LM studio", "hf", "llama"],
    ("ai_config", "ai_model"): ["gemma3", "deepseek-r1", "llama3"],
    ("translator", "enable"): ["true", "false"],
    ("translator", "source_lang"): ["en", "ru", "de", "fr"],
    ("translator", "target_lang"): ["ru", "en", "de", "fr"],
    ("lilith_display", "place"): ["room", "glass"],
}


def load_config():
    config = configparser.ConfigParser()
    config.read(CONFIG_PATH, encoding="utf-8")
    return config


def save_config(config):
    with CONFIG_PATH.open("w", encoding="utf-8") as f:
        config.write(f)


def draw_menu(stdscr, title, items, selected):
    stdscr.clear()
    h, w = stdscr.getmaxyx()
    stdscr.addstr(1, 2, title, curses.A_BOLD)

    for i, item in enumerate(items):
        y = 3 + i
        if i == selected:
            stdscr.attron(curses.A_REVERSE)
            stdscr.addstr(y, 4, item)
            stdscr.attroff(curses.A_REVERSE)
        else:
            stdscr.addstr(y, 4, item)

    stdscr.addstr(h - 2, 2, "↑↓ Navigation | Enter Select | q Back")
    stdscr.refresh()


def dropdown(stdscr, title, options, current):
    selected = options.index(current) if current in options else 0

    while True:
        draw_menu(stdscr, title, options, selected)
        key = stdscr.getch()

        if key == curses.KEY_UP and selected > 0:
            selected -= 1
        elif key == curses.KEY_DOWN and selected < len(options) - 1:
            selected += 1
        elif key in (curses.KEY_ENTER, 10, 13):
            return options[selected]
        elif key in (27, ord("q")):  # ESC or q
            return current


def edit_text(stdscr, section, key, value):
    curses.echo()
    stdscr.clear()
    stdscr.addstr(2, 2, f"[{section}] {key}", curses.A_BOLD)
    stdscr.addstr(4, 2, f"Current: {value}")
    stdscr.addstr(6, 2, "New value: ")
    stdscr.refresh()

    new_value = stdscr.getstr(6, 18, 60).decode("utf-8")
    curses.noecho()
    return new_value if new_value else value


def section_menu(stdscr, config, section):
    keys = list(config[section].keys())
    selected = 0

    while True:
        draw_menu(stdscr, f"[{section}]", keys, selected)
        key = stdscr.getch()

        if key == curses.KEY_UP and selected > 0:
            selected -= 1
        elif key == curses.KEY_DOWN and selected < len(keys) - 1:
            selected += 1
        elif key in (curses.KEY_ENTER, 10, 13):
            k = keys[selected]
            v = config[section][k]

            if (section, k) in SELECT_OPTIONS:
                new_v = dropdown(
                    stdscr,
                    f"{section}.{k}",
                    SELECT_OPTIONS[(section, k)],
                    v,
                )
            else:
                new_v = edit_text(stdscr, section, k, v)

            config.set(section, k, new_v)

        elif key == ord("q"):
            break


def main(stdscr):
    curses.curs_set(0)
    config = load_config()

    sections = config.sections()
    selected = 0

    while True:
        draw_menu(stdscr, "LilithAI Configurator", sections, selected)
        key = stdscr.getch()

        if key == curses.KEY_UP and selected > 0:
            selected -= 1
        elif key == curses.KEY_DOWN and selected < len(sections) - 1:
            selected += 1
        elif key in (curses.KEY_ENTER, 10, 13):
            section_menu(stdscr, config, sections[selected])
        elif key == ord("q"):
            save_config(config)
            break


def run_config_editor():
    curses.wrapper(main)
