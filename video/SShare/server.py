import socket
import threading
import zlib
import mss
import tkinter
import pyautogui

coordinates = {"x1":None, "y1":None, "x2":None, "y2":None}

class ApplicationToSnip():
    def __init__(self, rootApp):
        self.master = rootApp
        self.master.geometry("250x50+0+0")
        self.coordinates = {"Rec":{"x1":None, "y1":None, "x2":None, "y2":None}, "start":{"x":None, "y": None}, "end":{"x":None, "y":None}}
        self.rect = None
        self.x = self.y = 0

        self.snippingButton = tkinter.Button(self.master, text="click here to select the area", width=25, command=self.createCanvasToSnip)
        self.snippingButton.pack(fill=tkinter.BOTH, expand=tkinter.YES)

        self.snippingScreen = tkinter.Toplevel(self.master)
        self.snippingScreen.withdraw()
        self.snippingScreen.attributes("-transparent","blue")
        self.snippingFrame = tkinter.Frame(self.snippingScreen, background="blue")
        self.snippingFrame.pack(fill=tkinter.BOTH, expand=tkinter.YES)

    def createCanvasToSnip(self):
        self.snippingScreen.deiconify()
        self.master.withdraw()

        self.snippingCanvas = tkinter.Canvas(self.snippingFrame, cursor="cross", bg="grey11")
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
                            "y2" : (int)(max(self.coordinates["start"]["y"], self.coordinates["end"]["y"]))}
        global coordinates
        coordinates = self.coordinates
        self.snippingCanvas.destroy()
        self.snippingScreen.withdraw()
        self.master.deiconify()
        self.master.destroy()

    def onClick(self, event):
        self.coordinates["start"]["x"] = self.snippingCanvas.canvasx(event.x)
        self.coordinates["start"]["y"] = self.snippingCanvas.canvasy(event.y)
        self.rect = self.snippingCanvas.create_rectangle(self.x, self.y, 1, 1, outline='red', width=3, fill="blue")

    def onMove(self, event):
        self.coordinates["end"]["x"] = self.snippingCanvas.canvasx(event.x)
        self.coordinates["end"]["y"] = self.snippingCanvas.canvasy(event.y)
        self.snippingCanvas.coords(self.rect, self.coordinates["start"]["x"], self.coordinates["start"]["y"], self.coordinates["end"]["x"], self.coordinates["end"]["y"])

class server:
    def __init__(self, coordinates):
        self.connected = 0
        self.coordinates = coordinates
        self.HEIGHT = self.coordinates["y2"]-self.coordinates["y1"]
        self.WIDTH = self.coordinates["x2"]-self.coordinates["x1"]
    
    def handle_client(self, conn, addr):
        print(f'Client connected [{addr}]')
        with mss.mss() as mss_instance:
            rect = {'top': self.coordinates["y1"], 'left': self.coordinates["x1"], 'width': self.WIDTH, 'height': self.HEIGHT}

            screenRecord = True
            while screenRecord:

                img = mss_instance.grab(rect)
                
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
                    self.connected -= 1

    def start_server(self):
        HOST = socket.gethostbyname(socket.gethostname())
        PORT = 9999
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
                thread = threading.Thread(target=self.handle_client, args=(conn, addr))
                thread.start()
                self.connected += 1

        finally:
            server.close()

if __name__ == "__main__":
    rootApp = tkinter.Tk(screenName=None, baseName=None, className='Setup', useTk=1)
    app = ApplicationToSnip(rootApp)
    rootApp.mainloop()
    print(coordinates["Rec"])
    SERVER = server(coordinates["Rec"])
    SERVER.start_server()
