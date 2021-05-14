import tkinter as tk
from tkinter import *
from tkinter import ttk, messagebox
from custom_tk import *
from nq_frame import nqFrame
from vl_frame import vlFrame
from a_frame import aFrame
import os
from os import listdir
from os.path import isfile, join
from threadQ import threadQueue
import ctypes

if os.name == "nt": # If OS is windows...
    try:
        ctypes.windll.shcore.SetProcessDpiAwareness(True) # This makes tkinter text appear sharp and well defined
    except:
        pass

# This is to only ensure the folder exists when the pyinstaller generates the .exe (--onefile obviously)
folders = ["metadata", "tmp", "tmp2", "viewing", "zip"]
for folder in folders:
    if not os.path.exists(folder):
        os.mkdir(folder, mode=0o777)
        if folder == "metadata": # Make sure the file to maintain history exists
            w = open("metadata/history.csv", "w")
            w.close()

''' Clear out any remaining images within '''
def clear_images():

    files = [f for f in listdir("viewing/") if isfile(join("viewing/", f))]
    for file in files:
        os.remove("viewing/"+file)

''' List composition of all tab names '''
def all_tabs():

    return [task_tab.tab(i, option="text") for i in task_tab.tabs()]

''' Create Tab '''
def add_tab():

    if all_tabs().__contains__(tab_entry_var.get()):
        messagebox.showerror("Tab Creation Error", "A pre-existing tab currently holds that name. Please enter tab name that is unique.")
        return
    elif tab_entry_var.get() == "":
        tab_name = "Tab " + str(all_tabs().__len__() + 1)
    else:
        tab_name = tab_entry_var.get()
    tab = ttk.Frame(task_tab, style="s1.TNotebook.Tab")
    center_frame = ttk.LabelFrame(tab, text="MassBlast", style="s1.TLabelframe")
    center_frame.grid(row=0, column=0, sticky="", padx=5, pady=5)
    center_frame.place(in_=tab, anchor="s",relx=.5, rely=.5)
    li2 = ttk.Label(center_frame, text="Navigate through tabs using CTRL + " + u"\u2192 / " + u"\u2190", style="s1.TLabel")
    li2.grid(row=1, column=0, sticky=W, padx=5, pady=5)
    li3 = ttk.Label(center_frame, text="Access NEW QUERY with CTRL + N", style="s1.TLabel")
    li3.grid(row=2, column=0, sticky=W, padx=5, pady=5)
    li4 = ttk.Label(center_frame, text="Access MANAGE QUERY with CTRL + M", style="s1.TLabel")
    li4.grid(row=3, column=0, sticky=W, padx=5, pady=5)
    li5 = ttk.Label(center_frame, text="Access IMPORT QUERY with CTRL + I", style="s1.TLabel")
    li5.grid(row=4, column=0, sticky=W, padx=5, pady=5)
    li6 = ttk.Label(center_frame, text="Access EXPORT QUERY with CTRL + E", style="s1.TLabel")
    li6.grid(row=5, column=0, sticky=W, padx=5, pady=5)
    li7 = ttk.Label(center_frame, text="Access ANALYZE QUERY with CTRL + A", style="s1.TLabel")
    li7.grid(row=6, column=0, sticky=W, padx=5, pady=5)
    task_tab.add(tab, text=tab_name)
    task_tab.add(tab, text=tab_name)
    tab_entry_var.set("")

''' Rename Tab '''
def rename_tab():

    if tab_entry_var.get() == "":
        messagebox.showerror("Tab Renaming Error", "Unable to rename a tab with a name less than one character in length.")
        return
    elif all_tabs().__contains__(tab_entry_var.get()):
        messagebox.showerror("Tab Renaming Error", "A pre-existing tab currently holds that name. Please enter tab name that is unique.")
        return
    task_tab.tab(task_tab.select(), text=tab_entry_var.get())

''' Delete Tab '''
def del_tab():

    if all_tabs().__len__() != 0:
        for tab in task_tab.winfo_children():
            if str(tab) == task_tab.select():
                tab.destroy()
                return

''' Submit Query Request '''
def new_query():

    tab = nqFrame(Q, task_tab)
    task_tab.add(tab, text="New Query")
    task_tab.select(all_tabs().__len__()-1)

''' If on the (n)th tab, go to the (n+1)th tab '''
def right_tab():

    try:
        index = task_tab.index(task_tab.select())
        task_tab.select(index+1)
    except:
        pass

