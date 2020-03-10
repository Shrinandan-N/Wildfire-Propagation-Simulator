import tkinter as tk
import random as rand
from random import randint
from tkinter import ttk
import webbrowser
import folium
import csv
import pandas as pd
import random as rd
import math
import configparser
import requests


# button methods

window = tk.Tk()
window.title("Wildfire Propagation")
window.geometry("300x220")

# latitude text field
latController = tk.IntVar()
latLabel = ttk.Label(window, text="LATITUDE", width=14)
latLabel.grid(row=2, column=0)
latEntry = ttk.Entry(window, width=10, textvariable=latController)
latEntry.grid(row=2, column=1)

# long text field
longController = tk.IntVar()
longLabel = ttk.Label(window, text="LONGITUDE", width=14)
longLabel.grid(row=3, column=0)
longEntry = ttk.Entry(window, width=10, textvariable=longController)
longEntry.grid(row=3, column=1)

# time text field
timeController = tk.IntVar()
timeLabel = ttk.Label(window, text="DURATION (hours)", width=14)
timeLabel.grid(row=4, column=0)
timeEntry = ttk.Entry(window, width=10, textvariable=timeController)
timeEntry.grid(row=4, column=1)


def get_api_key():
    config = configparser.ConfigParser()
    config.read('config.ini')
    return config['openweathermap']['api']


def get_weather(api_key, lat, long):
    url = "http://api.openweathermap.org/data/2.5/weather?lat={}andlon={}andappid={}".format(lat, long, api_key)
    r = requests.get(url)
    return r.json()


api_key = get_api_key()

