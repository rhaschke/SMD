#!/usr/bin/python3
# coding: utf8
# GUI for Race and team data receive and transmitt over CAN bus 0

import time
from datetime import datetime
import struct
import can
import os, sys
import binascii
from struct import unpack
from threading import Thread, Event
import tkinter as tk
import tkinter.font
import tkinter.messagebox
from PIL import Image, ImageTk
import sqlite3
import pandas as pd

event_1 = Event()  # Event CAN Send

noShift = 1
Text = 0


class input_race_GUI(Thread):
    def __init__(self, event_1):
        Thread.__init__(self)
        self.event_1 = event_1

    def run(self):
        global raceNumber
        global PointsTeam1
        global PointsTeam2
        global PointsTeam3
        raceNumber = 0
        PointsTeam1 = 0
        PointsTeam2 = 0
        PointsTeam3 = 0
        # Main window
        self.window1 = tk.Tk()
        self.window1.config(background="#FFFFFF")  # Background color of window
        self.window1.title("Solarcup Bahn Version 2.0")

        self.img1 = Image.open("logo.png")
        self.pic1 = ImageTk.PhotoImage(self.img1)

        self.checkDisqual1_1 = tk.StringVar()
        self.checkDisqual1_2 = tk.StringVar()
        self.checkDisqual1_3 = tk.StringVar()
        self.checkDisqual2_1 = tk.StringVar()
        self.checkDisqual2_2 = tk.StringVar()
        self.checkDisqual2_3 = tk.StringVar()
        self.checkDisqual3_1 = tk.StringVar()
        self.checkDisqual3_2 = tk.StringVar()
        self.checkDisqual3_3 = tk.StringVar()

        self.checkDisqual1_1.set("no")
        self.checkDisqual1_2.set("no")
        self.checkDisqual1_3.set("no")
        self.checkDisqual2_1.set("no")
        self.checkDisqual2_2.set("no")
        self.checkDisqual2_3.set("no")
        self.checkDisqual3_1.set("no")
        self.checkDisqual3_2.set("no")
        self.checkDisqual3_3.set("no")

        # Define Image
        vde_Logo1 = tk.PhotoImage(file="logo.png")
        self.logo1 = tk.Label(master=self.window1, image=vde_Logo1, background="#FFFFFF")
        smd_Logo1 = ImageTk.PhotoImage(self.img1)
        self.logo2 = tk.Label(master=self.window1, image=smd_Logo1, background="#FFFFFF")

        # Define label
        self.txtRaceClass = tk.Label(
            master=self.window1,
            text="Rennklasse: ",
            background="#FFFFFF",
            font="Arial 15 bold",
        )

        self.txtTeam1 = tk.Label(
            master=self.window1, text=" Team 1", background="#FFFFFF", font="Arial 15 bold"
        )
        self.txtTeam2 = tk.Label(
            master=self.window1, text=" Team 2", background="#FFFFFF", font="Arial 15 bold"
        )
        self.txtTeam3 = tk.Label(
            master=self.window1, text=" Team 3", background="#FFFFFF", font="Arial 15 bold"
        )

        self.txtBahn1 = tk.Label(
            master=self.window1, text="Bahn 1", background="#FFFFFF", font="Arial 22 bold"
        )
        self.txtBahn2 = tk.Label(
            master=self.window1, text="Bahn 2", background="#FFFFFF", font="Arial 22 bold"
        )
        self.txtBahn3 = tk.Label(
            master=self.window1, text="Bahn 3", background="#FFFFFF", font="Arial 22 bold"
        )

        self.txtRound1 = tk.Label(
            master=self.window1, text="Lauf 1", background="#FFFFFF", font="Arial 15 bold"
        )
        self.txtRound2 = tk.Label(
            master=self.window1, text="Lauf 2", background="#FFFFFF", font="Arial 15 bold"
        )
        self.txtRound3 = tk.Label(
            master=self.window1, text="Lauf 3", background="#FFFFFF", font="Arial 15 bold"
        )

        self.txtTime1 = tk.Label(
            master=self.window1,
            text="Zeiten: ",
            background="#FFFFFF",
            font="Arial 15 bold",
            fg="blue",
        )
        self.txtTime2 = tk.Label(
            master=self.window1,
            text="Zeiten: ",
            background="#FFFFFF",
            font="Arial 15 bold",
            fg="blue",
        )
        self.txtTime3 = tk.Label(
            master=self.window1,
            text="Zeiten: ",
            background="#FFFFFF",
            font="Arial 15 bold",
            fg="blue",
        )

        self.txtTeam = tk.Label(
            master=self.window1, text=" Team:", background="#FFFFFF", font="Arial 15 bold"
        )
        self.txtRaceNum = tk.Label(
            master=self.window1, text="Rennen:", background="#FFFFFF", font="Arial 15 bold"
        )
        self.txtPoints = tk.Label(
            master=self.window1,
            text="Punkte: ",
            background="#FFFFFF",
            font="Arial 15 bold",
            fg="green",
        )
        self.txtBestTime = tk.Label(
            master=self.window1,
            text="Best Zeit: ",
            background="#FFFFFF",
            font="Arial 15 bold",
            fg="green",
        )

        self.blank = tk.Label(master=self.window1, text="", background="#FFFFFF")
        self.crText = tk.Label(
            master=self.window1,
            text="Dipl.-Ing. Norbert Surowy, Version 0.9.4.0",
            background="#FFFFFF",
            font="Arial 8",
        )

        self.label_Timer1_1 = tk.Label(master=self.window1, font="Arial 15 bold")
        self.label_Timer2_1 = tk.Label(master=self.window1, font="Arial 15 bold")
        self.label_Timer3_1 = tk.Label(master=self.window1, font="Arial 15 bold")

        self.label_Timer1_2 = tk.Label(master=self.window1, font="Arial 15 bold")
        self.label_Timer2_2 = tk.Label(master=self.window1, font="Arial 15 bold")
        self.label_Timer3_2 = tk.Label(master=self.window1, font="Arial 15 bold")

        self.label_Timer1_3 = tk.Label(master=self.window1, font="Arial 15 bold")
        self.label_Timer2_3 = tk.Label(master=self.window1, font="Arial 15 bold")
        self.label_Timer3_3 = tk.Label(master=self.window1, font="Arial 15 bold")

        self.label_bestTimeTeam1 = tk.Label(
            master=self.window1, background="#FFFFFF", font="Arial 15 bold"
        )
        self.label_bestTimeTeam2 = tk.Label(
            master=self.window1, background="#FFFFFF", font="Arial 15 bold"
        )
        self.label_bestTimeTeam3 = tk.Label(
            master=self.window1, background="#FFFFFF", font="Arial 15 bold"
        )

        self.label_pTeam1 = tk.Label(
            master=self.window1, background="#FFFFFF", font="Arial 15 bold"
        )
        self.label_pTeam2 = tk.Label(
            master=self.window1, background="#FFFFFF", font="Arial 15 bold"
        )
        self.label_pTeam3 = tk.Label(
            master=self.window1, background="#FFFFFF", font="Arial 15 bold"
        )

        # Define entrys
        self.Team1 = tk.Entry(master=self.window1, font="Arial 15 bold")
        self.Team2 = tk.Entry(master=self.window1, font="Arial 15 bold")
        self.Team3 = tk.Entry(master=self.window1, font="Arial 15 bold")
        self.race1Team1 = tk.Entry(master=self.window1, font="Arial 15 bold")
        self.race1Team2 = tk.Entry(master=self.window1, font="Arial 15 bold")
        self.race1Team3 = tk.Entry(master=self.window1, font="Arial 15 bold")
        self.race2Team1 = tk.Entry(master=self.window1, font="Arial 15 bold")
        self.race2Team2 = tk.Entry(master=self.window1, font="Arial 15 bold")
        self.race2Team3 = tk.Entry(master=self.window1, font="Arial 15 bold")
        self.race3Team1 = tk.Entry(master=self.window1, font="Arial 15 bold")
        self.race3Team2 = tk.Entry(master=self.window1, font="Arial 15 bold")
        self.race3Team3 = tk.Entry(master=self.window1, font="Arial 15 bold")
        self.PointsTeam1 = tk.Entry(master=self.window1, font="Arial 15 bold")
        self.PointsTeam2 = tk.Entry(master=self.window1, font="Arial 15 bold")
        self.PointsTeam3 = tk.Entry(master=self.window1, font="Arial 15 bold")
        self.raceClass = tk.Entry(master=self.window1, font="Arial 15 bold")
        self.raceNum = tk.Entry(master=self.window1, font="Arial 15 bold")

        # Define buttons
        self.Ok = tk.Button(
            master=self.window1, text="Ok", command=self.race_x_Teams, font="Arial 12 bold"
        )
        self.Clear = tk.Button(
            master=self.window1,
            text="Clear all",
            command=self.clear_TeamOrderRace,
            font="Arial 12 bold",
        )
        self.race1 = tk.Button(
            master=self.window1,
            text="SEND",
            command=self.send_TeamOrderRace1,
            font="Arial 12 bold",
        )
        self.race2 = tk.Button(
            master=self.window1,
            text="SEND",
            command=self.send_TeamOrderRace2,
            font="Arial 12 bold",
        )
        self.race3 = tk.Button(
            master=self.window1,
            text="SEND",
            command=self.send_TeamOrderRace3,
            font="Arial 12 bold",
        )
        self.quit = tk.Button(
            master=self.window1, text="Quit", command=self.stop_All, font="Arial 12 bold"
        )
        self.applyData = tk.Button(
            master=self.window1,
            text="Daten übernehmen",
            command=self.apply_data,
            font="Arial 12 bold",
        )

        self.disqualRace1Team1 = tk.Checkbutton(
            master=self.window1,
            text="Disqualifikation",
            command=self.ena_disqualRace1Team1,
            variable=self.checkDisqual1_1,
            offvalue="no",
            onvalue="yes",
            background="#FFFFFF",
            font="Arial 10",
        )
        self.disqualRace1Team2 = tk.Checkbutton(
            master=self.window1,
            text="Disqualifikation",
            command=self.ena_disqualRace1Team2,
            variable=self.checkDisqual1_2,
            onvalue="yes",
            offvalue="no",
            background="#FFFFFF",
            font="Arial 10",
        )
        self.disqualRace1Team3 = tk.Checkbutton(
            master=self.window1,
            text="Disqualifikation",
            command=self.ena_disqualRace1Team3,
            variable=self.checkDisqual1_3,
            onvalue="yes",
            offvalue="no",
            background="#FFFFFF",
            font="Arial 10",
        )
        self.disqualRace2Team1 = tk.Checkbutton(
            master=self.window1,
            text="Disqualifikation",
            command=self.ena_disqualRace2Team1,
            variable=self.checkDisqual2_1,
            onvalue="yes",
            offvalue="no",
            background="#FFFFFF",
            font="Arial 10",
        )
        self.disqualRace2Team2 = tk.Checkbutton(
            master=self.window1,
            text="Disqualifikation",
            command=self.ena_disqualRace2Team2,
            variable=self.checkDisqual2_2,
            onvalue="yes",
            offvalue="no",
            background="#FFFFFF",
            font="Arial 10",
        )
        self.disqualRace2Team3 = tk.Checkbutton(
            master=self.window1,
            text="Disqualifikation",
            command=self.ena_disqualRace2Team3,
            variable=self.checkDisqual2_3,
            onvalue="yes",
            offvalue="no",
            background="#FFFFFF",
            font="Arial 10",
        )
        self.disqualRace3Team1 = tk.Checkbutton(
            master=self.window1,
            text="Disqualifikation",
            command=self.ena_disqualRace3Team1,
            variable=self.checkDisqual3_1,
            onvalue="yes",
            offvalue="no",
            background="#FFFFFF",
            font="Arial 10",
        )
        self.disqualRace3Team2 = tk.Checkbutton(
            master=self.window1,
            text="Disqualifikation",
            command=self.ena_disqualRace3Team2,
            variable=self.checkDisqual3_2,
            onvalue="yes",
            offvalue="no",
            background="#FFFFFF",
            font="Arial 10",
        )
        self.disqualRace3Team3 = tk.Checkbutton(
            master=self.window1,
            text="Disqualifikation",
            command=self.ena_disqualRace3Team3,
            variable=self.checkDisqual3_3,
            onvalue="yes",
            offvalue="no",
            background="#FFFFFF",
            font="Arial 10",
        )

        # packen der Widgets mit grid Methode
        self.logo1.place(x=600, y=0, width=350, height=110)
        self.logo2.place(x=100, y=0, width=350, height=110)
        self.blank.grid(column=1, row=0, pady=70)

        self.txtRaceClass.grid(column=1, row=3, pady=1)
        self.raceClass.grid(column=2, row=3)
        self.txtRaceNum.grid(column=5, row=3, pady=1)
        self.raceNum.grid(column=6, row=3)

        self.txtTeam1.grid(column=1, row=6, pady=15)
        self.Team1.grid(column=2, row=6)
        self.txtTeam2.grid(column=3, row=6)
        self.Team2.grid(column=4, row=6)
        self.txtTeam3.grid(column=5, row=6)
        self.Team3.grid(column=6, row=6)
        self.Ok.grid(column=7, row=6)
        #        self.Clear.grid(column=7, row=7)

        self.txtBahn1.grid(column=2, row=10, pady=7)
        self.txtBahn2.grid(column=4, row=10)
        self.txtBahn3.grid(column=6, row=10)

        self.txtRound1.grid(column=1, row=13, pady=7)
        self.race1Team1.grid(column=2, row=13)
        self.race1Team2.grid(column=4, row=13)
        self.race1Team3.grid(column=6, row=13)
        self.race1.grid(column=7, row=13)

        self.txtTime1.grid(column=1, row=16)
        self.label_Timer1_1.grid(column=2, row=16)
        self.label_Timer2_1.grid(column=4, row=16)
        self.label_Timer3_1.grid(column=6, row=16)

        self.disqualRace1Team1.grid(column=2, row=17)
        self.disqualRace1Team2.grid(column=4, row=17)
        self.disqualRace1Team3.grid(column=6, row=17)

        self.txtRound2.grid(column=1, row=19, pady=15)
        self.race2Team1.grid(column=2, row=19)
        self.race2Team2.grid(column=4, row=19)
        self.race2Team3.grid(column=6, row=19)
        self.race2.grid(column=7, row=19)

        self.txtTime2.grid(column=1, row=22)
        self.label_Timer1_2.grid(column=2, row=22)
        self.label_Timer2_2.grid(column=4, row=22)
        self.label_Timer3_2.grid(column=6, row=22)

        self.disqualRace2Team1.grid(column=2, row=23)
        self.disqualRace2Team2.grid(column=4, row=23)
        self.disqualRace2Team3.grid(column=6, row=23)

        self.txtRound3.grid(column=1, row=25, pady=15)
        self.race3Team1.grid(column=2, row=25)
        self.race3Team2.grid(column=4, row=25)
        self.race3Team3.grid(column=6, row=25)
        self.race3.grid(column=7, row=25)

        self.txtTime3.grid(column=1, row=28)
        self.label_Timer1_3.grid(column=2, row=28)
        self.label_Timer2_3.grid(column=4, row=28)
        self.label_Timer3_3.grid(column=6, row=28)

        self.disqualRace3Team1.grid(column=2, row=29, pady=15)
        self.disqualRace3Team2.grid(column=4, row=29)
        self.disqualRace3Team3.grid(column=6, row=29)

        self.txtTeam.grid(column=1, row=30, pady=1)
        self.label_pTeam1.grid(column=2, row=30)
        self.label_pTeam2.grid(column=4, row=30)
        self.label_pTeam3.grid(column=6, row=30)

        self.txtBestTime.grid(column=1, row=31, pady=1)
        self.label_bestTimeTeam1.grid(column=2, row=31)
        self.label_bestTimeTeam2.grid(column=4, row=31)
        self.label_bestTimeTeam3.grid(column=6, row=31)

        self.txtPoints.grid(column=1, row=32, pady=1)
        self.PointsTeam1.grid(column=2, row=32)
        self.PointsTeam2.grid(column=4, row=32)
        self.PointsTeam3.grid(column=6, row=32)

        self.applyData.grid(column=4, row=35, pady=10)
        self.Clear.grid(column=7, row=35, pady=10)
        self.crText.grid(column=6, row=40, pady=20)

        self.quit.grid(column=7, row=40)

        self.label_bestTimeTeam1.config(text=str(bestTimeTeam1))
        self.label_bestTimeTeam1.after(100, self.bestTimeTeam1_label)
        self.label_bestTimeTeam2.config(text=str(bestTimeTeam2))
        self.label_bestTimeTeam2.after(100, self.bestTimeTeam2_label)
        self.label_bestTimeTeam3.config(text=str(bestTimeTeam3))
        self.label_bestTimeTeam3.after(100, self.bestTimeTeam3_label)

        self.label_pTeam1.config(text=str(self.raceClass.get()) + str(self.Team1.get()))
        self.label_pTeam1.after(100, self.pTeam1_label)
        self.label_pTeam2.config(text=str(self.raceClass.get()) + str(self.Team2.get()))
        self.label_pTeam2.after(100, self.pTeam2_label)
        self.label_pTeam3.config(text=str(self.raceClass.get()) + str(self.Team3.get()))
        self.label_pTeam3.after(100, self.pTeam3_label)

        self.label_Timer1_1.config(text=str(Timer1_1))
        self.label_Timer1_1.after(100, self.timer1_1_label)
        self.label_Timer2_1.config(text=str(Timer2_1))
        self.label_Timer2_1.after(100, self.timer2_1_label)
        self.label_Timer3_1.config(text=str(Timer3_1))
        self.label_Timer3_1.after(100, self.timer3_1_label)

        self.label_Timer1_2.config(text=str(Timer1_2))
        self.label_Timer1_2.after(100, self.timer1_2_label)
        self.label_Timer2_2.config(text=str(Timer2_2))
        self.label_Timer2_2.after(100, self.timer2_2_label)
        self.label_Timer3_2.config(text=str(Timer3_2))
        self.label_Timer3_2.after(100, self.timer3_2_label)

        self.label_Timer1_3.config(text=str(Timer1_3))
        self.label_Timer1_3.after(100, self.timer1_3_label)
        self.label_Timer2_3.config(text=str(Timer2_3))
        self.label_Timer2_3.after(100, self.timer2_3_label)
        self.label_Timer3_3.config(text=str(Timer3_3))
        self.label_Timer3_3.after(100, self.timer3_3_label)

        #        self.teamResult()
        self.raceNum.delete(0, tk.END)
        self.raceNum.insert(0, raceNumber)
        self.PointsTeam1.delete(0, tk.END)
        self.PointsTeam1.insert(0, PointsTeam1)
        self.PointsTeam2.delete(0, tk.END)
        self.PointsTeam2.insert(0, PointsTeam2)
        self.PointsTeam3.delete(0, tk.END)
        self.PointsTeam3.insert(0, PointsTeam3)

        # display main window
        self.window1.mainloop()

    # Fill all fields with team numbers
    def race_x_Teams(self):

        global Team1
        global Team2
        global Team3
        global dispTeam1
        global dispTeam2
        global dispTeam3
        global raceClass
        Team1 = ()
        Team2 = ()
        Team3 = ()
        Team1 = str(self.Team1.get())
        Team2 = str(self.Team2.get())
        Team3 = str(self.Team3.get())
        raceClass = " %s" % str(self.raceClass.get())

        # If team number "-" set "---"
        if (Team1) == "-":
            Team1 = "---"
        if (Team2) == "-":
            Team2 = "---"
        if (Team3) == "-":
            Team3 = "---"

        if len(Team1) >= 2:
            dispTeam1 = "%s" % (raceClass + str(Team1))
        else:
            dispTeam1 = "%s^" % (raceClass + str(Team1))
        if len(Team2) >= 2:
            dispTeam2 = "%s" % (raceClass + str(Team2))
        else:
            dispTeam2 = "%s^" % (raceClass + str(Team2))
        if len(Team3) >= 2:
            dispTeam3 = "%s" % (raceClass + str(Team3))
        else:
            dispTeam3 = "%s^" % (raceClass + str(Team3))

        self.race1Team1.delete(0, tk.END)
        self.race1Team2.delete(0, tk.END)
        self.race1Team3.delete(0, tk.END)
        self.race2Team1.delete(0, tk.END)
        self.race2Team2.delete(0, tk.END)
        self.race2Team3.delete(0, tk.END)
        self.race3Team1.delete(0, tk.END)
        self.race3Team2.delete(0, tk.END)
        self.race3Team3.delete(0, tk.END)

        if (Team3) == "---":
            self.race1Team1.insert(0, raceClass + str(Team1))
            self.race1Team2.insert(0, str(Team3))
            self.race1Team3.insert(0, raceClass + str(Team2))
            self.race2Team1.insert(0, raceClass + str(Team2))
            self.race2Team2.insert(0, str(Team3))
            self.race2Team3.insert(0, raceClass + str(Team1))
            self.race3Team1.insert(0, str(Team3))
            self.race3Team2.insert(0, str(Team3))
            self.race3Team3.insert(0, str(Team3))
        else:
            self.race1Team1.insert(0, raceClass + str(Team1))
            self.race1Team2.insert(0, raceClass + str(Team2))
            self.race1Team3.insert(0, raceClass + str(Team3))
            self.race2Team1.insert(0, raceClass + str(Team3))
            self.race2Team2.insert(0, raceClass + str(Team1))
            self.race2Team3.insert(0, raceClass + str(Team2))
            self.race3Team1.insert(0, raceClass + str(Team2))
            self.race3Team2.insert(0, raceClass + str(Team3))
            self.race3Team3.insert(0, raceClass + str(Team1))

        self.txtRound1["fg"] = "black"
        self.txtRound2["fg"] = "black"
        self.txtRound3["fg"] = "black"
        self.race1Team1["fg"] = "black"
        self.race1Team2["fg"] = "black"
        self.race1Team3["fg"] = "black"
        self.race2Team1["fg"] = "black"
        self.race2Team2["fg"] = "black"
        self.race2Team3["fg"] = "black"
        self.race3Team1["fg"] = "black"
        self.race3Team2["fg"] = "black"
        self.race3Team3["fg"] = "black"

    # Clear all fields
    def clear_TeamOrderRace(self):
        global textToSendFront
        global textToSendBack
        global canIdText
        global raceClass
        global Timer1_1
        global Timer2_1
        global Timer3_1
        global Timer1_2
        global Timer2_2
        global Timer3_2
        global Timer1_3
        global Timer2_3
        global Timer3_3
        global bestTimeTeam1
        global bestTimeTeam2
        global bestTimeTeam3

        Timer1_1 = 0
        Timer2_1 = 0
        Timer3_1 = 0
        Timer1_2 = 0
        Timer2_2 = 0
        Timer3_2 = 0
        Timer1_3 = 0
        Timer2_3 = 0
        Timer3_3 = 0
        bestTimeTeam1 = 0
        bestTimeTeam2 = 0
        bestTimeTeam3 = 0

        # self.raceClass.delete(0, len(self.raceClass.get()) )
        self.Team1.delete(0, len(self.Team1.get()))
        self.Team2.delete(0, len(self.Team2.get()))
        self.Team3.delete(0, len(self.Team3.get()))
        self.race1Team1.delete(0, len(self.race1Team1.get()))
        self.race1Team2.delete(0, len(self.race1Team2.get()))
        self.race1Team3.delete(0, len(self.race1Team3.get()))
        self.race2Team1.delete(0, len(self.race2Team1.get()))
        self.race2Team2.delete(0, len(self.race2Team2.get()))
        self.race2Team3.delete(0, len(self.race2Team3.get()))
        self.race3Team1.delete(0, len(self.race3Team1.get()))
        self.race3Team2.delete(0, len(self.race3Team2.get()))
        self.race3Team3.delete(0, len(self.race3Team3.get()))

        self.txtRound1["fg"] = "black"
        self.txtRound2["fg"] = "black"
        self.txtRound3["fg"] = "black"
        self.race1Team1["fg"] = "black"
        self.race1Team2["fg"] = "black"
        self.race1Team3["fg"] = "black"
        self.race2Team1["fg"] = "black"
        self.race2Team2["fg"] = "black"
        self.race2Team3["fg"] = "black"
        self.race3Team1["fg"] = "black"
        self.race3Team2["fg"] = "black"
        self.race3Team3["fg"] = "black"

        textToSendFront = " Bahn 1 | Bahn 2 | Bahn 3"
        canIdText = 0x1FFBEC00  # set CAN Bus ID for send text to signal controller
        self.event_1.set()
        self.event_1.clear()
        time.sleep(0.3)  # wait for send all data ready
        textToSendBack = " Bahn 3 | Bahn 2 | Bahn 1"
        canIdText = 0x1FFBEC10  # set CAN Bus ID for send text to signal controller
        self.event_1.set()
        self.event_1.clear()

    def send_RaceClass(self):
        global raceClass
        raceClass = str(self.raceClass.get())

    def send_TeamOrderRace1(self):
        global blockClock2
        global textToSendFront
        global textToSendBack
        global canIdText
        global TimeRace

        TimeRace = 1
        self.txtRound1["fg"] = "red"
        self.txtRound2["fg"] = "black"
        self.txtRound3["fg"] = "black"
        self.race1Team1["fg"] = "red"
        self.race1Team2["fg"] = "red"
        self.race1Team3["fg"] = "red"
        self.race2Team1["fg"] = "black"
        self.race2Team2["fg"] = "black"
        self.race2Team3["fg"] = "black"
        self.race3Team1["fg"] = "black"
        self.race3Team2["fg"] = "black"
        self.race3Team3["fg"] = "black"

        if (Team3) == "---":
            canIdText = 0x1FFB6200  # set CAN Bus ID for send block clock2
            blockClock2 = 1
            self.event_1.set()
            self.event_1.clear()
            time.sleep(0.2)  # wait for send all data ready
        else:
            canIdText = 0x1FFB6200  # set CAN Bus ID for send block clock2
            blockClock2 = 0
            self.event_1.set()
            self.event_1.clear()
            time.sleep(0.2)  # wait for send all data ready

        setTextSpacer1 = "^%s^" % (dispTeam1)
        if (Team3) == "---":
            setTextSpacer2 = "^%s- ^" % (Team3)
            setTextSpacer3 = "^%s^" % (dispTeam2)
        else:
            setTextSpacer2 = "^%s^" % (dispTeam2)
            setTextSpacer3 = "^%s^" % (dispTeam3)

        canIdText = 0x1FFBEC00  # set CAN Bus ID for send text to signal controller
        textToSendFront = "%s|%s|%s" % (setTextSpacer1, setTextSpacer2, setTextSpacer3)
        self.event_1.set()
        self.event_1.clear()
        time.sleep(0.2)  # wait for send all data ready
        canIdText = 0x1FFBEC10  # set CAN Bus ID for send text to signal controller
        textToSendBack = "%s|%s|%s" % (setTextSpacer3, setTextSpacer2, setTextSpacer1)
        self.event_1.set()
        self.event_1.clear()

    def send_TeamOrderRace2(self):
        global textToSendFront
        global textToSendBack
        global canIdText
        global TimeRace
        global blockClock2
        TimeRace = 2
        self.txtRound1["fg"] = "black"
        self.txtRound2["fg"] = "red"
        self.txtRound3["fg"] = "black"
        self.race1Team1["fg"] = "black"
        self.race1Team2["fg"] = "black"
        self.race1Team3["fg"] = "black"
        self.race2Team1["fg"] = "red"
        self.race2Team2["fg"] = "red"
        self.race2Team3["fg"] = "red"
        self.race3Team1["fg"] = "black"
        self.race3Team2["fg"] = "black"
        self.race3Team3["fg"] = "black"

        if (Team3) == "---":
            canIdText = 0x1FFB6200  # set CAN Bus ID for send block clock2
            blockClock2 = 1
            self.event_1.set()
            self.event_1.clear()
            time.sleep(0.2)  # wait for send all data ready
        else:
            canIdText = 0x1FFB6200  # set CAN Bus ID for send block clock2
            blockClock2 = 0
            self.event_1.set()
            self.event_1.clear()
            time.sleep(0.2)  # wait for send all data ready

        setTextSpacer1 = "^%s^" % (dispTeam2)
        if (Team3) == "---":
            setTextSpacer1 = "^%s^" % (dispTeam2)
            setTextSpacer2 = "^%s- ^" % (Team3)
            setTextSpacer3 = "^%s^" % (dispTeam1)
        else:
            setTextSpacer1 = "^%s^" % (dispTeam3)
            setTextSpacer2 = "^%s^" % (dispTeam1)
            setTextSpacer3 = "^%s^" % (dispTeam2)

        canIdText = 0x1FFBEC00  # set CAN Bus ID for send text to signal controller
        textToSendFront = "%s|%s|%s" % (setTextSpacer1, setTextSpacer2, setTextSpacer3)
        self.event_1.set()
        self.event_1.clear()
        time.sleep(0.2)  # wait for send all data ready
        canIdText = 0x1FFBEC10  # set CAN Bus ID for send text to signal controller
        textToSendBack = "%s|%s|%s" % (setTextSpacer3, setTextSpacer2, setTextSpacer1)
        self.event_1.set()
        self.event_1.clear()

    def send_TeamOrderRace3(self):
        global textToSendFront
        global textToSendBack
        global canIdText
        global TimeRace
        TimeRace = 3
        #        self.txtRace1["fg"] = "black"
        self.txtRound1["fg"] = "black"
        self.txtRound2["fg"] = "black"
        self.txtRound3["fg"] = "red"
        self.race1Team1["fg"] = "black"
        self.race1Team2["fg"] = "black"
        self.race1Team3["fg"] = "black"
        self.race2Team1["fg"] = "black"
        self.race2Team2["fg"] = "black"
        self.race2Team3["fg"] = "black"
        self.race3Team1["fg"] = "red"
        self.race3Team2["fg"] = "red"
        self.race3Team3["fg"] = "red"

        if (Team3) == "---":
            setTextSpacer1 = "^%s- ^" % (Team3)
            setTextSpacer2 = "^%s- ^" % (Team3)
            setTextSpacer3 = "^%s- ^" % (Team3)
        else:
            setTextSpacer1 = "^%s^" % (dispTeam2)
            setTextSpacer2 = "^%s^" % (dispTeam3)
            setTextSpacer3 = "^%s^" % (dispTeam1)

        canIdText = 0x1FFBEC00  # set CAN Bus ID for send text to signal controller
        textToSendFront = "%s|%s|%s" % (setTextSpacer1, setTextSpacer2, setTextSpacer3)
        self.event_1.set()
        self.event_1.clear()
        time.sleep(0.2)  # wait for send all data ready
        canIdText = 0x1FFBEC10  # set CAN Bus ID for send text to signal controller
        textToSendBack = "%s|%s|%s" % (setTextSpacer3, setTextSpacer2, setTextSpacer1)
        self.event_1.set()
        self.event_1.clear()

    # Evaluate disqualification
    def ena_disqualRace1Team1(self):
        if (self.checkDisqual1_1.get()) == "yes":
            Timer1_1 = 888

    def ena_disqualRace1Team2(self):
        if (self.checkDisqual1_2.get()) == "yes":
            Timer1_2 = 888

    def ena_disqualRace1Team3(self):
        if (self.checkDisqual1_3.get()) == "yes":
            Timer1_3 = 888

    def ena_disqualRace2Team1(self):
        if (self.checkDisqual2_1.get()) == "yes":
            Timer2_1 = 888

    def ena_disqualRace2Team2(self):
        if (self.checkDisqual2_2.get()) == "yes":
            Timer2_2 = 888

    def ena_disqualRace2Team3(self):
        if (self.checkDisqual2_3.get()) == "yes":
            Timer2_3 = 888

    def ena_disqualRace3Team1(self):
        if (self.checkDisqual3_1.get()) == "yes":
            Timer3_1 = 888

    def ena_disqualRace3Team2(self):
        if (self.checkDisqual3_2.get()) == "yes":
            Timer3_2 = 888

    def ena_disqualRace3Team3(self):
        if (self.checkDisqual3_3.get()) == "yes":
            Timer3_3 = 888

    # Refresch Field Point and Best Time
    def bestTimeTeam1_label(self):
        def label():
            self.label_bestTimeTeam1.config(
                text="%.2f s" % bestTimeTeam1, font="Arial 15 bold", fg="red"
            )
            self.label_bestTimeTeam1.after(100, label)

        label()

    def bestTimeTeam2_label(self):
        def label():
            self.label_bestTimeTeam2.config(
                text="%.2f s" % bestTimeTeam2, font="Arial 15 bold", fg="red"
            )
            self.label_bestTimeTeam2.after(100, label)

        label()

    def bestTimeTeam3_label(self):
        def label():
            if (str(self.Team3.get())) == "-":
                self.label_bestTimeTeam3.config(text="---")
                self.label_bestTimeTeam3.after(100, label)
            else:
                self.label_bestTimeTeam3.config(
                    text="%.2f s" % bestTimeTeam3, font="Arial 15 bold", fg="red"
                )
                self.label_bestTimeTeam3.after(100, label)

        label()

    def pTeam1_label(self):
        def label():
            self.label_pTeam1.config(
                text=str(self.raceClass.get()) + str(self.Team1.get()),
                font="Arial 15 bold",
                fg="black",
            )
            self.label_pTeam1.after(100, label)

        label()

    def pTeam2_label(self):
        def label():
            self.label_pTeam2.config(
                text=str(self.raceClass.get()) + str(self.Team2.get()),
                font="Arial 15 bold",
                fg="black",
            )
            self.label_pTeam2.after(100, label)

        label()

    def pTeam3_label(self):
        def label():
            if (str(self.Team3.get())) == "-":
                self.label_pTeam3.config(text="")
                self.label_pTeam3.after(100, label)
            else:
                self.label_pTeam3.config(
                    text=str(self.raceClass.get()) + str(self.Team3.get()),
                    font="Arial 15 bold",
                    fg="black",
                )
                self.label_pTeam3.after(100, label)

        label()

    # Refresh Timer fields
    def timer1_1_label(self):
        def label():
            self.label_Timer1_1.config(
                text="%.2f s" % Timer1_1, font="Arial 28 bold", fg="blue"
            )
            self.label_Timer1_1.after(100, label)

        label()

    def timer2_1_label(self):
        def label():
            self.label_Timer2_1.config(
                text="%.2f s" % Timer2_1, font="Arial 28 bold", fg="blue"
            )
            self.label_Timer2_1.after(100, label)

        label()

    def timer3_1_label(self):
        def label():
            self.label_Timer3_1.config(
                text="%.2f s" % Timer3_1, font="Arial 28 bold", fg="blue"
            )
            self.label_Timer3_1.after(100, label)

        label()

    def timer1_2_label(self):
        def label():
            self.label_Timer1_2.config(
                text="%.2f s" % Timer1_2, font="Arial 28 bold", fg="blue"
            )
            self.label_Timer1_2.after(100, label)

        label()

    def timer2_2_label(self):
        def label():
            self.label_Timer2_2.config(
                text="%.2f s" % Timer2_2, font="Arial 28 bold", fg="blue"
            )
            self.label_Timer2_2.after(100, label)

        label()

    def timer3_2_label(self):
        def label():
            self.label_Timer3_2.config(
                text="%.2f s" % Timer3_2, font="Arial 28 bold", fg="blue"
            )
            self.label_Timer3_2.after(100, label)

        label()

    def timer1_3_label(self):
        def label():
            self.label_Timer1_3.config(
                text="%.2f s" % Timer1_3, font="Arial 28 bold", fg="blue"
            )
            self.label_Timer1_3.after(100, label)

        label()

    def timer2_3_label(self):
        def label():
            self.label_Timer2_3.config(
                text="%.2f s" % Timer2_3, font="Arial 28 bold", fg="blue"
            )
            self.label_Timer2_3.after(100, label)

        label()

    def timer3_3_label(self):
        def label():
            self.label_Timer3_3.config(
                text="%.2f s" % Timer3_3, font="Arial 28 bold", fg="blue"
            )
            self.label_Timer3_3.after(100, label)

        label()

    def apply_data(self):

        global raceNumber
        now = datetime.now()
        connection = sqlite3.connect(databaseName)
        connection.execute(
            "INSERT INTO Race VALUES(?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)",
            (
                int(self.raceNum.get()),
                now.strftime("%d/%m/%Y %H:%M:%S"),
                str(self.raceClass.get()),
                (raceClass + Team1),
                Timer1_1,
                (raceClass + Team2),
                Timer2_1,
                (raceClass + Team3),
                Timer3_1,
                (raceClass + Team3),
                Timer1_2,
                (raceClass + Team1),
                Timer2_2,
                (raceClass + Team2),
                Timer3_2,
                (raceClass + Team2),
                Timer1_3,
                (raceClass + Team3),
                Timer2_3,
                (raceClass + Team1),
                Timer3_3,
                int(self.PointsTeam1.get()),
                int(self.PointsTeam2.get()),
                int(self.PointsTeam3.get()),
            ),
        )
        connection.commit()
        connection.close()
        raceNumber = int(self.raceNum.get()) + 1
        self.raceNum.delete(0, tk.END)
        self.raceNum.insert(0, raceNumber)

    # Teminate all threats
    def stop_All(self):
        global textToSendFront
        global canIdText
        self.window1.destroy()
        # stop()
        canIdText = 0x1FFBEB00  # set CAN Bus ID for send text to signal controller
        textToSendFront = "Ende"
        self.event_1.set()
        self.event_1.clear()


