import tkinter as tk
from tkinter import ttk, messagebox, filedialog
from tkinter import *
from custom_tk import *
from os import path
from blastp import *
import threading
from shutil import copyfile
from zipfile import ZipFile

class vlFrame(Frame):

    def __init__(self, master, starting_mode, **kwargs):

        Frame.__init__(self, master, **kwargs)
        self.mode = starting_mode
        self.thread = None # Thread to auto update 
        self.kill = False # Switch made to kill vlFrame's thread
        self.history = None # Dictionary that contains history
        self.tree = None # Only exists to expand scope of treeview

        master_frame = ttk.Frame(self)
        master_frame.pack(padx=5, pady=5)
        master_frame.place(anchor="s",relx=.5, rely=.5)
        self.master_frame = master_frame # Frame to hold all widgets

        frame_1 = ttk.Frame(self.master_frame)
        frame_1.grid(row=0, column=0, padx=0, pady=0)
        self.frame1 = frame_1 # 1/2 of master
        self.render_f1(0)

        frame_2 = ttk.LabelFrame(self.master_frame, text="")
        frame_2.grid(row=0, column=1, padx=0, pady=0)
        self.frame2 = frame_2 # 2/2 of master
        self.render_f2(None, 0)

        self.s1 = ttk.Style(self)
        self.s1_font = ("Segoe UI", 8)
        self.s1.configure("s1.TLabelframe", font=self.s1_font)
        self.s1.configure("s1.TLabel", font=self.s1_font)
        self.s1.configure("s1.TEntry", font=self.s1_font)
        self.s1.configure("s1.TButton", font=self.s1_font)
        self.s1.configure("s1.TNumentry", font=self.s1_font)
        self.s1.configure("s1.TCheckbutton", font=self.s1_font)
        self.s1.configure("s1.Treeview", font=self.s1_font)
        self.s1.configure("s1.TRadiobutton", font=self.s1_font)

    def render_f1(self, index):

        ''' Render the table the first time '''

        table_frame = ttk.Frame(self.frame1) # This exists so we don't delete all widgets in frame1
        table_frame.grid(row=0, column=0, padx=5, pady=5)

        cols = ("Focus Fasta File", "Subject Folder", "Save As")
        tree = ttk.Treeview(table_frame, columns=cols, show="headings", style="s1.Treeview")
        tree.grid(row=0, column=0, padx=5, pady=5)
        tree.column("Focus Fasta File", width=125)
        tree.column("Subject Folder", width=125)
        tree.column("Save As", width=125)
        for col in cols:
            tree.heading(col, text=col)
        history = get_history()
        for a in range(0, history.__len__()):
            tree.insert("", "end", values=(history[a]["focus_path"].split("/")[-1], history[a]["subject_folder"].split("/")[-1], history[a]["save_as"]))
        tree.bind("<ButtonRelease-1>", lambda event: self.render_f2(event, get_index()))
        self.tree = tree

        children_id = self.tree.get_children()
        if children_id.__len__() != 0:
            self.tree.focus(children_id[index])
            self.tree.selection_set(children_id[index])

        ''' Render the table again if history changes '''
        def render_table():   
            
            if not self.kill: # Kill switch since threading module cannot be manually terminated
                threading.Timer(2.5, render_table).start() # Thread to recursively render the treeview every 2.5 sec
                history = get_history()
                if self.history != history or self.history == None:
                    self.history = history
                    for widget in table_frame.winfo_children():
                        widget.destroy()
                    cols = ("Focus Fasta File", "Subject Folder", "Save As")
                    tree = ttk.Treeview(table_frame, columns=cols, show="headings", style="s1.Treeview")
                    tree.grid(row=0, column=0, padx=5, pady=5)
                    tree.column("Focus Fasta File", width=125)
                    tree.column("Subject Folder", width=125)
                    tree.column("Save As", width=125)
                    for col in cols:
                        tree.heading(col, text=col)
                    for a in range(0, history.__len__()):
                        tree.insert("", "end", values=(history[a]["focus_path"].split("/")[-1], history[a]["subject_folder"].split("/")[-1], history[a]["save_as"]))
                    tree.bind("<ButtonRelease-1>", lambda event: self.render_f2(event, get_index()))
                    self.tree = tree
                    children_id = self.tree.get_children()
                    if children_id.__len__() != 0:
                        self.tree.focus(children_id[index])
                        self.tree.selection_set(children_id[index])

        ''' Keep reference to thread to delete later '''
        self.thread = threading.Thread(target=render_table)
        self.thread.start()

        # Buttons to switch modes
        modes_frame = ttk.Frame(self.frame1)
        modes_frame.grid(row=1, column=0, padx=5, pady=5)
        more_details = ttk.Button(modes_frame, text="More Details", command=lambda: give_details(), style="s1.TButton")
        more_details.grid(row=0, column=0)
        delete_this_query = ttk.Button(modes_frame, text="Delete Query", command=lambda: delete_query(), style="s1.TButton")
        delete_this_query.grid(row=0, column=1)
        import_this_query = ttk.Button(modes_frame, text="Import Query", command=lambda: import_query(), style="s1.TButton")
        import_this_query.grid(row=1, column=0)
        export_this_query = ttk.Button(modes_frame, text="Export Query", command=lambda: export_query(), style="s1.TButton")
        export_this_query.grid(row=1, column=1)

        def get_index():
            
            history = get_history()
            if history.__len__() != 0:
                children_id = self.tree.get_children()
                index = children_id.index(self.tree.focus())
                return index # Index of choice selected on the tree

        def give_details():

            self.mode = "give_info"
            self.render_f2(None, get_index())

        def delete_query():

            # Parameter checking
            if self.history.__len__() == 0:
                # messagebox.showerror("No Existing Queries", "There is no existing query to call this function on. Please create/execute a few queries before trying to delete a query.")
                return
            data = self.history[get_index()]
            response = messagebox.askyesno("Warning", "Are you sure you want to delete " + data["save_as"] + "? Deletion can later be reversed by importing the query's zip file.")
            if response == 0:
                return
            # Delete the zip containing the save
            os.remove("zip/"+data["save_as"]+".zip")

            # Rewrite the metadata 
            w = open("metadata/history.csv", "w")
            to_write = ''
            for a in range(0, self.history.__len__()):
                if self.history[a] != data:
                    to_write += self.history[a]["focus_path"] + ", " + self.history[a]["from"] + ", " + self.history[a]["to"] + ", " + self.history[a]["subject_folder"] + ", ["
                    for b in range (0, self.history[a]["subject_files"].__len__()):
                        to_write += self.history[a]["subject_files"][b]
                        if b+1 != self.history[a]["subject_files"].__len__():
                            to_write += "|"
                    to_write += "], " + self.history[a]["save_as"] + ", " + self.history[a]["source"] + "\n"
            if to_write.__len__() != 0:
                if to_write[-1] == '\n':
                    to_write = to_write[:-1]
            w.write(to_write)
            w.close()

            self.tree.delete(self.tree.selection())

        def import_query():

            self.mode = "import_query"
            self.render_f2(None, get_index())

        def export_query():

            self.mode = "export_query"
            self.render_f2(None, get_index())

    def render_f2(self, event, index):
        
        history = get_history()
        if index is None and self.mode != "import_query":
            return
        if history.__len__() == 0 and self.mode != "import_query":
            messagebox.showerror("No Existing Queries", "A query must exist before try to access/manage that query.")
            return
        
        for widget in self.frame2.winfo_children():
            widget.destroy()

        if self.mode == "give_info": # Different modes have different views
            
            data = history[index]

            self.frame2.config(text=data["save_as"]+" Details")

            frame_1 = ttk.Frame(self.frame2)
            frame_1.grid(row=0, column=0, sticky=W, padx=5, pady=5)
            label_11 = ttk.Label(frame_1, text="Full Focus Fasta File Path:", style="s1.TLabel")
            label_11.grid(row=0, column=0, sticky=W, padx=5, pady=5)
            label_12 = ttk.Label(frame_1, text=data["focus_path"], style="s1.TLabel")
            label_12.grid(row=1, column=0, sticky=W, padx=5, pady=5)

            frame_2 = ttk.Frame(self.frame2)
            frame_2.grid(row=1, column=0, sticky=W, padx=5, pady=5)
            label_21 = ttk.Label(frame_2, text="Peptide Indices:", style="s1.TLabel")
            label_21.grid(row=0, column=0, sticky=W, padx=5, pady=5)
            label_22 = ttk.Label(frame_2, text="(" + data["from"] + ", " + data["to"] + ")", style="s1.TLabel")
            label_22.grid(row=1, column=0, sticky=W, padx=5, pady=5)

            frame_3 = ttk.Frame(self.frame2)
            frame_3.grid(row=2, column=0, sticky=W, padx=5, pady=5)
            label_31 = ttk.Label(frame_3, text="Full Subject Folder Path:", style="s1.TLabel")
            label_31.grid(row=0, column=0, sticky=W, padx=5, pady=5)
            label_32 = ttk.Label(frame_3, text=data["subject_folder"], style="s1.TLabel")
            label_32.grid(row=1, column=0, sticky=W, padx=5, pady=5)

            sub_cols = ("Index", "Subject Files")
            listsub = ttk.Treeview(self.frame2, columns=sub_cols, show="headings", style="s1.Treeview")
            listsub.grid(row=3, column=0, padx=5, pady=5)
            listsub.config(height=8)
            for sub_col in sub_cols:
                listsub.heading(sub_col, text=sub_col)
            for a in range(0, data["subject_files"].__len__()):
                listsub.insert("", "end", values=(a+1, data["subject_files"][a]))

        elif self.mode == "import_query":
            
            self.frame2.config(text="Import Query")
            label_zip = ttk.Label(self.frame2, text="Please select the zip file of the query to import:", style="s1.TLabel")
            label_zip.grid(row=0, column=0, sticky=W, padx=5, pady=5)
            button_browse = ttk.Button(self.frame2, text="Browse", command=lambda: browse_import(), style="s1.TButton")
            button_browse.grid(row=0, column=1, sticky=W, padx=5, pady=5)

            def browse_import():

                filename = filedialog.askopenfilename(filetypes=[("zip", "*.zip")])
                import_var.set(filename)
            
            import_var = StringVar()
            import_path = ttk.Entry(self.frame2, textvariable=import_var, style="s1.TEntry")
            import_path.grid(row=1, column=0, columnspan=2, sticky="nesw", padx=5, pady=5)
            
            def _import():

                if import_var.get() == "":
                    messagebox.showerror("Invalid Input", "Please select the path of directory to export the data to.")
                    return
                with ZipFile(import_var.get()) as zipObj:
                    file_name = zipObj.namelist()
                    index = -1
                    for a in range(0, file_name.__len__()):
                        if file_name[a].split("/")[-1] == "all_blastp.txt":
                            index = a
                            break
                    if file_name.__len__() != 10 or index == -1:
                        messagebox.showerror("Invalid Input", "The selected file is not recognizable. Please ensure you are selecting a zip MassBlast generated.")
                        return
                    info = []
                    mode = 0
                    with zipObj.open(file_name[index]) as r:
                        for line in r:
                            line = line.decode("utf-8")
                            if mode == 0 and line.__contains__("****************************************************************************************************"):
                                mode = 1
                            elif mode == 1:
                                mode = 2
                                info.append(line)
                            elif mode == 2 and line.__contains__("****************************************************************************************************"):
                                mode = 0
                    tmp = info[0].split(", ")
                    focus = "???/" + tmp[0].split("/")[-1].split("(")[0]
                    index_from = tmp[0].split(".faa")[-1].replace("(", "").replace(")", "").split(",")[0]
                    index_to = tmp[0].split(".faa")[-1].replace("(", "").replace(")", "").split(",")[1]
                    subject_path = "???/" + tmp[1].split("/")[-1]
                    subject_files = []
                    save_as = tmp[-1].split("=")[-1].replace("\n", "")
                    for line in info:
                        line = line.split(", ")
                        line = line[2]
                        subject_files.append(line.split("=")[-1])
                    history = get_history()
                    shared = False
                    for record in history:
                        if record["save_as"] == save_as:
                            shared = True
                    if shared:
                        response = messagebox.askyesno("Warning", "There is a pre-existing query saved with the same name. Clicking YES will overwrite this query. Are you sure you want to proceed?")
                        if response == 0:
                            return
                    add_history(focus, index_from, index_to, subject_path, subject_files, save_as, "IMPORT")
                    copyfile(import_var.get(), "zip/"+import_var.get().split("/")[-1])
                    messagebox.showinfo("Import Status", "Query " + save_as + "has been succesfully imported.")

                    self.render_f1(0)

            submit = ttk.Button(self.frame2, text="Import", command=lambda: _import(), style="s1.TButton")
            submit.grid(row=2, column=0, columnspan=2, padx=5, pady=5)
            
        elif self.mode == "export_query":

            data = history[index]

            self.frame2.config(text="Exporting "+data["save_as"])

            label_qoi = ttk.Label(self.frame2, text="Please select the directory to export the data to:", style="s1.TLabel")
            label_qoi.grid(row=0, column=0, sticky=W, padx=5, pady=5)
            button_browse = ttk.Button(self.frame2, text="Browse", command=lambda: browse_export(), style="s1.TButton")
            button_browse.grid(row=0, column=1, sticky=W, padx=5, pady=5)

            def browse_export():

                foldername = filedialog.askdirectory()
                export_var.set(foldername)

            export_var = StringVar()
            export_path = ttk.Entry(self.frame2, textvariable=export_var, style="s1.TEntry")
            export_path.grid(row=1, column=0, columnspan=2, sticky="nesw", padx=5, pady=5)
            radio_frame = ttk.Frame(self.frame2)
            radio_frame.grid(row=2, column=0, sticky=W, padx=5, pady=5)
            export_method = IntVar(value=0)
            radio_unzip = ttk.Radiobutton(radio_frame, text=" Unzipped", variable=export_method, value=1, style="s1.TRadiobutton")
            radio_unzip.grid(row=0, column=0, sticky=W, padx=5, pady=5)
            radio_zip = ttk.Radiobutton(radio_frame, text=" Zipped", variable=export_method, value=2, style="s1.TRadiobutton")
            radio_zip.grid(row=0, column=1, sticky=W, padx=5, pady=5)

            def export():

                if export_path.get() == "":
                    messagebox.showerror("Invalid Input", "Please select the path of directory to export the data to.")
                    return
                if export_method.get() == 0:
                    messagebox.showerror("Invalid Input", "Please select the form the data should be exported as.")
                    return
                if export_method.get() == 1:
                    with ZipFile("zip/" + data["save_as"] + ".zip", "r") as zipObj:
                        zipObj.extractall(export_path.get())
                else:
                    copyfile("zip/" + data["save_as"] + ".zip", export_path.get() + "/" + data["save_as"] + ".zip")

                messagebox.showinfo("Export Status", "Query has been succesfully exported.")

            export_btn = ttk.Button(self.frame2, text="Export", command=lambda: export(), style="s1.TButton")
            export_btn.grid(row=3, column=0, columnspan=2)

    def destroy(self):

        self.kill = True # Forceful kill of thread
        self.thread.join()
        Frame.destroy(self)