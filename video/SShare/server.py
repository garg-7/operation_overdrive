import socket
import threading
import zlib
import mss
import tkinter
import pyautogui
from _thread import start_new_thread
from test import screenShareSave

coordinates = {"x1": 0, "y1": 0, "x2": 1920, "y2": 1080}


class ApplicationToSnip():
    def __init__(self, rootApp):
        self.master = rootApp
        self.master.geometry("250x50+0+0")
        self.coordinates = {"Rec": {"x1": None, "y1": None, "x2": None, "y2": None}, "start": {
            "x": None, "y": None}, "end": {"x": None, "y": None}}
        self.rect = None
        self.x = self.y = 0

        self.snippingButton = tkinter.Button(
            self.master, text="click here to select the area", width=25, command=self.createCanvasToSnip)
        self.snippingButton.pack(fill=tkinter.BOTH, expand=tkinter.YES)

        self.snippingScreen = tkinter.Toplevel(self.master)
        self.snippingScreen.withdraw()
        self.snippingScreen.attributes("-transparent", "blue")
        self.snippingFrame = tkinter.Frame(
            self.snippingScreen, background="blue")
        self.snippingFrame.pack(fill=tkinter.BOTH, expand=tkinter.YES)

    def createCanvasToSnip(self):
        self.snippingScreen.deiconify()
        self.master.withdraw()

        self.snippingCanvas = tkinter.Canvas(
            self.snippingFrame, cursor="cross", bg="grey11")
        self.snippingCanvas.pack(fill=tkinter.BOTH, expand=tkinter.YES)

        self.snippingCanvas.bind("<ButtonPress-1>", self.onClick)
        self.snippingCanvas.bind("<B1-Motion>", self.onMove)
        self.snippingCanvas.bind("<ButtonRelease-1>", self.onRelease)

        self.snippingScreen.attributes('-fullscreen', True)
        self.snippingScreen.attributes('-alpha', .3)
        self.snippingScreen.lift()
        self.snippingScreen.attributes("-topmost", True)

    def onRelease(self, event):
        self.coordinates["Rec"] = {"x1": (int)(min(self.coordinates["start"]["x"], self.coordinates["end"]["x"])),
                                   "y1": (int)(min(self.coordinates["start"]["y"], self.coordinates["end"]["y"])),
                                   "x2": (int)(max(self.coordinates["start"]["x"], self.coordinates["end"]["x"])),
                                   "y2": (int)(max(self.coordinates["start"]["y"], self.coordinates["end"]["y"]))}
        global coordinates
        coordinates = self.coordinates
        self.snippingCanvas.destroy()
        self.snippingScreen.withdraw()
        self.master.deiconify()
        self.master.destroy()

    def onClick(self, event):
        self.coordinates["start"]["x"] = self.snippingCanvas.canvasx(event.x)
        self.coordinates["start"]["y"] = self.snippingCanvas.canvasy(event.y)
        self.rect = self.snippingCanvas.create_rectangle(
            self.x, self.y, 1, 1, outline='red', width=3, fill="blue")

    def onMove(self, event):
        self.coordinates["end"]["x"] = self.snippingCanvas.canvasx(event.x)
        self.coordinates["end"]["y"] = self.snippingCanvas.canvasy(event.y)
        self.snippingCanvas.coords(
            self.rect, self.coordinates["start"]["x"], self.coordinates["start"]["y"], self.coordinates["end"]["x"], self.coordinates["end"]["y"])

class manager:
    def __init__(self):
        self.frames = []
        self.kept_frames = []
        self.keep_going = True

class server:
    def __init__(self, coordinates):
        self.connected = 0
        self.coordinates = coordinates
        self.HEIGHT = self.coordinates["y2"]-self.coordinates["y1"]
        self.WIDTH = self.coordinates["x2"]-self.coordinates["x1"]

    def handle_client(self, conn, addr, scr_m):
        print(f'Client connected [{addr}]')
        screenRecord=True
        while screenRecord:
            try:
                img = scr_m.frames.pop(0)
                pixels = zlib.compress(img.rgb, 6)
                size = len(pixels)
                size_len = (size.bit_length() + 7) // 8
                size_bytes = size.to_bytes(size_len, 'big')
                try:
                    conn.send(bytes([size_len]))
                    conn.send(size_bytes)
                    conn.sendall(pixels)
                except:
                    print(f'Client Disconnected [{addr}]')
                    screenRecord = False
                    scr_m.keep_going=False
                    self.connected -= 1
            except IndexError:
                pass

    def record_stream(self, scr_m):
        with mss.mss() as mss_instance:
            rect = {'top': self.coordinates["y1"], 'left': self.coordinates["x1"],
                    'width': self.WIDTH, 'height': self.HEIGHT}
            while scr_m.keep_going:
                img = mss_instance.grab(rect)
                scr_m.frames.append(img)


    def start_server(self):
        HOST = socket.gethostbyname(socket.gethostname())
        PORT = 9999
        scr_m = manager()
        ADDR = (HOST, PORT)
        server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        server.bind(ADDR)
        try:
            server.listen()
            print(f'Server started on {HOST}:{PORT}')

            print(f'WIDTH: {self.WIDTH}')
            print(f'HEIGHT: {self.HEIGHT}')
            connected = True
            while connected:
                conn, addr = server.accept()
                thread1 = threading.Thread(
                    target=self.record_stream, args=(scr_m, ))
                thread1.start()
                thread = threading.Thread(
                    target=self.handle_client, args=(conn, addr, scr_m))
                thread.start()
                self.connected += 1

        finally:
            server.close()


def saveScreen(input):
    screenShareSave()


if __name__ == "__main__":
    start_new_thread(saveScreen, ("screen",))
    # rootApp = tkinter.Tk(screenName=None, baseName=None, className='Setup', useTk=1)
    # app = ApplicationToSnip(rootApp)
    # rootApp.mainloop()
    # print(coordinates["Rec"])
    SERVER = server(coordinates)
    SERVER.start_server()