class calculate_time_Points(Thread):
    def __init__(self, running):
        Thread.__init__(self)
        self.running = running

    def run(self):
        global timeRecieved
        global bestTimeTeam1
        global bestTimeTeam2
        global bestTimeTeam3
        bestTimeTeam1 = 0
        bestTimeTeam2 = 0
        bestTimeTeam3 = 0

        timeRecieved = 0

        while self.running:
            time.sleep(0.1)
            if Timer1_1 > 0:
                timeRecieved = 1
                bestTimeTeam1 = Timer1_1
            if Timer2_1 > 0:
                timeRecieved = 1
                bestTimeTeam2 = Timer2_1
            if Timer3_1 > 0:
                timeRecieved = 1
                if Team3 == "---":
                    bestTimeTeam2 = Timer3_1
                else:
                    bestTimeTeam3 = Timer3_1

            if Timer1_2 > 0:
                timeRecieved = 1
                if Team3 == "---":
                    if Timer1_2 < bestTimeTeam2:
                        bestTimeTeam2 = Timer1_2
                else:
                    if Timer1_2 < bestTimeTeam3:
                        bestTimeTeam3 = Timer1_2
            if Timer2_2 > 0:
                timeRecieved = 1
                if Timer2_2 < bestTimeTeam1:
                    bestTimeTeam1 = Timer2_2
            if Timer3_2 > 0:
                timeRecieved = 1
                if Team3 == "---":
                    if Timer3_2 < bestTimeTeam1:
                        bestTimeTeam1 = Timer3_2
                else:
                    if Timer3_2 < bestTimeTeam2:
                        bestTimeTeam2 = Timer3_2

            if Timer1_3 > 0:
                timeRecieved = 1
                if Timer1_3 < bestTimeTeam2:
                    bestTimeTeam2 = Timer1_3
            if Timer2_3 > 0:
                timeRecieved = 1
                if Timer2_3 < bestTimeTeam3:
                    bestTimeTeam3 = Timer2_3
            if Timer3_3 > 0:
                timeRecieved = 1
                if Timer3_3 < bestTimeTeam1:
                    bestTimeTeam1 = Timer3_3

    def stop(self):
        self._is_running = False


