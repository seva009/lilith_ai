import curses


class ConversationTUI:
    def __init__(self, manager):
        self.manager = manager
        self.selected = 0

    def draw(self, stdscr, conversations):
        stdscr.clear()
        h, w = stdscr.getmaxyx()

        current = self.manager.get_current_conversation_name()

        stdscr.addstr(1, 2, "Conversation Manager", curses.A_BOLD)
        stdscr.addstr(2, 2, f"Текущий: {current or '-'}", curses.A_DIM)

        for i, name in enumerate(conversations):
            y = 4 + i
            label = f"* {name}" if name == current else f"  {name}"

            if i == self.selected:
                stdscr.attron(curses.A_REVERSE)
                stdscr.addstr(y, 4, label)
                stdscr.attroff(curses.A_REVERSE)
            else:
                stdscr.addstr(y, 4, label)

        stdscr.addstr(
            h - 2,
            2,
            "↑↓ выбор | Enter переключить | c создать | d удалить | q выход",
        )
        stdscr.refresh()

    def input_dialog(self, stdscr, prompt):
        curses.echo()
        stdscr.clear()
        stdscr.addstr(2, 2, prompt, curses.A_BOLD)
        stdscr.addstr(4, 2, "> ")
        stdscr.refresh()
        value = stdscr.getstr(4, 4, 40).decode("utf-8")
        curses.noecho()
        return value.strip()

    def confirm(self, stdscr, text):
        stdscr.clear()
        stdscr.addstr(3, 2, text)
        stdscr.addstr(5, 2, "y — да | n — нет")
        stdscr.refresh()
        return stdscr.getch() == ord("y")

    def run(self, stdscr):
        curses.curs_set(0)

        while True:
            conversations = self.manager.list_conversations()

            if conversations:
                self.selected = max(0, min(self.selected, len(conversations) - 1))
            else:
                self.selected = 0

            self.draw(stdscr, conversations)
            key = stdscr.getch()

            if key == curses.KEY_UP and self.selected > 0:
                self.selected -= 1

            elif key == curses.KEY_DOWN and self.selected < len(conversations) - 1:
                self.selected += 1

            elif key in (curses.KEY_ENTER, 10, 13) and conversations:
                name = conversations[self.selected]
                self.manager.switch_conversation(name)

            elif key == ord("c"):
                name = self.input_dialog(stdscr, "Имя нового разговора:")
                if name:
                    self.manager.create_conversation(name, switch_to=True)

            elif key == ord("d") and conversations:
                name = conversations[self.selected]
                if self.confirm(stdscr, f"Удалить разговор '{name}'?"):
                    self.manager.delete_conversation(name)

            elif key == ord("q"):
                break

def run_conversation_manager(manager):
    curses.wrapper(ConversationTUI(manager).run)