from urllib.request import urlopen

from datetime import date, timedelta, datetime

import re

import tkinter 

import tkinter.ttk 

from time import sleep

#tes

import sys

import os


# check if 

if os.environ.get('DISPLAY','') == '':

    print('no display found. Using :0.0')

    os.environ.__setitem__('DISPLAY', ':0.0')

while(True):

    #Celé velké okno

    okno = tkinter.Tk()

    okno.attributes('-fullscreen', True)


    aktualnicas = datetime.now()


    #Labely v okně


    restaurace1 = tkinter.Label(okno, text = "Jídlena Wintrovka")

    restaurace2 = tkinter.Label(okno, text = "U Lízalky")

    restaurace3 = tkinter.Label(okno, text = "U Ševců")

    restaurace4 = tkinter.Label(okno, text = "Belvedere")


    restaurace1.grid(row=0, column= 0, sticky=tkinter.N, pady=2)

    restaurace1.config(font=("Comic Sans",16))

    restaurace2.grid(row=0, column= 1, sticky=tkinter.N, pady=2)

    restaurace2.config(font=("Comic Sans",16))

    restaurace3.grid(row=2, column= 0, sticky=tkinter.N, pady=2)

    restaurace3.config(font=("Comic Sans",16))

    restaurace4.grid(row=2, column= 1, sticky=tkinter.N, pady=2)

    restaurace4.config(font=("Comic Sans",16))


    today = date.today()


    if aktualnicas.hour >= 14:

        today = today + timedelta(1)


    zitrek = today + timedelta(1)

    DayNameZitra = zitrek.strftime("%A")

    datum = today.strftime("%d.%m.%Y")

    zitrek = zitrek.strftime("%d.%m.%Y")

    DayNameDatum = today.strftime("%A")


    """

    match DayNameDatum:

        case "Monday":

            DayNameDatum = "Pondělí"

        case "Tuesday":

            DayNameDatum = "Úterý"

        case "Wednesday":

            DayNameDatum = "Středa"

        case "Thursday":

            DayNameDatum = "Čtvrtek"

        case "Friday":

            DayNameDatum = "Pátek"

        case "Saturday":

            DayNameDatum = "Sobota"

        case "Sunday":

            DayNameDatum = "Neděle"

    """

    if DayNameDatum == "Monday":

        DayNameDatum = "Pondělí"

    elif DayNameDatum == "Tuesday":

        DayNameDatum = "Úterý"

    elif DayNameDatum == "Wednesday":

        DayNameDatum = "Středa"

    elif DayNameDatum == "Thursday":

        DayNameDatum = "Čtvrtek"

    elif DayNameDatum == "Friday":

        DayNameDatum = "Pátek"

    elif DayNameDatum == "Saturday":

        DayNameDatum = "Sobota"

    elif DayNameDatum == "Sunday":

        DayNameDatum = "Neděle"                    


    """

    match DayNameZitra:

        case "Monday":

            DayNameZitra = "Pondělí"

        case "Tuesday":

            DayNameZitra = "Úterý"

        case "Wednesday":

            DayNameZitra = "Středa"

        case "Thursday":

            DayNameZitra = "Čtvrtek"

        case "Friday":

            DayNameZitra = "Pátek"

        case "Saturday":

            DayNameZitra = "Sobota"

        case "Sunday":

            DayNameZitra = "Neděle"

    """

    if DayNameZitra == "Monday":

        DayNameZitra = "Pondělí"

    elif DayNameZitra == "Tueasday":

        DayNameZitra = "Úterý"

    elif DayNameZitra == "Wednesday":

        DayNameZitra = "Středa"

    elif DayNameZitra == "Thursday":

        DayNameZitra = "Čtvrtek"

    elif DayNameZitra == "Friday":

        DayNameZitra = "Pátek"

    elif DayNameZitra == "Saturday":

        DayNameZitra = "Sobota"

    elif DayNameZitra == "Sunday":

        DayNameZitra = "Neděle"


    if datum[0] == "0":

        datum = datum[1:]


    tecka_index=datum.find(".")


    if datum[tecka_index+1] == "0":

        datum = datum[:tecka_index+1]+datum[tecka_index+2:]


    if zitrek[0] == "0":

        zitrek = zitrek[1:]


    tecka_index=zitrek.find(".")


    if zitrek[tecka_index+1] == "0":

        zitrek = zitrek[:tecka_index+1]+zitrek[tecka_index+2:]    


    urls = ["https://menicka.cz/api/iframe/?id=5043","https://menicka.cz/api/iframe/?id=1461","https://menicka.cz/api/iframe/?id=1602","https://menicka.cz/api/iframe/?id=2115"]


    radek=1

    sloupec=0


    for i in range(0,len(urls)):

        url = urls[i]

        page = urlopen(url)


        #print(page)


        html_bytes = page.read()

        html = html_bytes.decode("windows-1250")


        #print(html)


        start_index = html.find(datum)

        #start_index = dnes_index# + len("datum")


        end_index = html.find(zitrek,start_index)

        if DayNameDatum == "Pondělí":

            end_index = end_index - len(zitrek)


        dnes = html[start_index:end_index]


        dnes = re.sub(datum, datum + " " + DayNameDatum, dnes)

        dnes = re.sub("&laquo; dnes", "", dnes)

        dnes= re.sub("<em.*?>","(",dnes)

        dnes= re.sub("</em>",")",dnes)

        dnes = re.sub("<.*?>","",dnes)

        dnes = re.sub(DayNameZitra,"", dnes)


        menu = tkinter.Label(okno,text=dnes, wraplength=900)

        menu.config(font=("Comic Sans",14))

        menu.grid(row=radek, column=sloupec, sticky=tkinter.N,pady=2)


        if sloupec == 0:

            sloupec = 1

        else:

            sloupec = 0


        if i == 1:

            radek =3


        print(dnes)


    cas = tkinter.Label(okno, text = "Aktualizováno : " + str(aktualnicas))

    cas.grid(row=4, column=0)


    NaObedSKVD = tkinter.Label(okno, text = "Kam na oběd s KVD?")

    NaObedSKVD.config(font=("Comic Sans",50))

    NaObedSKVD.grid(row=4, column=1)


    print(aktualnicas.hour)

    okno.after(3600000, lambda:okno.destroy())

    #okno.after(3000, lambda:okno.destroy())

    okno.mainloop()



"""from bs4 import BeautifulSoup #BeautifulSoup nepoužita, protože byl problém s alergeny a drsným odstraněním HTML tagů. Proto zvolen ruční postup. BeautifulSoup je vynikající na web scraping

from urllib.request import urlopen


urls = ["https://menicka.cz/api/iframe/?id=5043","https://menicka.cz/api/iframe/?id=1602","https://menicka.cz/api/iframe/?id=1461","https://menicka.cz/api/iframe/?id=2115"]

page = urlopen(urls[3])

html = page.read().decode("windows-1250")


soup = BeautifulSoup(html, "html.parser")


menu=soup.get_text() #parametr je separator

print(menu)


dnes_index = menu.find("« dnes")

start_index = dnes_index + len("« dnes")


dny = ["Pondělí", "Úterý", "Středa", "Čtvrtek", "Pátek", "Sobota", "Neděle"] #Snaha hledat prvek z pole

end_index = menu.find("Čtvrtek" or "Středa" or "Pátek" or "Sobota" or "Neděle" or "Pondělí" or "Úterý", dnes_index)


dnes = menu[start_index:end_index]


print("Dnešní menu je:" + dnes)

""" 