# Class GUI controller data, brigthness, timer control and more
class input_control_GUI(Thread):
    def __init__(self, event_1):
        Thread.__init__(self)
        self.event_1 = event_1

    def run(self):

        # Main window
        self.window2 = tk.Tk()
        self.window2.config(background="#FFFFFF")  # Background color of window
        self.window2.title("Solarcup Bahn Version 2.0 Controll Parameter")

        # Define Image
        # vde_Logo2 = tk.PhotoImage(file="/home/VDE/workspace/pictures/vde-logo-bild_2.png")
        # self.logo2 = tk.Label(master=self.window2, image=vde_Logo2)

        # Define label

        self.txtHead = tk.Label(
            master=self.window2,
            text="Parameter für Display und Timer Controller",
            background="#FFFFFF",
            font="Arial 15 bold",
        )

        self.txtSetRaceDatabase = tk.Label(
            master=self.window2,
            text="Datenbank für Rennen anlegen",
            background="#FFFFFF",
            font="Arial 15 bold",
        )

        self.txtExportDatabaseToCSV = tk.Label(
            master=self.window2,
            text="Datenbank in CSV Datei expotieren",
            background="#FFFFFF",
            font="Arial 15 bold",
        )

        self.txtBrightness = tk.Label(
            master=self.window2,
            text="Helligkeit Display: (0 - 15)",
            background="#FFFFFF",
            font="Arial 15 bold",
            fg="green",
        )
        self.txtSensivity = tk.Label(
            master=self.window2,
            text="Sensor Empflichkeit: (0 - 10, (max = 0) )",
            background="#FFFFFF",
            font="Arial 15 bold",
            fg="red",
        )
        self.txtBlockSensorTime = tk.Label(
            master=self.window2,
            text="Sensor block (sec): (default = 4 sec)",
            background="#FFFFFF",
            font="Arial 15 bold",
            fg="blue",
        )

        self.txtStatus = tk.Label(
            master=self.window2,
            text="Status Time Controller",
            background="#FFFFFF",
            font="Arial 15 bold",
            fg="orange",
        )
        self.txtReset = tk.Label(
            master=self.window2,
            text="Reset Controller",
            background="#FFFFFF",
            font="Arial 15 bold",
            fg="blue",
        )

        self.txtDisplayTime = tk.Label(
            master=self.window2,
            text="Time on MD ON/OFF",
            background="#FFFFFF",
            font="Arial 15 bold",
            fg="blue",
        )
        self.txtCountDown = tk.Label(
            master=self.window2,
            text="Countdown ON/OFF",
            background="#FFFFFF",
            font="Arial 15 bold",
            fg="blue",
        )

        self.blank = tk.Label(master=self.window2, text=" ", background="#FFFFFF")
        self.crText = tk.Label(
            master=self.window2,
            text="Dipl.-Ing. Norbert Surowy, Version 0.9.4.0",
            background="#FFFFFF",
            font="Arial 8",
        )

        self.txtText1 = tk.Label(
            master=self.window2,
            text="Display Text: ",
            background="#FFFFFF",
            font="Arial 15 bold",
        )
        self.txtRounds = tk.Label(
            master=self.window2,
            text="Durchläufe: ",
            background="#FFFFFF",
            font="Arial 15 bold",
        )

        # Define entrys

        self.raceDatabase = tk.Entry(master=self.window2, font="Arial 15 bold")
        self.sensivity = tk.Entry(master=self.window2, font="Arial 15 bold")
        self.brightness = tk.Entry(master=self.window2, font="Arial 15 bold")
        self.blockSensorTime = tk.Entry(master=self.window2, font="Arial 15 bold")
        # self.rad1 = tk.Radiobutton(master=self.window,text="2", value=2)
        # self.rad2 = tk.Radiobutton(master=self.window,text="4", value=4)
        self.displayText = tk.Entry(master=self.window2, font="Arial 15 bold")
        self.rounds = tk.Entry(master=self.window2, font="Arial 15 bold")

        # Define buttons
        self.createRaceDatabase = tk.Button(
            master=self.window2,
            text="Create",
            command=self.create_RaceDatabase,
            font="Arial 12 bold",
        )
        self.exportDatabaseToCSV = tk.Button(
            master=self.window2,
            text="Export",
            command=self.export_DatabaseToCSV,
            font="Arial 12 bold",
        )
        self.reset = tk.Button(
            master=self.window2,
            text="Reset Cont.",
            command=self.send_Reset,
            font="Arial 12 bold",
        )
        self.status = tk.Button(
            master=self.window2,
            text="Status TC",
            command=self.send_StatusRequest,
            font="Arial 12 bold",
        )
        self.sendSensivity = tk.Button(
            master=self.window2,
            text="SEND",
            command=self.send_Sensivity,
            font="Arial 12 bold",
        )
        self.sendBrightness = tk.Button(
            master=self.window2,
            text="SEND",
            command=self.send_Brightness,
            font="Arial 12 bold",
        )
        self.sendBlockSensorTime = tk.Button(
            master=self.window2,
            text="SEND",
            command=self.send_BlockSensorTime,
            font="Arial 12 bold",
        )
        self.quit = tk.Button(
            master=self.window2, text="Quit", command=self.stop_All, font="Arial 12 bold"
        )
        self.displayTime = tk.Button(
            master=self.window2,
            text="ON",
            relief="raised",
            command=self.show_Time,
            font="Arial 12 bold",
        )
        self.countDown = tk.Button(
            master=self.window2,
            text="ON",
            relief="raised",
            command=self.set_CountDown,
            font="Arial 12 bold",
        )
        self.sendText = tk.Button(
            master=self.window2, text="SEND", command=self.send_Text, font="Arial 12 bold"
        )
        self.sendRounds = tk.Button(
            master=self.window2, text="SEND", command=self.send_Round, font="Arial 12 bold"
        )
        self.clearText = tk.Button(
            master=self.window2, text="Clear", command=self.clear_Text, font="Arial 12 bold"
        )

        # packen der Widgets mit grid Methode
        self.txtHead.grid(column=1, row=0, columnspan=3)
        self.blank.grid(column=1, row=1, pady=15)

        self.txtSetRaceDatabase.grid(column=1, row=2, pady=10)
        self.raceDatabase.grid(column=2, row=2)
        self.createRaceDatabase.grid(column=3, row=2)

        self.txtExportDatabaseToCSV.grid(column=1, row=3, pady=10)
        self.exportDatabaseToCSV.grid(column=2, row=3)

        self.txtText1.grid(column=1, row=5, pady=10)
        self.displayText.grid(column=2, row=5)
        self.sendText.grid(column=3, row=5)
        self.clearText.grid(column=4, row=5)
        # self.blank.grid(column=1, row=5, pady=20)

        self.txtRounds.grid(column=1, row=6, pady=10)
        self.rounds.grid(column=2, row=6)
        self.sendRounds.grid(column=3, row=6)

        self.txtBrightness.grid(column=1, row=15, pady=10)
        self.brightness.grid(column=1, row=16)
        self.sendBrightness.grid(column=2, row=16)

        self.txtDisplayTime.grid(column=4, row=15)
        self.displayTime.grid(column=4, row=16)

        self.txtCountDown.grid(column=4, row=20)
        self.countDown.grid(column=4, row=21)

        self.txtSensivity.grid(column=1, row=20, pady=10)
        self.sensivity.grid(column=1, row=21)
        self.sendSensivity.grid(column=2, row=21)

        self.txtBlockSensorTime.grid(column=1, row=22, pady=10)
        self.blockSensorTime.grid(column=1, row=23)
        self.sendBlockSensorTime.grid(column=2, row=23)

        self.txtStatus.grid(column=1, row=24, pady=10)
        self.status.grid(column=1, row=25)

        self.txtReset.grid(column=4, row=22)
        self.reset.grid(column=4, row=23)
        self.crText.grid(column=2, row=25)

        self.quit.grid(column=4, row=25)

        # display main window
        self.window2.mainloop()

    def create_RaceDatabase(self):
        global databaseName
        databaseName = (self.raceDatabase.get()) + ".db"
        if os.path.exists(databaseName):
            tkinter.messagebox.showinfo(0, "Datenbank existiert bereits!")
        # sys.exit(0)
        else:
            connection = sqlite3.connect(databaseName)
            cursor = connection.cursor()

            # create database table
            sql = """CREATE TABLE Race (
                Rennen INTEGER, Uhrzeit TEXT, Rennklasse TEXT,
                Team1_1 TEXT, Zeit1_1 REAL, Team2_1 TEXT, Zeit2_1 REAL, Team3_1 TEXT, Zeit3_1 REAL,
                Team3_2 TEXT, Zeit1_2 REAL, Team1_2 TEXT, Zeit2_2 REAL, Team2_2 TEXT, Zeit3_2 REAL,
                Team2_3 TEXT, Zeit1_3 REAL, Team3_3 TEXT, Zeit2_3 REAL, Team1_3 TEXT, Zeit3_3 REAL,
                PunkteTeam1 INTEGER, PunkteTeam2 INTEGER, PunkteTeam3 INTEGER
                );"""
            cursor.execute(sql)
            connection.commit()
            connection.close()

    def export_DatabaseToCSV(self):
        global raceNumber
        now = datetime.now()
        databaseName = (self.raceDatabase.get()) + ".db"
        connection = sqlite3.connect(databaseName)
        df = pd.read_sql_query("SELECT * FROM Race", connection)
        df.to_csv((self.raceDatabase.get()) + ".csv")
        connection.close()

    # Clear display text
    def clear_Text(self):
        global textToSendFront
        # global textToSendBack
        global canIdText
        canIdText = 0x1FFBEB00  # set CAN Bus ID for send text to signal controller
        self.displayText.delete(0, len(self.displayText.get()))
        textToSendFront = " "
        self.event_1.set()
        self.event_1.clear()

    def send_Text(self):
        global textToSendFront
        # global textToSendBack
        global canIdText
        canIdText = 0x1FFBEB00  # set CAN Bus ID for send text to signal controller
        textToSendFront = str(self.displayText.get())
        if len(textToSendFront) > 21:
            tkinter.messagebox.showerror("Error", "Text zu lang. max 21 Zeichen!")
        else:
            self.event_1.set()
            self.event_1.clear()

    def send_Round(self):
        global rCount
        global canIdText
        canIdText = 0x1FFB2000  # set CAN Bus ID for send round count to time controller
        rCount = int(self.rounds.get())
        self.event_1.set()
        self.event_1.clear()

    def show_Time(self):
        global displayTimeDC
        global canIdText
        canIdText = 0x1FFB3300  # set CAN Bus ID for send reset to the controllers
        if self.displayTime.config("relief")[-1] == "sunken":
            self.displayTime.config(text="ON", relief="raised")
            displayTimeDC = 1
        else:
            self.displayTime.config(text="OFF", relief="sunken")
            displayTimeDC = 0
        self.event_1.set()
        self.event_1.clear()

    def set_CountDown(self):
        global countDownDC
        global canIdText
        canIdText = 0x1FFB3400  # set CAN Bus ID for send reset to the controllers
        if self.countDown.config("relief")[-1] == "sunken":
            self.countDown.config(text="ON", relief="raised")
            countDownDC = 1
        else:
            self.countDown.config(text="OFF", relief="sunken")
            countDownDC = 0
        self.event_1.set()
        self.event_1.clear()

    def send_Reset(self):
        global sendReset
        global canIdText
        canIdText = 0x1FFB1000  # set CAN Bus ID for send reset to the controllers
        sendReset = 1
        self.event_1.set()
        self.event_1.clear()

    def send_Brightness(self):
        global displayBrightness
        global canIdText
        canIdText = 0x1FFB3000  # set CAN Bus ID for send display brightness to DC
        displayBrightness = int(self.brightness.get())
        self.event_1.set()
        self.event_1.clear()

    def send_Sensivity(self):
        global sensorSensivity
        global canIdText
        canIdText = 0x1FFB4000  # set CAN Bus ID for send sensor sensivity to TC
        sensorSensivity = int(self.sensivity.get())
        self.event_1.set()
        self.event_1.clear()

    def send_BlockSensorTime(self):
        global blockedSensorTime
        global canIdText
        canIdText = 0x1FFB5000  # set CAN Bus ID for send sensor blocking time to TC
        blockedSensorTime = int(self.blockSensorTime.get())
        self.event_1.set()
        self.event_1.clear()

    def send_StatusRequest(self):
        global canIdText
        canIdText = 0x1FFBF000  # set CAN Bus ID for send status request to TC
        self.event_1.set()
        self.event_1.clear()

    # Teminate all threats
    def stop_All(self):
        global textToSendFront
        global canIdText
        self.window2.destroy()
        # stop()
        canIdText = 0x1FFBEB00  # set CAN Bus ID for send text to signal controller
        textToSendFront = "Quit"
        self.event_1.set()
        self.event_1.clear()


