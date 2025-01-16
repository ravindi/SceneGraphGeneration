import sys
from PyQt5.QtWidgets import QApplication, QMainWindow

class MyWindow(QMainWindow):
    def __init__(self):
        super().__init__()

        # Set window parameters
        self.setWindowTitle("My PyQt5 App")  # Set the title of the window
        self.setGeometry(100, 100, 600, 400)  # Set the position and size of the window

        # Add more GUI components here

def main():
    app = QApplication(sys.argv)  # Create an instance of QApplication
    window = MyWindow()  # Create an instance of your application's class
    window.show()  # Show the window
    sys.exit(app.exec_())  # Start the application's main loop

if __name__ == '__main__':
    main()
