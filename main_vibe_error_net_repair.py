from urllib.request import urlopen, Request
from urllib.error import URLError
from datetime import date, timedelta, datetime
import re
import tkinter 

# --- Logika stahování a čištění ---

def vycisti_denni_blok(html_den):
    """Zpracuje HTML jednoho dne a poskládá jídla do čistých řádků: číslo, název, cena."""
    radky_menu = []
    
    # Vytáhneme jednotlivé řádky tabulky <tr>
    tr_bloky = re.findall(r"<tr[^>]*>(.*?)</tr>", html_den, flags=re.DOTALL)
    
    for tr in tr_bloky:
        # Vytáhneme texty z buněk <td>
        bunky = re.findall(r"<td[^>]*>(.*?)</td>", tr, flags=re.DOTALL)
        if not bunky:
            continue
            
        ciste_bunky = []
        for b in bunky:
            # Odstranit vnitřní tagy (např. <em> pro alergeny) a smazat přebytečné mezery/tabulátory
            text = re.sub(r"<.*?>", "", b)
            text = re.sub(r"\s+", " ", text).strip()
            if text:
                ciste_bunky.append(text)
                
        if not ciste_bunky:
            continue
            
        # Spojení buňky do jednoho čitelného řádku
        if len(ciste_bunky) == 1:
            radky_menu.append(ciste_bunky[0])
        elif len(ciste_bunky) == 2:
            # Většinou polévka + cena, nebo jídlo bez čísla + cena
            radky_menu.append(f"{ciste_bunky[0]}  —  {ciste_bunky[1]}")
        elif len(ciste_bunky) >= 3:
            # Číslo + Název jídla + Cena
            radky_menu.append(f"{ciste_bunky[0]} {ciste_bunky[1]}  —  {ciste_bunky[2]}")
            
    return "\n".join(radky_menu)


def stahni_menu():
    aktualnicas = datetime.now()
    today = date.today()

    if aktualnicas.hour >= 14:
        today = today + timedelta(days=1)

    zitrek = today + timedelta(days=1)
    day_names = {
        "Monday": "Pondělí", "Tuesday": "Úterý", "Wednesday": "Středa",
        "Thursday": "Čtvrtek", "Friday": "Pátek", "Saturday": "Sobota", "Sunday": "Neděle"
    }

    day_name_datum = day_names.get(today.strftime("%A"), "")
    datum_str = f"{today.day}.{today.month}.{today.year}"
    zitrek_str = f"{zitrek.day}.{zitrek.month}.{zitrek.year}"

    restaurace = [
        {"nazev": "Wintrovka", "url": "https://menicka.cz/api/iframe/?id=5043"},
        {"nazev": "Bistro Chodský", "url": "https://menicka.cz/api/iframe/?id=8040"},
        {"nazev": "U ševců", "url": "https://menicka.cz/api/iframe/?id=1602"},
        {"nazev": "Belvedere", "url": "https://menicka.cz/api/iframe/?id=2115"}
    ]
    
    vysledky = []
    chyby_site = 0
    headers = {"User-Agent": "Mozilla/5.0 (X11; Linux armv7l)"}

    for r in restaurace:
        try:
            req = Request(r["url"], headers=headers)
            with urlopen(req, timeout=8) as page:
                html = page.read().decode("utf-8", errors="replace")

            # Hledání dnešního dne
            start_index = html.find(datum_str)
            if start_index == -1:
                vysledky.append(f"{day_name_datum} {datum_str}\n\nMenu pro dnešek není zadáno.")
                continue

            # Hledání konce dnešního dne (zítřejší datum nebo konec body)
            end_index = html.find(zitrek_str, start_index)
            if end_index == -1:
                end_index = html.find("</body>", start_index)
            if end_index == -1:
                end_index = start_index + 2500

            vyrez_dne = html[start_index:end_index]
            menu_text = vycisti_denni_blok(vyrez_dne)
            
            hlavicka = f"{day_name_datum} {datum_str}\n" + ("—" * 30)
            vysledky.append(f"{hlavicka}\n{menu_text}" if menu_text else f"{hlavicka}\nMenu je prázdné.")

        except (URLError, TimeoutError, OSError) as e:
            print(f"Chyba sítě u {r['nazev']}: {e}")
            chyby_site += 1
            vysledky.append(f"{r['nazev']}\nChyba spojení.")
        except Exception as e:
            print(f"Chyba u {r['nazev']}: {e}")
            vysledky.append(f"{r['nazev']}\nChyba zpracování.")

    # Pouze pokud neprošla žádná restaurace kvůli síti, spouštíme červenou
    if chyby_site == len(restaurace):
        return [], aktualnicas, False

    return vysledky, aktualnicas, True


