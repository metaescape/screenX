import tkinter as tk

TITLE = "ScreenX"

import subprocess


def notify_send(message, seconds=5):
    # 使用 notify-send 发送通知
    command = ["notify-send", message, "-t", str(seconds * 1000)]
    subprocess.run(command, stdout=subprocess.PIPE, stderr=subprocess.PIPE)


class BorderLine(tk.Toplevel):
    def __init__(self, root, x, y, width, height):
        super().__init__(root)
        self.geometry(f"{width}x{height}+{x}+{y}")
        self.overrideredirect(True)
        self.attributes("-topmost", True)
        self.config(bg="#bf616a")


class ScreenRecorderApp:
    def __init__(self):

        # 初始化窗口
        self.init_root()
        self.recording_hook = lambda: print("Recording...")
        self.end_hook = lambda: print("Recording stopped.")
        self.stop_event = None
        self.threads = []
        self.bbox = {
            "top": 0,
            "left": 0,
            "width": 128,
            "height": 128,
        }

    def init_root(self):
        self.root = tk.Tk()
        self.root.bind("<Escape>", self.exit_program)
        self.recording = False

        screen_width = self.root.winfo_screenwidth()
        screen_height = self.root.winfo_screenheight()

        print(f"Screen size: {screen_width}x{screen_height}")
        self.root.attributes("-topmost", True)

        self.root.attributes("-type", "dialog")
        self.root.attributes(
            "-alpha", 0.25
        )  # Set transparency level (0.0 to 1.0)
        self.root.geometry(f"{screen_width}x{screen_height}")
        self.root.title(TITLE)
        self.root.configure(bg="white")
        self.border_thickness = 2

        self.canvas = tk.Canvas(self.root, cursor="cross")

        self.canvas.pack(fill=tk.BOTH, expand=True)

        self.canvas.bind("<ButtonPress-1>", self.on_button_press)
        self.canvas.bind("<B1-Motion>", self.on_mouse_drag)
        self.canvas.bind("<ButtonRelease-1>", self.on_button_release)
        self.selection_box = None
        self.buttons = {}
        self.borders = []

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
            outline="black",
            width=2,
        )

    def on_mouse_drag(self, event):
        self.canvas.coords(
            self.selection_box, self.start_x, self.start_y, event.x, event.y
        )

    def on_button_release(self, event):
        self.end_x = event.x
        self.end_y = event.y

        self.start_x = min(self.start_x, self.end_x)
        self.start_y = min(self.start_y, self.end_y)
        self.end_x = max(self.start_x, self.end_x)
        self.end_y = max(self.start_y, self.end_y)

        self.bbox["top"] = self.start_y
        self.bbox["left"] = self.start_x
        self.bbox["width"] = self.end_x - self.start_x
        self.bbox["height"] = self.end_y - self.start_y

        # 调整 root 窗口的大小和位置以匹配选择框
        width = self.end_x - self.start_x + 4
        height = self.end_y - self.start_y + 4
        x = self.start_x - 2
        y = self.start_y - 2

        self.transparent_window_with_borders(x, y, width, height)

        self.create_button_window()

    def transparent_window_with_borders(self, x, y, width, height):
        self.root.geometry(f"{width}x{height}+{x}+{y}")
        self.root.attributes("-alpha", 0)

        top_border = BorderLine(self.root, x, y, width, self.border_thickness)

        left_border = BorderLine(
            self.root, x, y, self.border_thickness, height
        )

        bottom_border = BorderLine(
            self.root,
            x,
            y + height - self.border_thickness,
            width,
            self.border_thickness,
        )
        right_border = BorderLine(
            self.root,
            x + width - self.border_thickness,
            y,
            self.border_thickness,
            height,
        )
        self.borders = [top_border, left_border, bottom_border, right_border]

    def create_button_window(self):
        self.button_window = tk.Toplevel(self.root)
        self.button_window.overrideredirect(True)  # 去掉窗口边框
        self.button_window.geometry(
            f"+{self.end_x}+{self.start_y}"
        )  # 将按钮窗口放置在选择框的右侧
        self.button_window.attributes("-alpha", 1.0)  # 确保按钮窗口不透明

        video_button = tk.Button(
            self.button_window,
            text="video",
            command=self.toggle_video_recording,
        )
        video_button.pack(side=tk.TOP, padx=5, pady=5)

        gif_button = tk.Button(
            self.button_window,
            text="gif",
            command=self.toggle_gif_recording,
        )
        gif_button.pack(side=tk.TOP, padx=5, pady=5)

        image_button = tk.Button(
            self.button_window,
            text="image",
            command=self.capture_image,
        )
        image_button.pack(side=tk.TOP, padx=5, pady=5)

        reset_button = tk.Button(
            self.button_window, text="resel", command=self.reset_selection
        )
        reset_button.pack(side=tk.TOP, padx=5, pady=5)

        exit_button = tk.Button(
            self.button_window, text="exit", command=self.exit_program
        )
        exit_button.pack(side=tk.TOP, padx=5, pady=5)
        self.buttons = {
            "video": video_button,
            "image": image_button,
            "gif": gif_button,
            "reset": reset_button,
            "exit": exit_button,
        }

    def reset_selection(self):
        self.root.destroy()
        self.init_root()

    def toggle_video_recording(self):
        if not self.recording:
            self.recording = True
            self.stop_event, *self.threads = self.start_video_hook()
            self.buttons["video"].config(text="stop")
        else:
            self.recording = False
            self.buttons["video"].config(text="video")
            self.stop_recording()
            self.stop_video_hook()

    def toggle_gif_recording(self):
        if not self.recording:
            self.recording = True
            self.stop_event, *self.threads = self.start_gif_hook()
            self.buttons["gif"].config(text="stop")
        else:
            self.recording = False
            self.buttons["gif"].config(text="gif")
            self.stop_recording()
            self.stop_gif_hook()

    def capture_image(self):
        self.capture_image_hook()

    def register_capture_image_hook(self, hook):
        self.capture_image_hook = hook

    def register_video_hooks(self, start_hook, end_hook):
        self.start_video_hook = start_hook
        self.stop_video_hook = end_hook

    def register_gif_hooks(self, start_hook, end_hook):
        self.start_gif_hook = start_hook
        self.stop_gif_hook = end_hook

    def stop_recording(self):
        self.stop_event.set()
        for thread in self.threads:
            thread.join()

    def exit_app(self):
        self.root.destroy()

    def run(self):
        self.root.mainloop()

    def exit_program(self, event=None):
        self.root.destroy()
        exit(0)


# Example of how to use this selection in your recording
if __name__ == "__main__":

    app = ScreenRecorderApp()
    app.run()

    print(app.bbox)
