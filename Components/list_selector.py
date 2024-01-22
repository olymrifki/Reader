import tkinter as tk


class ListSelector(tk.Frame):
    def __init__(self, current_choice, choices, command, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.current_choice = current_choice
        self.choices = choices
        self.command = command
        self.option_menu = tk.OptionMenu(
            self,
            current_choice,
            *choices,
            command=command,
        )
        self.option_menu.pack()

    def get_current_choice(self):
        return self.current_choice.get().split(" at page ")[0]

    # def set_current_choice(self, new_value):
    #     return

    def update_choices(self, new_choices):
        menu = self.option_menu["menu"]
        menu.delete(0, "end")
        for choice in new_choices:

            def func(value=choice):
                self.current_choice.set(value)
                self.command()

            menu.add_command(label=choice, command=func)
