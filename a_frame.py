import tkinter as tk
from tkinter import ttk, messagebox, filedialog
from tkinter import *
from custom_tk import *
from zipfile import ZipFile
from heatmap import *
from blastp import *
import os
from os import path
import string 
import random
from math import floor
from copy import deepcopy
from time import sleep
import matplotlib.pyplot as plt
import threading
from c_frame import cFrame

class aFrame(Frame):

    def __init__(self, master, **kwargs):

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

        self.queryOI = None # Query Name
        self.unit = None # Score, Id, Positive, Gap
        self.scale = None # X, X^2, log(X)
        self.indices = [None, None] # From - To (Inclusive)
        self.data = None # self.score, self.id, self.positive, self.gap (reference to data we are playing with)
        self.subjects = [] # All the files compared to the focus fasta file
        self.filter = [None, None, None] # (score, id, positive, gap)[0], (Between the indices of [1] and [2]) 
        self.path = None # Random key 
        self.peptide = [] # List of all peptides (Used to generate links)
        self.blast_reports = [] # List format of all blast reports found in all_blastp.txt

        # This only exists so we don't have to do io operations repeatedly (ineffecient by miles)
        self.orig_score = [] # 5 units of data (Never manipulate)
        self.orig_id = []
        self.orig_positive = []
        self.orig_gap = []
        self.orig_frequency = []

        self.score = [] # 5 units of data that can be alterred as needed
        self.id = []
        self.positive = []
        self.gap = []
        self.frequency = []

        frame_1 = ttk.Frame(self) # Interface that has all knobs, switches, buttons
        frame_1.grid(row=0, column=0, sticky="nesw", padx=5, pady=5)
        self.frame1 = frame_1
        self.render_f11() 

        frame_2 = ttk.Frame(self) # Interface with the heatmap
        frame_2.grid(row=0, column=1, sticky="nesw", padx=5, pady=5)
        self.frame2 = frame_2
        self.grid_columnconfigure(1, weight=1)

    ''' Widgets to choose which query to analyze '''
    def render_f11(self):
        
        contain = ttk.LabelFrame(self.frame1, text="Generate Heatmap", style="s1.TLabelframe")
        contain.grid(row=0, column=0, sticky="nesw", padx=5, pady=5)

        choose_query = ttk.Frame(contain)
        choose_query.pack(padx=5, pady=5)

        li1 = ttk.Label(choose_query, text="Select the query to view:", style="s1.TLabel")
        li1.grid(row=0, column=0, padx=5, pady=5)
        
        history = get_history()
        query_list = ["-"]
        query_oi = StringVar()
        for record in history:
            query_list.append(record["save_as"])
        dropdown = ttk.OptionMenu(choose_query, query_oi, *query_list)
        dropdown.grid(row=1, column=0, sticky="nesw", padx=5, pady=5)

        submit = ttk.Button(choose_query, text="View", command=lambda: view(), style="s1.TButton")
        submit.grid(row=2, column=0, columnspan=2, padx=5, pady=5)

        def view():

            if query_oi.get() == "-": # Cannot be default choice
                messagebox.showerror("Invalid Input", "Please select a query.")
                return

            self.queryOI = query_oi.get()

            self.master.tab(self, text="Analyze - " + self.queryOI) # Update tab name

            self.unit = "score" # Always default to unit score upon viewing new query
            self.scale = "linear" # Always default to linear scale upon viewing new query
            self.filter = ["No Filter", "-", "-"]
            self.focus = "" # Focus fasta file in this query
            self.subjects = [] # List of all subject fasta files in this query

            self.orig_score = [] # 4 units of data
            self.orig_id = []
            self.orig_positive = []
            self.orig_gap = []
            self.orig_frequency = []
            self.peptide = []
            self.blast_reports = []

            with ZipFile("zip/" + self.queryOI + ".zip") as zipObj: # Read files in zip without having to extract
                with zipObj.open(self.queryOI+"/score.csv") as r:
                    first_line = True
                    for line in r:
                        line = line.decode("utf-8")
                        line = line.replace("\n", "").split(",")
                        if first_line:
                            first_line = False
                            self.indices[0] = int(line[1]) # Indices FROM and TO are read here
                            self.indices[1] = int(line[-2])
                        else:
                            self.subjects.append(line[0])
                            tmp_score = []
                            for a in range(1, line.__len__()-1):
                                tmp_score.append(float(line[a]))
                            self.orig_score.append(tmp_score)
                    r.close()
                with zipObj.open(self.queryOI+"/id.csv") as r:
                    first_line = True
                    for line in r:
                        line = line.decode("utf-8")
                        line = line.replace("\n", "").split(",")
                        if first_line:
                            first_line = False
                        else:
                            tmp_id = []
                            for a in range(1, line.__len__()-1):
                                tmp_id.append(float(line[a]))
                            self.orig_id.append(tmp_id)
                    r.close()
                with zipObj.open(self.queryOI+"/positive.csv") as r:
                    first_line = True
                    for line in r:
                        line = line.decode("utf-8")
                        line = line.replace("\n", "").split(",")
                        if first_line:
                            first_line = False
                        else:
                            tmp_pos = []
                            for a in range(1, line.__len__()-1):
                                tmp_pos.append(float(line[a]))
                            self.orig_positive.append(tmp_pos)
                    r.close()
                with zipObj.open(self.queryOI+"/gap.csv") as r:
                    first_line = True
                    for line in r:
                        line = line.decode("utf-8")
                        line = line.replace("\n", "").split(",")
                        if first_line:
                            first_line = False
                        else:
                            tmp_gap = []
                            for a in range(1, line.__len__()-1):
                                tmp_gap.append(float(line[a]))
                            self.orig_gap.append(tmp_gap)
                    r.close()
                with zipObj.open(self.queryOI+"/frequency.csv") as r:
                    first_line = True
                    for line in r:
                        line = line.decode("utf-8")
                        line = line.replace("\n", "").split(",")
                        if first_line:
                            first_line = False
                        else:
                            tmp_freq = []
                            for a in range(1, line.__len__()-1):
                                tmp_freq.append(float(line[a]))
                            self.orig_frequency.append(tmp_freq)
                    r.close()
                with zipObj.open(self.queryOI+"/peptide.csv") as r:
                    first_line = True
                    for line in r:
                        line = line.decode("utf-8")
                        line = line.replace("\n", "").split(",")
                        if first_line:
                            first_line = False
                        else:
                            tmp_pep = []
                            for a in range(1, line.__len__()-1):
                                line[a] = line[a].replace(">", "").split("|")
                                tmp_pep.append(line[a])
                            self.peptide.append(tmp_pep)
                    r.close()
                blast_reports = []
                tmp_index = 0
                with zipObj.open(self.queryOI+"/all_blastp.txt") as r:
                    mode = 0
                    skips = 3
                    this_report = ""
                    for line in r:
                        if skips != 0:
                            skips -= 1
                            continue
                        line = line.decode("utf-8")
                        if line == "****************************************************************************************************\n":
                            skips = 2
                            this_report = ""
                            mode = 0
                            continue
                        if line.__contains__("Query="):
                            this_report += line
                            mode = 1
                        elif mode == 1 and not line.__contains__("Effective search space used:"):
                            this_report += line
                        elif mode == 1 and line.__contains__("Effective search space used:"):
                            this_report += line
                            mode = 0
                            blast_reports.append(this_report)
                            this_report = ""
                    r.close()
                lower = 0
                upper = int(blast_reports.__len__()/self.subjects.__len__()) - 1
                for a in range(0, self.subjects.__len__()):
                    self.blast_reports.append(blast_reports[lower:upper+1])
                    lower = upper + 1
                    upper += int(blast_reports.__len__()/self.subjects.__len__())
                with zipObj.open(self.queryOI+"/all_blastp.txt") as r:
                    skipped_first_line = False
                    for line in r:
                        if not skipped_first_line:
                            skipped_first_line = True
                            continue
                        else:
                            line = line.decode("utf-8")
                            focus = line.replace("query=", "").split(",")[0].split("(")[0]
                            if focus.__contains__("/"):
                                self.focus = focus.split("/")[-1]
                            else:
                                self.focus = focus
                            break
                    r.close()

            self.score = deepcopy(self.orig_score)
            self.id = deepcopy(self.orig_id)
            self.positive = deepcopy(self.orig_positive)
            self.gap = deepcopy(self.orig_gap)
            self.frequency = deepcopy(self.orig_frequency)
            self.data = self.score
            if self.path != None:
                os.remove("viewing/"+self.path+"-hm.png")
                os.remove("viewing/"+self.path+"-x.png")
                os.remove("viewing/"+self.path+"-y.png")
            self.path = ''.join(random.choices(string.ascii_uppercase + string.digits, k = 10))
            col_headings = [] # Just a list of numbers from self.indices[0] to self.indices[1] inclusive
            for a in range(int(self.indices[0]), int(self.indices[1])+1):
                col_headings.append(a)
            gen_hxy(col_headings, self.subjects, self.data, self.scale, self.path) # Generate the heatmap
            # Render/Update the other parts of frame 1
            self.render_f12()
            self.render_f13()
            # self.render_f14()
            self.render_f2()

    ''' Widgets that give info as in what query is selected, focus fasta of query, etc. '''
    def render_f12(self):

        contain = ttk.LabelFrame(self.frame1, text="Current View", style="s1.TLabelframe")
        contain.grid(row=1, column=0, sticky="nesw", padx=5, pady=5)

        li1 = ttk.Label(contain, text="Query: " + self.queryOI, style="s1.TLabel") # Query selected
        li1.grid(row=0, column=0, sticky=W, padx=5, pady=5)
        focus_to_report = self.focus
        if self.focus.__len__() >= 12:
            focus_to_report = focus_to_report[:12] + "..."
        li2 = ttk.Label(contain, text="Focus: " + self.focus, style="s1.TLabel") # Focus fasta of selected Query 
        li2.grid(row=1, column=0, sticky=W, padx=5, pady=5)
        li3 = ttk.Label(contain, text="Unit: " + self.unit.upper(), style="s1.TLabel") # Unit selected of current view (SIPG)
        li3.grid(row=2, column=0, sticky=W, padx=5, pady=5)
        li4 = ttk.Label(contain, text="Scale: " + self.scale.upper(), style="s1.TLabel") # Scale selected of current view 
        li4.grid(row=3, column=0, sticky=W, padx=5, pady=5)
        li5 = ttk.Label(contain, text="Filter: " + self.filter[0] + " [" + str(self.filter[1]) + ", " + str(self.filter[2]) + "]", style="s1.TLabel") # Filter characteristics if any applied
        li5.grid(row=4, column=0, sticky=W, padx=5, pady=5)

    def render_f13(self):

        # Menu to change what unit heatmap displays and is scaled againt
        contain1 = ttk.LabelFrame(self.frame1, text="Heatmap Unit", style="s1.TLabelframe")
        contain1.grid(row=2, column=0, sticky="nesw", padx=5, pady=5)
        unit_btn_frame = ttk.Frame(contain1)
        unit_btn_frame.pack(padx=5, pady=5)
        score_button = ttk.Button(unit_btn_frame, text="Score", command=lambda: unit_score(), style="s1.TButton")
        score_button.grid(row=0, column=0, sticky="nesw", padx=5, pady=5)
        id_button = ttk.Button(unit_btn_frame, text="ID", command=lambda: unit_id(), style="s1.TButton")
        id_button.grid(row=0, column=1, sticky="nesw", padx=5, pady=5)
        pos_button = ttk.Button(unit_btn_frame, text="Positive", command=lambda:unit_positive(), style="s1.TButton")
        pos_button.grid(row=1, column=0, sticky="nesw", padx=5, pady=5)
        gap_button = ttk.Button(unit_btn_frame, text="Gap", command=lambda: unit_gap(), style="s1.TButton")
        gap_button.grid(row=1, column=1, sticky="nesw", padx=5, pady=5)

        col_headings = []
        for a in range(int(self.indices[0]), int(self.indices[1])+1):
            col_headings.append(a)

        def unit_score():
            
            self.unit = "score"
            self.data = self.score
            gen_hxy(col_headings, self.subjects, self.score, self.scale, self.path)
            self.render_f12()
            self.render_f2()

        def unit_id():

            self.unit = "id"
            self.data = self.id
            gen_hxy(col_headings, self.subjects, self.id, self.scale, self.path)
            self.render_f12()
            self.render_f2()

        def unit_positive():

            self.unit = "positive"
            self.data = self.positive
            gen_hxy(col_headings, self.subjects, self.positive, self.scale, self.path)
            self.render_f12()
            self.render_f2()
        
        def unit_gap():
            
            self.unit = "gap"
            self.data = self.gap
            '''
                Scaling is reversed for a graph with a unit of graph
                Stronger hits in a blast+ query have a higher scores, ids, and positives
                If 2 peptide sequences are similar, they have less peptides that differ from one another. 
                This can be interpretted as basically less gaps where the peptides differ, so a stronger hit has a lower gap value
            '''
            gen_hxy(col_headings, self.subjects, self.gap, self.scale, self.path, True)
            self.render_f12()
            self.render_f2()

        # Widgets to select how the heatmap scales RGB values
        contain2 = ttk.LabelFrame(self.frame1, text="Heatmap Scale", style="s1.TLabelframe")
        contain2.grid(row=3, column=0, sticky="nesw", padx=5, pady=5)
        scale_btn_frame = ttk.Frame(contain2)
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
            gen_hxy(col_headings, self.subjects, self.data, self.scale, self.path, reverse)
            self.render_f12()
            self.render_f2()

        def scale_x2():
            reverse = False
            if self.unit == "gap":
                reverse = True
            self.scale = "quadratic"
            gen_hxy(col_headings, self.subjects, self.data, self.scale, self.path, reverse)
            self.render_f12()
            self.render_f2()

        def scale_log():
            reverse = False
            if self.unit == "gap":
                reverse = True
            self.scale = "logarithmic"
            gen_hxy(col_headings, self.subjects, self.data, self.scale, self.path, reverse)
            self.render_f12()
            self.render_f2()

        # Widgets to alter heatmap filter
        contain3 = ttk.LabelFrame(self.frame1, text="Heatmap Filter", style="s1.TLabelframe")
        contain3.grid(row=4, column=0, sticky="nesw", padx=5, pady=5)
        filter_btn = ttk.Frame(contain3)
        filter_btn.pack(padx=5, pady=5)

        lirange = ttk.Label(filter_btn, text="Range:", style="s1.TLabel")
        lirange.grid(row=0, column=0, padx=5, pady=5)
        c3_frame = ttk.Frame(filter_btn)
        c3_frame.grid(row=1, column=0)
        _from = ttk.Entry(c3_frame, width=6, style="s1.TEntry")
        _from.grid(row=0, column=0, sticky=W, padx=5, pady=5)
        _li = ttk.Label(c3_frame, text="-", style="s1.TLabel")
        _li.grid(row=0, column=1, padx=5, pady=5)
        _to = ttk.Entry(c3_frame, width=6, style="s1.TEntry")
        _to.grid(row=0, column=2, sticky=W, padx=5, pady=5)
        filter_type = StringVar(value="null")
        li_filter = ttk.Label(filter_btn, text="Filter Type: ", style="s1.TLabel")
        li_filter.grid(row=2, column=0, padx=5, pady=5)

        radio_frame = ttk.Frame(filter_btn)
        radio_frame.grid(row=3, column=0, padx=5, pady=4)
        radio_score = ttk.Radiobutton(radio_frame, text="Score", variable=filter_type, value="score", style="s1.TRadiobutton")
        radio_score.grid(row=3, column=0, padx=5, sticky=W)
        radio_id = ttk.Radiobutton(radio_frame, text="ID", variable=filter_type, value="id", style="s1.TRadiobutton")
        radio_id.grid(row=3, column=1, padx=5, sticky=W)
        radio_positive = ttk.Radiobutton(radio_frame, text="Positive", variable=filter_type, value="positive", style="s1.TRadiobutton")
        radio_positive.grid(row=4, column=0, padx=5, sticky=W)
        radio_gap = ttk.Radiobutton(radio_frame, text="Gap", variable=filter_type, value="gap", style="s1.TRadiobutton")
        radio_gap.grid(row=4, column=1, padx=5, sticky=W)

        def filter_data():

            # Check the parameters if valid
            if filter_type.get() == "null": # Is filter type chosen
                messagebox.showerror("Invalid Input", "Please select the type of filter.")
                return
            if _from.get() == "" and _to.get() == "": # Are filter indices both not blanks?
                messagebox.showerror("Invalid Input", "Please enter indices of the filter.")
                return
            try:
                # Are filter indices correct in comparison to one another and are both above 0? (From < To)
                if (_from.get() != "" and _to.get() != "" and float(_from.get()) > float(_to.get())) or (_from.get() != "" and float(_from.get()) < 0) or (_to.get() != "" and float(_to.get()) < 0):
                    messagebox.showerror("Invalid Input", "Please enter valid indices.")
                    return
            except:
                # If unable convert to a float, most likely the entry does not hold a number
                messagebox.showerror("Invalid Input", "Filter Indices are not seen as legitimate numbers.")

            # Update the filters
            _from_value = "-"
            if _from.get() != "":
                _from_value = float(_from.get())
            _to_value = "-"
            if _to.get() != "":
                _to_value = float(_to.get())
            self.filter = [filter_type.get(), _from_value, _to_value]

            '''
                3 modes of filtration
                bound - a upper and lower limit are given
                ceiling - a upper limit is only given
                floor - a lower limit is only given
            '''
            filter_mode = ""
            if self.filter[1] == "-" and self.filter[2] != "-":
                filter_mode = "ceiling"
            elif self.filter[1] != "-" and self.filter[2] == "-":
                filter_mode = "floor"
            elif self.filter[1] != "-" and self.filter[2] != "-":
                filter_mode = "bound"

            # Before generating a new heatmap, delete previous hm if they exist
            if self.path != None:
                os.remove("viewing/"+self.path+"-hm.png")
                os.remove("viewing/"+self.path+"-x.png")
                os.remove("viewing/"+self.path+"-y.png")
            self.path = ''.join(random.choices(string.ascii_uppercase + string.digits, k = 10))

            # Fetch the original data to apply filters on
            self.score = deepcopy(self.orig_score)
            self.id = deepcopy(self.orig_id)
            self.positive = deepcopy(self.orig_positive)
            self.gap = deepcopy(self.orig_gap)
            self.frequency = deepcopy(self.orig_frequency)

            filter_by = None
            if filter_type.get() == "score":
                filter_by = self.score
            elif filter_type.get() == "id":
                filter_by = self.id
            elif filter_type.get() == "positive":
                filter_by = self.positive
            elif filter_type.get() == "gap":
                filter_by = self.gap

            # Different ways of filtering, already explained in block comment above
            if filter_mode == "bound":
                for a in range(0, filter_by.__len__()):
                    for b in range(0, filter_by[a].__len__()):
                        if (filter_by[a][b] > self.filter[2] or filter_by[a][b] < self.filter[1]) and filter_by[a][b] != -1:
                            self.score[a][b] = -2
                            self.id[a][b] = -2
                            self.positive[a][b] = -2
                            self.gap[a][b] = -2
                            self.frequency[a][b] = -2
            elif filter_mode == "ceiling":
                for a in range(0, filter_by.__len__()):
                    for b in range(0, filter_by[a].__len__()):
                        if filter_by[a][b] > self.filter[2]:
                            self.score[a][b] = -2
                            self.id[a][b] = -2
                            self.positive[a][b] = -2
                            self.gap[a][b] = -2
                            self.frequency[a][b] = -2
            elif filter_mode == "floor":
                 for a in range(0, filter_by.__len__()):
                    for b in range(0, filter_by[a].__len__()):
                        if filter_by[a][b] < self.filter[1] and filter_by[a][b] != -1: # Remember, -1 means no hit found, -2 means hit found, but filtered out
                            self.score[a][b] = -2
                            self.id[a][b] = -2
                            self.positive[a][b] = -2
                            self.gap[a][b] = -2
                            self.frequency[a][b] = -2

            # If filtering with a certain unit, most likely user wants to continue with that unit
            if filter_type.get() == "score":
                self.data = self.score
            elif filter_type.get() == "id":
                self.data = self.id
            elif filter_type.get() == "positive":
                self.data = self.positive
            elif filter_type.get() == "gap":
                self.data = self.gap
            self.unit = filter_type.get()

            col_headings = []
            for a in range(int(self.indices[0]), int(self.indices[1])+1):
                col_headings.append(a)
            if self.unit != "gap":
                gen_hxy(col_headings, self.subjects, self.data, self.scale, self.path)
            else:
                gen_hxy(col_headings, self.subjects, self.data, self.scale, self.path, True)

            self.render_f12()
            self.render_f13()
            self.render_f2()

        contain_7_0 = ttk.Frame(filter_btn)
        contain_7_0.grid(row=7, column=0, padx=5, pady=5)

        apply_filter = ttk.Button(contain_7_0, text="Apply Filter", command=lambda: filter_data(), style="s1.TButton")
        apply_filter.grid(row=0, column=0, padx=5, pady=5)

        def remove_filter():

            # Resets the filter as in render_11()
            self.filter = ["No Filter", "-", "-"]

            # Fetch the original data to apply filters on
            self.score = deepcopy(self.orig_score)
            self.id = deepcopy(self.orig_id)
            self.positive = deepcopy(self.orig_positive)
            self.gap = deepcopy(self.orig_gap)
            self.frequency = deepcopy(self.orig_frequency)

            # Recycled code

            if self.unit == "score":
                self.data = self.score
            elif self.unit == "id":
                self.data = self.id
            elif self.unit == "positive":
                self.data = self.positive
            elif filter_type.get() == "gap":
                self.data = self.gap

            os.remove("viewing/"+self.path+"-hm.png")
            os.remove("viewing/"+self.path+"-x.png")
            os.remove("viewing/"+self.path+"-y.png")
            self.path = ''.join(random.choices(string.ascii_uppercase + string.digits, k = 10))

            col_headings = []
            for a in range(int(self.indices[0]), int(self.indices[1])+1):
                col_headings.append(a)
            if self.unit != "gap":
                gen_hxy(col_headings, self.subjects, self.data, self.scale, self.path)
            else:
                gen_hxy(col_headings, self.subjects, self.data, self.scale, self.path, True)

            self.render_f12()
            self.render_f13()
            self.render_f2()

        rm_filter = ttk.Button(contain_7_0, text="Remove Filter", command=lambda: remove_filter(), style="s1.TButton")
        rm_filter.grid(row=0, column=1, padx=5, pady=5)

        contain4 = ttk.LabelFrame(self.frame1, text="Export Heatmap", style="s1.TLabelframe")
        contain4.grid(row=6, column=0, sticky="nesw", padx=5, pady=5)

        export_hm = ttk.Frame(contain4)
        export_hm.pack(padx=5, pady=5)
        li4 = ttk.Label(export_hm, text="Path to Export:", style="s1.TLabel")
        li4.grid(row=0, column=0, sticky=W, padx=5, pady=5)
        button_browse = ttk.Button(export_hm, text="Browse", command=lambda: browse_export(), style="s1.TButton")
        button_browse.grid(row=0, column=1, sticky=E, padx=5)

        def browse_export():

            foldername = filedialog.askdirectory()
            export_var.set(foldername)

        export_var = StringVar()
        export_path = ttk.Entry(export_hm, textvariable=export_var, style="s1.TEntry")
        export_path.grid(row=1, column=0, columnspan=2, sticky="nesw", padx=5, pady=5)

        submit = ttk.Button(export_hm, text="Export", command=lambda: export_heatmap(), style="s1.TButton")
        submit.grid(row=4, column=0, columnspan=2, padx=5, pady=5)

        ''' Export the heatmap '''
        def export_heatmap():
            
            # Parameter checking
            if export_var.get() == "":
                messagebox.showerror("Invalid Input", "Please select a valid path to export the heatmap to.")
                return
            elif not path.exists((export_var.get())):
                messagebox.showerror("Invalid Input", "The path to export the image is not found in the computer. Please ensure the path is valid.")
                return
            export_as = export_var.get()  + "/" + self.queryOI + "-" + ''.join(random.choices(string.ascii_uppercase + string.digits, k = 5)) + ".png"
            gen_export(self.path, export_as)
            messagebox.showinfo("Exported Heatmap Successfully", "The heatmap can be found at: " + export_as)
    
    '''
    def render_f14(self):

        contain = ttk.LabelFrame(self.frame1, text="Background Processes", style="s1.TLabelframe")
        contain.grid(row=7, column=0, sticky="nesw", padx=5, pady=5)

        self.status = ttk.Label(contain, text="None", style="s1.TLabel")
        self.status.grid(row=0, column=0, sticky="nesw", padx=5, pady=5)

        self.statusbar = ttk.Progressbar(contain, orient=HORIZONTAL, length=100, mode="determinate")
        self.statusbar['value'] = 100
        self.statusbar.grid(row=1, column=0, sticky="nesw", padx=5, pady=5)
    '''

    def render_f2(self):

        panX = panXCanvas(self.frame2, height=20)
        self.imgX = PhotoImage(file="viewing/"+self.path+"-x.png")      
        panX.create_image(0, 0, anchor=NW, image=self.imgX) 
        panX.grid(row=0, column=1, sticky="nesw")

        panY = panYCanvas(self.frame2, width=250, height=(self.subjects.__len__()+2)*20)
        self.imgY = PhotoImage(file="viewing/"+self.path+"-y.png")
        panY.create_image(0, 0, anchor=NW, image=self.imgY)
        panY.grid(row=1, column=0, sticky="nesw")

        aFrame_self = self # This is made to access aFrame obj since self in panMaster refers to the panMaster instance

        class panMaster(panCanvas): # Custom class to work with panX and panY

            # I don't like doing it this way but I want it all to connect to instances of panX and panY

            def __init__(self, master, **kwargs):

                Canvas.__init__(self, master, kwargs)
                self.bind("<B1-Motion>", self.drag)
                self.bind("<Button-1>", self.click)
                self.bind("<ButtonRelease-1>", self.release)
                self.bind("<Double-Button-1>", self.doubleclick)
                self.bind("<Shift-Button-1>", self.shiftclick)
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
                if plotx < 0 or ploty < 0 or plotx > self.master.master.indices[1] or ploty > self.master.master.subjects.__len__(): 
                    return
                plotx = floor(plotx)
                ploty = floor(ploty)
                query_to_display = self.master.master.queryOI
                report_to_display = self.master.master.blast_reports[ploty][plotx]
                subject_report = self.master.master.subjects[ploty]
                index_report = self.master.master.indices[0] + plotx
                focus_report = self.master.master.focus

                tab = ttk.Frame(self.master.master.master)

                center_frame = ttk.LabelFrame(tab, text="Report Details", style="s1.TLabelframe")
                center_frame.grid(row=0, column=0, sticky="", padx=5, pady=5)
                center_frame.place(in_=tab, anchor="c",relx=.5, rely=.5)

                # Details about query to show
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

                # Compile a formatted list of links
                peptide_focus_link = report_to_display.split("\n")[0].split(" ")[0]
                links = "Focus Peptide:\nhttps://www.ncbi.nlm.nih.gov/protein/" + peptide_focus_link + "\n\nSubject Peptides:\n"
                if self.master.master.peptide[ploty][plotx] == ["0"]:
                    links += "NO HIT\n"
                else:
                    for a in range(0, self.master.master.peptide[ploty][plotx].__len__()):
                        links += "https://www.ncbi.nlm.nih.gov/protein/" + self.master.master.peptide[ploty][plotx][a].replace("  ", " ").split(" ")[1] + "\n"
                display_report.insert(END, links+"\n")
                display_report.insert(END, report_to_display)

                self.master.master.master.add(tab, text="Blast Report")
                self.master.master.master.select([self.master.master.master.tab(i, option="text") for i in self.master.master.master.tabs()].__len__()-1)
            
            def shiftclick(self, event):

                plotx, ploty = self.coords(1)
                plotx -= event.x
                ploty -= event.y
                plotx /= -40
                ploty /= -20
                if plotx < 0 or ploty < 0 or plotx >= self.master.master.indices[1] or ploty >= self.master.master.subjects.__len__(): 
                    return
                plotx = floor(plotx)
                ploty = floor(ploty)

                # Collect the peptide of every subject and the focus to create the correlation matrix
                seqs = []
                seq_names = []
                adj_index = plotx - aFrame_self.indices[0] + 1
                these_subjects = []
                for a in range(0, aFrame_self.blast_reports.__len__()):
                    first_sbjct = False
                    this_peptide = ""
                    this_seq_name = ""
                    this_report = aFrame_self.blast_reports[a][adj_index].split("\n")
                    for b in range(0, this_report.__len__()):
                        line = this_report[b]
                        if not first_sbjct and line.__contains__(">"):
                            first_sbjct = True
                            this_seq_name = line
                            if line.__contains__("[") and not line.__contains__("]"):
                                this_seq_name += this_report[b+1]
                            continue
                        if first_sbjct and line.__contains__("***** No hits found *****"):
                            break
                        if first_sbjct and line.__contains__("Sbjct"):
                            while line.__contains__("  "):
                                line = line.replace("  ", " ")
                            line = line.split(" ")
                            this_peptide += line[2] + "\n"
                            continue
                        if first_sbjct and line.__contains__("Lambda"):
                            break
                    if this_seq_name != "":
                        this_peptide = this_peptide.replace("-", "")
                        seqs.append(this_peptide.replace("\n", ""))
                        seq_names.append(this_seq_name.replace("\r", "").replace("\n", ""))
                        these_subjects.append(aFrame_self.subjects[a])

                if seqs.__len__() > 1: # Only run when more than 1 hit is found, 1x1 HM is useless

                    def launch_cFrame():

                        messagebox.showinfo("Correlation HM", "request has been acknowledged and is processing in the background.")
                        s, i, p, g, reports = corr_blastp(seqs, seq_names, aFrame_self.path)
                        new_cFrame = cFrame(self.master.master.master, these_subjects, aFrame_self.queryOI, aFrame_self.unit, adj_index, seqs, seq_names, s, i, p, g, reports)
                        self.master.master.master.add(new_cFrame, text="HM Correlation - " + aFrame_self.queryOI + " | PI:" + str(plotx+1))
                        self.master.master.master.select([self.master.master.master.tab(i, option="text") for i in self.master.master.master.tabs()].__len__()-1)

                    t = threading.Thread(target=launch_cFrame)
                    t.start()

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

        panLR = ttk.Frame(self.frame2)
        panLR.grid(row=0, column=0)
        button_left = ttk.Button(panLR, text=u"\u2190", command=lambda: pan_left(), style="s1.TButton")
        button_left.grid(row=0, column=0, padx=5, pady=5)
        button_right = ttk.Button(panLR, text=u"\u2192", command=lambda: pan_right(), style="s1.TButton")
        button_right.grid(row=0, column=1, padx=5, pady=5)

    def destroy(self):

        Frame.destroy(self)
        if self.path != None:
            os.remove("viewing/"+self.path+"-hm.png")
            os.remove("viewing/"+self.path+"-x.png")
            os.remove("viewing/"+self.path+"-y.png")