# Receive data from CAN bus
class can_recvData(Thread):
    def __init__(self, can_bus, running):
        Thread.__init__(self)
        self.can_bus = can_bus
        self.running = running

    def run(self):
        # global can_readMsg
        global blockClock1
        global blockClock2
        global blockClock3
        global Timer1_1
        global Timer2_1
        global Timer3_1
        global Timer1_2
        global Timer2_2
        global Timer3_2
        global Timer1_3
        global Timer2_3
        global Timer3_3
        global TimeRace
        TimeRace = 0
        Timer1_1 = 0
        Timer2_1 = 0
        Timer3_1 = 0
        Timer1_2 = 0
        Timer2_2 = 0
        Timer3_2 = 0
        Timer1_3 = 0
        Timer2_3 = 0
        Timer3_3 = 0

        while self.running:
            msg = can_bus.recv()
            if msg.arbitration_id == 0x1FFA2000:
                #            print ("Daten empfangen")
                # print ("ID", hex(msg.arbitration_id))
                # print (msg.data)
                # print (msg.data[0])
                traknum = msg.data[0]
                reciveTime = msg.data[1:]  # [-4:]
                (raceTime,) = unpack(">i", reciveTime)
                raceTime = raceTime / 1000

                if TimeRace == 1:
                    if traknum == 1:
                        Timer1_1 = round(raceTime, 2)
                        # Timer1 = (str(raceTime1))
                        print(Timer1_1)
                    if traknum == 2:
                        Timer2_1 = round(raceTime, 2)
                        # Timer2 = (str(raceTime2))
                        print(Timer2_1)
                    if traknum == 3:
                        Timer3_1 = round(raceTime, 2)
                        # Timer3 = (str(raceTime3))
                        print(Timer3_1)
                    # blockClock2 = 0
                if TimeRace == 2:
                    if traknum == 1:
                        Timer1_2 = round(raceTime, 2)
                        # Timer1 = (str(raceTime1))
                        print(Timer1_2)
                    if traknum == 2:
                        Timer2_2 = round(raceTime, 2)
                        # Timer2 = (str(raceTime2))
                        print(Timer2_2)
                    if traknum == 3:
                        Timer3_2 = round(raceTime, 2)
                        # Timer3 = (str(raceTime3))
                        print(Timer3_2)
                #                        timeRecieved = 1
                # blockClock2 = 0
                if TimeRace == 3:
                    if traknum == 1:
                        Timer1_3 = round(raceTime, 2)
                        # Timer1 = (str(raceTime1))
                        print(Timer1_3)
                    if traknum == 2:
                        Timer2_3 = round(raceTime, 2)
                        # Timer2 = (str(raceTime2))
                        print(Timer2_3)
                    if traknum == 3:
                        Timer3_3 = round(raceTime, 2)
                        # Timer3 = (str(raceTime3))
                        print(Timer3_3)

            elif msg.arbitration_id == 0x1FFA2000:
                Timer1_1 = 0
                Timer2_1 = 0
                Timer3_1 = 0
                Timer1_2 = 0
                Timer2_2 = 0
                Timer3_2 = 0
                Timer1_3 = 0
                Timer2_3 = 0
                Timer3_3 = 0

            # elif msg.arbitration_id == 0x1FFC3000:  # Receive time controller status
            # print (msg.data)
            # print (msg.data[1])
            # print (msg.data[2])
            # print (msg.data[3])
            # print (msg.data[4])

    def stop(self):
        self._is_running = False


