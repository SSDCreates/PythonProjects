import tkinter as tk
#from tkinter import ttk  # holds widgets
import ttkbootstrap as ttk

def convert():
    mile_input = entry_int.get()
    km_output = mile_input  * 1.61
    output_string.set(km_output)


# window
window = ttk.Window(themename = 'journal')

window.title('Converter')
window.geometry('300x150')  # sets window size

# Widget title
# master is the parent, or window in this case, essentially where that widget exists within
title_label = ttk.Label(
    master=window, text='Miles to Kilometers', font="Calibri 24 bold")
title_label.pack()  # places into window

# input field
input_frame = ttk.Frame(master=window)
entry_int = tk.IntVar()  # creates sep variable that stores and updates values
entry = ttk.Entry(master=input_frame, textvariable=entry_int)
# PASS a function, do not call () it
button = ttk.Button(master=input_frame, text="Convert", command=convert)

entry.pack(side='left', padx=10)
button.pack(side='left')
input_frame.pack(pady=10)

# output
output_string = tk.StringVar()  # stores string instead of int
output_label = ttk.Label(master=window, text='Output',
                         font="Calibri 24", textvariable=output_string)
output_label.pack(pady=5)

# run
window.mainloop()  # creates basic window
