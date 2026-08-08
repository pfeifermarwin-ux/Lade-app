import customtkinter as ctk
import tkintermapview
import requests

SearchURL = "https://nominatim.openstreetmap.org/search"

def searchDef(name):
    params = {
        'q' : name,
        'format': 'json',
        'limit': 1
    }
    headers = {
        'User-Agent': 'MeinePrivateLadeApp_v1.0'
    }
    response = requests.get(SearchURL, params=params, headers=headers)
    if response.status_code == 200:
        print(response.json()[0]['boundingbox'])
        box = response.json()[0]['boundingbox']
        chargeMap.fit_bounding_box((float(box[1]), float(box[2])), (float(box[0]), float(box[3])))
    else:
        print(response)

app = ctk.CTk()
app.title("Ladeapp")
app.geometry("800x500")

search = ctk.CTkEntry(app)
searchbtn = ctk.CTkButton(app, command=lambda: searchDef(search.get()))
search.pack()
searchbtn.pack()

chargeMap = tkintermapview.TkinterMapView(app)
chargeMap.pack(fill="both", expand=True)

app.mainloop()
