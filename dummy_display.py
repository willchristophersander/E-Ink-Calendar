# dummy_display.py
from PIL import Image

class DummyEPD:
    def init(self):
        print("Dummy EPD initialized.")

    def Clear(self):
        print("Dummy EPD cleared.")

    def display(self, buffer):
        # Convert the buffer back to an image and display or save it
        image = Image.frombytes('1', (800, 480), buffer)
        image.show()  # Opens the image using your system's default viewer
        print("Dummy EPD display called.")

    def getbuffer(self, image):
        return image.tobytes()

    def sleep(self):
        print("Dummy EPD put to sleep.")