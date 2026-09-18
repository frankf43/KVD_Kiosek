from urllib.request import urlopen, Request
from urllib.error import URLError
from datetime import date, timedelta, datetime
import re
import tkinter

# --- Logika stahování a čištění z Meníček ---

def vycisti_denni_blok(html_den):
    radky_menu = []
    tr_bloky = re.findall(r"<tr[^>]*>(.*?)</tr>", html_den, flags=re.DOTALL)
    
    for tr in tr_bloky:
        bunky = re.findall(r"<td[^>]*>(.*?)</td>", tr, flags=re.DOTALL)
        if not bunky:
            continue
            
        ciste_bunky = []
        for b in bunky:
            text = re.sub(r"<.*?>", "", b)
            text = re.sub(r"\s+", " ", text).strip()
            if text:
                ciste_bunky.append(text)
                
        if not ciste_bunky:
            continue
            
        if "soup" in tr:
            nazev = ciste_bunky[0]
            cena = f"  ({ciste_bunky[1]})" if len(ciste_bunky) > 1 else ""
            radky_menu.append(f"🍲  Polévka: {nazev}{cena}\n")
        elif len(ciste_bunky) == 1:
            radky_menu.append(f"•  {ciste_bunky[0]}")
        elif len(ciste_bunky) == 2:
            radky_menu.append(f"•  {ciste_bunky[0]}   [{ciste_bunky[1]}]")
        elif len(ciste_bunky) >= 3:
            cislo = ciste_bunky[0]
            jidlo = ciste_bunky[1]
            cena = ciste_bunky[2]
            radky_menu.append(f"{cislo}  {jidlo}\n    ↳  {cena}\n")
            
    return "\n".join(radky_menu).strip()


def stahni_menu():
    aktualnicas = datetime.now()
    target_date = date.today()

    if aktualnicas.hour >= 14:
        target_date += timedelta(days=1)

    zitrek = target_date + timedelta(days=1)
    datum_str = f"{target_date.day}.{target_date.month}.{target_date.year}"
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

            start_index = html.find(datum_str)
            if start_index == -1:
                vysledky.append("\nMenu pro dnešní den\nnení zadáno.")
                continue

            end_index = html.find(zitrek_str, start_index)
            if end_index == -1:
                end_index = html.find("</body>", start_index)
            if end_index == -1:
                end_index = start_index + 2500

            vyrez_dne = html[start_index:end_index]
            menu_text = vycisti_denni_blok(vyrez_dne)
            vysledky.append(menu_text if menu_text else "\nMenu pro dnešní den je prázdné.")

        except (URLError, TimeoutError, OSError):
            chyby_site += 1
            vysledky.append("\nNelze se spojit se serverem.")
        except Exception:
            vysledky.append("\nChyba při zpracování dat.")

    if chyby_site == len(restaurace):
        return [], False

    return vysledky, True


# --- Třída pro samo-rolovací kartu restaurace ---

