import os
import subprocess
import sys
import threading
from CTkMessagebox import CTkMessagebox
import customtkinter as ctk
import requests
import tkintermapview
import sqlite3

VERSION = "v.0.0.0" #dont change

app = ctk.CTk()
app.title("Ladeapp")
app.geometry("800x500")

def setTab(tab: str):
    tabview.set(tab)
    if tab == "dashboard":
        DashListSelect.configure(values=[f"{list[1]}" for list in loadLists()])
        DashComboCallback(DashListSelect.get())
    if tab == "addCharge":
        listSelect.configure(values=[f"{list[1]}" for list in loadLists()])
        addChargeComboCallback(listSelect.get())

def selectLocationMessageBox():
    msg = CTkMessagebox(icon="question", option_1="Zuhause", option_2="Ladesäule", title="Ortauswahl", message="Bitteauswählen")
    if msg.get() == "Ladesäule":
        msg = CTkMessagebox(icon="question", option_1="Karte öffnen", option_2="eigene eingeben", title=" ", message="Bitteauswählen")
        if msg.get() == "Karte öffnen":
            #setTab("map")
            CTkMessagebox(icon="info", title="Info", message="Noch nicht implementiert")
        if msg.get() == "eigene eingeben":
            dialog = ctk.CTkInputDialog(text="Bitte Ort eingeben:", title="Ort eingeben")
            locationLabel.configure(text=f"Ort: {dialog.get_input()}")
    if msg.get() == "Zuhause":
        locationLabel.configure(text=f"Ort: Zuhause")

def lade_und_platziere_marker():
    pass

def loadLists():
    connection = sqlite3.connect("database.db")
    cursor = connection.cursor()
    cursor.execute("SELECT * FROM lists")
    lists = cursor.fetchall()
    connection.close()
    return lists

def loadCharges(listID):
    connection = sqlite3.connect("database.db")
    cursor = connection.cursor()
    cursor.execute("SELECT * FROM charges WHERE listID=?", (listID,))
    charges = cursor.fetchall()
    connection.close()
    return charges

def loadListByName(listName):
    connection = sqlite3.connect("database.db")
    cursor = connection.cursor()
    cursor.execute("SELECT * FROM lists WHERE name=?", (listName,))
    list = cursor.fetchone()
    connection.close()
    return list

def initialiseDatabase():
    connection = sqlite3.connect("database.db")
    cursor = connection.cursor()
    cursor.execute("""CREATE TABLE IF NOT EXISTS lists (id INTEGER PRIMARY KEY AUTOINCREMENT, name TEXT NOT NULL, currentMileage INTEGER NOT NULL)""")
    cursor.execute("""CREATE TABLE IF NOT EXISTS charges (id INTEGER PRIMARY KEY AUTOINCREMENT, listID INTEGER, chargeBefore INTEGER, chargeAfter INTEGER, chargedKW INTEGER, price INTEGER, location TEXT, kilometersDriven INTEGER, FOREIGN KEY (listID) REFERENCES lists(id) ON DELETE CASCADE)""")
    connection.commit()
    connection.close()

def DashComboCallback(choice):
    for widget in chargeList.winfo_children():
        widget.destroy()
    charges = loadCharges(loadListByName(choice)[0])
    for charge in charges:
        chargeItem = ctk.CTkButton(master=chargeList, text=f"Charge Before: {charge[2]}% | Charge After: {charge[3]}% | Charged KW: {charge[4]} | Price: {charge[5]}€ | Location: {charge[6]} | Kilometers Driven: {charge[7]}",)
        chargeItem.pack(fill="x", padx=10, pady=5)
        chargeItem.configure(command=lambda ItemID=charge[0]: item_click(ItemID))
    DashListMileageLabel.configure(text=f"Aktueller Kilometerstand: {getLastMileage(loadListByName(choice)[0])}")

def addChargeComboCallback(choice):
    chargeCurrentKilometerLabel.configure(text=f"Current Kilometer: {getLastMileage(loadListByName(choice)[0])}")

def item_click(itemID):
    connection = sqlite3.connect("database.db")
    cursor = connection.cursor()
    msg = CTkMessagebox(icon="warning", option_1="Delete", option_2="Cancel", title="Charge Options", message="Delete?")
    if msg.get() == "Delete":
        cursor.execute("DELETE FROM charges WHERE id=?", (itemID,))
        connection.commit()
        connection.close()
    DashComboCallback(DashListSelect.get())