''' If on the (n)th tab, go to the (n-1)th tab '''
def left_tab():

    try:
        index = task_tab.index(task_tab.select())
        task_tab.select(index-1)
    except:
        pass

''' Manage Queries '''
def view_list(mode):

    tab = vlFrame(task_tab, mode)

    task_tab.add(tab, text="Manage Queries")
    task_tab.select(all_tabs().__len__()-1)

''' Analyze Queries '''
def analyze():

    tab = aFrame(task_tab)
    task_tab.add(tab, text="Analyze Query")
    task_tab.select(all_tabs().__len__()-1)

clear_images()

Q = threadQueue()

root = tk.Tk()
root.title("MassBlast")
root.state("zoomed")
icon = PhotoImage(file="resources/massBlast.png")
root.iconphoto(False, icon)

''' Setting up style configs '''
s1 = ttk.Style(root)
s1_font = ("Segoe UI", 8)
s1.configure("s1.TLabelframe", font=s1_font)
s1.configure("s1.TLabel", font=s1_font)
s1.configure("s1.TEntry", font=s1_font)
s1.configure("s1.TButton", font=s1_font)
s1.configure("s1.TNotebook.Tab", font=s1_font)
s1.configure("s1.TNotebook.Tab", background="#d9d9d9")

''' Toolbar '''
tool_bar = Menu(root)
root.config(menu=tool_bar, bg="#54524a")
query_menu = Menu(tool_bar, tearoff=0)
query_menu.add_command(label="New", command=lambda: new_query(), font=s1_font)
query_menu.add_command(label="Manage", command=lambda: view_list("give_info"), font=s1_font)
query_menu.add_command(label="Import", command=lambda: view_list("import_query"), font=s1_font)
query_menu.add_command(label="Export", command=lambda: view_list("export_query"), font=s1_font)
tool_bar.add_cascade(label="Query", menu=query_menu, font=s1_font)
tool_bar.add_command(label="Analyze", command=lambda: analyze(), font=s1_font)

'''
help_menu = Menu(tool_bar, tearoff=0)
help_menu.add_command(label="About", command=None)
help_menu.add_command(label="FAQ", command=None)
help_menu.add_command(label="Guides", command=None)
help_menu.add_command(label="Online MassBlast", command=None)
tool_bar.add_cascade(label="Help", menu=help_menu)
'''

''' Task Manager '''
tm_frame = ttk.Frame(root)
tm_frame.pack(fill=tk.X)
tab_name = ttk.Label(tm_frame, text="Tab Name: ", style="s1.TLabel")
tab_name.grid(row=0, column=0, padx=5, pady=5)
tab_entry_var = StringVar()
tab_entry = ttk.Entry(tm_frame, textvariable=tab_entry_var, style="s1.TEntry")
tab_entry.grid(row=0, column=1, padx=5, pady=5)
tab_rename = ttk.Button(tm_frame, text="Rename Tab", command=lambda: rename_tab(), style="s1.TButton")
tab_rename.grid(row=0, column=2, padx=5, pady=5)
tab_create = ttk.Button(tm_frame, text="Create Tab", command=lambda: add_tab(), style="s1.TButton")
tab_create.grid(row=0, column=3, padx=5, pady=5)
tab_delete = ttk.Button(tm_frame, text="Close Tab", command=lambda: del_tab(), style="s1.TButton")
tab_delete.grid(row=0, column=4, padx=5, pady=5)
tm_frame_frame = ttk.Frame(tm_frame)  
tm_frame_frame.grid(row=0, column=4)

''' Tabs '''
s1.configure("s1.TNotebook", font=s1_font)
task_tab = ttk.Notebook(root, style="s1.TNotebook")
task_tab.pack(fill=tk.BOTH, expand=True)

''' Default Tabs '''
add_tab()

''' Binds '''
root.bind("<Control-n>",lambda event: new_query())
root.bind("<Control-m>", lambda event: view_list("give_info"))
root.bind("<Control-i>", lambda event: view_list("import_query"))
root.bind("<Control-e>", lambda event: view_list("export_query"))
root.bind("<Control-a>", lambda event: analyze())
root.bind("<Control-Left>", lambda event: left_tab())
root.bind("<Control-Right>", lambda event: right_tab())

root.mainloop()

Q.destroy()
clear_images()