class RolovaciKarta:
    def __init__(self, parent, nazev, barva_hlavicky, barva_textu, sirka):
        self.nazev = nazev
        self.barva_textu = barva_textu
        
        self.card = tkinter.Frame(parent, bg="#ffffff", highlightbackground="#d5ded4", highlightthickness=1)
        
        # Zelená hlavička karty
        self.card_head = tkinter.Frame(self.card, bg=barva_hlavicky)
        self.card_head.pack(fill="x")
        
        lbl_title = tkinter.Label(
            self.card_head, 
            text=nazev.upper(), 
            font=("DejaVu Sans", 14, "bold"), 
            fg="#ffffff", 
            bg=barva_hlavicky
        )
        lbl_title.pack(side="left", padx=16, pady=9)
        
        # Scrollovací canvas
        self.canvas = tkinter.Canvas(self.card, bg="#ffffff", highlightthickness=0, bd=0)
        self.canvas.pack(fill="both", expand=True, padx=14, pady=10)
        
        self.inner_frame = tkinter.Frame(self.canvas, bg="#ffffff")
        self.canvas_win = self.canvas.create_window((0, 0), window=self.inner_frame, anchor="nw", width=sirka)
        
        self.lbl_content = tkinter.Label(
            self.inner_frame, 
            text="Načítám menu...", 
            font=("DejaVu Sans", 11), 
            fg=barva_textu, 
            bg="#ffffff", 
            justify="left", 
            anchor="nw",
            wraplength=sirka - 20
        )
        self.lbl_content.pack(fill="both", expand=True)
        
        # Stav rolování
        self.can_scroll = False
        self.scroll_pos = 0.0
        self.max_scroll = 0.0
        self.total_h = 0
        self.state = "PAUSE_TOP"
        self.timer = 150  # ~6 sekund prodleva
        
        self.canvas.bind("<Configure>", self._on_resize)

    def _on_resize(self, event):
        self.canvas.itemconfig(self.canvas_win, width=event.width)
        self.lbl_content.config(wraplength=event.width - 15)
        self.prepocitej_limity()

    def nastav_text(self, text):
        self.lbl_content.config(text=text)
        self.card.update_idletasks()
        self.scroll_pos = 0.0
        self.canvas.yview_moveto(0)
        self.state = "PAUSE_TOP"
        self.timer = 150
        self.prepocitej_limity()

    def prepocitej_limity(self):
        self.inner_frame.update_idletasks()
        req_h = self.inner_frame.winfo_reqheight()
        vis_h = self.canvas.winfo_height()
        
        if req_h > vis_h and vis_h > 20:
            self.can_scroll = True
            self.total_h = req_h
            self.max_scroll = req_h - vis_h
            self.canvas.configure(scrollregion=(0, 0, self.canvas.winfo_width(), req_h))
        else:
            self.can_scroll = False
            self.canvas.yview_moveto(0)

    def krok_animace(self):
        if not self.can_scroll:
            return

        if self.state == "PAUSE_TOP":
            self.timer -= 1
            if self.timer <= 0:
                self.state = "SCROLLING"

        elif self.state == "SCROLLING":
            self.scroll_pos += 1.0  # Rychlost posunu: 1 px za tik (velmi plynulé)
            if self.scroll_pos >= self.max_scroll:
                self.scroll_pos = self.max_scroll
                self.state = "PAUSE_BOTTOM"
                self.timer = 150  # ~6 sekund dole na dočtení
            
            fraction = self.scroll_pos / self.total_h
            self.canvas.yview_moveto(fraction)

        elif self.state == "PAUSE_BOTTOM":
            self.timer -= 1
            if self.timer <= 0:
                # Návrat nahoru a nová pauza
                self.scroll_pos = 0.0
                self.canvas.yview_moveto(0)
                self.state = "PAUSE_TOP"
                self.timer = 120


# --- GUI Rozhraní ---

okno = tkinter.Tk()
okno.attributes('-fullscreen', True)
okno.configure(bg="#f4f6f4")
okno.bind("<Escape>", lambda e: okno.destroy())

COLOR_KVD_GREEN = "#4d8334"
COLOR_KVD_ACCENT = "#87be69"
COLOR_KVD_DARK = "#273024"
COLOR_BG = "#f4f6f4"

FONT_BRAND = ("DejaVu Sans", 19, "bold")
FONT_SUB_BRAND = ("DejaVu Sans", 11)
FONT_CLOCK = ("DejaVu Sans", 20, "bold")
FONT_FOOTER = ("DejaVu Sans", 10)