# --- GUI Funkce ---

def aktualizuj_okno():
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
        label_cas.config(text="CHYBA PŘIPOJENÍ!")

    okno.after(30000, aktualizuj_okno)


# --- Inicializace GUI ---
okno = tkinter.Tk()
okno.attributes('-fullscreen', True)
okno.configure(bg="white")
okno.bind("<Escape>", lambda e: okno.destroy())

# Zjištění rozměrů pro zalamování textu
okno.update_idletasks()
sirka_poloviny = (okno.winfo_screenwidth() // 2) - 80

# Pevné rozdělení sloupců na 50 % : 50 %
okno.grid_columnconfigure(0, weight=1, uniform="sloupec")
okno.grid_columnconfigure(1, weight=1, uniform="sloupec")
okno.grid_rowconfigure(1, weight=1)
okno.grid_rowconfigure(3, weight=1)

font_nadpis = ("Arial", 16, "bold")
font_menu = ("Arial", 12)

# Názvy podniků
lbl_n1 = tkinter.Label(okno, text="Wintrovka", font=font_nadpis, bg="white", fg="#b71c1c")
lbl_n1.grid(row=0, column=0, pady=(15, 0))
lbl_n2 = tkinter.Label(okno, text="Bistro Chodský", font=font_nadpis, bg="white", fg="#b71c1c")
lbl_n2.grid(row=0, column=1, pady=(15, 0))

# Labely pro menu: zarovnání doleva (justify="left", anchor="nw") a pevný wraplength
label_menu1 = tkinter.Label(okno, text="Načítám...", font=font_menu, justify="left", anchor="nw", bg="white", wraplength=sirka_poloviny)
label_menu1.grid(row=1, column=0, padx=25, pady=5, sticky="nsew")

label_menu2 = tkinter.Label(okno, text="Načítám...", font=font_menu, justify="left", anchor="nw", bg="white", wraplength=sirka_poloviny)
label_menu2.grid(row=1, column=1, padx=25, pady=5, sticky="nsew")

lbl_n3 = tkinter.Label(okno, text="U ševců", font=font_nadpis, bg="white", fg="#b71c1c")
lbl_n3.grid(row=2, column=0, pady=(15, 0))
lbl_n4 = tkinter.Label(okno, text="Belvedere", font=font_nadpis, bg="white", fg="#b71c1c")
lbl_n4.grid(row=2, column=1, pady=(15, 0))

label_menu3 = tkinter.Label(okno, text="Načítám...", font=font_menu, justify="left", anchor="nw", bg="white", wraplength=sirka_poloviny)
label_menu3.grid(row=3, column=0, padx=25, pady=5, sticky="nsew")

label_menu4 = tkinter.Label(okno, text="Načítám...", font=font_menu, justify="left", anchor="nw", bg="white", wraplength=sirka_poloviny)
label_menu4.grid(row=3, column=1, padx=25, pady=5, sticky="nsew")

label_cas = tkinter.Label(okno, text="Startuji...", font=("Arial", 10), bg="white", fg="#888888")
label_cas.grid(row=4, column=0, columnspan=2, pady=10)

# --- Varovná obrazovka ---
warning_overlay = tkinter.Frame(okno, bg="red")
warning_text = tkinter.Label(
    warning_overlay, 
    text="⚠️ NEJDE NET! ⚠️\nZkontroluj kabel nebo Wi-Fi.\nZkouším se znovu připojit...", 
    font=("Arial", 40, "bold"), 
    fg="white", 
    bg="red"
)
warning_text.place(relx=0.5, rely=0.5, anchor="center")

aktualizuj_okno()
okno.mainloop()