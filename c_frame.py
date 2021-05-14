import tkinter as tk
from tkinter import ttk, messagebox, filedialog
from custom_tk import *
from zipfile import ZipFile
from heatmap import *
from blastp import *
import os
from os import path
import string 
import random
from math import floor
from time import sleep
import matplotlib.pyplot as plt
import threading 

class cFrame(Frame):

    def __init__(self, master, subjects, queryOI, unit, index, seqs, seq_names, s, i, p, g, reports, **kwargs):

        Frame.__init__(self, master, **kwargs)
        self.pack(fill=BOTH, expand=True, padx=5, pady=5)

        self.s1 = ttk.Style(self)
        self.s1_font = ("Segoe UI", 8)
        self.s1.configure("s1.TLabelframe", font=self.s1_font)
        self.s1.configure("s1.TLabel", font=self.s1_font)
        self.s1.configure("s1.TEntry", font=self.s1_font)
        self.s1.configure("s1.TButton", font=self.s1_font)
        self.s1.configure("s1.TNumentry", font=self.s1_font)
        self.s1.configure("s1.TCheckbutton", font=self.s1_font)
        self.s1.configure("s1.TOptionmenu", font=self.s1_font)

        self.subjects = subjects
        self.path = ''.join(random.choices(string.ascii_uppercase + string.digits, k = 10)) # Random string of 10 characters as a prefix to heatmap names
        self.queryOI = queryOI
        self.unit = "score"
        self.scale = "linear" # "quadratic", "logarithmic" are other option, default linear
        self.index = index
        self.seqs = seqs
        self.seq_names = seq_names
        self.score = s
        self.id = i
        self.positive = p
        self.gap = g
        self.reports = reports
        self.indices = [1, self.seqs.__len__()]

        frame_1 = ttk.Frame(self)
        frame_1.grid(row=0, column=0, sticky="nesw", padx=5, pady=5)
        self.frame1 = frame_1
        
        frame_2 = ttk.Frame(self)
        frame_2.grid(row=0, column=1, sticky="nesw", padx=5, pady=5)
        self.frame2 = frame_2
        self.render_f12()

        self.render_f13()
        self.render_f14()
        self.render_f2()

    def render_f11(self):

        contain = ttk.Frame(self.frame1)
        contain.grid(row=0, column=0, sticky="nesw", padx=5, pady=5)
        cols = ["Subject", "Sequence Name"]
        tree = ttk.Treeview(contain, columns=cols, show="headings", style="s1.Treeview")
        tree.grid(row=0, column=0, padx=5, pady=5)
        tree.column("Subject", width=200)
        tree.column("Sequence Name", width=1000)
        for col in cols:
            tree.heading(col, text=col)
        for a in range(0, self.subjects.__len__()):
            tree.insert("", "end", values=(self.subjects[a], self.seq_names[a].replace("> ", "")))

    def render_f12(self):

        contain = ttk.LabelFrame(self.frame1, text="Correlation Details", style="s1.TLabelframe")
        contain.grid(row=1, column=0, sticky="nesw", padx=5, pady=5)

        label_q_src = ttk.Label(contain, text="Query Source: " + self.queryOI, style="s1.TLabel")
        label_q_src.grid(row=0, column=0, sticky=W, padx=5, pady=5)
        label_p_index = ttk.Label(contain, text="Peptide Index: " + str(self.index+1), style="s1.TLabel")
        label_p_index.grid(row=1, column=0, sticky=W, padx=5, pady=5)
        label_unit = ttk.Label(contain, text="Unit: " + self.unit.upper(), style="s1.TLabel")
        label_unit.grid(row=2, column=0, sticky=W, padx=5, pady=5)
        label_scale = ttk.Label(contain, text="Scale: " + self.scale.upper(), style="s1.TLabel")
        label_scale.grid(row=3, column=0, sticky=W, padx=5, pady=5)
    
    def render_f13(self):

        contain = ttk.LabelFrame(self.frame1, text="Heatmap Unit", style="s1.TLabelframe")
        contain.grid(row=2, column=0, sticky="nesw", padx=5, pady=5)

        unit_btn_frame = ttk.Frame(contain)
        unit_btn_frame.pack(padx=5, pady=5)
        score_button = ttk.Button(unit_btn_frame, text="Score", command=lambda: unit_score(), style="s1.TButton")
        score_button.grid(row=0, column=0, sticky="nesw", padx=5, pady=5)
        id_button = ttk.Button(unit_btn_frame, text="ID", command=lambda: unit_id(), style="s1.TButton")
        id_button.grid(row=0, column=1, sticky="nesw", padx=5, pady=5)
        pos_button = ttk.Button(unit_btn_frame, text="Positive", command=lambda: unit_positive(), style="s1.TButton")
        pos_button.grid(row=1, column=0, sticky="nesw", padx=5, pady=5)
        gap_button = ttk.Button(unit_btn_frame, text="Gap", command=lambda: unit_gap(), style="s1.TButton")
        gap_button.grid(row=1, column=1, sticky="nesw", padx=5, pady=5)

        def unit_score():

            self.unit = "score"
            self.render_f12()
            self.render_f2()

        def unit_id():
            
            self.unit = "id"
            self.render_f12()
            self.render_f2()
        
        def unit_positive():
            
            self.unit = "positive"
            self.render_f12()
            self.render_f2()
        
        def unit_gap():
            
            self.unit = "gap"
            self.render_f12()
            self.render_f2()
    
    def render_f14(self):

        contain = ttk.LabelFrame(self.frame1, text="Heatmap Scale", style="s1.TLabelframe")
        contain.grid(row=3, column=0, sticky="nesw", padx=5, pady=5)

        scale_btn_frame = ttk.Frame(contain)
        scale_btn_frame.pack(padx=5, pady=5)
        line = ttk.Button(scale_btn_frame, text="X", command=lambda: scale_x(), style="s1.TButton")
        line.grid(row=0, column=0, sticky="nesw", padx=5, pady=5)
        quad = ttk.Button(scale_btn_frame, text="X^2", command=lambda: scale_x2(), style="s1.TButton")
        quad.grid(row=0, column=1, sticky="nesw", padx=5, pady=5)
        log = ttk.Button(scale_btn_frame, text="log(X)", command=lambda: scale_log(), style="s1.TButton")
        log.grid(row=1, column=0, sticky="nesw", padx=5, pady=5)

        def scale_x():
            reverse = False
            if self.unit == "gap":
                reverse = True
            self.scale = "linear"
            self.render_f12()
            self.render_f2()
        
        def scale_x2():
            reverse = False
            if self.unit == "gap":
                reverse = True
            self.scale = "quadratic"
            self.render_f12()
            self.render_f2()
        
        def scale_log():
            reverse = False
            if self.unit == "gap":
                reverse = True
            self.scale = "logarithmic"
            self.render_f12()
            self.render_f2()

    def render_f2(self):

        reverse = False
        data = None
        if self.unit == "score":
            data = self.score
        elif self.unit == "id":
            data = self.id
        elif self.unit == "positive":
            data = self.positive
        elif self.unit == "gap":
            data = self.gap
            reverse = True

        corr_gen_hxy(self.subjects, data, self.scale, self.path, reverse)

        panX = panXCanvas(self.frame2, height=250)
        self.imgX = PhotoImage(file="viewing/"+self.path+"-x.png")      
        panX.create_image(0, 0, anchor=NW, image=self.imgX) 
        panX.grid(row=0, column=1, sticky="nesw")

        panY = panYCanvas(self.frame2, width=250, height=(self.subjects.__len__()+2)*20)
        self.imgY = PhotoImage(file="viewing/"+self.path+"-y.png")
        panY.create_image(0, 0, anchor=NW, image=self.imgY)
        panY.grid(row=1, column=0, sticky="nesw")

        cFrame_self = self

        class panMaster(panCanvas):

            def __init__(self, master, **kwargs):

                Canvas.__init__(self, master, kwargs)
                self.bind("<B1-Motion>", self.drag)
                self.bind("<Button-1>", self.click)
                self.bind("<ButtonRelease-1>", self.release)
                self.bind("<Double-Button-1>", self.doubleclick)
                self.index = None
            
            def click(self, event):

                self.index = 1
                self.x, self.y = event.x, event.y

            def drag(self, event):
                
                try:
                    self.move(self.index, event.x-self.x, event.y-self.y)
                    panX.move(self.index, event.x-self.x, 0)
                    panY.move(self.index, 0, event.y-self.y)
                    self.x = event.x
                    self.y = event.y
                except:
                    pass

            def release(self, event):

                self.index = None

            ''' Pull up a tab that contains the blast report for that particular peptide from the focus '''
            def doubleclick(self, event):
            
                plotx, ploty = self.coords(1)
                plotx -= event.x
                ploty -= event.y
                plotx /= -40
                ploty /= -20
                if plotx < 0 or ploty < 0 or plotx >= self.master.master.indices[1] or ploty >= self.master.master.subjects.__len__(): 
                    return
                plotx = floor(plotx)
                ploty = floor(ploty)
                query_to_display = self.master.master.queryOI
                report_to_display = self.master.master.reports[ploty][plotx]
                subject_report = self.master.master.subjects[ploty]
                index_report = self.master.master.indices[0] + plotx
                focus_report = self.master.master.subjects[plotx]

                tab = ttk.Frame(self.master.master.master)

                center_frame = ttk.LabelFrame(tab, text="Report Details", style="s1.TLabelframe")
                center_frame.grid(row=0, column=0, sticky="", padx=5, pady=3)
                center_frame.place(in_=tab, anchor="c",relx=.5, rely=.5)

                li1 = ttk.Label(center_frame, text="Query: " + query_to_display, style="s1.TLabel")
                li1.grid(row=0, column=0, sticky=W, padx=5, pady=5)
                li2 = ttk.Label(center_frame, text="Focus: " + focus_report, style="s1.TLabel")
                li2.grid(row=1, column=0, sticky=W, padx=5, pady=5)
                li3 = ttk.Label(center_frame, text="Subject: " + subject_report, style="s1.TLabel")
                li3.grid(row=2, column=0, sticky=W, padx=5, pady=5)
                li4 = ttk.Label(center_frame, text="Peptide Index: " + str(index_report), style="s1.TLabel")
                li4.grid(row=3, column=0, sticky=W, padx=5, pady=5)
                display_report = Text(center_frame, width=100, height=25)
                display_report.grid(row=4, column=0, padx=5, pady=5)

                display_report.insert(END, cFrame_self.reports[plotx][ploty])

                self.master.master.master.add(tab, text="Correlation Blast Report")
                self.master.master.master.select([self.master.master.master.tab(i, option="text") for i in self.master.master.master.tabs()].__len__()-1)

        panXY = panMaster(self.frame2, width=1800, height=(self.subjects.__len__())*20)
        self.imgXY = PhotoImage(file="viewing/"+self.path+"-hm.png")
        panXY.create_image(0, 0, anchor=NW, image=self.imgXY)
        panXY.grid(row=1, column=1, sticky="nesw")

        def pan_right():
            panXY.move(1, -1000, 0)
            panX.move(1, -1000, 0)
        
        def pan_left():
            panXY.move(1, 1000, 0)
            panX.move(1, 1000, 0)

        panLR = ttk.Frame(self.frame2, width=40, height=20)
        panLR.grid(row=0, column=0)
        button_left = ttk.Button(panLR, text=u"\u2190", command=lambda: pan_left(), style="s1.TButton")
        button_left.grid(row=0, column=0)
        button_right = ttk.Button(panLR, text=u"\u2192", command=lambda: pan_right(), style="s1.TButton")
        button_right.grid(row=0, column=1)

    def destroy(self):

        Frame.destroy(self)
        if self.path != None:
            os.remove("viewing/"+self.path+"-hm.png")
            os.remove("viewing/"+self.path+"-x.png")
            os.remove("viewing/"+self.path+"-y.png")