okno.update_idletasks()
sirka_obrazovky = okno.winfo_screenwidth()
sirka_karty = (sirka_obrazovky // 2) - 80

# --- 1. INSTITUCIONÁLNÍ HLAVIČKA KVD ---
header = tkinter.Frame(okno, bg=COLOR_KVD_GREEN, height=86)
header.pack(fill="x")
header.pack_propagate(False)

brand_frame = tkinter.Frame(header, bg=COLOR_KVD_GREEN)
brand_frame.pack(side="left", padx=25, pady=(14, 10))

logo_icon = tkinter.Label(
    brand_frame, 
    text="101\n010", 
    font=("Courier", 11, "bold"), 
    bg="#ffffff", 
    fg=COLOR_KVD_GREEN, 
    padx=7, 
    pady=3
)
logo_icon.pack(side="left", padx=(0, 12))

brand_text_frame = tkinter.Frame(brand_frame, bg=COLOR_KVD_GREEN)
brand_text_frame.pack(side="left")

lbl_brand = tkinter.Label(brand_text_frame, text="KVD • FPE ZČU", font=FONT_BRAND, fg="#ffffff", bg=COLOR_KVD_GREEN)
lbl_brand.pack(anchor="w")

lbl_sub_brand = tkinter.Label(
    brand_text_frame, 
    text="Katedra výpočetní a didaktické techniky  |  Denní nabídka v okolí (data poskytla Meníčka.cz)", 
    font=FONT_SUB_BRAND, 
    fg="#d5eed0", 
    bg=COLOR_KVD_GREEN
)
lbl_sub_brand.pack(anchor="w")

meta_frame = tkinter.Frame(header, bg=COLOR_KVD_GREEN)
meta_frame.pack(side="right", padx=25, pady=(12, 10))

lbl_hodiny = tkinter.Label(meta_frame, text="", font=FONT_CLOCK, fg="#ffffff", bg=COLOR_KVD_GREEN)
lbl_hodiny.pack(anchor="e")

lbl_datum = tkinter.Label(meta_frame, text="", font=FONT_SUB_BRAND, fg="#eaf7e7", bg=COLOR_KVD_GREEN)
lbl_datum.pack(anchor="e", pady=(1, 4))

accent_stripe = tkinter.Frame(okno, bg=COLOR_KVD_ACCENT, height=4)
accent_stripe.pack(fill="x")

# --- 2. GRID KARET (2x2) ---
grid_container = tkinter.Frame(okno, bg=COLOR_BG)
grid_container.pack(fill="both", expand=True, padx=20, pady=15)

grid_container.grid_columnconfigure(0, weight=1, uniform="col")
grid_container.grid_columnconfigure(1, weight=1, uniform="col")
grid_container.grid_rowconfigure(0, weight=1, uniform="row")
grid_container.grid_rowconfigure(1, weight=1, uniform="row")

nazvy_podniku = ["Wintrovka", "Bistro Chodský", "U ševců", "Belvedere"]
souradnice = [(0, 0), (0, 1), (1, 0), (1, 1)]
karty = []

for i in range(4):
    r, c = souradnice[i]
    karta = RolovaciKarta(grid_container, nazvy_podniku[i], COLOR_KVD_GREEN, COLOR_KVD_DARK, sirka_karty)
    karta.card.grid(row=r, column=c, padx=12, pady=10, sticky="nsew")
    karty.append(karta)

# --- 3. PATIČKA ---
footer_frame = tkinter.Frame(okno, bg=COLOR_BG)
footer_frame.pack(fill="x", padx=30, pady=(0, 10))

lbl_status = tkinter.Label(footer_frame, text="● KVD Kiosek Online", font=FONT_FOOTER, fg="#386a24", bg=COLOR_BG)
lbl_status.pack(side="left")

lbl_aktualizace = tkinter.Label(footer_frame, text="Aktualizuji data...", font=FONT_FOOTER, fg="#6e786b", bg=COLOR_BG)
lbl_aktualizace.pack(side="right")

# --- 4. CHYBOVÝ OVERLAY PŘI VÝPADKU ---
warning_overlay = tkinter.Frame(okno, bg="#8f1d1d")
warning_box = tkinter.Frame(warning_overlay, bg="#ffffff", padx=45, pady=35, highlightbackground=COLOR_KVD_GREEN, highlightthickness=3)
warning_box.place(relx=0.5, rely=0.5, anchor="center")

tkinter.Label(warning_box, text="⚠️  VÝPADEK PŘIPOJENÍ", font=("DejaVu Sans", 24, "bold"), fg="#b91c1c", bg="#ffffff").pack(pady=(0, 12))
tkinter.Label(
    warning_box, 
    text="Kiosek nemá přístup k síti Internet.\nProbíhá automatický pokus o obnovení...", 
    font=("DejaVu Sans", 14), 
    fg=COLOR_KVD_DARK, 
    bg="#ffffff", 
    justify="center"
).pack()

# --- Časové a animační smyčky ---

def tick_hodiny():
    nyni = datetime.now()
    dny = ["Pondělí", "Úterý", "Středa", "Čtvrtek", "Pátek", "Sobota", "Neděle"]
    
    target = nyni + timedelta(days=1) if nyni.hour >= 14 else nyni
    target_den_nazev = dny[target.weekday()]
    
    if nyni.hour >= 14:
        lbl_datum.config(text=f"Nabídka na zítra: {target_den_nazev} {target.day}. {target.month}.")
    else:
        lbl_datum.config(text=f"Dnes je: {target_den_nazev} {target.day}. {target.month}.")
        
    lbl_hodiny.config(text=nyni.strftime("%H:%M:%S"))
    okno.after(1000, tick_hodiny)


def tick_animace():
    """Běží každých 40 ms (~25 fps) a plynule posouvá přeteklé texty."""
    for karta in karty:
        karta.krok_animace()
    okno.after(40, tick_animace)


def obnov_data():
    jidla, online = stahni_menu()
    nyni = datetime.now()
    
    if online:
        warning_overlay.place_forget()
        for i in range(4):
            karty[i].nastav_text(jidla[i])
        lbl_status.config(text="● KVD Kiosek Online", fg="#386a24")
        lbl_aktualizace.config(text=f"Poslední kontrola: {nyni.strftime('%H:%M')}")
    else:
        warning_overlay.place(relx=0, rely=0, relwidth=1, relheight=1)
        lbl_status.config(text="○ Bez připojení k síti", fg="#b91c1c")
        
    okno.after(60000, obnov_data)


tick_hodiny()
tick_animace()
obnov_data()
okno.mainloop()