import tkinter as tk
from tkinter import ttk
from tkinter import *

''' Drag and drop canvas for dragging and dropping the subject names in the order desired '''
class ddCanvas(Canvas):

    def __init__(self, master, **kwargs):

        Canvas.__init__(self, master, kwargs)
        self.bind('<B1-Motion>', self.drag)
        self.bind('<Button-1>', self.click)
        self.bind('<ButtonRelease-1>', self.release)
        self.index = None
    
    def click(self, event):

        tmp_index = self.find_closest(event.x, event.y)[0]
        if self.gettags(tmp_index) != "LOCKED":
            self.index = tmp_index

    def drag(self, event):
        
        try:
            if self.index != None:
                x, y = self.coords(self.index)
                self.move(self.index, event.x-x, event.y-y)
        except:
            pass

    def release(self, event):

        self.index = None

''' Child class used as a template for panMaster '''
class panCanvas(Canvas):

    def __init__(self, master, **kwargs):

        Canvas.__init__(self, master, kwargs)
        self.bind('<B1-Motion>', self.drag)
        self.bind('<Button-1>', self.click)
        self.index = None
    
    def click(self, event):

        self.index = self.find_closest(event.x, event.y)[0]
        self.x, self.y = event.x, event.y

    def drag(self, event):
        
        try:
            if self.index != None:
                self.move(self.index, event.x-self.x, event.y-self.y)
                self.x = event.x
                self.y = event.y
        except:
            pass

''' Pan in the X direction, panMaster has its movements in the X direction mimicked to this '''
class panXCanvas(Canvas):

    def __init__(self, master, **kwargs):

        Canvas.__init__(self, master, kwargs)
        # self.bind('<B1-Motion>', self.drag)
        # self.bind('<Button-1>', self.click)
        self.index = None
    
    def click(self, event):

        self.index = self.find_closest(event.x, event.y)[0]
        self.x, self.y = event.x, event.y

    def drag(self, event):
        
        try:
            if self.index != None:
                self.move(self.index, event.x-self.x, 0)
                self.x = event.x
        except:
            pass

''' Same as panXCanvas, but in the Y direction '''
class panYCanvas(Canvas):

    def __init__(self, master, **kwargs):

        Canvas.__init__(self, master, kwargs)
        # self.bind('<B1-Motion>', self.drag)
        # self.bind('<Button-1>', self.click)
        self.index = None
    
    def click(self, event):

        self.index = self.find_closest(event.x, event.y)[0]
        self.x, self.y = event.x, event.y

    def drag(self, event):
        
        try:
            if self.index != None:
                self.move(self.index, 0, event.y-self.y)
                self.y = event.y
        except:
            pass

# I don't use this, ddCanvas is better, but this is worth keeping since it's good practice of OOP in python
'''
class ddListbox(Listbox):

    def __init__(self, master, **kwargs):

        kwargs['selectmode'] = SINGLE
        Listbox.__init__(self, master, kwargs)
        self.bind('<Button-1>', self.click)
        self.bind('<B1-Motion>', self.drag)
        self.index = None

    def click(self, event):

        self.index = self.nearest(event.y)

    def drag(self, event):

        i = self.nearest(event.y)
        if i < self.index:
            x = self.get(i)
            self.delete(i)
            self.insert(i+1, x)
            self.index = i
        elif i > self.index:
            x = self.get(i)
            self.delete(i)
            self.insert(i-1, x)
            self.index = i
'''

''' Entry that only takes numbers '''
class numEntry(Entry):

    def __init__(self, master, **kwargs):

        self.var = StringVar()
        Entry.__init__(self, master, textvariable=self.var, **kwargs)
        self.old_value = None
        self.var.trace('w', self.validate)
        self.get, self.set = self.var.get, self.var.set

    def validate(self, *args):

        if self.get().isdigit() or self.get() == "":
            self.old_value = self.get()
        else:
            self.set(self.old_value)

''' Frame that just has additional variable, step, and sp, that keeps track of the step the user is in some form '''
class spFrame(Frame):

    def __init__(self, master, **kwargs):
        
        Frame.__init__(self, master, **kwargs)
        self.sp = None
        self.step = 0