weather = get_weather(api_key, latController.get(), longController.get())
def initValues():


    initLabel = tk.Label(window,
                         text="Initialized Values : " "\n Location: " +  str(weather['name']) + "\n Latitude: " + str(
                             latController.get()) + "\n Longitude: " +
                              str(longController.get()) +
                              "\n Wind Speed: " + str(weather['wind']['speed'] + " mi/hr" + "\n Wind Degrees: " + str(weather['wind']['deg']) + "\n", width=18)
    initLabel.grid(row=6, column=0)


def generateBaseMap(default_location=[latController.get(), longController.get()], default_zoom_start=30):
    base_map = folium.Map(location=default_location, zoom_start=default_zoom_start)
    return base_map


from folium.plugins import HeatMap


def simulateValues():

    with open('fireVal.csv', 'w', newline='') as fp:
        fieldnames = ['latitude', 'longitude', 'count', 'minute']
        a = csv.DictWriter(fp, fieldnames=fieldnames)
        a.writeheader()

        latt = latController.get()
        longg = longController.get()
        backLat = latController.get()
        backLong = longController.get()
        duration = timeController.get() * 60
        for i in range(0, duration):  # make 4320 minutes
            fluct = randint(0, 10)
            windSpeed = randint(int(weather['wind']['speed']) - fluct, int(weather['wind']['speed']) + fluct) #needs to be fixed!
            slope = rd.uniform(0.0, 1.0)

            # variables
            Mf = randint(100, 200)
            Qig = 250 + (116 * Mf)
            E = 0.924  # fluctuating
            Pb = 0.55
            squig = 0.4824
            Ir = 62889.331
            s = 1764
            Ro = (Ir * squig) / (Pb * E * Qig)

            Ow = (0.005235)*(windSpeed*5280/60)**1.43
            Os = (17.851) * (slope ** 2)

            R = Ro * (1 + Ow + Os)

            #backing fire
            Rh = Ro*(1 + 1/Ow + Os)

            C = 7.47 * (math.exp(-0.133*(s**0.55)))
            B = 0.02526*s**0.54
            E = 0.715*(math.exp(-3.59*(10**-4)*s))
            esum = Ow + Os

            Ue = ((esum*(2.35)**E)/C)**(-B)
            z = 1 + 0.25*(Ue)
            v = ((z**2 - 1)**0.5) / z
            Rb = Rh*(1-v / 1+v)




            #wind degrees
            windDeg = weather['wind']['deg']
            fluxValue = randint(28, 95)

            #determining wind direction
            windFlux = randint(windDeg - fluxValue, windDeg + fluxValue)
            if(windFlux>= 0 and windFlux<= 29):
                windDir = "N"
            elif(windFlux> 29 and windFlux<= 65):
                windDir = "NE"
            elif(windFlux> 65 and windFlux<= 111):
                windDir = "E"
            elif (windFlux> 111 and windFlux<= 165):
                windDir = "SE"
            elif (windFlux> 165 and windFlux<= 204):
                windDir = "S"
            elif (windFlux> 204 and windFlux<= 245):
                windDir = "SW"
            elif (windFlux> 245 and windFlux<= 291):
                windDir = "W"
            elif (windFlux> 291 and windFlux<= 359):
                windDir = "NW"


            #convert to latitude/longitude using nautical miles calculation
            convert = (R / 364567.2)


            if(windDir == "N"):
                lat = latt + convert
                long = longg - convert

                lat2 = backLat - (Rb / 364567.2)
                long2 = backLong + (Rb / 364567.2)
            elif(windDir == "NE"):
                lat = latt + convert
                long = longg + convert
                lat2 = backLat - (Rb / 364567.2)
                long2 = backLong - (Rb / 364567.2)
            elif(windDir == "E"):
                lat = latt
                long = longg + convert

                lat2 = backLat
                long2 = backLong - (Rb / 364567.2)
            elif(windDir == "SE"):
                lat = latt - convert
                long = longg + convert

                lat2 = backLat + (Rb / 364567.2)
                long2 = backLong - (Rb / 364567.2)
            elif(windDir == "S"):
                lat = latt - convert
                long = longg

                lat2 = backLat + (Rb / 364567.2)
                long2 = backLong
            elif(windDir == "SW"):
                lat = latt - convert
                long = longg - convert

                lat2 = backLat + (Rb / 364567.2)
                long2 = backLong + (Rb / 364567.2)
            elif(windDir == "W"):
                lat = latt
                long = longg - convert

                lat2 = backLat
                long2 = backLong + (Rb / 364567.2)
            elif(windDir == "NW"):
                lat = latt + convert
                long = longg - convert

                lat2 = backLat - (Rb / 364567.2)
                long2 = backLong + (Rb / 364567.2)



            #convert to degrees
            a.writerow({'latitude': lat, 'longitude': long, 'count': 1, 'minute': i})
            a.writerow({'latitude': lat2, 'longitude': long2, 'count': 1, 'minute': i})

            latt = lat
            longg = long
            backLat = lat2
            backLong = long2

    df_train = pd.read_csv('fireVal.csv')
    df_test = pd.read_csv('fireVal.csv')
    df = pd.concat([df_train, df_test], sort=False, ignore_index=True)


    map = generateBaseMap(default_location=[latController.get(), longController.get()], default_zoom_start=15)

    tooltip = 'click for more info'


    folium.Marker([latController.get(), longController.get()], popup='<strong>Fire Initialization Site</strong>',
                  tooltip=tooltip,
                  icon=folium.Icon(icon='fire', color='red')).add_to(map)

    for index, row in df.iterrows():
        firetip = "Time: " + str(row['minute']) + " minutes"
        folium.CircleMarker([row['latitude'], row['longitude']],
                            radius=3,
                            fill_color="#ff0000", tooltip= firetip, color = "#32d302").add_to(map)

    from folium.plugins import HeatMap
    df_copy = df.copy()
    df_copy['count'] = 1
    HeatMap(data=df_copy[['latitude', 'longitude', 'count']].groupby(
        ['latitude', 'longitude']).sum().reset_index().values.tolist(), radius=30, gradient={0.29: 'blue', 0.63: 'lime', 0.94: 'orange', 1: 'red'}, max_zoom=13).add_to(
        map)

    df_min_list = []
    for minute in df_copy.minute.sort_values().unique():
        df_min_list.append(df_copy.loc[df_copy.minute == minute, ['latitude', 'longitude', 'count']].groupby(
            ['latitude', 'longitude']).sum().reset_index().values.tolist())

    from folium.plugins import HeatMapWithTime
    HeatMapWithTime(df_min_list, radius=45, gradient={0.2: 'red', 0.4: 'orange', 0.6: 'lime', 1: 'blue'},
                    min_opacity=0.5, max_opacity=0.8, use_local_extrema=True).add_to(map)

    map.save("fireSimu.html")

    url = "/Users/shrinandan-n/PycharmProjects/WildfireSimulation/fireSimu.html"


    webbrowser.open(url)


# simulate values button
simuBtn = tk.Button(window, text="SIMULATE VALUES", fg="blue", width=15,
                    command=simulateValues)  # , command=recieverValues
simuBtn.grid(row=5, column=1)
initBtn = tk.Button(window, text="INITIALIZE VALUES", fg="red", width=15,
                    command=initValues)  # , command=recieverValues
initBtn.grid(row=5, column=0)


window.mainloop()