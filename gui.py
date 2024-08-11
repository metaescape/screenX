import tkinter as tk


class SelectionBox:
    def __init__(self, root):
        self.root = root
        self.start_x = None
        self.start_y = None
        self.rect = None

        self.canvas = tk.Canvas(root, cursor="cross")
        self.canvas.pack(fill=tk.BOTH, expand=True)

        self.canvas.bind("<ButtonPress-1>", self.on_button_press)
        self.canvas.bind("<B1-Motion>", self.on_mouse_drag)
        self.canvas.bind("<ButtonRelease-1>", self.on_button_release)

        self.selection_box = None

    def on_button_press(self, event):
        # Start the selection
        self.start_x = event.x
        self.start_y = event.y

        if self.rect:
            self.canvas.delete(self.rect)
        self.rect = self.canvas.create_rectangle(
            self.start_x,
            self.start_y,
            self.start_x,
            self.start_y,
            outline="red",
            width=2,
        )

    def on_mouse_drag(self, event):
        # Update the selection rectangle
        self.canvas.coords(
            self.rect, self.start_x, self.start_y, event.x, event.y
        )

    def on_button_release(self, event):
        # Finalize the selection
        self.end_x = event.x
        self.end_y = event.y

        self.selection_box = {
            "top": self.start_y,
            "left": self.start_x,
            "width": self.end_x - self.start_x,
            "height": self.end_y - self.start_y,
        }
        self.root.quit()

    def get_selection(self):
        return self.selection_box


def select_screen_area():
    root = tk.Tk()
    # get screen size
    screen_width = root.winfo_screenwidth()
    screen_height = root.winfo_screenheight()
    print(f"Screen size: {screen_width}x{screen_height}")
    root.attributes("-topmost", True)

    root.attributes("-type", "dialog")
    root.attributes("-alpha", 0.3)  # Set transparency level (0.0 to 1.0)
    root.geometry(f"{screen_width}x{screen_height}")
    root.title("ScreenX")
    app = SelectionBox(root)

    root.mainloop()
    root.destroy()

    return app.get_selection()


# Example of how to use this selection in your recording
if __name__ == "__main__":
    screen_area = select_screen_area()
    if screen_area:
        print(f"Selected area: {screen_area}")
    else:
        print("No area selected")
    while True:
        pass
