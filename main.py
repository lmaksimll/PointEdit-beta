import tkinter as tk
from tkinter import (filedialog, messagebox, ttk)
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import (FigureCanvasTkAgg, NavigationToolbar2Tk)
from matplotlib.patches import Ellipse
import csv
import time
import concurrent.futures

class PointPlotterApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Point Edit")
        self.root.attributes('-fullscreen', True)
        self.root.protocol("WM_DELETE_WINDOW", self.on_closing)

        self.frame_top = tk.Frame(root)
        self.frame_top.pack(fill='both', expand=True)
        self.figure, self.ax = plt.subplots(dpi=100)

        self.ellipse = Ellipse((0,0), 1, 1, fill=False, edgecolor='black')

        self.canvas = FigureCanvasTkAgg(self.figure, master=self.frame_top)
        self.canvas.draw()
        self.canvas.get_tk_widget().pack(fill='both', expand=True)

        # -------------------variables-------------------
        self.points = []
        self.del_points = []

        self.ellipse_coord_0 = [None,None]
        self.ellipse_coord_1 = [None,None]
        self.ellipse_width = None
        self.ellipse_height = None
        self.ellipse_center = [None,None]

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
        self.root.bind('<i>', self.button_pressed_event)
        self.root.bind('<Delete>', self.delete_points_event)
        self.root.bind('<\>', self.return_points)

        self.edit_button.bind("<Enter>", lambda event: self.on_enter(event, 'edit'))
        self.edit_button.bind("<Leave>", lambda event: self.on_leave(event, 'edit'))

        self.delete_button.bind("<Enter>", lambda event: self.on_enter(event, 'delete'))
        self.delete_button.bind("<Leave>", lambda event: self.on_leave(event, 'delete'))

        # -------------------connect-------------------
        self.canvas.mpl_connect('button_press_event', self.on_press)
        self.canvas.mpl_connect('button_release_event', self.on_release)

    def button_pressed_event(self, event):
        self.button_pressed()

    def button_pressed(self):
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
        elif btn == 'delete':
            self.delete_button.tooltip = ttk.Label(self.root, text="Apply changes (Key - Delete)")
            self.delete_button.tooltip.place(x=self.root.winfo_pointerx(), y=self.root.winfo_pointery())
            self.delete_button.tooltip.lift()

    def on_leave(self, event, btn):
        if btn == 'edit':
            self.edit_button.tooltip.destroy()
        elif btn == 'delete':
            self.delete_button.tooltip.destroy()

    def on_closing(self, event):
        if messagebox.askokcancel("Close", "Are you sure you want to close the application?"):
            self.root.destroy()

    def on_press(self, event):
        if self.button_state == True:
            self.ellipse_coord_0[0] = (event.xdata)
            self.ellipse_coord_0[1] = (event.ydata)

    def on_release(self, event):
        if self.button_state == True:
            self.ellipse_coord_1[0] = (event.xdata)
            self.ellipse_coord_1[1] = (event.ydata)

            self.ellipse_height = abs(self.ellipse_coord_1[1] - self.ellipse_coord_0[1])
            self.ellipse.set_height(self.ellipse_height)

            self.ellipse_width = abs(self.ellipse_coord_1[0] - self.ellipse_coord_0[0])
            self.ellipse.set_width(self.ellipse_width)

            self.ellipse_center[0] = ((self.ellipse_coord_0[0] + self.ellipse_coord_1[0]) / 2)
            self.ellipse_center[1] = ((self.ellipse_coord_0[1] + self.ellipse_coord_1[1]) / 2)
            self.ellipse.set_center(self.ellipse_center)

            self.ax.add_patch(self.ellipse)
            self.canvas.draw()

            if len(self.points) > 0:
                self.selection_points_thread()

            self.ellipse.remove()

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
                    self.points.append([x, y1, y2, y3, y4, y5])
            self.plot_points()

    def save_points(self):
        file_path = filedialog.asksaveasfilename(defaultextension=".csv", filetypes=[("CSV files", "*.csv")])
        if file_path:
            with open(file_path,'w',encoding='utf-8',newline='') as file:
                writer = csv.DictWriter(file, fieldnames=['Time','Frequency (Hz)1','Frequency (Hz)2','Frequency (Hz)3','Frequency (Hz)4','Frequency (Hz)5'], delimiter=';', quoting=csv.QUOTE_MINIMAL)
                writer.writeheader()
                for point in self.points:
                    writer.writerow({'Time': point[0], 'Frequency (Hz)1': point[1], 'Frequency (Hz)2': point[2], 'Frequency (Hz)3': point[3], 'Frequency (Hz)4': point[4], 'Frequency (Hz)5': point[5]})

    def delete_points_event(self, event):
        self.delete_points()

    def delete_points(self):
        if len(self.del_points) == 0:
            return

        for del_point in self.del_points:
            for point in self.points:
                if point[0] == del_point[0] and point[int(del_point[2])] == del_point[1]:
                    point[int(del_point[2])] = ''
                    if point[1] and point[2] and point[3] and point[4] and point[5] == '':
                        self.points.remove(point)

        self.del_points.clear()
        self.plot_points()

    def return_points(self,event):
        if len(self.del_points) == 0:
            return

        point = self.del_points[-1]
        if point[2] == 1:
            self.ax.plot(point[0], point[1], 'ro')
        elif point[2] == 2:
            self.ax.plot(point[0], point[1], 'go')
        elif point[2] == 3:
            self.ax.plot(point[0], point[1], 'bo')
        elif point[2] == 4:
            self.ax.plot(point[0], point[1], 'yo')
        elif point[2] == 5:
            self.ax.plot(point[0], point[1], 'mo')

        self.canvas.draw()
        self.del_points.pop()

    def plot_points(self):
        self.ax.clear()

        for point in self.points:
            if point[0] != '' and point[1] != '' :
                self.ax.plot(point[0], point[1], 'r.')
            if point[0] != '' and point [2] != '':
                self.ax.plot(point[0], point[2], 'g.')
            if point[0] != '' and point[3] != '':
                self.ax.plot(point[0], point[3], 'b.')
            if point[0] != '' and point[4] != '':
                self.ax.plot(point[0], point[4], 'y.')
            if point[0] != '' and point[5] != '':
                self.ax.plot(point[0], point[5], 'm.')

        self.canvas.draw()

    def selection_points_thread(self):
        start_time = time.time()
        with concurrent.futures.ThreadPoolExecutor() as executor:
            futures = [executor.submit(self.process_point, point, self.ellipse_center, self.ellipse_width, self.ellipse_height) for point in self.points]
            concurrent.futures.wait(futures)

            for future in futures:
                result = future.result()
                if result is not None:
                    for del_point in result:
                        self.del_points.append(del_point)

        self.cross_out_points()

        end_time = time.time()
        print("Время выполнения функции", end_time - start_time, "секунд")

    @staticmethod
    def process_point(point, ellipse_center, ellipse_width, ellipse_height):
        flag_point = False
        del_points = []
        for i in range(1, 6):
            if point[i] != '':
                if ((point[0] - ellipse_center[0]) ** 2) / ((ellipse_width / 2)) ** 2 + ((point[i] - ellipse_center[1]) ** 2) / ((ellipse_height / 2) ** 2) <= 1:
                    flag_point = True
                    del_points.append([point[0], point[i], i])

        if flag_point == True:
            return del_points
        else:
            return

    def cross_out_points(self):
        for del_point in self.del_points:
            self.ax.plot(del_point[0], del_point[1], 'kx')
        self.canvas.draw()

root = tk.Tk()
app = PointPlotterApp(root)
root.mainloop()