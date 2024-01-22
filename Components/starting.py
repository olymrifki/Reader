import tkinter as tk

from separator import Separator


class StartingGui(tk.Frame):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        # self.configure(background="blue")

        self.components = []

    def add_component(self, new_component):
        self.components.append(new_component)
        self.place_components()

    def place_components(self):
        for i, component in enumerate(self.components):
            component.grid(row=i, column=0, sticky="nwe")
        for col in range(self.grid_size()[0]):
            self.grid_columnconfigure(col, weight=1)


if __name__ == "__main__":
    from const import *

    root = tk.Tk()
    root.title("App Window")
    x_offset = 23
    target_width = int(SCREEN_WIDTH * 0.3) + x_offset
    target_height = int(SCREEN_HEIGHT * 0.7)
    root.geometry(f"{target_width}x{target_height}")

    nv = StartingGui(root)
    nv.grid(row=0, column=0, padx=10, pady=10, sticky="nsew")
    nv.add_component(Separator(nv))
    nv.add_component(Separator(nv))

    root.grid_rowconfigure(0, weight=1)
    root.grid_columnconfigure(0, weight=1)

    # def resize_frame(event):
    #     nv.grid_propagate(0)

    # root.bind("<Configure>", resize_frame)

    root.mainloop()