# Send Text to signal controller over CAN bus
class can_sendData(Thread):
    def __init__(self, can_bus, event_1, running):
        Thread.__init__(self)
        self.event_1 = event_1
        self.can_bus = can_bus
        self.running = running

    def run(self):
        while self.running:
            self.event_1.wait()
            # Send team order or Text to the signal controller
            # print(textToSendFront)
            # Send Text lenght
            if canIdText == 0x1FFBEB00:
                can_ID = 0x1FFBE900  # set CAN Bus ID for text lenght to signal controller
                ba_canSend = bytearray(struct.pack("<h", len(textToSendFront)))
                # send data to can bus
                msg = can.Message(arbitration_id=can_ID, data=ba_canSend, is_extended_id=True)
                can_bus.send(msg)
                time.sleep(0.05)
                index = 0
                # Send Text
                while index < len(textToSendFront):
                    letter = textToSendFront[index]
                    ba_canSend = bytearray(
                        struct.pack("<h", ord(textToSendFront[index].encode("cp437")))
                    )
                    index = index + 1
                    can_ID = canIdText
                    # send data to can bus
                    msg = can.Message(
                        arbitration_id=can_ID, data=ba_canSend, is_extended_id=True
                    )
                    can_bus.send(msg)
                    time.sleep(0.003)
            elif canIdText == 0x1FFBEC00:
                print(textToSendFront)
                can_ID = (
                    0x1FFBEA00
                )  # set CAN Bus ID for send text lenght to signal controller
                ba_canSend = bytearray(struct.pack("<h", len(textToSendFront)))
                # send data to can bus
                msg = can.Message(arbitration_id=can_ID, data=ba_canSend, is_extended_id=True)
                can_bus.send(msg)
                time.sleep(0.05)
                index = 0
                # Send Text
                while index < len(textToSendFront):
                    letter = textToSendFront[index]
                    ba_canSend = bytearray(
                        struct.pack("<h", ord(textToSendFront[index].encode("cp437")))
                    )
                    index = index + 1
                    can_ID = canIdText
                    # send data to can bus
                    msg = can.Message(
                        arbitration_id=can_ID, data=ba_canSend, is_extended_id=True
                    )
                    can_bus.send(msg)
                    time.sleep(0.003)
            elif canIdText == 0x1FFBEC10:
                print(textToSendBack)
                can_ID = (
                    0x1FFBEA10
                )  # set CAN Bus ID for send text lenght to signal controller
                ba_canSend = bytearray(struct.pack("<h", len(textToSendFront)))
                # send data to can bus
                msg = can.Message(arbitration_id=can_ID, data=ba_canSend, is_extended_id=True)
                can_bus.send(msg)
                time.sleep(0.05)
                index = 0
                while index < len(textToSendBack):
                    letter = textToSendBack[index]
                    ba_canSend = bytearray(
                        struct.pack("<h", ord(textToSendBack[index].encode("cp437")))
                    )
                    index = index + 1
                    can_ID = canIdText
                    # send data to can bus
                    msg = can.Message(
                        arbitration_id=can_ID, data=ba_canSend, is_extended_id=True
                    )
                    can_bus.send(msg)
                    time.sleep(0.003)

            # Send "make soft reset" to the controllers
            elif canIdText == 0x1FFB1000:
                can_ID = canIdText
                # print sendReset)
                ba_canSend = bytearray(struct.pack("<h", sendReset))
                # send data to can bus
                msg = can.Message(arbitration_id=can_ID, data=ba_canSend, is_extended_id=True)
                can_bus.send(msg)
                time.sleep(0.005)
            # Send Round count (2/4) to the signal controller
            elif canIdText == 0x1FFB2000:
                can_ID = canIdText
                # print(rCount)
                ba_canSend = bytearray(struct.pack("<h", rCount))
                # send data to can bus
                msg = can.Message(arbitration_id=can_ID, data=ba_canSend, is_extended_id=True)
                can_bus.send(msg)
                time.sleep(0.005)
            elif canIdText == 0x1FFB3000:  # send display brightness to signal controller
                can_ID = canIdText
                # print(displayBrightness)
                ba_canSend = bytearray(struct.pack("<h", displayBrightness))
                # send data to can bus
                msg = can.Message(arbitration_id=can_ID, data=ba_canSend, is_extended_id=True)
                can_bus.send(msg)
                time.sleep(0.005)
            elif canIdText == 0x1FFB3300:  # send Time Display ON/OFF to DC
                can_ID = canIdText
                # print(displayBrightness)
                ba_canSend = bytearray(struct.pack("<h", displayTimeDC))
                # send data to can bus
                msg = can.Message(arbitration_id=can_ID, data=ba_canSend, is_extended_id=True)
                can_bus.send(msg)
                time.sleep(0.005)
            elif canIdText == 0x1FFB3400:  # send Countdown ON/OFF to DC
                can_ID = canIdText
                # print(displayBrightness)
                ba_canSend = bytearray(struct.pack("<h", countDownDC))
                # send data to can bus
                msg = can.Message(arbitration_id=can_ID, data=ba_canSend, is_extended_id=True)
                can_bus.send(msg)
                time.sleep(0.005)
            elif canIdText == 0x1FFB4000:  # send sensor sensivity to time controller
                can_ID = canIdText
                # print(sensorSensivity)
                ba_canSend = bytearray(struct.pack("<h", sensorSensivity))
                # send data to can bus
                msg = can.Message(arbitration_id=can_ID, data=ba_canSend, is_extended_id=True)
                can_bus.send(msg)
                time.sleep(0.005)
            elif canIdText == 0x1FFB5000:  # send sensor blocking time to time controller
                can_ID = canIdText
                ba_canSend = bytearray(struct.pack("<h", blockedSensorTime))
                # send data to can bus
                msg = can.Message(arbitration_id=can_ID, data=ba_canSend, is_extended_id=True)
                can_bus.send(msg)
                time.sleep(0.005)
            #            elif canIdText == 0x1FFB6100: # send sensor blocking time to time controller
            #                can_ID = canIdText
            #                ba_canSend = bytearray(struct.pack("<h", blockClock1))
            #                # send data to can bus
            #                msg = can.Message(arbitration_id=can_ID,
            #                                  data=ba_canSend, is_extended_id=True)
            #                can_bus.send(msg)
            #                time.sleep(0.005)
            elif canIdText == 0x1FFB6200:  # send sensor blocking time to time controller
                can_ID = canIdText
                print("Clock2 " + str(blockClock2))
                ba_canSend = bytearray(struct.pack("<h", blockClock2))
                # send data to can bus
                msg = can.Message(arbitration_id=can_ID, data=ba_canSend, is_extended_id=True)
                can_bus.send(msg)
                time.sleep(0.005)
            #            elif canIdText == 0x1FFB6300: # send sensor blocking time to time controller
            #                can_ID = canIdText
            #                ba_canSend = bytearray(struct.pack("<h", blockClock3))
            #                # send data to can bus
            #                msg = can.Message(arbitration_id=can_ID,
            #                                  data=ba_canSend, is_extended_id=True)
            #                can_bus.send(msg)
            #                time.sleep(0.005)

            elif canIdText == 0x1FFBF000:  # Send status request to time controller
                can_ID = canIdText
                ba_canSend = 0x01
                # send data to can bus
                msg = can.Message(arbitration_id=can_ID, data=ba_canSend, is_extended_id=True)
                can_bus.send(msg)
                time.sleep(0.005)

            # Send shift/no shift
            # can_ID = 0x1FFBEB00  # set CAN Bus ID for send shift/no shift
            # ba_canSend = bytearray(struct.pack("<h", noShift))
            # msg = can.Message(arbitration_id=can_ID, data=ba_canSend, is_extended_id=True)   # send data to can bus
            # can_bus.send(msg)
            # time.sleep(1)

    def stop(self):
        self._is_running = False


