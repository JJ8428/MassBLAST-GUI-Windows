import tkinter as tk
from tkinter import ttk, filedialog
from tkinter import *
from custom_tk import *
from os import path
from blastp import *
import threading
from threadQ import threadQueue

class nqFrame(Frame):

    def __init__(self, queue, master, **kwargs):
        
        self.queue = queue
        Frame.__init__(self, master, **kwargs)
        self.query = {
            "focus_path" : "",
            "subject_path" : "",
            "from" : "",
            "to" : "",
            "subject_files" : "",
            "save_as" : "",
            "notify" : 0
        }
        self.s1 = ttk.Style(self)
        self.s1_font = ("Segoe UI", 8)
        self.s1.configure("s1.TLabelframe", font=self.s1_font)
        self.s1.configure("s1.TLabel", font=self.s1_font)
        self.s1.configure("s1.TEntry", font=self.s1_font)
        self.s1.configure("s1.TButton", font=self.s1_font)
        self.s1.configure("s1.TNotebook.Tab", font=self.s1_font)
        self.s1.configure("s1.TCheckbutton", font=self.s1_font)
        self.s1.configure("s1.TNotebook.Tab", background="#d9d9d9")
        self.step1()

    def clear(self):

        for widget in self.winfo_children():
            widget.destroy()
        
    def step1(self):

        self.clear()
        central_frame = ttk.LabelFrame(self, text="New Query - Step 1", style="s1.TLabelframe")
        central_frame.pack(padx=5, pady=5)
        central_frame.place(in_=self, anchor="c",relx=.5, rely=.5)

        label_focus = ttk.Label(central_frame, text="Please select the focus fasta file:", style="s1.TLabel")
        label_focus.grid(row=0, column=0, sticky=tk.W, padx=5, pady=5)

        def browse_focus():

            filename = filedialog.askopenfilename(filetypes=[("fasta", "*.faa"), ("fasta", "*.fasta")])
            focus.set(filename)
        
        browse_f = ttk.Button(central_frame, text="Browse", command=lambda: browse_focus(), style="s1.TButton")
        browse_f.grid(row=0, column=1, padx=5, pady=5)
        focus = StringVar()
        focus.set(self.query["focus_path"])
        focus_path = ttk.Entry(central_frame, textvariable=focus, style="s1.TEntry")
        focus_path.grid(row=1, column=0, columnspan=2, sticky="nesw", padx=5, pady=5)

        label_subjects = ttk.Label(central_frame, text="Please select the folder containing subject fasta file(s):", style="s1.TLabel")
        label_subjects.grid(row=2, column=0, sticky=tk.W, padx=5, pady=5)

        def browse_subject():

            foldername = filedialog.askdirectory()
            subject.set(foldername)
        
        subject = StringVar()
        subject.set(self.query["subject_path"])
        browse_s = ttk.Button(central_frame, text="Browse", command=lambda: browse_subject(), style="s1.TButton")
        browse_s.grid(row=2, column=1, padx=5, pady=5)
        subject_path = ttk.Entry(central_frame, textvariable=subject, style="s1.TEntry")
        subject_path.grid(row=3, column=0, columnspan=2, sticky="nesw", padx=5, pady=5)

        def next1():
            
            if focus_path.get() == "" or subject_path.get() == "":
                messagebox.showerror("Invalid Input", "Please choose or enter the paths for the focus fasta file and/or folder containing subject fasta files.")
                return
            elif not path.exists(focus_path.get()):
                messagebox.showerror("Invalid Input", "The path to the focus file: " + focus_path.get() + ", is not found in the computer. Please ensure the path is valid.")
                return
            elif not path.exists(subject_path.get()):
                messagebox.showerror("Invalid Input", "The path to the folder containing subject fasta file(s): " + subject_path.get() + ", is not found in the computer. Please ensure the path is valid.")
                return
            self.query["focus_path"] = focus_path.get()
            self.query["subject_path"] = subject_path.get()
            self.step2()

        submit = ttk.Button(central_frame, text="Next", command=lambda: next1(), style="s1.TButton")
        submit.grid(row=4, column=0, columnspan=2, padx=5, pady=5)

    def step2(self):
        
        self.clear()
        central_frame = ttk.LabelFrame(self, text="New Query - Step 2", style="s1.TLabelframe")
        central_frame.pack(padx=5, pady=5)
        central_frame.place(in_=self, anchor="c",relx=.5, rely=.5)

        r = open(self.query["focus_path"])
        peptideCount = 0
        for line in r.readlines():
            if line.__contains__('>'):
                peptideCount += 1
        label_peptide_count = ttk.Label(central_frame, text="The provided focus fasta file contains " + str(peptideCount) + " peptide sequences.", style="s1.TLabel")
        label_peptide_count.grid(row=0, column=0, sticky=tk.W, padx=5, pady=5)
        label_instruction_indices = ttk.Label(central_frame, text="Please enter the indices of the peptide sequences to process: (inclusive)", style="s1.TLabel")
        label_instruction_indices.grid(row=1, column=0, sticky=tk.W, padx=5, pady=5)

        inputs_frame = ttk.Frame(central_frame)
        inputs_frame.grid(row=2, column=0, sticky=tk.W, padx=5, pady=5)
        label_from = ttk.Label(inputs_frame, text="From: ", style="s1.TLabel")
        label_from.grid(row=0, column=0, sticky=E, padx=5, pady=5)
        peptides_from = numEntry(inputs_frame, font=self.s1_font)
        peptides_from.grid(row=0, column=1, sticky=tk.W, padx=5, pady=5)
        peptides_from.insert(END, self.query["from"])
        label_from = ttk.Label(inputs_frame, text="To: ", style="s1.TLabel")
        label_from.grid(row=1, column=0, stick=E, padx=5, pady=5)
        peptides_to = numEntry(inputs_frame, font=self.s1_font)
        peptides_to.grid(row=1, column=1, sticky=tk.W, padx=5, pady=5)
        peptides_to.insert(END, self.query["to"])

        filelist = []
        for filename in sorted(os.listdir(self.query["subject_path"])):
                filelist.append(filename)

        if filelist.__len__() <= 50:
            instruction_subject = ["The LEFT rectangle contains every files found within the given folder containing said subject fasta file(s).",
                                   "Drag and drop any choice of files into the RIGHT rectagle and arrange from top to bottom the order of file to process."]
            label_instruction_subject_0 = ttk.Label(central_frame, text=instruction_subject[0], style="s1.TLabel")
            label_instruction_subject_0.grid(row=3, column=0, sticky=tk.W, padx=5, pady=5)
            label_instruction_subject_1 = ttk.Label(central_frame, text=instruction_subject[1], style="s1.TLabel")
            label_instruction_subject_1.grid(row=4, column=0, sticky=tk.W, padx=5, pady=5)
            canvas_subjects = ddCanvas(central_frame, height=(filelist.__len__() + 3)*15, width=500, bg="white")
            canvas_subjects.grid(row=5, column=0, padx=5, pady=5)
            canvas_subjects.create_line(250, (filelist.__len__()+3)*15, 250, 0, tags="LOCKED")
            for a in range(0, filelist.__len__()):
                if not self.query["subject_files"].__contains__(filelist[a]):
                    canvas_subjects.create_text(125, 15*(a+2), font=("Segoe UI", 7), text=filelist[a], tags=filelist[a])
            for b in range(0, self.query["subject_files"].__len__()):
                canvas_subjects.create_text(375, 15*(b+2), font=("Segoe UI", 7), text=self.query["subject_files"][b], tags=self.query["subject_files"][b])
            check_var = IntVar()
            check_all = ttk.Checkbutton(central_frame, text=" Ignore the drag and drop above and SELECT ALL fasta files", variable=check_var, style="s1.TCheckbutton")
            check_all.grid(row=6, column=0, columnspan=2, padx=5, pady=5)
        else:
            instruction_subject = ["The provided source folder contains more than 50 files.",
                                   "The GUI is unable to render without comprimising screen porportions.",
                                   "All files in source folder will be used in the MassBlast query."]
            label_instruction_subject_0 = ttk.Label(central_frame, text=instruction_subject[0], style="s1.TLabel")
            label_instruction_subject_0.grid(row=3, column=0, sticky=tk.W, padx=5, pady=5)
            label_instruction_subject_1 = ttk.Label(central_frame, text=instruction_subject[1], style="s1.TLabel")
            label_instruction_subject_1.grid(row=4, column=0, sticky=tk.W, padx=5, pady=5)
            label_instruction_subject_2 = ttk.Label(central_frame, text=instruction_subject[2], style="s1.TLabel")
            label_instruction_subject_2.grid(row=5, column=0, sticky=tk.W, padx=5, pady=5)

        frame_submit = ttk.Frame(central_frame)
        frame_submit.grid(row=7, column=0, columnspan=2, padx=5, pady=5)
        submit_next = ttk.Button(frame_submit, text="Next", command=lambda: next2(), style="s1.TButton")
        submit_next.grid(row=0, column=1, padx=5, pady=5)
        submit_back = ttk.Button(frame_submit, text="Back", command=lambda: back2(), style="s1.TButton")
        submit_back.grid(row=0, column=0, padx=5, pady=5)

        def next2():

            if peptides_from.get() == "" or peptides_to.get() == "":
                messagebox.showerror("Invalid Input", "Please enter peptide indices.")
                return
            if int(peptides_from.get()) > int(peptides_to.get()):
                messagebox.showerror("Invalid Input", "The peptide indices in FROM must be lesser than or equal to TO.")
                return
            if int(peptides_from.get()) <= 0 or int(peptides_to.get()) > peptideCount:
                messagebox.showerror("Invalid Input", "Peptide indices FROM and TO can only range between 1 and " + str(peptideCount) + " (inclusive)")
                return
            if filelist.__len__() <= 50:
                canvas_indices = canvas_subjects.find_all()
                canvas_tags = []
                for index in canvas_indices:
                    canvas_tags.append(canvas_subjects.gettags(index))
                selected_files = []
                x_coord = []
                for a in range(0, canvas_tags.__len__()):
                    if canvas_tags[a][0] != "LOCKED" and (canvas_subjects.coords(canvas_tags[a])[0] > 251 or check_var.get() == 1):
                        selected_files.append(canvas_tags[a][0])
                        x_coord.append(canvas_subjects.coords(canvas_tags[a])[1])
                subject_files = [x for _,x in sorted(zip(x_coord, selected_files))]
                if subject_files.__len__() == 0 and check_var.get() == 0:
                    messagebox.showerror("Invalid Input", "Please select atleast one subject fasta file to compare with the focus fasta file.")
                    return
                self.query["subject_files"] = subject_files
            else:
                self.query["subject_files"] = filelist              
            self.query["from"] = peptides_from.get()
            self.query["to"] = peptides_to.get()
            self.step3()

        def back2():
            
            subject_files = []
            if filelist.__len__() <= 50:    
                canvas_indices = canvas_subjects.find_all()
                canvas_tags = []
                for index in canvas_indices:
                    canvas_tags.append(canvas_subjects.gettags(index))
                selected_files = []
                x_coord = []
                for a in range(0, canvas_tags.__len__()):
                    if canvas_subjects.gettags(canvas_tags[a]) != "LOCKED" and canvas_subjects.coords(canvas_tags[a])[0] > 250:
                        selected_files.append(canvas_tags[a][0])
                        x_coord.append(canvas_subjects.coords(canvas_tags[a])[1])
                subject_files = [x for _,x in sorted(zip(x_coord, selected_files))]
            self.query["from"] = peptides_from.get()
            self.query["to"] = peptides_to.get()
            self.query["subject_files"] = subject_files
            self.step1()

    def step3(self):

        self.clear()
        central_frame = ttk.LabelFrame(self, text="New Query - Step 3", style="s1.TLabelframe")
        central_frame.pack(padx=5, pady=5)
        central_frame.place(in_=self, anchor="c",relx=.5, rely=.5)

        label_name = ttk.Label(central_frame, text="Please enter a name to save this query as:", style="s1.TLabel")
        label_name.grid(row=0, column=0, sticky=W, padx=5, pady=5)
        entry_name = ttk.Entry(central_frame, style="s1.TEntry")
        entry_name.grid(row=0, column=1, sticky=W, padx=5, pady=5)
        entry_name.insert(END, self.query["save_as"])

        checked = IntVar()
        checked.set(self.query["notify"])
        check_quiet = ttk.Checkbutton(central_frame, text=" Notify user upon completion of executing the query", variable=checked, style="s1.TCheckbutton")
        check_quiet.grid(row=1, column=0, sticky=W, padx=5, pady=5)

        frame_submit = ttk.Frame(central_frame, style="s1.TFrame")
        frame_submit.grid(row=2, column=0, columnspan=2, padx=5, pady=5)
        submit_next = ttk.Button(frame_submit, text="Submit", command=lambda: next3(), style="s1.TButton")
        submit_next.grid(row=0, column=1, padx=5, pady=5)
        submit_back = ttk.Button(frame_submit, text="Back", command=lambda: back3(), style="s1.TButton")
        submit_back.grid(row=0, column=0, padx=5, pady=5)

        def next3():

            if entry_name.get() == "":
                messagebox.showerror("Invalid Input", "Please enter a name to save the query under.")
                return
            r = open("metadata/history.csv")
            history = []
            for line in r.readlines():
                line = line.replace("\n", "").split(", ")
                history.append(line)
            r.close()
            shared_name = False
            for record in history:
                if record[-2] == entry_name.get():
                    shared_name = True
                    break
            if shared_name:
                response = messagebox.askyesno("Warning", "There is a pre-existing query saved with the same name. Selecting YES will overwrite the pre-existing query with this query. Proceed?")
                if response == 0:
                    return
            self.query["save_as"] = entry_name.get()
            self.query["notify"] = checked.get()
            add_history(self.query["focus_path"], int(self.query["from"]), int(self.query["to"]), self.query["subject_path"], self.query["subject_files"], self.query["save_as"], "LOCAL")
            t = threading.Thread(target=massblastp, args=[self.query["focus_path"], int(self.query["from"]), int(self.query["to"]), self.query["subject_path"], self.query["subject_files"], self.query["save_as"], self.query["notify"]])
            self.queue.addJob(t)
            self.step4()

        def back3():

            self.query["save_as"] = entry_name.get()
            self.query["notify"] = checked.get()
            self.step2()
        
    def step4(self):

        self.clear()
        central_frame = ttk.LabelFrame(self, text="New Query Submitted", style="s1.TLabelframe")
        central_frame.pack(padx=5, pady=5)
        central_frame.place(in_=self, anchor="c",relx=.5, rely=.5)
        conclude = ttk.Label(central_frame, text="Query " + self.query["save_as"] + " has been submitted. You can view the data using ANALYZE after it has been fully executed and processed.", style="s1.TLabel")
        conclude.grid(row=0, column=0, sticky=W, padx=5, pady=5)
