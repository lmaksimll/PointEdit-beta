import tkinter as tk
from tkinter import filedialog
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import (
    FigureCanvasTkAgg, NavigationToolbar2Tk)
from matplotlib.patches import Rectangle
import csv

class PointPlotterApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Point Edit")
        self.root.geometry("850x700")

        self.frame_top = tk.Frame(root)
        self.frame_top.pack(fill='both', expand=True)
        self.figure, self.ax = plt.subplots(dpi=100)

        self.rect = Rectangle((0, 0), 1, 1, facecolor='None', edgecolor='black')

        self.canvas = FigureCanvasTkAgg(self.figure, master=self.frame_top)
        self.canvas.draw()
        self.canvas.get_tk_widget().pack(fill='both', expand=True)

        self.toolbar = NavigationToolbar2Tk(self.canvas, self.frame_top)
        self.toolbar.update()

        self.button_state = False
        self.tool = tk.Button(self.toolbar, text="Edit point",command=self.button_pressed)
        self.tool.pack(side='left')

        self.points = []
        self.del_points = []
        self.rec_x0 = None
        self.rec_y0 = None
        self.rec_x1 = None
        self.rec_y1 = None

        self.canvas.mpl_connect('button_press_event', self.on_click)
        self.canvas.mpl_connect('button_press_event', self.on_press)
        self.canvas.mpl_connect('button_release_event', self.on_release)

        self.frame_bottom = tk.Frame(root)
        self.frame_bottom.pack(fill='x')

        self.import_button = tk.Button(self.frame_bottom, text="Import csv file", command=self.import_points, height=2)
        self.import_button.pack(side='left', fill='x', expand=True)

        self.export_button = tk.Button(self.frame_bottom, text="Export csv file", command=self.export_points, height=2)
        self.export_button.pack(side='left', fill='x', expand=True)

        self.delete_button = tk.Button(self.frame_bottom, text="Apply changes", command=self.delete_points, height=2)
        self.delete_button.pack(side='left', fill='x', expand=True)

    def button_pressed(self):
        if self.button_state == False:
            self.tool.config(relief="sunken")
            self.button_state = True
        else:
            self.tool.config(relief="raised")
            self.button_state = False
            self.canvas.draw()

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

            if len(self.points) > 0:
                self.selection_points()

            self.rect.remove()

    def on_click(self, event):
        if len(self.del_points) == 0:
            return

        for del_point in self.del_points:
            if abs(event.xdata - del_point[0]) < 0.1 and abs(event.ydata - del_point[1]) < 0.1:
                self.ax.plot(del_point[0], del_point[1], 'ro')
                self.del_points.remove(del_point)
                self.canvas.draw()
                return

    def import_points(self):
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

    def export_points(self):
        file_path = filedialog.asksaveasfilename(defaultextension=".csv", filetypes=[("CSV files", "*.csv")])
        if file_path:
            with open(file_path,'w',encoding='utf-8',newline='') as file:
                writer = csv.DictWriter(file, fieldnames=['x','y'], delimiter=';', quoting=csv.QUOTE_MINIMAL)
                writer.writeheader()
                for point in self.points:
                    writer.writerow({'x': point[0], 'y': point[1]})

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