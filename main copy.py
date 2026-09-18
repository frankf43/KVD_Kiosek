from urllib.request import urlopen
from urllib.error import URLError  # Import pro odchycení chyby sítě
from datetime import date, timedelta, datetime
import re
import tkinter 
import os

# --- Logika stahování s ošetřením chyb ---

def stahni_menu():
    aktualnicas = datetime.now()
    today = date.today()

    if aktualnicas.hour >= 14:
        today = today + timedelta(1)

    zitrek = today + timedelta(1)
    day_names = {
        "Monday": "Pondělí", "Tuesday": "Úterý", "Wednesday": "Středa",
        "Thursday": "Čtvrtek", "Friday": "Pátek", "Saturday": "Sobota", "Sunday": "Neděle"
    }

    day_name_datum = day_names.get(today.strftime("%A"))
    day_name_zitra = day_names.get(zitrek.strftime("%A"))
    
    datum_str = today.strftime("%d.%m.%Y").replace(".0", ".").lstrip("0")
    zitrek_str = zitrek.strftime("%d.%m.%Y").replace(".0", ".").lstrip("0")

    urls = [
        "https://menicka.cz/api/iframe/?id=5043", #Wintrovka
        "https://menicka.cz/api/iframe/?id=8040", #Bistro Chodský
        "https://menicka.cz/api/iframe/?id=1602", #U ševců
        "https://menicka.cz/api/iframe/?id=2115" #Belvedere
    ]
    
    vysledky = []
    
    try:
        # Zkusíme otevřít aspoň první URL, abychom ověřili spojení
        for url in urls:
            page = urlopen(url, timeout=10) # Timeout je důležitý, aby skript nevisel
            html = page.read().decode("UTF-8")

            start_index = html.find(datum_str)
            end_index = html.find(zitrek_str, start_index)
            
            if day_name_datum == "Pondělí" and end_index != -1:
                end_index = end_index - len(zitrek_str)

            dnes_menu = html[start_index:end_index]
            
            # Tvoje originální regexy
            dnes_menu = re.sub(datum_str, f"{datum_str} {day_name_datum}", dnes_menu)
            dnes_menu = re.sub("&laquo; dnes", "", dnes_menu)
            dnes_menu = re.sub("<em.*?>", "(", dnes_menu)
            dnes_menu = re.sub("</em>", ")", dnes_menu)
            dnes_menu = re.sub("<.*?>", "", dnes_menu)
            dnes_menu = re.sub(day_name_zitra if day_name_zitra else "", "", dnes_menu)
            vysledky.append(dnes_menu.strip())
            
        return vysledky, aktualnicas, True # True znamená, že je vše OK
        
    except (URLError, Exception) as e:
        print(f"Chyba sítě: {e}")
        return [], aktualnicas, False # False znamená výpadek

# --- GUI Funkce ---

def aktualizuj_okno():
    jidla, cas, online = stahni_menu()
    
    if online:
        # Schovat varování, pokud existuje
        warning_overlay.place_forget()
        
        # Aktualizace textů
        label_menu1.config(text=jidla[0])
        label_menu2.config(text=jidla[1])
        label_menu3.config(text=jidla[2])
        label_menu4.config(text=jidla[3])
        label_cas.config(text=f"Aktualizováno: {cas.strftime('%H:%M:%S')}")
    else:
        # Zobrazit varování přes celé okno
        warning_overlay.place(relx=0, rely=0, relwidth=1, relheight=1)
        label_cas.config(text="CHYBA PŘIPOJENÍ!")

    # Opakovat za 30 sekund
    okno.after(30000, aktualizuj_okno)

# --- Inicializace GUI ---
okno = tkinter.Tk()
okno.attributes('-fullscreen', True)
okno.configure(bg="white")

# ... (tady zůstává stejné rozvržení labelů jako minule) ...
font_nadpis = ("Arial", 16, "bold")
font_menu = ("Arial", 14)

# Labely pro menu (zjednodušený zápis pro ukázku)
label_menu1 = tkinter.Label(okno, text="Načítám...", font=font_menu, justify="center", bg="white")
label_menu1.grid(row=1, column=0)
label_menu2 = tkinter.Label(okno, text="Načítám...", font=font_menu, justify="center", bg="white")
label_menu2.grid(row=1, column=1)
label_menu3 = tkinter.Label(okno, text="Načítám...", font=font_menu, justify="center", bg="white")
label_menu3.grid(row=3, column=0)
label_menu4 = tkinter.Label(okno, text="Načítám...", font=font_menu, justify="center", bg="white")
label_menu4.grid(row=3, column=1)
label_cas = tkinter.Label(okno, text="Startuji...")
label_cas.grid(row=4, column=0)

# --- SPECIÁLNÍ VRSTVA PRO VAROVÁNÍ ---
# Vytvoříme Frame, který je zatím schovaný
warning_overlay = tkinter.Frame(okno, bg="red")
warning_text = tkinter.Label(
    warning_overlay, 
    text="⚠️ NEJDE NET! ⚠️\nZkontroluj kabel nebo Wi-Fi.\nZkouším se znovu připojit...", 
    font=("Arial", 40, "bold"), 
    fg="white", 
    bg="red"
)
warning_text.place(relx=0.5, rely=0.5, anchor="center")

# První spuštění
aktualizuj_okno()
okno.mainloop()