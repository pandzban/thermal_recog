# -*- coding: utf-8 -*-
"""
Created on Wed Jul 15 16:56:46 2015

@author: Alexander Hoch
"""

import tkinter as tk
#import tkMessageBox
from tkinter import messagebox
from tkinter import ttk
import colorsys
import time
from GridEyeKit import GridEYEKit
import numpy as np


# Grid Eye related numbers

Num_of_Middle = 190
Num_of_Outputs = 8
Middle_Weights = np.array([], dtype=np.float)
Output_Weights = np.array([])
Input = np.array([])
Output = np.zeros(Num_of_Outputs)
index = 50
first_time = 0
last_time = 0
last_time_check = 0

iteration = 0
counting = False
transfering = True
samples = []

class GridEYE_Viewer():

    def __init__(self, root):

        """ Initialize Window """
        self.tkroot = root
        self.tkroot.protocol('WM_DELETE_WINDOW', self.exitwindow)  # Close serial connection and close window

        """ Initialize variables for color interpolation """
        self.HUEstart = 0.5  # initial color for min temp (0.5 = blue)
        self.HUEend = 1  # initial color for max temp (1 = red)
        self.HUEspan = self.HUEend - self.HUEstart

        """ Grid Eye related variables"""
        self.MULTIPLIER = 0.25  # temp output multiplier

        """ Initialize Loop bool"""
        self.START = False

        """Initialize frame tor temperature array (tarr)"""
        self.frameTarr = tk.Frame(master=self.tkroot, bg='white')
        self.frameTarr.place(x=5, y=5, width=400, height=400)

        """Initialize pixels tor temperature array (tarr)"""
        self.tarrpixels = []
        for i in range(8):
            # frameTarr.rowconfigure(i,weight=1) # self alignment
            # frameTarr.columnconfigure(i,weight=1) # self alignment
            for j in range(8):
                pix = tk.Label(master=self.frameTarr, bg='gray', text='11')
                spacerx = 1
                spacery = 1
                pixwidth = 40
                pixheight = 40
                pix.place(x=spacerx + j * (spacerx + pixwidth), y=spacery + i * (pixheight + spacery), width=pixwidth,
                          height=pixheight)
                print(self.tarrpixels.append(pix))  # attache all pixels to tarrpixel list

        """Initialize frame tor Elements"""
        self.frameElements = tk.Frame(master=self.tkroot, bg='white')
        self.frameElements.place(x=410, y=5, width=100, height=400)



        """Initialize controll buttons"""
        self.buttonStart = tk.Button(master=self.frameElements, text='start', bg='white',
                                     command=self.start_update)
        self.buttonStart.pack()
        self.buttonStop = tk.Button(master=self.frameElements, text='stop', bg='white',
                                    command=self.stop_update)
        self.buttonStop.pack()
        self.buttonSave = tk.Button(master=self.frameElements, text='Save', bg='white',
                                    command=self.save_to_file)
        self.buttonSave.pack()


        self.labelTop = tk.Label(master=self.frameElements,
                            text="Gest:")
        self.labelTop.pack()

        self.combobox = ttk.Combobox(master=self.frameElements, values=["gest0", "gest1", "gest2", "gest3", "gest4",
                                                                        "gest5", "gest6", "gest7", "gest8"])
        self.combobox.pack()
        self.combobox.current(0)

        """Initialize temperature adjustment"""
        self.lableTEMPMAX = tk.Label(master=self.frameElements, text='Max Temp (red)')
        self.lableTEMPMAX.pack()
        self.MAXTEMP = tk.Scale(self.frameElements, from_=-20, to=120, resolution=0.25)
        self.MAXTEMP.set(31)
        self.MAXTEMP.pack()
        self.lableMINTEMP = tk.Label(master=self.frameElements, text='Min Temp (blue)')
        self.lableMINTEMP.pack()
        self.MINTEMP = tk.Scale(self.frameElements, from_=-20, to=120, resolution=0.25)
        self.MINTEMP.set(27)
        self.MINTEMP.pack()

        self.kit = GridEYEKit()

    def exitwindow(self):
        """ if windwow is clsoed, serial connection has to be closed!"""
        self.kit.close()
        self.tkroot.destroy()

    def save_to_file(self):
        """Nasza funkcja do zapisu"""
        tarr = self.get_tarr()
        #print(tarr)
        global index
        global first_time
        global counting
        #print("AAAAAAAA", self.combobox.current(), self.combobox.get()) ## wartość comboboxa
        counting = True
        file_index = open("index.txt", "w+")
        print("index: ", index)
        #print(str(index))

        file_saved = open("saved.txt", "a")
        file_saved.write(str(index) + "_" + str(self.combobox.current()))
        file_saved.write("\n")
        file_saved.close()
        first_time = time.time()
        global last_time
        last_time = first_time
        file_index.write(str(index))
        file_index.close()

    def stop_update(self):
        """ stop button action - stops infinite loop """
        self.START = False
        self.update_tarrpixels()

    def get_weights(self):
        """ nasz kod do pobierania wag"""
        global Num_of_Middle
        global Num_of_Outputs
        global Middle_Weights
        global Output_Weights
        for m in range(Num_of_Middle):
            text = "wages" + str(m) + ".txt"
            source = open(text, "r")
            vect = np.array([], dtype=np.float)
            for x in range(256):
                text = source.readline()
                var = float(text)
                vect = np.append(vect, var)
            source.close()
            if Middle_Weights.size == 0:
                Middle_Weights = vect
            else:
                Middle_Weights = np.vstack((Middle_Weights, vect))
        for m in range(Num_of_Outputs):
            text = "output_wages" + str(m) + ".txt"
            source = open(text, "r")
            vect = np.array([], dtype=np.float)
            for x in range(Num_of_Middle):
                text = source.readline()
                var = float(text)
                vect = np.append(vect, var)
            source.close()
            if Output_Weights.size == 0:
                Output_Weights = vect
            else:
                Output_Weights = np.vstack((Output_Weights, vect))
        print("Załadowano wagi!")

    def start_update(self):
        if self.kit.connect():
            """ start button action -start serial connection and start pixel update loop"""
            self.START = True
            self.get_weights()
            global index

            file_index = open("index.txt", "r")
            index = int(file_index.read())
            index += 1
            print(index)
            file_index.close()

            """ CAUTION: Wrong com port error is not handled"""
            self.update_tarrpixels()
        else:
            #tkMessageBox.showerror("Not connected",
            messagebox.showerror("Not connected",

                                   "Could not find Grid-EYE Eval Kit - please install driver and connect")

    def get_tarr(self):
        """ unnecessary function - only converts numpy array to tuple object"""
        tarr = []
        for temp in self.kit.get_temperatures():  # only fue to use of old rutines
            for temp2 in temp:
                tarr.append(temp2)
        return tarr

    def process_tarr(self):
        " Nasza własna funkcja"
        tarr_copy = self.get_tarr()
        tarr_proc = []
        tarr = tarr_copy
        maxx = max(tarr)
        minn = min(tarr)
        diff = maxx - minn
        mid = (maxx + minn)/2
        for x in range(len(tarr)):
            temp = (tarr[x] - mid)/diff
            tarr_proc.append(temp)
        tarr_copy.clear()
        #input("Press Enter to continue...")
        return tarr_copy

    def write_samples(self):
        global samples
        global index
        idx = str(index)
        file_example = open(idx + "_" + str(self.combobox.current()) + ".txt", "a")
        for x in range(256):
            file_example.write(str(samples[x]))
            file_example.write("\n")
        file_example.close()
        samples.clear()
        index += 1

    def transfer(self):   ### przepuszczanie przez sieć
        global Input
        global Middle_Weights
        global Output_Weights
        global Num_of_Middle
        global Num_of_Outputs
        global Output
        Between = np.zeros(Num_of_Middle)
        for k in range(Num_of_Middle):
            temp = 0.0
            for ix in range(256):
                temp += Middle_Weights[k][ix] * Input[ix]
            Between[k] = 1.0/(1.0 + np.exp((-1) * temp))
        for k in range(Num_of_Outputs):
            temp = 0.0
            for ix in range(Num_of_Middle):
                temp += Output_Weights[k][ix] * Between[ix]
            Output[k] = 1.0/(1.0 + np.exp((-1) * temp))       ## zapisane wyjscie

    def update_tarrpixels(self):
        """ Loop for updating pixels with values from funcion "get_tarr" - recursive function with exit variable"""
        if self.START == True:
            tarr = self.get_tarr()  # Get temerature array
            #tarr = self.process_tarr()
            global counting
            global transfering
            if counting:    ### kod odpowiedzialny za zapisywanie przykladow do nauki
                global last_time
                timex = time.time()
                diff = timex - last_time
                global iteration
                global samples
                if (diff > 0.25) & (iteration > 0):
                    tarr_proc = []
                    maxx = max(tarr)
                    minn = min(tarr)
                    diff = maxx - minn
                    mid = (maxx + minn) / 2
                    for x in range(len(tarr)):
                        temp = (tarr[x] - mid) / diff
                        tarr_proc.append(temp)
                    samples += tarr_proc  # dolozenie
                    tarr_proc.clear()
                    last_time = timex
                    iteration += 1
                    print("Iteration: ", iteration)
                    if iteration > 3:
                        iteration = 0
                        counting = False
                        self.write_samples()
                elif (diff > 1.0) & (iteration == 0):
                    tarr_proc = []
                    maxx = max(tarr)
                    minn = min(tarr)
                    diff = maxx - minn
                    mid = (maxx + minn) / 2
                    for x in range(len(tarr)):
                        temp = (tarr[x] - mid) / diff
                        tarr_proc.append(temp)
                    iteration += 1
                    print("Iteration: ", iteration)
                    last_time = timex
                    samples += tarr_proc  # dolozenie
                    tarr_proc.clear()
                elif iteration == 0:
                    print("Time to start: ", round(1.0-diff, 2), "s")
            elif transfering:            ### kod odpowiedzialny za sprawdzanie w czasie rzeczywistym
                global last_time_check
                timex = time.time()
                diff = timex - last_time_check
                if diff > 0.25:
                    global Input
                    temp = np.array([])
                    maxx = max(tarr)
                    minn = min(tarr)
                    diff = maxx - minn
                    mid = (maxx + minn) / 2
                    for x in range(64):
                        tempxx = (tarr[x] - mid) / diff
                        temp = np.append(temp, 2 * tempxx)
                    if Input.size == 0:
                        Input = temp
                    else:
                        Input = np.hstack((Input, temp))
                    last_time_check = time.time()
                    if Input.size == 320:
                        Input = Input[64:320]
                        self.transfer()
                        global Output
                        maxxx = max(Output)
                        summ = sum(Output)
                        for m in range(Num_of_Outputs):
                            if maxxx == Output[m]:
                                if ((maxxx > 0.80) & ((summ-maxxx) < 0.5)):
                                    if m == 0:
                                        print("Gest0: Pięść")
                                    elif m == 1:
                                        print("Gest1: Otwarta dłoń")
                                    elif m == 2:
                                        print("Gest2: Otwarta dłoń zbliżająca się")
                                    elif m == 3:
                                        print("Gest3: jeden palec")
                                    elif m == 4:
                                        print("Gest4: dwa palce")
                                    elif m == 5:
                                        print("Gest5: Dłoń przesuwana w lewo")
                                    elif m == 6:
                                        print("Gest6: Dłoń przesuwana w prawo")
                                    #elif m == 7:
                                    #    print("Gest7: NaN")

            i = 0
            if len(tarr) == len(self.tarrpixels):  # check if problem with readout
                for tarrpix in self.tarrpixels:
                    tarrpix.config(text=tarr[i])  # Update Pixel text
                    if tarr[i] < self.MINTEMP.get():  # For colors, set borders to min/max temp
                        normtemp = 0
                    elif tarr[i] > self.MAXTEMP.get():  # For colors, set borders to min/max temp
                        normtemp = 1
                    else:
                        TempSpan = self.MAXTEMP.get() - self.MINTEMP.get()
                        if TempSpan <= 0:  # avoid division by 0 and negative values
                            TempSpan = 1
                        normtemp = (float(tarr[i]) - self.MINTEMP.get()) / TempSpan  # Normalize temperature 0...1
                    h = normtemp * self.HUEspan + self.HUEstart  # Convert to HSV colors (only hue used)
                    if h > 1:
                        print(h)
                        print(normtemp)
                        print(self.HUEspan)
                        print(self.HUEstart)
                    bgrgb = tuple(255 * j for j in colorsys.hsv_to_rgb(h, 1, 1))  # convert to RGB colors
                    lixt = list(bgrgb)
                    for x in range(len(lixt)):
                        tempx = lixt[x]
                        lixt[x] = int(tempx)
                    bgrgb = tuple(lixt)
                    tarrpix.config(bg=('#%02x%02x%02x' % bgrgb))  # Convert to Hex String
                    #tarrpix.config(bg="ivory")

                    i += 1  # incement tarr counter
            else:
                print("Error - temperarure array lenth wrong")
            self.frameTarr.after(10,
                                 self.update_tarrpixels)  # recoursive function call all 10 ms (get_tarr will need about 100 ms to respond)


root = tk.Tk()
root.title('Grid-Eye Viewer')
root.geometry('520x430')
Window = GridEYE_Viewer(root)
root.mainloop()
