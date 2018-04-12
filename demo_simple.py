from tkinter import *
from tkinter import messagebox
import algoAI
import sql
from time import time
import sqlite3
import random

def getDatabase():
    return 'english.db'

def onselect(evt):
    for child in frame.winfo_children():
        child.destroy()
    Frame3.config(text='Query evaluation : 0 tuples')
    w = evt.widget
    try:
        index = int(w.curselection()[0])
        value = w.get(index)
        requetes = value.split('    (')[0].lower().splitlines()
        requete = ' '.join(requetes)

        eval_query(requete)
    except sqlite3.OperationalError as e:
        messagebox.showwarning('Warning',"Please check SQL syntax \n Error message : \n {0}".format(e))
    except IndexError:
        pass

def eval_query(requete=''):
    if len(requete) == 0:
        for child in frame.winfo_children():
            child.destroy()
        # Note here that Tkinter passes an event object to onselect()
        requete = e1.get("1.0", END)[:-1]
    try:
        rows, headers = sql.execute_query(requete, getDatabase())

        for j in range(len(headers)):
            l = Label(frame, text=headers[j])
            l.grid(row=0, column=j, sticky=NSEW)

        limit = len(rows)
        Frame3.config(text='Query evaluation : ' + str(limit) + ' tuples')
        if limit > 100:
            rows = random.sample(rows, 100)

        for i in range(len(rows)):
            for j in range(len(headers)):
                l = Label(frame, text=rows[i][j], relief=FLAT, bg='white')
                l.grid(row=i+1, column=j, sticky=NSEW)

        canvas.create_window(0, 0, anchor=NW, window=frame)

        frame.update_idletasks()

        canvas.config(scrollregion=canvas.bbox("all"))

    except sqlite3.OperationalError as e:
        messagebox.showwarning('Warning',"Please check SQL syntax \n Error message : \n {0}".format(e))


master = Tk()
master.wm_title("Query Completion Framework")

# frame 1
Frame1 = LabelFrame(master, borderwidth=2, relief=GROOVE, text='Write SQL input query')
Frame1.grid(row=0, column=0, sticky=N+S+E+W)
Label(Frame1).grid()

# frame 3
Frame3 = LabelFrame(master, borderwidth=2, relief=GROOVE, text='Query evaluation : 0 tuples')
Frame3.grid(row=1, column=0, sticky=N+S+E+W)
Label(Frame3).grid()

master.grid_columnconfigure(0, weight=1, uniform="foo")
master.grid_rowconfigure(0, weight=2, uniform="foo")
master.grid_rowconfigure(1, weight=3, uniform="foo")

for i in range(5):
    Frame1.grid_columnconfigure(i, weight=1, uniform="foo")

for i in range(2):
    Frame1.grid_rowconfigure(i, weight=1, uniform="foo")

e1 = Text(Frame1, height=15)
e1.grid(row = 0, column =0, columnspan=5, rowspan=2, sticky=N+S+E+W)

Button(Frame1, text='Evaluate query', command=eval_query).grid(row=2, column=2, pady=4, sticky=N+S+E+W)

# Remplissage Frame 3
vscrollbar = Scrollbar(Frame3)
vscrollbar.grid(row=0, column=1, sticky=N+S)

canvas = Canvas(Frame3, yscrollcommand=vscrollbar.set)
canvas.grid(row=0, column=0, columnspan=1, sticky=N+S+E+W)

vscrollbar.config(command=canvas.yview)

# make the canvas expandable
Frame3.grid_rowconfigure(0, weight=1)
Frame3.grid_columnconfigure(0, weight=1)

#
# create canvas contents
frame = Frame(canvas)
frame.rowconfigure(1, weight=1)
frame.columnconfigure(1, weight=1)



master.resizable(0,0)
mainloop( )

