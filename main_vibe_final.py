from urllib.request import urlopen
from urllib.error import URLError
from datetime import date, timedelta, datetime
import re
import tkinter 
import os

# --- Logika stahování a čištění dat ---

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
        "https://menicka.cz/api/iframe/?id=1602", # U ševců
        "https://menicka.cz/api/iframe/?id=2115", # Belvedere
        "https://menicka.cz/api/iframe/?id=5043", # Wintrovka
        "https://menicka.cz/api/iframe/?id=8040"  # Bistro Chodské
    ]
    
    vysledky = []
    
    try:
        for url in urls:
            page = urlopen(url, timeout=10)
            html = page.read().decode("windows-1250")

            start_index = html.find(datum_str)
            end_index = html.find(zitrek_str, start_index)
            
            if day_name_datum == "Pondělí" and end_index != -1:
                end_index = end_index - len(zitrek_str)

            dnes_menu = html[start_index:end_index]
            
            dnes_menu = re.sub(datum_str, f"{datum_str} {day_name_datum}", dnes_menu)
            dnes_menu = re.sub("&laquo; dnes", "", dnes_menu)
            dnes_menu = re.sub("<em.*?>", "(", dnes_menu)
            dnes_menu = re.sub("</em>", ")", dnes_menu)
            dnes_menu = re.sub("<.*?>", "", dnes_menu)
            dnes_menu = re.sub(day_name_zitra if day_name_zitra else "", "", dnes_menu)
            vysledky.append(dnes_menu.strip())
            
        return vysledky, aktualnicas, True
        
    except (URLError, Exception):
        return [], aktualnicas, False

# --- GUI Funkce ---

def tik_tak():
    """Funkce pro živé hodiny, aktualizuje se každou sekundu."""
    nyni = datetime.now().strftime("%H:%M:%S")
    label_hodiny.config(text=f"Aktuální čas: {nyni}")
    okno.after(1000, tik_tak)

def aktualizuj_okno():
    """Aktualizace menu (každých 30 sekund)."""
    jidla, cas, online = stahni_menu()
    
    if online:
        warning_overlay.place_forget()
        label_menu1.config(text=jidla[0])
        label_menu2.config(text=jidla[1])
        label_menu3.config(text=jidla[2])
        label_menu4.config(text=jidla[3])
        label_cas.config(text=f"Aktualizováno: {cas.strftime('%H:%M:%S')}")
    else:
        warning_overlay.place(relx=0, rely=0, relwidth=1, relheight=1)

    okno.after(30000, aktualizuj_okno)

# --- Inicializace GUI ---

if os.environ.get('DISPLAY','') == '':
    os.environ.__setitem__('DISPLAY', ':0.0')

okno = tkinter.Tk()
okno.configure(bg="white")
okno.config(cursor="none")

# 1. Nejdříve okno vykreslíme (bez tohoto kroku fullscreen občas selže)
okno.update()

# 2. Teď, když systém o okně ví, zapneme fullscreen
okno.attributes('-fullscreen', True)

# 3. Pojistka: Pokud by fullscreen přesto selhal, roztáhneme ho na max
sirka = okno.winfo_screenwidth()
vyska = okno.winfo_screenheight()
okno.geometry(f"{sirka}x{vyska}+0+0")

font_nadpis = ("Arial", 20, "bold")
font_menu = ("Times New Roman", 16)

# --- RESTAURACE ---
# (Ponechala jsem tvoji mřížku tak, jak je)
tkinter.Label(okno, text="U Ševců", font=font_nadpis, bg="white").grid(row=0, column=0, sticky="n", pady=(10, 0))
label_menu1 = tkinter.Label(okno, text="Načítám...", font=font_menu, wraplength=800, justify="left", bg="white")
label_menu1.grid(row=1, column=0, sticky="n", padx=20, pady=5)

tkinter.Label(okno, text="Belvedere", font=font_nadpis, bg="white").grid(row=0, column=1, sticky="n", pady=(10, 0))
label_menu2 = tkinter.Label(okno, text="Načítám...", font=font_menu, wraplength=800, justify="left", bg="white")
label_menu2.grid(row=1, column=1, sticky="n", padx=20, pady=5)

tkinter.Label(okno, text="Jídelna Wintrovka", font=font_nadpis, bg="white").grid(row=2, column=0, sticky="n", pady=(20, 0))
label_menu3 = tkinter.Label(okno, text="Načítám...", font=font_menu, wraplength=800, justify="left", bg="white")
label_menu3.grid(row=3, column=0, sticky="n", padx=20, pady=5)

tkinter.Label(okno, text="Bistro Chodské", font=font_nadpis, bg="white").grid(row=2, column=1, sticky="n", pady=(20, 0))
label_menu4 = tkinter.Label(okno, text="Načítám...", font=font_menu, wraplength=800, justify="left", bg="white")
label_menu4.grid(row=3, column=1, sticky="n", padx=20, pady=5)

# --- PATIČKA ---
# Původní label s časem aktualizace
label_cas = tkinter.Label(okno, text="Hledám spojení...", bg="white", font=("Arial", 10))
label_cas.grid(row=4, column=0, pady=(40, 0))

# NOVÝ: Label pro běžící čas (pod aktualizací)
label_hodiny = tkinter.Label(okno, text="", bg="white", font=("Arial", 14, "bold"), fg="gray")
label_hodiny.grid(row=5, column=0, pady=(0, 20))

NaObed = tkinter.Label(okno, text="Kam na oběd s KVD?", font=("Arial", 40), bg="white")
NaObed.grid(row=4, column=1, rowspan=2, pady=40)

okno.grid_columnconfigure(0, weight=1)
okno.grid_columnconfigure(1, weight=1)

# --- VAROVNÁ VRSTVA ---
warning_overlay = tkinter.Frame(okno, bg="red")
warning_text = tkinter.Label(
    warning_overlay, 
    text="⚠️ NEJDE NET! ⚠️\nZkouším se znovu připojit...", 
    font=("Arial", 40, "bold"), fg="white", bg="red"
)
warning_text.place(relx=0.5, rely=0.5, anchor="center")

# Spuštění obou smyček
tik_tak()
aktualizuj_okno()
okno.mainloop()