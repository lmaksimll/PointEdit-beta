import tkinter as tk
from tkinter import (filedialog, messagebox, ttk)
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import (
    FigureCanvasTkAgg, NavigationToolbar2Tk)
from matplotlib.patches import Rectangle, Ellipse
import csv

class PointPlotterApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Point Edit")
        self.root.attributes('-fullscreen', True)
        self.root.protocol("WM_DELETE_WINDOW", self.on_closing)

        self.frame_top = tk.Frame(root)
        self.frame_top.pack(fill='both', expand=True)
        self.figure, self.ax = plt.subplots(dpi=100)

        self.rect = Rectangle((0, 0), 1, 1, facecolor='None', edgecolor='black')

        self.canvas = FigureCanvasTkAgg(self.figure, master=self.frame_top)
        self.canvas.draw()
        self.canvas.get_tk_widget().pack(fill='both', expand=True)

        # -------------------variables-------------------
        self.points = []
        self.del_points = []
        self.rec_x0 = None
        self.rec_y0 = None
        self.rec_x1 = None
        self.rec_y1 = None
        self.button_state = False

        # -------------------buttons-------------------
        self.toolbar = NavigationToolbar2Tk(self.canvas, self.frame_top)
        self.toolbar.update()

        self.edit_button = tk.Button(self.toolbar, text="Edit point",command=self.button_pressed)
        self.edit_button.pack(side='left', padx=5)

        self.open_button = tk.Button(self.toolbar, text="Open file", command=self.open_points)
        self.open_button.pack(side='left', padx=5)

        self.save_button = tk.Button(self.toolbar, text="Save file", command=self.save_points)
        self.save_button.pack(side='left', padx=5)

        self.delete_button = tk.Button(self.toolbar, text="Apply changes", command=self.delete_points)
        self.delete_button.pack(side='left', padx=5)

        # -------------------bind-------------------
        self.root.bind('<Escape>', self.on_closing)
        self.root.bind('<i>', self.button_pressed)

        self.edit_button.bind("<Enter>", lambda event: self.on_enter(event, 'edit'))
        self.edit_button.bind("<Leave>", lambda event: self.on_leave(event, 'edit'))

        self.open_button.bind("<Enter>", lambda event: self.on_enter(event, 'open'))
        self.open_button.bind("<Leave>", lambda event: self.on_leave(event, 'open'))

        self.save_button.bind("<Enter>", lambda event: self.on_enter(event, 'save'))
        self.save_button.bind("<Leave>", lambda event: self.on_leave(event, 'save'))

        self.delete_button.bind("<Enter>", lambda event: self.on_enter(event, 'delete'))
        self.delete_button.bind("<Leave>", lambda event: self.on_leave(event, 'delete'))

        # -------------------connect-------------------
        self.canvas.mpl_connect('button_press_event', self.on_press)
        self.canvas.mpl_connect('button_release_event', self.on_release)

    def button_pressed(self, event):
        if self.button_state == False:
            self.edit_button.config(relief="sunken")
            self.button_state = True
        else:
            self.edit_button.config(relief="raised")
            self.button_state = False
            self.canvas.draw()

    def on_enter(self, event, btn):
        if btn == 'edit':
            self.edit_button.tooltip = ttk.Label(self.root, text="Selecting an area (Key - I)")
            self.edit_button.tooltip.place(x=self.root.winfo_pointerx(), y=self.root.winfo_pointery())
            self.edit_button.tooltip.lift()
        elif btn == 'open':
            self.open_button.tooltip = ttk.Label(self.root, text="Open file")
            self.open_button.tooltip.place(x=self.root.winfo_pointerx(), y=self.root.winfo_pointery())
            self.open_button.tooltip.lift()
        elif btn == 'save':
            self.save_button.tooltip = ttk.Label(self.root, text="Save file")
            self.save_button.tooltip.place(x=self.root.winfo_pointerx(), y=self.root.winfo_pointery())
            self.save_button.tooltip.lift()
        elif btn == 'delete':
            self.delete_button.tooltip = ttk.Label(self.root, text="Prepare points for deletion(Key - Del) \n Apply changes (Key - Enter)")
            self.delete_button.tooltip.place(x=self.root.winfo_pointerx(), y=self.root.winfo_pointery())
            self.delete_button.tooltip.lift()

    def on_leave(self, event, btn):
        if btn == 'edit':
            self.edit_button.tooltip.destroy()
        elif btn == 'open':
            self.open_button.tooltip.destroy()
        elif btn == 'save':
            self.save_button.tooltip.destroy()
        elif btn == 'delete':
            self.delete_button.tooltip.destroy()

    def on_closing(self, event):
        if messagebox.askokcancel("Close", "Are you sure you want to close the application?"):
            self.root.destroy()

    def on_press(self, event):
        if self.button_state == True:
            self.rec_x0 = event.xdata
            self.rec_y0 = event.ydata

    def on_release(self, event):
        if self.button_state == True:
            self.rec_x1 = event.xdata
            self.rec_y1 = event.ydata
            self.rect.set_width(self.rec_x1 - self.rec_x0)
            self.rect.set_height(self.rec_y1 - self.rec_y0)
            self.rect.set_xy((self.rec_x0, self.rec_y0))
            self.ax.add_patch(self.rect)
            self.canvas.draw()

            # ellipse = plt.Circle((0, 0), radius=ellipse_width / 2, fill=False, edgecolor='blue')


            if len(self.points) > 0:
                self.selection_points()

            self.rect.remove()

    def open_points(self):
        file_path = filedialog.askopenfilename(filetypes=[("CSV files", "*.csv")])
        if file_path:
            self.points.clear()
            with open(file_path, 'r', encoding='utf-8') as file:
                reader = csv.DictReader(file, delimiter=';', quotechar='"')
                for row in reader:
                    if row['Time'] != '':
                        x = float(row['Time'])
                        if row['Frequency (Hz)1'] != '':
                            y1 = float(row['Frequency (Hz)1'])
                            if row['Frequency (Hz)2'] != '':
                                y2 = float(row['Frequency (Hz)2'])
                                if row['Frequency (Hz)3'] != '':
                                    y3 = float(row['Frequency (Hz)3'])
                                    if row['Frequency (Hz)4'] != '':
                                        y4 = float(row['Frequency (Hz)4'])
                                        if row['Frequency (Hz)5'] != '':
                                            y5 = float(row['Frequency (Hz)5'])
                                        else:
                                            y5 = ''
                                    else:
                                        y4, y5 = '',''
                                else:
                                    y3, y4, y5 = '','',''
                            else:
                                y2, y3, y4, y5 = '','','',''
                        else:
                            y1, y2, y3, y4, y5 = '','','','',''
                    else:
                        return
                    self.points.append((x, y1, y2, y3, y4, y5))
            self.plot_points()

    def save_points(self):
        file_path = filedialog.asksaveasfilename(defaultextension=".csv", filetypes=[("CSV files", "*.csv")])
        if file_path:
            with open(file_path,'w',encoding='utf-8',newline='') as file:
                writer = csv.DictWriter(file, fieldnames=['Time','Frequency (Hz)1','Frequency (Hz)2','Frequency (Hz)3','Frequency (Hz)4','Frequency (Hz)5'], delimiter=';', quoting=csv.QUOTE_MINIMAL)
                writer.writeheader()
                for point in self.points:
                    writer.writerow({'Time': point[0], 'Frequency (Hz)1': point[1], 'Frequency (Hz)2': point[2], 'Frequency (Hz)3': point[3], 'Frequency (Hz)4': point[4], 'Frequency (Hz)5': point[5]})

    def delete_points(self):
        if len(self.del_points) == 0:
            return

        for del_point in self.del_points:
            for point in self.points:
                if point[0] == del_point[0] and point[1] == del_point[1]:
                    self.points.remove(point)

        self.del_points.clear()
        self.plot_points()

    def plot_points(self):
        self.ax.clear()

        for point in self.points:
            if point[0] != '' and point[1] != '' :
                self.ax.plot(point[0], point[1], 'r.')
                if point [2] != '':
                    self.ax.plot(point[0], point[2], 'g.')
                    if point[3] != '':
                        self.ax.plot(point[0], point[3], 'b.')
                        if point[4] != '':
                            self.ax.plot(point[0], point[4], 'y.')
                            if point[5] != '':
                                self.ax.plot(point[0], point[5], 'm.')

        self.canvas.draw()

    def selection_points(self):
        for point in self.points:
            if self.rec_x1 > self.rec_x0:
                if point[0] >= self.rec_x0 and point[0] <= self.rec_x1 and point[1] <= self.rec_y0 and point[1] >= self.rec_y1:
                    self.ax.plot(point[0], point[1], 'kx')
                    self.del_points.append(point)
                    self.canvas.draw()
            else:
                if point[0] <= self.rec_x0 and point[0] >= self.rec_x1 and point[1] >= self.rec_y0 and point[1] <= self.rec_y1:
                    self.ax.plot(point[0], point[1], 'kx')
                    self.del_points.append(point)
                    self.canvas.draw()

root = tk.Tk()
app = PointPlotterApp(root)
root.mainloop()