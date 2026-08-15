import json
import os

import customtkinter as ctk
import tkintermapview
import requests

SearchURL = "https://nominatim.openstreetmap.org/search"
ChargeApi = "https://ladestationen.api.bund.dev/query"
api_timer_id = None

def searchDef(name):
    params = {
        'q' : name,
        'format': 'json',
        'limit': 1,
        'accept-language': 'de-de'
    }
    headers = {
        'User-Agent': 'MeinePrivateLadeApp_v1.0'
    }
    response = requests.get(SearchURL, params=params, headers=headers)
    if response.status_code == 200:
        #print(response.json())
        type = response.json()[0]['addresstype']
        ResName = response.json()[0]['name']
        displayName = response.json()[0]['display_name']
        infoLabel.configure(text=f"Type:{type} | Name:{ResName} | Display Name:{displayName}")
        box = response.json()[0]['boundingbox']
        chargeMap.fit_bounding_box((float(box[1]), float(box[2])), (float(box[0]), float(box[3])))
    else:
        print(response)

def  combobox_callback(choice):
    if choice == "Google":
        chargeMap.set_tile_server("https://mt0.google.com/vt/lyrs=m&hl=en&x={x}&y={y}&z={z}&s=Ga", max_zoom=22)
    if choice == "Google Sattelit":
        chargeMap.set_tile_server("https://mt0.google.com/vt/lyrs=s&hl=en&x={x}&y={y}&z={z}&s=Ga", max_zoom=22)
    if choice == "OpenStreetMap":
        chargeMap.set_tile_server("https://a.tile.openstreetmap.org/{z}/{x}/{y}.png")

def loadChagingPoints(ereignis=None):
    global api_timer_id
    if api_timer_id is not None:
        app.after_cancel(api_timer_id)
    api_timer_id = app.after(500, chagingPointApiRequest)

def chagingPointApiRequest():
    print(chargeMap.get_position())


app = ctk.CTk()
app.title("Ladeapp")
app.geometry("800x500")

search = ctk.CTkEntry(app)
searchbtn = ctk.CTkButton(app, command=lambda: searchDef(search.get()))
search.pack()
searchbtn.pack()

infoLabel = ctk.CTkLabel(app)
infoLabel.pack()
combobox_var = ctk.StringVar(value="Google")
mapProviderSelect = ctk.CTkComboBox(app, values=["Google", "Google Sattelit", "OpenStreetMap"], command=combobox_callback, variable=combobox_var)
mapProviderSelect.pack()

chargeMap = tkintermapview.TkinterMapView(app)
chargeMap.canvas.bind("<B1-Motion>", loadChagingPoints, add="+")
chargeMap.canvas.bind("<ButtonRelease-1>", loadChagingPoints, add="+")
chargeMap.canvas.bind("<MouseWheel>", loadChagingPoints, add="+")
chargeMap.pack(fill="both", expand=True)


app.mainloop()