def addList(name, currentMileage):
    connection = sqlite3.connect("database.db")
    cursor = connection.cursor()
    cursor.execute("INSERT INTO lists (name, currentMileage) VALUES (?, ?)", (name, currentMileage))
    connection.commit()
    connection.close()
    listNameIn.delete(0, "end")
    currentKilometerIn.delete(0, "end")

def addCharge(listName, chargeBefore, chargeAfter, chargedKW, price, location, kilometersDriven):
    listID = loadListByName(listName)[0]
    connection = sqlite3.connect("database.db")
    cursor = connection.cursor()
    cursor.execute("INSERT INTO charges (listID, chargeBefore, chargeAfter, chargedKW, price, location, kilometersDriven) VALUES (?, ?, ?, ?, ?, ?, ?)", (listID, chargeBefore, chargeAfter, chargedKW, price, location, kilometersDriven))
    cursor.execute("UPDATE lists SET currentMileage = ? WHERE id = ?", (int(chargeCurrentKilometerIn.get()), listID))
    connection.commit()
    connection.close()
    chargeCurrentKilometerIn.delete(0, "end")
    batteryChargeBeforeCharge.delete(0, "end")
    batteryChargeAfterCharge.delete(0, "end")
    chargedKwIN.delete(0, "end")
    chargePrice.delete(0, "end")

def getLastMileage(listID):
    connection = sqlite3.connect("database.db")
    cursor = connection.cursor()
    cursor.execute("SELECT currentMileage FROM lists WHERE id=?", (listID,))
    lastMileage = cursor.fetchone()[0]
    connection.close()
    return lastMileage

def deleteList(listName):
    msg = CTkMessagebox(icon="warning", option_1="Delete", option_2="Cancel", title="List Options", message="Delete?")
    if msg.get() == "Delete":
        connection = sqlite3.connect("database.db")
        cursor = connection.cursor()
        cursor.execute("PRAGMA foreign_keys = ON")
        cursor.execute("DELETE FROM lists WHERE name=?", (listName,))
        connection.commit()
        connection.close()
        lists = [f"{list[1]}" for list in loadLists()]
        DashListSelect.configure(values=lists)
        if lists:
            DashListSelect.set(lists[0])
        else:
            DashListSelect.set("")
        DashComboCallback(DashListSelect.get())

def releaseRequest():
    try:
        response = requests.get("https://api.github.com/repos/pfeifermarwin-ux/Lade-app/releases",)
        release = response.json()[0]
        return release['tag_name']
    except Exception as e:
        print(f"Error fetching releases: {e}")

def downloadUpdater():
    release = requests.get("https://api.github.com/repos/pfeifermarwin-ux/Lade-app/releases").json()[0]
    for asset in release["assets"]:
        if asset["name"] == "updater.exe":
            updater_url = asset["browser_download_url"]
            break
    else:
        updaterApp.after(
            0,
            lambda: CTkMessagebox(
                icon="cancel",
                title="Update Error",
                message="Der Updater konnte nicht gefunden werden."
            )
        )
        updaterApp.after(100, stopUpdater)
        return

    response = requests.get(updater_url, stream=True)
    response.raise_for_status()
    total = int(response.headers.get("content-length", 0))
    downloaded = 0
    with open("updater.exe", "wb") as f:
        for chunk in response.iter_content(chunk_size=8192):
            if chunk:
                f.write(chunk)
                downloaded += len(chunk)
                if total:
                    updaterApp.after(
                        0,
                        lambda value=downloaded / total: progressBar.set(value)
                    )
    updaterApp.after(0, updater_finished)

def updater_finished():
    if getattr(sys, "frozen", False):
        CurrentProgramPath = os.path.abspath(sys.executable)
    else:
        CurrentProgramPath = os.path.abspath(__file__)
    new_version = releaseRequest()

    if new_version is None:
        updaterApp.destroy()
        return
    updaterApp.destroy()
    app.destroy()
    subprocess.Popen(["updater.exe", "--current-programm", CurrentProgramPath, "--new-version", new_version])
def stopUpdater():
    updaterApp.destroy()
    app.destroy()

initialiseDatabase()

