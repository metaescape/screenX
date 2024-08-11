import tkinter as tk


class ScreenRecorderApp:
    def __init__(self):

        # 初始化窗口
        self.init_root()

    def init_root(self):
        self.root = tk.Tk()
        self.recoding = False

        screen_width = self.root.winfo_screenwidth()
        screen_height = self.root.winfo_screenheight()
        self.selection_box = {
            "top": 0,
            "left": 0,
            "width": screen_width,
            "height": screen_height,
        }
        print(f"Screen size: {screen_width}x{screen_height}")
        self.root.attributes("-topmost", True)

        self.root.attributes("-type", "dialog")
        self.root.attributes(
            "-alpha", 0.3
        )  # Set transparency level (0.0 to 1.0)
        self.root.geometry(f"{screen_width}x{screen_height}")
        self.root.title("ScreenX")

        self.canvas = tk.Canvas(self.root, cursor="cross")

        self.canvas.pack(fill=tk.BOTH, expand=True)

        self.canvas.bind("<ButtonPress-1>", self.on_button_press)
        self.canvas.bind("<B1-Motion>", self.on_mouse_drag)
        self.canvas.bind("<ButtonRelease-1>", self.on_button_release)

        self.selection_box = None
        self.buttons = []

    def on_button_press(self, event):
        self.start_x = event.x
        self.start_y = event.y

        if self.selection_box:
            self.canvas.delete(self.selection_box)
        self.selection_box = self.canvas.create_rectangle(
            self.start_x,
            self.start_y,
            self.start_x,
            self.start_y,
            outline="red",
            width=2,
        )

    def on_mouse_drag(self, event):
        self.canvas.coords(
            self.selection_box, self.start_x, self.start_y, event.x, event.y
        )

    def on_button_release(self, event):
        self.end_x = event.x
        self.end_y = event.y

        self.bbox = {
            "top": self.start_y,
            "left": self.start_x,
            "width": self.end_x - self.start_x,
            "height": self.end_y - self.start_y,
        }

        # 调整 root 窗口的大小和位置以匹配选择框
        self.root.geometry(
            f"{abs(self.end_x - self.start_x)}x{abs(self.end_y - self.start_y)}+{min(self.start_x, self.end_x)}+{min(self.start_y, self.end_y)}"
        )
        self.canvas.pack_forget()  # 移除画布，防止遮挡按钮

        self.create_buttons()

    def create_buttons(self):
        button_texts = ["重选", "开始录制", "退出"]
        commands = [self.reset_selection, self.toggle_recording, self.exit_app]

        for i, text in enumerate(button_texts):
            btn = tk.Button(self.root, text=text, command=commands[i])
            btn.pack(side=tk.RIGHT, padx=5, pady=5)
            self.buttons.append(btn)

    def reset_selection(self):
        self.root.destroy()
        self.init_root()

    def toggle_recording(self):
        if not self.recoding:
            self.recoding = True
            self.buttons[1].config(text="结束录制")
            # 在这里开始录制逻辑
        else:
            self.recoding = False
            self.buttons[1].config(text="开始录制")
            # 在这里结束录制逻辑
            self.exit_app()

    def exit_app(self):
        self.root.destroy()

    def run(self):
        self.root.mainloop()


# Example of how to use this selection in your recording
if __name__ == "__main__":

    app = ScreenRecorderApp()
    app.run()

    print(app.bbox)
