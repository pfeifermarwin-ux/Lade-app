import customtkinter as ctk

app = ctk.CTk()
app.title("Ladeapp")
app.geometry("800x500")

tabview = ctk.CTkTabview(master=app)
tabview.pack(fill="both", expand=True)
tabview.add("addCharge")
tabview.add("addList")
tabview.add("dashboard")
tabview.add("removeCharge")
tabview.add("removeList")

app.mainloop()
