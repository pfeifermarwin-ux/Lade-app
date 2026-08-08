from CTkMessagebox import CTkMessagebox
import customtkinter as ctk
import requests
import tkintermapview

app = ctk.CTk()
app.title("Ladeapp")
app.geometry("800x500")

def setTab(tab: str):
    tabview.set(tab)

def selectLocationMessageBox():
    msg = CTkMessagebox(icon="question", option_1="Zuhause", option_2="Ladesäule", title="Ortauswahl", message="Bitteauswählen")
    if msg.get() == "Ladesäule":
        msg = CTkMessagebox(icon="question", option_1="Karte öffnen", option_2="eigene eingeben", title=" ", message="Bitteauswählen")
        if msg.get() == "Karte öffnen":
            setTab("map")

def lade_und_platziere_marker():
    try:
        url = "https://bund.dev"
        
        headers = {
            "User-Agent": "MeinLadesaeulenFinderApp/1.0 (Kontakt: meinprojekt@example.com)"
        }
        
        antwort = requests.get(url, headers=headers, timeout=15)
        
        if antwort.status_code != 200:
            print(f"Server-Fehler! Status-Code: {antwort.status_code}")
            print("Server-Antwort:", antwort.text[:200])
            return
            
        ladesaeulen = antwort.json()
        
        gesetzte_marker = 0
        for saeule in ladesaeulen[:500]:
            lat = saeule.get("latitude")
            lon = saeule.get("longitude")
            betreiber = saeule.get("operator", "Unbekannter Betreiber")
            ort = saeule.get("city", "")
            
            if lat and lon:
                chargeMap.set_marker(
                    lat, 
                    lon, 
                    text=f"{betreiber}\n{ort}"
                )
                gesetzte_marker += 1
                
        print(f"Erfolgreich {gesetzte_marker} Marker auf der Karte platziert.")
        
    except requests.exceptions.JSONDecodeError:
        print("Fehler: Der Server hat kein gültiges JSON gesendet. Eventuell ist die API temporär überlastet.")
    except Exception as e:
        print("Anderer Fehler beim Laden:", e)

tabview = ctk.CTkTabview(master=app)
tabview.pack(fill="both", expand=True)
tabview.add("addCharge")
tabview.add("addList")
tabview.add("dashboard")
tabview.add("removeCharge")
tabview.add("removeList")
tabview.add("menu")
tabview.add("map")
tabview._top_spacing = 0
tabview._top_button_overhang = 0
tabview._segmented_button.grid_forget()
tabview._configure_grid()
tabview.set("menu")

#Menu

addListBTN = ctk.CTkButton(master=tabview.tab("menu"), text="Add List", command=lambda: setTab("addList"))
addListBTN.pack()
addChargeBTN = ctk.CTkButton(master=tabview.tab("menu"), text="Add Charge", command=lambda: setTab("addCharge"))
addChargeBTN.pack()
dashboardBTN = ctk.CTkButton(master=tabview.tab("menu"), text="Dashboard", command=lambda: setTab("dashboard"))
dashboardBTN.pack()

#Add List

listNameIn = ctk.CTkEntry(master=tabview.tab("addList"), placeholder_text="List Name:")
listNameIn.pack()
currentKilometerIn = ctk.CTkEntry(master=tabview.tab("addList"), placeholder_text="Current Kilometer:")
currentKilometerIn.pack()
addListaddBTN = ctk.CTkButton(master=tabview.tab("addList"), text="Add")
addListaddBTN.pack()
backaddListBTN = ctk.CTkButton(master=tabview.tab("addList"), text="Back", command=lambda: setTab("menu"))
backaddListBTN.pack()

#Add Charge

listSelect = ctk.CTkComboBox(master=tabview.tab("addCharge"), values=["list1","list2"])
listSelect.pack()
chargeCurrentKilometerIn = ctk.CTkEntry(master=tabview.tab("addCharge"), placeholder_text="Current Kilometer:")
chargeCurrentKilometerIn.pack()
kilometersSinceLastChargeLabel = ctk.CTkLabel(master=tabview.tab("addCharge"), text=f"Kiloter seit letztem Laden: +{"None"}")
kilometersSinceLastChargeLabel.pack()
batteryChargeBeforeCharge = ctk.CTkEntry(master=tabview.tab("addCharge"), placeholder_text="Batterieladung vor Laden in %:")
batteryChargeBeforeCharge.pack()
batteryChargeAfterCharge = ctk.CTkEntry(master=tabview.tab("addCharge"), placeholder_text="Batterieladung vor Laden in %:")
batteryChargeAfterCharge.pack()
selectLocation = ctk.CTkButton(master=tabview.tab("addCharge"), text="Select Location", command=lambda: selectLocationMessageBox())
selectLocation.pack()
locationLabel = ctk.CTkLabel(master=tabview.tab("addCharge"), text=f"Ort:{"None"}")
locationLabel.pack()
chargedKwIN = ctk.CTkEntry(master=tabview.tab("addCharge"), placeholder_text="Geladene KW:")
chargedKwIN.pack()
chargePrice = ctk.CTkEntry(master=tabview.tab("addCharge"), placeholder_text="Preis")
chargePrice.pack()
addChargeaddBTN = ctk.CTkButton(master=tabview.tab("addCharge"), text="Add")
addChargeaddBTN.pack()

#Dashboard

chargeList = ctk.CTkScrollableFrame(master=tabview.tab("dashboard"), height=340)
chargeList.pack(fill="x")

def item_click(item_text):
    print(f"Selected: {item_text}")

for i in range(20):
    btn = ctk.CTkButton(
        chargeList, 
        text=f"List Item {i+1}",
        command=lambda t=f"List Item {i+1}": item_click(t)
    )
    btn.pack(pady=4, fill="x")

#Map

chargeMap = tkintermapview.TkinterMapView(master=tabview.tab("map"))
chargeMap.pack(fill="both", expand=True)
chargeMap.set_position(51.1657, 10.4515)
chargeMap.set_zoom(6)
app.after(500, lade_und_platziere_marker)


app.mainloop()