def main():
    # read data from Threads
    can_send = can_sendData(can_bus, event_1, running)
    can_recv = can_recvData(can_bus, running)
    input_race_data = input_race_GUI(event_1)
    input_control_data = input_control_GUI(event_1)
    calc_race_data = calculate_time_Points(running)
    # start threads
    can_send.start()  # data send to CAN Bus
    can_recv.start()  # data send to CAN Bus
    input_race_data.start()  # GUI Input Teams
    time.sleep(0.5)
    input_control_data.start()  # GUI Input controller data
    calc_race_data.start()  # Calculate best time and piont of teams

    can_send.join()
    can_recv.join()
    input_race_data.join()
    input_control_data.join()
    calc_race_data.join()


class DummyCanMsg:
    arbitration_id = 0


class DummyCanBus:
    def send(self, msg):
        pass

    def recv(self):
        time.sleep(0.1)
        return DummyCanMsg()


if __name__ == "__main__":
    # Set I2C Bus 1
    # i2c_bus = SMBus(1)

    # Set CAN Bus 0
    try:
        can_bus = can.interface.Bus(bustype="socketcan", channel="can0", bitrate=1000000)
    except Exception as e:
        print("Failed to initialize can bus: ", e)
        can_bus = DummyCanBus()
    # reset_msg = can.Message(arbitration_id=0x003, data=[0, 0, 0, 0, 0, 0], is_extended_id=False)
    # can.set_filter[{"can_id": 0x1FFA2000, "can_mask": 0x1FFFFFFF, "extended": True}]
    running = True
    main()
# while 1:
# main()
