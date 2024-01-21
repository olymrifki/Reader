import tkinter as tk


class PlaceholderEntry(tk.Entry):
    def __init__(self, *args, placeholder_text, **kwargs):
        super().__init__(*args, **kwargs)
        self.placeholder_text = placeholder_text
        self.config(fg="gray")
        self.insert(0, placeholder_text)
        self.bind("<FocusIn>", self.on_entry_click)
        self.bind("<FocusOut>", self.on_focus_out)

    def on_entry_click(self, event):
        if self.get() == self.placeholder_text:
            self.delete(0, tk.END)
            self.config(fg="black")

    def on_focus_out(self, event):
        if self.get() == "" or self.cget("fg") == "gray":
            self.delete(0, tk.END)
            self.insert(0, self.placeholder_text)
            self.config(fg="gray")

    def clear_entry(self):
        self.delete(0, tk.END)
        self.on_focus_out("_")


def remove_focus():
    # Set the focus to the root window to remove focus from the Entry widget
    root.focus_set()


if __name__ == "__main__":
    root = tk.Tk()

    button = tk.Button(root, text="Remove Focus", command=remove_focus)
    button.pack()

    placeholder_text = "Enter your text here"

    entry = PlaceholderEntry(root, placeholder_text="enter text")

    entry.pack()

    root.mainloop()
