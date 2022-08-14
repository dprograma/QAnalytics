from kivy.app import App
from kivy.lang import Builder
from kivy.uix.popup import Popup
from kivy.properties import BooleanProperty
import threading
from time import sleep


def show_popup(function):
    def wrap(app, *args, **kwargs):
        popup = CustomPopup()  # Instantiate CustomPopup (could add some kwargs if you wish)
        app.done = False  # Reset the app.done BooleanProperty
        app.bind(done=popup.dismiss)  # When app.done is set to True, then popup.dismiss is fired
        popup.open()  # Show popup
        t = threading.Thread(target=function, args=[app, popup, *args], kwargs=kwargs)  # Create thread
        t.start()  # Start thread
        return t

    return wrap


class CustomPopup(Popup):
    pass


kv = Builder.load_string(  # Generic kv stuff
"""
<CustomPopup>:
    size_hint: .8, .4
    auto_dismiss: False
    progress: 0
    text: ''
    title: "Drink Progress"
    
    BoxLayout:
        orientation: 'vertical'
        
        Label:
            text: root.text
            size_hint: 1, 0.8
            
        ProgressBar:
            value: root.progress

FloatLayout:
    Button:
        text: 'Pour me a Drink!'
        on_release: app.mix_drinks()
"""
)


class MyMainApp(App):
    done = BooleanProperty(False)

    def build(self):
        return kv

    @show_popup
    def mix_drinks(self, popup):  # Decorate function to show popup and run the code below in a thread
        popup.text = 'Slicing limes...'
        sleep(1)
        popup.progress = 20
        popup.text = 'Muddling sugar...' # Changing the popup attributes as the function runs!
        sleep(2)
        popup.progress = 50
        popup.text = 'Pouring rum...'
        sleep(2)
        popup.progress = 80
        popup.text = 'Adding ice...'
        sleep(1)
        popup.progress = 100
        popup.text = 'Done!'
        sleep(0.5)
        self.done = True


if __name__ == '__main__':
    MyMainApp().run()