tabview = ctk.CTkTabview(master=app)
tabview.pack(fill="both", expand=True)
tabview.add("addCharge")
tabview.add("addList")
tabview.add("dashboard")
tabview.add("removeCharge")
tabview.add("removeList")
tabview.add("menu")
tabview.add("map")
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
addListaddBTN = ctk.CTkButton(master=tabview.tab("addList"), text="Add", command=lambda: addList(listNameIn.get(), currentKilometerIn.get()))
addListaddBTN.pack()
backaddListBTN = ctk.CTkButton(master=tabview.tab("addList"), text="Back", command=lambda: setTab("menu"))
backaddListBTN.pack()

#Add Charge

listSelect = ctk.CTkComboBox(master=tabview.tab("addCharge"), values=[f"{list[1]}" for list in loadLists()], command=addChargeComboCallback)
listSelect.pack()
chargeCurrentKilometerLabel = ctk.CTkLabel(master=tabview.tab("addCharge"), text=f"Current Kilometer: {"None"}")
chargeCurrentKilometerLabel.pack()
chargeCurrentKilometerIn = ctk.CTkEntry(master=tabview.tab("addCharge"), placeholder_text="Current Kilometer:")
chargeCurrentKilometerIn.pack()
chargeCurrentKilometerIn.bind("<KeyRelease>", lambda event: kilometersSinceLastChargeLabel.configure(text=f"Kilometer seit letztem Laden: {int(chargeCurrentKilometerIn.get()) - int(getLastMileage(loadListByName(listSelect.get())[0])) if chargeCurrentKilometerIn.get().isdigit() and listSelect.get() != '' else 'None'}"))
kilometersSinceLastChargeLabel = ctk.CTkLabel(master=tabview.tab("addCharge"), text=f"Kiloter seit letztem Laden: {"None"}")
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
addChargeaddBTN = ctk.CTkButton(master=tabview.tab("addCharge"), text="Add", command=lambda: addCharge(
    listSelect.get(),
    batteryChargeBeforeCharge.get(),
    batteryChargeAfterCharge.get(),
    chargedKwIN.get(),
    chargePrice.get(),
    locationLabel.cget("text").replace("Ort: ", ""),
    int(chargeCurrentKilometerIn.get()) - int(getLastMileage(loadListByName(listSelect.get())[0]))
))
addChargeaddBTN.pack()
addChargeBackBTN = ctk.CTkButton(master=tabview.tab("addCharge"), text="Back", command=lambda: setTab("menu"))
addChargeBackBTN.pack()

#Dashboard
DashListSelect = ctk.CTkComboBox(master=tabview.tab("dashboard"), values=[f"{list[1]}" for list in loadLists()], command=DashComboCallback)
DashListSelect.pack()
chargeList = ctk.CTkScrollableFrame(master=tabview.tab("dashboard"), height=340)
chargeList.pack(fill="x")
DashListMileageLabel = ctk.CTkLabel(master=tabview.tab("dashboard"), text=f"Aktueller Kilometerstand: {"None"}")
DashListMileageLabel.pack()
DashDeleteListBTN = ctk.CTkButton(master=tabview.tab("dashboard"), text="Delete List", command=lambda: deleteList(DashListSelect.get()))
DashDeleteListBTN.pack()
DashBackBTN = ctk.CTkButton(master=tabview.tab("dashboard"), text="Back", command=lambda: setTab("menu"))
DashBackBTN.pack()

#Map

chargeMap = tkintermapview.TkinterMapView(master=tabview.tab("map"))
chargeMap.pack(fill="both", expand=True)
chargeMap.set_position(51.1657, 10.4515)
chargeMap.set_zoom(6)
app.after(500, lade_und_platziere_marker)

#updater

updaterApp = ctk.CTk()
updaterApp.title("Updater")
updaterApp.geometry("400x200")

ctk.CTkLabel(master=updaterApp, text="Download Updater").pack(pady=20)
progressBar = ctk.CTkProgressBar(master=updaterApp, orientation="horizontal", mode="determinate")
progressBar.pack(pady=20)

if releaseRequest() != VERSION:
    msg = CTkMessagebox(icon="info", option_1="Update", option_2="Cancel", title="Update Available", message=f"Version {releaseRequest()} is available. You are currently on version {VERSION}.")
    if msg.get() == "Update":
        threading.Thread(target=downloadUpdater, daemon=True).start()
        updaterApp.mainloop()
    else:
        app.mainloop()
else:
    app.mainloop()


