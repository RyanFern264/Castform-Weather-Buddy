import requests
import tkinter as tk
from PIL import Image, ImageTk
from itertools import count
from random import choice
import time

from urllib3.exceptions import MaxRetryError

api_key = ""
my_city = "miami"
OWM_endpoint = "https://api.openweathermap.org/data/2.5/forecast"
castform_base = "castform-base.gif"
castform_rainy = "castform-rainy.gif"
castform_snowy = "castform-snowy.gif"
castform_sunny = "castform-sunny.gif"
hour_mili = 10800000


lat = 25.684850

lon = -80.366312

weather_params = {
    "lat": lat,
    "lon": lon,
    "appid": api_key,
    "cnt":4
}

class ImageLabel(tk.Label):
    """a label that displays images, and plays them if they are gifs"""
    def load(self, im):
        if isinstance(im, str):
            im = Image.open(im)
        self.loc = 0
        self.frames = []

        try:
            for i in count(1):
                frame = im.copy()
                frame = frame.resize((640, 480), Image.Resampling.LANCZOS)  # Resize frame
                self.frames.append(ImageTk.PhotoImage(frame))
                im.seek(i)
        except EOFError:
            pass

        try:
            self.delay = im.info['duration']
        except:
            self.delay = 100

        if len(self.frames) == 1:
            self.config(image=self.frames[0])
        else:
            self.next_frame()

    def unload(self):
        self.config(image="")
        self.frames = None

    def next_frame(self):
        if self.frames:
            self.loc += 1
            self.loc %= len(self.frames)
            self.config(image=self.frames[self.loc])
            self.after(self.delay, self.next_frame)
    #  checks weather and will determine which Castform form to display accordingly
    def weather_check(self):
        try:
            weather_api_call = requests.get(OWM_endpoint, params=weather_params)
            weather_api_call.raise_for_status()
            weather_data = weather_api_call.json()
            if weather_api_call.status_code == 200: #  checking if api call was successful.
                weather_data_code = int(weather_data["list"][0]["weather"][0]["id"]) #  long aah call to get the weather code for most recent hour
                print(weather_data_code)
                if weather_data_code  < 299: #  2xx weather codes are thundering
                    self.unload()
                    self.load('castform-snowy.gif') #  it doesn't snow where I live and I want to see the snowy one
                    window.after(hour_mili, self.weather_check)
                elif weather_data_code < 399: #  3xx weather codes are drizzling
                    self.unload()
                    self.load('castform-rainy.gif')
                    window.after(hour_mili, lbl.weather_check)
                elif weather_data_code < 599: #  5xx weather codes are rain
                    self.unload()
                    self.load('castform-rainy.gif')
                    window.after(hour_mili, self.weather_check)
                elif weather_data_code < 699: #  6xx weather codes are snow
                    self.unload()
                    self.load('castform-snowy.gif')
                    window.after(hour_mili, lbl.weather_check)
                elif weather_data_code < 799:  # 7xx weather codes are atmosphere (ie fog, dust, smoke, tornado [lol], sand etc.)
                    self.unload()
                    self.load('castform-snowy.gif') #  it doesn't snow where I live and I want to see the snowy one
                    window.after(hour_mili, self.weather_check)
                elif weather_data_code == 800:  #  800 specifically is Clear
                    self.unload()
                    self.load('castform-sunny.gif')
                    window.after(hour_mili, lbl.weather_check)
                elif weather_data_code < 899: #  every other 8xx are cloudy
                    self.unload()
                    self.load('castform-base.gif')
                    window.after(hour_mili, lbl.weather_check)
            else:
                self.unload()
                self.load('castform-shiny.gif') #  display the shiny base form if api call failed (for reasons other than no internet, which the outer try/except will catch
                window.after(hour_mili, lbl.weather_check)
        except requests.exceptions.ConnectionError:
            castforms = ['castform-base.gif', 'castform-rainy.gif', 'castform-shiny.gif', 'castform-snowy.gif', 'castform-sunny.gif']
            rando_form = choice(castforms)
            self.unload()
            self.load(rando_form)  # display a random one, with a star in the corner to indicate no internet.
            star = tk.Label(window,text="*", bg="black", fg="white")
            star.place(relx=0.0, rely=1.0, anchor="sw")
            window.after(hour_mili, lbl.weather_check)

window = tk.Tk()
#window.overrideredirect(True)
lbl = ImageLabel(window, bg="black")
lbl.pack()
lbl.load('castform-snowy.gif')

window.after(3000, lbl.weather_check)

window.mainloop()