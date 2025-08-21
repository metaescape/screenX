import tkinter as tk
import time
import subprocess, threading
import sys

TITLE = "ScreenX"


def notify_send(message, seconds=10):
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

    def update_geometry(self, x, y, width, height):
        self.geometry(f"{width}x{height}+{x}+{y}")


class ScreenRecorderApp:
    def __init__(self):

        # 初始化窗口
        self.init_root()
        self.recording_hook = lambda: print("Recording...")
        self.end_hook = lambda: print("Recording stopped.")
        self.stop_event = None
        self.pause_event = None
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

        # print(f"Screen size: {screen_width}x{screen_height}")
        self.root.attributes("-topmost", True)
        self.root.attributes("-type", "dialog")
        self.root.title(TITLE)

        self.buttons = {}
        self.border_thickness = 2
        self.borders = []
        self.reset_root()

    def reset_root(self):
        self.state = "to_select"
        self.recording_seconds = 0
        screen_width = self.root.winfo_screenwidth()
        screen_height = self.root.winfo_screenheight()
        self.root.geometry(f"{screen_width}x{screen_height}+0+0")

        # Set transparency level (0.0 to 1.0)
        self.root.attributes("-alpha", 0.2)
        self.root.configure(bg="white")

        self.canvas = tk.Canvas(self.root, cursor="cross")
        self.canvas.pack(fill=tk.BOTH, expand=True)

        self.canvas.bind("<ButtonPress-1>", self.on_button_press)
        self.canvas.bind("<B1-Motion>", self.on_mouse_drag)
        self.canvas.bind("<ButtonRelease-1>", self.on_button_release)

        # initialize the selection box, the coordinates will be updated on mouse drag
        # so it initial coordinates are not important
        self.selection_box = self.canvas.create_rectangle(
            0,
            0,
            0,
            0,
            outline="black",
            width=2,
        )

    def update_bbox(self):
        self.bbox = {
            "top": self.root.winfo_y(),
            "left": self.root.winfo_x(),
            "width": self.root.winfo_width(),
            "height": self.root.winfo_height(),
        }

    def on_button_press(self, event):
        if self.state == "to_select":
            self.start_x = event.x
            self.start_y = event.y

    def on_mouse_drag(self, event):
        if self.state == "to_select":
            # update the coordinates of the selection box
            self.canvas.coords(
                self.selection_box,
                self.start_x,
                self.start_y,
                event.x,
                event.y,
            )

    def on_button_release(self, event):
        if self.state == "to_select":
            self.end_x = event.x
            self.end_y = event.y

            left_top_x = (
                min(self.start_x, self.end_x) + self.root.winfo_rootx()
            )

            left_top_y = (
                min(self.start_y, self.end_y) + self.root.winfo_rooty()
            )
            right_bottom_x = (
                max(self.start_x, self.end_x) + self.root.winfo_rootx()
            )
            right_bottom_y = (
                max(self.start_y, self.end_y) + self.root.winfo_rooty()
            )

            self.bbox["top"] = left_top_y
            self.bbox["left"] = left_top_x
            self.bbox["width"] = right_bottom_x - left_top_x
            self.bbox["height"] = right_bottom_y - left_top_y

            self.transparent_window_with_borders(
                left_top_x,
                left_top_y,
                self.bbox["width"],
                self.bbox["height"],
            )
            self.create_button_window(left_top_x, left_top_y)

    def transparent_window_with_borders(self, x, y, width, height):
        self.state = "to_record"
        self.root.attributes("-alpha", 0)

        b1 = BorderLine(
            self.root,
            x,
            y - self.border_thickness,
            width,
            self.border_thickness,
        )

        b2 = BorderLine(
            self.root,
            x - self.border_thickness,
            y,
            self.border_thickness,
            height,
        )

        b3 = BorderLine(
            self.root,
            x,
            y + height,
            width,
            self.border_thickness,
        )
        b4 = BorderLine(
            self.root,
            x + width,
            y,
            self.border_thickness,
            height,
        )
        self.borders = [b1, b2, b3, b4]

    def validate_input(self, value):
        if value.isdigit() or value == "":
            return True
        else:
            return False

    def create_button_window(self, x, y):
        self.button_window = tk.Toplevel(self.root)
        self.button_window.overrideredirect(True)  # 去掉窗口边框
        self.button_window.attributes("-alpha", 0.8)  # 确保按钮窗口不透明

        self.input_area = tk.Entry(
            self.button_window, width=5, font=("Helvetica", 14)
        )
        self.input_area.pack(side=tk.LEFT)
        vcmd = (self.root.register(self.validate_input), "%P")
        self.input_area.config(validate="key", validatecommand=vcmd)

        video_button = tk.Button(
            self.button_window,
            text="video",
            command=lambda: self.toggle_recording("video"),
        )
        video_button.pack(side=tk.LEFT)

        gif_button = tk.Button(
            self.button_window,
            text="gif",
            command=lambda: self.toggle_recording("gif"),
        )
        gif_button.pack(side=tk.LEFT)

        pause_button = tk.Button(
            self.button_window,
            text="pause",
            command=self.toggle_pause,
        )
        pause_button.pack(side=tk.LEFT)

        image_button = tk.Button(
            self.button_window,
            text="img",
            command=self.capture_image,
        )
        image_button.pack(side=tk.LEFT)

        reset_button = tk.Button(
            self.button_window, text="resel", command=self.reset_selection
        )
        reset_button.pack(side=tk.LEFT)

        exit_button = tk.Button(
            self.button_window, text="X", command=self.exit_program
        )
        exit_button.pack(side=tk.LEFT)
        self.buttons = {
            "video": video_button,
            "image": image_button,
            "gif": gif_button,
            "pause": pause_button,
            "reset": reset_button,
            "exit": exit_button,
        }

        # Update the button window size and position
        self.button_window.update_idletasks()
        # get height of self.button_window
        height = self.button_window.winfo_height()
        width = self.button_window.winfo_width()
        # 将按钮窗口放置在选择框的上方
        self.button_window.geometry(f"+{x-2}+{y-height-2}")
        self.root.geometry(f"{width+20}x{height}+{x-20}+{y-height-2}")

    def reset_selection(self):
        if self.state in [
            "recording_video",
            "recording_gif",
            "pause_video",
            "pause_gif ",
        ]:
            self.state = "to_record"
            self.exit_recording()
            notify_send(f"exit recording")
            return
        # distroy the button window
        if hasattr(self, "button_window"):
            self.button_window.destroy()
        # distroy the borders
        for border in self.borders:
            border.destroy()

        # distroy canvas
        self.canvas.destroy()

        self.reset_root()

    def toggle_recording(self, media="video"):
        if self.state == "to_record":
            self.state = f"recording_{media}"
            if media == "video":
                self.stop_event, self.pause_event, *self.threads = (
                    self.start_video_hook()
                )
                self.update_video_button_text()
            else:
                self.stop_event, self.pause_event, *self.threads = (
                    self.start_gif_hook()
                )
                self.update_gif_button_text()
        elif (
            self.state == f"recording_{media}"
            or self.state == f"pause_{media}"
        ):
            self.state = "to_record"
            self.stop_recording()
            if media == "video":
                self.stop_video_hook()
            elif media == "gif":
                self.stop_gif_hook()
            self.buttons[media].config(text=media)
        else:
            notify_send(
                f"Invalid state: {self.state}. Cannot toggle recording"
            )

    def toggle_pause(self):
        if self.state.startswith("recording_"):
            media = self.state.split("_")[1]
            self.state = f"pause_{media}"
            self.pause_event.clear()
            self.buttons["pause"].config(text="resume")
        elif self.state.startswith("pause_"):
            media = self.state.split("_")[1]
            self.state = f"recording_{media}"
            self.pause_event.set()
            self.buttons["pause"].config(text="pause")
        else:
            notify_send(f"Cannot pause/resume in state: {self.state}")

    def capture_image(self):
        self.capture_image_hook()

    def update_video_button_text(self):
        if self.state == "recording_video":
            self.buttons["video"].config(text=f"{self.recording_seconds}")
            self.timer_id = self.root.after(
                1000, self.update_video_button_text
            )
            # 获取用户输入的秒数
            input_value = self.input_area.get()

            if input_value.isdigit():
                limit = int(input_value)
                if self.recording_seconds > limit and limit != 0:
                    self.toggle_recording("video")
                    notify_send(f"Video recording stopped after {limit}s")
            self.recording_seconds += 1
        elif self.state == "pause_video":
            self.timer_id = self.root.after(
                1000, self.update_video_button_text
            )
        else:
            if hasattr(self, "timer_id"):
                self.root.after_cancel(self.timer_id)
            self.buttons["video"].config(text="video")
            self.recording_seconds = 0

    def update_gif_button_text(self):
        if self.state == "recording_gif":
            self.buttons["gif"].config(text=f"{self.recording_seconds}")
            self.timer_id = self.root.after(1000, self.update_gif_button_text)

            # 获取用户输入的秒数
            input_value = self.input_area.get()

            if input_value.isdigit():
                limit = int(input_value)
                if self.recording_seconds > limit and limit != 0:
                    self.toggle_recording("gif")
                    notify_send(f"GIF recording stopped after {limit}s")
            self.recording_seconds += 1
        elif self.state == "pause_gif":
            self.timer_id = self.root.after(1000, self.update_gif_button_text)
        else:
            if hasattr(self, "timer_id"):
                self.root.after_cancel(self.timer_id)
            self.buttons["gif"].config(text="gif")
            self.recording_seconds = 0

    def register_capture_image_hook(self, hook):
        self.capture_image_hook = hook

    def register_video_hooks(self, start_hook, end_hook):
        self.start_video_hook = start_hook
        self.stop_video_hook = end_hook

    def register_gif_hooks(self, start_hook, end_hook):
        self.start_gif_hook = start_hook
        self.stop_gif_hook = end_hook

    def exit_recording(self):
        for thread in self.threads:
            thread.exit()

    def stop_recording(self):
        self.stop_event.set()
        for thread in self.threads:
            thread.join()

    def exit_app(self):
        self.root.destroy()

    def run(self):
        self.root.mainloop()

    def exit_program(self, event=None):
        if self.stop_event:
            self.stop_event.set()
        for thread in self.threads:
            if thread.is_alive():
                thread.join()
        self.root.destroy()
        sys.exit(0)


# Example of how to use this selection in your recording
if __name__ == "__main__":

    app = ScreenRecorderApp()
    app.run()

    print(app.bbox)
