import tkinter as tk
from tkinter import (filedialog, messagebox, ttk)
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import (FigureCanvasTkAgg, NavigationToolbar2Tk)
from matplotlib.patches import Rectangle
import csv
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

        self.rect = Rectangle((0, 0), 1, 1, facecolor='None', edgecolor='black', linestyle='--', linewidth=2)

        self.canvas = FigureCanvasTkAgg(self.figure, master=self.frame_top)
        self.canvas.draw()
        self.canvas.get_tk_widget().pack(fill='both', expand=True)

        # -------------------variables-------------------
        self.points = []
        self.del_points = []

        self.rec_x = [None, None]
        self.rec_y = [None, None]

        self.button_select_flag = False
        self.button_zoom_flag = False
        self.button_pan_flag = False

        self.button_release_flag = False

        # -------------------buttons-------------------
        self.toolbar = NavigationToolbar2Tk(self.canvas, self.frame_top)
        self.toolbar.update()

        self.edit_button = tk.Button(self.toolbar, text="Edit point",command=self.button_select_pressed)
        self.edit_button.pack(side='left', padx=5)

        self.open_button = tk.Button(self.toolbar, text="Open file", command=self.open_points)
        self.open_button.pack(side='left', padx=5)

        self.save_button = tk.Button(self.toolbar, text="Save file", command=self.save_points)
        self.save_button.pack(side='left', padx=5)

        self.delete_button = tk.Button(self.toolbar, text="Apply changes", command=self.delete_points)
        self.delete_button.pack(side='left', padx=5)

        # -------------------bind-------------------
        self.root.bind('<Escape>', self.on_closing)
        self.root.bind('<Delete>', self.delete_points_event)
        self.root.bind('<\>', self.return_points)
        self.root.bind('<i>', self.button_select_pressed_event)
        self.root.bind('<o>', self.button_zoom_pressed_event)
        self.root.bind('<p>', self.button_pan_pressed_event)

        self.edit_button.bind("<Enter>", lambda event: self.on_enter(event, 'edit'))
        self.edit_button.bind("<Leave>", lambda event: self.on_leave(event, 'edit'))

        self.delete_button.bind("<Enter>", lambda event: self.on_enter(event, 'delete'))
        self.delete_button.bind("<Leave>", lambda event: self.on_leave(event, 'delete'))

        # -------------------connect-------------------
        self.canvas.mpl_connect('button_press_event', self.on_press)
        self.canvas.mpl_connect('button_release_event', self.on_release)
        self.canvas.mpl_connect('motion_notify_event', self.on_motion)
        # self.toolbar._button_press_id = self.toolbar.canvas.mpl_connect('button_press_event', lambda event: self.on_toolbar_button_press(event))

    # def on_toolbar_button_press(self, event, *args, **kwargs):
    #     if event.inaxes is not None:
    #         if hasattr(event.inaxes, '_button_pressed'):
    #             toolbar_button = event.inaxes._button_pressed
    #             if toolbar_button is None:
    #                 return
    #             if toolbar_button == 'HELP':
    #                 print('Help button pressed on the toolbar')
    #             elif toolbar_button == 'BACK':
    #                 print('Back button pressed on the toolbar')
    #             elif toolbar_button == 'FORWARD':
    #                 print('Forward button pressed on the toolbar')
    #             elif toolbar_button == 'PAN':
    #                 print('Pan button pressed on the toolbar')
    #             elif toolbar_button == 'ZOOM':
    #                 print('Zoom button pressed on the toolbar')
    #             elif toolbar_button == 'HOME':
    #                 print('Home button pressed on the toolbar')
    #             elif toolbar_button == 'SAVE':
    #                 print('Save button pressed on the toolbar')
    #             elif toolbar_button == 'MOVE':
    #                 print('Move button pressed on the toolbar')
    #             elif toolbar_button == 'RECTANGLE':
    #                 print('Rectangle button pressed on the toolbar')
    #             elif toolbar_button == 'SELECT':
    #                 print('Select button pressed on the toolbar')

    def button_select_pressed_event(self, event):
        self.button_select_pressed()

    def button_zoom_pressed_event(self, event):
        if self.button_select_flag == True:
            self.button_select_flag = False
            self.edit_button.config(relief="raised")

        if self.button_pan_flag == True:
            self.button_pan_flag = False

        if self.button_zoom_flag == False:
            self.button_zoom_flag = True
        elif self.button_zoom_flag == True:
            self.button_zoom_flag = False

        self.canvas.draw()

    def button_pan_pressed_event(self, event):
        if self.button_select_flag == True:
            self.button_select_flag = False
            self.edit_button.config(relief="raised")

        if self.button_zoom_flag == True:
            self.button_zoom_flag = False

        if self.button_pan_flag == False:
            self.button_pan_flag = True
        elif self.button_pan_flag == True:
            self.button_pan_flag = False

        self.canvas.draw()

    def button_select_pressed(self):
        if self.button_zoom_flag == True:
            self.button_zoom_flag = False
            self.toolbar.zoom()

        if self.button_pan_flag == True:
            self.button_pan_flag = False
            self.toolbar.pan()

        if self.button_select_flag == False:
            self.button_select_flag = True
            self.edit_button.config(relief="sunken")
        else:
            self.button_select_flag = False
            self.edit_button.config(relief="raised")

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
        if self.button_select_flag == True:
            self.button_release_flag = False
            self.rec_x[0] = event.xdata
            self.rec_y[0] = event.ydata

            self.rect.set_xy((self.rec_x[0], self.rec_y[0]))

    def on_release(self, event):
        if self.button_select_flag == True:
            self.button_release_flag = True

            if len(self.points) > 0:
                self.selection_points_thread()

            self.rect.remove()

    def on_motion(self, event):
        if self.button_select_flag == True and self.rec_x[0] != None and self.button_release_flag == False:
            if len(self.ax.patches) > 0:
                for patch in self.ax.patches:
                    patch.remove()

            self.rec_x[1] = event.xdata
            self.rec_y[1] = event.ydata

            self.rect.set_width(self.rec_x[1] - self.rec_x[0])
            self.rect.set_height(self.rec_y[1] - self.rec_y[0])

            self.ax.add_patch(self.rect)
            self.canvas.draw()

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
            self.ax.plot(point[0], point[1], 'r.')
        elif point[2] == 2:
            self.ax.plot(point[0], point[1], 'g.')
        elif point[2] == 3:
            self.ax.plot(point[0], point[1], 'b.')
        elif point[2] == 4:
            self.ax.plot(point[0], point[1], 'y.')
        elif point[2] == 5:
            self.ax.plot(point[0], point[1], 'm.')

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
        with concurrent.futures.ThreadPoolExecutor() as executor:
            futures = [executor.submit(self.process_point, point, self.rec_x, self.rec_y) for point in self.points]
            concurrent.futures.wait(futures)

            for future in futures:
                result = future.result()
                if result is not None:
                    for del_point in result:
                        self.del_points.append(del_point)

        self.cross_out_points()

    @staticmethod
    def process_point(point, rec_x, rec_y):
        flag_point = False
        del_points = []

        if rec_x[0] <= point[0] <= rec_x[1] or rec_x[1] <= point[0] <= rec_x[0]:
            for i in range(1, 6):
                if point[i] != '':
                    if rec_x[1] >= point[0] >= rec_x[0] and rec_y[1] <= point[i] <= rec_y[0]:
                        flag_point = True
                        del_points.append([point[0], point[i], i])
                    elif rec_x[1] <= point[0] <= rec_x[0] and rec_y[1] <= point[i] <= rec_y[0]:
                        flag_point = True
                        del_points.append([point[0], point[i], i])
                    elif rec_x[1] <= point[0] <= rec_x[0] and rec_y[1] >= point[i] >= rec_y[0]:
                        flag_point = True
                        del_points.append([point[0], point[i], i])
                    elif rec_x[1] >= point[0] >= rec_x[0] and rec_y[1] >= point[i] >= rec_y[0]:
                        flag_point = True
                        del_points.append([point[0], point[i], i])

        if flag_point == True:
            return del_points
        else:
            return

    def cross_out_points(self):
        for del_point in self.del_points:
            self.ax.plot(del_point[0], del_point[1], 'k.')
        self.canvas.draw()

root = tk.Tk()
app = PointPlotterApp(root)
root.mainloop()