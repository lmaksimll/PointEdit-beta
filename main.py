import tkinter as tk
from tkinter import (filedialog, messagebox, ttk)
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import (FigureCanvasTkAgg, NavigationToolbar2Tk)
from matplotlib.patches import Rectangle
import csv
import concurrent.futures

class CustomToolbar(NavigationToolbar2Tk):
    def __init__(self, canvas_, parent_, root_):
        self.toolitems = (
            ('Home', 'Reset original view', 'home', 'home'),
            ('Back', 'Back to previous view', 'back', 'back'),
            ('Forward', 'Forward to next view', 'forward', 'forward'),
            (None, None, None, None),
            ('Pan', 'Pan axes with left mouse, zoom with right', 'move', 'pan'),
            ('Zoom', 'Zoom to rectangle', 'zoom_to_rect', 'zoom'),
            (None, None, None, None),
        )

        self.button_select_flag = False

        super().__init__(canvas_, parent_)

        self.custom_button = tk.Button(self, text="Edit points", command=self.custom_action)
        self.custom_button.pack(side=tk.LEFT)

        self.root = root_
        self.root.bind('<i>', self.custom_action_event)

    def custom_action_event(self,event):
        self.custom_action()

    def custom_action(self):
        if not self.button_select_flag:
            self.custom_button.config(relief="sunken")
            if self.mode == 'pan/zoom':
                self.pan()
            elif self.mode == 'zoom rect':
                self.zoom()
        else:
            self.custom_button.config(relief="raised")

        self.button_select_flag = not self.button_select_flag

    def pan(self):
        if self.button_select_flag:
            self.button_select_flag = False
            self.custom_button.config(relief="raised")
        super().pan()

    def zoom(self):
        if self.button_select_flag:
            self.button_select_flag = False
            self.custom_button.config(relief="raised")
        super().zoom()


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

        self.toolbar = CustomToolbar(self.canvas, self.frame_top, root)
        self.toolbar.update()

        # -------------------variables-------------------
        self.points = []
        self.tmp_points = []
        self.del_points = []
        self.extend_del_points = []

        self.rec_x = [None, None]
        self.rec_y = [None, None]

        self.button_release_flag = False

        # -------------------buttons-------------------
        ttk.Separator(self.toolbar, orient='vertical').pack(side='left', padx=5)

        self.open_button = tk.Button(self.toolbar, text="Open file", command=self.open_points)
        self.open_button.pack(side='left', padx=5)

        self.save_button = tk.Button(self.toolbar, text="Save file", command=self.save_points)
        self.save_button.pack(side='left', padx=5)

        ttk.Separator(self.toolbar, orient='vertical').pack(side='left', padx=5)

        self.delete_button = tk.Button(self.toolbar, text="Delete points", command=self.delete_points)
        self.delete_button.pack(side='left', padx=5)

        self.return_button = tk.Button(self.toolbar, text="Return points", command=self.selection_return)
        self.return_button.pack(side='left', padx=5)

        ttk.Separator(self.toolbar, orient='vertical').pack(side='left', padx=5)

        self.apply_button = tk.Button(self.toolbar, text="Apply_changes", command=self.apply_changes_warning)
        self.apply_button.pack(side='left', padx=100)

        # -------------------bind-------------------
        self.root.bind('<Escape>', self.on_closing)
        self.root.bind('<Delete>', self.delete_points_event)
        self.root.bind('<Return>', self.apply_changes_event)
        self.root.bind('<\>', self.return_points_event)

        # -------------------info bind-------------------
        self.toolbar.custom_button.bind("<Enter>", lambda event: self.on_enter(event, 'edit'))
        self.toolbar.custom_button.bind("<Leave>", lambda event: self.on_leave(event, 'edit'))

        self.delete_button.bind("<Enter>", lambda event: self.on_enter(event, 'delete'))
        self.delete_button.bind("<Leave>", lambda event: self.on_leave(event, 'delete'))

        self.return_button.bind("<Enter>", lambda event: self.on_enter(event, 'return'))
        self.return_button.bind("<Leave>", lambda event: self.on_leave(event, 'return'))

        # -------------------connect-------------------
        self.canvas.mpl_connect('button_press_event', self.on_press)
        self.canvas.mpl_connect('button_release_event', self.on_release)
        self.canvas.mpl_connect('motion_notify_event', self.on_motion)


    def on_enter(self, event, btn):
        if btn == 'edit':
            self.toolbar.custom_button.tooltip = ttk.Label(self.root, text="Selecting an area (Key - I)")
            self.toolbar.custom_button.tooltip.place(x=self.root.winfo_pointerx(), y=self.root.winfo_pointery())
            self.toolbar.custom_button.tooltip.lift()
        elif btn == 'delete':
            self.delete_button.tooltip = ttk.Label(self.root, text="Delete selected points (Key - Delete)")
            self.delete_button.tooltip.place(x=self.root.winfo_pointerx(), y=self.root.winfo_pointery())
            self.delete_button.tooltip.lift()
        elif btn == 'return':
            self.return_button.tooltip = ttk.Label(self.root, text="Return deleted points (Key - \)")
            self.return_button.tooltip.place(x=self.root.winfo_pointerx(), y=self.root.winfo_pointery())
            self.return_button.tooltip.lift()

    def on_leave(self, event, btn):
        if btn == 'edit':
            self.toolbar.custom_button.tooltip.destroy()
        elif btn == 'delete':
            self.delete_button.tooltip.destroy()
        elif btn == 'return':
            self.return_button.tooltip.destroy()

    def on_closing(self, event):
        if messagebox.askokcancel("Close", "Are you sure you want to close the application?"):
            self.root.destroy()

    def on_press(self, event):
        if self.toolbar.button_select_flag:
            self.button_release_flag = False
            self.rec_x[0] = event.xdata
            self.rec_y[0] = event.ydata

            self.rect.set_xy((self.rec_x[0], self.rec_y[0]))

        self.deselect_points()
        self.canvas.draw()

    def on_release(self, event):
        if self.toolbar.button_select_flag:
            self.button_release_flag = True

            if len(self.points) > 0:
                self.selection_points_thread()

            self.rect.remove()

    def on_motion(self, event):
        if self.toolbar.button_select_flag == True and self.rec_x[0] != None and self.button_release_flag == False:
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
            self.tmp_points.clear()
            self.del_points.clear()
            self.extend_del_points.clear()

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
        if len(self.tmp_points) == 0:
            return

        tmp_del_list = []

        if len(self.del_points) > 0:
            for del_point in self.extend_del_points:
                for tmp_point in self.tmp_points:
                    if tmp_point == del_point:
                        self.ax.plot(tmp_point[0], tmp_point[1], marker='.', color='#D3D3D3')
                        self.tmp_points.remove(tmp_point)

        for tmp_point in self.tmp_points:
            tmp_del_list.append(tmp_point)

        if len(self.tmp_points) > 0:
            self.del_points.append(tmp_del_list)
            self.extend_del_points.extend(tmp_del_list)
            self.tmp_points.clear()
            self.cross_out_del_points(tmp_del_list)

    def apply_changes_event(self, event):
        self.apply_changes_warning()

    def apply_changes_warning(self):
        if messagebox.askokcancel("Apply", "Are you sure you want to apply the changes? You will not be able to revert deleted points."):
            self.apply_changes()

    def apply_changes(self):
        if len(self.del_points) == 0:
            return

        for del_point in self.extend_del_points:
            for point in self.points:
                if point[0] == del_point[0] and point[int(del_point[2])] == del_point[1]:
                    point[int(del_point[2])] = ''
                    if point[1] and point[2] and point[3] and point[4] and point[5] == '':
                        self.points.remove(point)

        self.del_points.clear()
        self.tmp_points.clear()
        self.extend_del_points.clear()

        self.plot_points()

    def return_points_event(self, event):
        self.selection_return()

    def selection_return(self):
        if len(self.del_points) == 0:
            return

        tmp_list = self.return_points_in_area_by_Alex()

        if len(tmp_list) == 0:
            tmp_list = self.return_points()

        self.plot_return_points(tmp_list)

        self.extend_del_points.clear()
        for del_point in self.del_points:
            self.extend_del_points.extend(del_point)

        self.deselect_points()

    def return_points(self):
        tmp_list = self.del_points[-1]
        self.del_points.pop()

        return tmp_list

    def return_points_in_area_by_Alex(self):
        tmp_list = []
        points_to_remove = []

        for index, del_point in enumerate(self.del_points):
            for d_p in del_point:
                if self.rec_x[0] <= d_p[0] <= self.rec_x[1] or self.rec_x[1] <= d_p[0] <= self.rec_x[0]:
                    if self.rec_x[1] >= d_p[0] >= self.rec_x[0] and self.rec_y[1] <= d_p[1] <= self.rec_y[0]:
                        tmp_list.append(d_p)
                        points_to_remove.append((index, d_p))

                    elif self.rec_x[1] <= d_p[0] <= self.rec_x[0] and self.rec_y[1] <= d_p[1] <= self.rec_y[0]:
                        tmp_list.append(d_p)
                        points_to_remove.append((index, d_p))

                    elif self.rec_x[1] <= d_p[0] <= self.rec_x[0] and self.rec_y[1] >= d_p[1] >= self.rec_y[0]:
                        tmp_list.append(d_p)
                        points_to_remove.append((index, d_p))

                    elif self.rec_x[1] >= d_p[0] >= self.rec_x[0] and self.rec_y[1] >= d_p[1] >= self.rec_y[0]:
                        tmp_list.append(d_p)
                        points_to_remove.append((index, d_p))

        for index, point in points_to_remove:
            self.del_points[index].remove(point)

        # Удаление пустых списков
        self.del_points = [del_point for del_point in self.del_points if del_point]

        return tmp_list

    def plot_return_points(self, tmp_list):
        for res_point in tmp_list:
            if res_point[2] == 1:
                self.ax.plot(res_point[0], res_point[1], 'r.')
            elif res_point[2] == 2:
                self.ax.plot(res_point[0], res_point[1], 'g.')
            elif res_point[2] == 3:
                self.ax.plot(res_point[0], res_point[1], 'b.')
            elif res_point[2] == 4:
                self.ax.plot(res_point[0], res_point[1], 'y.')
            elif res_point[2] == 5:
                self.ax.plot(res_point[0], res_point[1], 'm.')
        self.canvas.draw()

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

    def deselect_points(self):
        if len(self.tmp_points) == 0:
            return

        if len(self.del_points) > 0:
            for del_point in self.extend_del_points:
                for tmp_point in self.tmp_points:
                    if tmp_point == del_point:
                        self.ax.plot(tmp_point[0], tmp_point[1], marker='.', color='#D3D3D3')
                        self.tmp_points.remove(tmp_point)

        self.plot_return_points(self.tmp_points)

        self.tmp_points.clear()

    def selection_points_thread(self):
        with concurrent.futures.ThreadPoolExecutor() as executor:
            futures = [executor.submit(self.process_point, point, self.rec_x, self.rec_y) for point in self.points]
            concurrent.futures.wait(futures)

            for future in futures:
                result = future.result()
                if result is not None:
                    for tmp_point in result:
                        self.tmp_points.append(tmp_point)

        self.cross_out_points()

    @staticmethod
    def process_point(point, rec_x, rec_y):
        flag_point = False
        tmp_points = []

        if rec_x[0] <= point[0] <= rec_x[1] or rec_x[1] <= point[0] <= rec_x[0]:
            for i in range(1, 6):
                if point[i] != '':
                    if rec_x[1] >= point[0] >= rec_x[0] and rec_y[1] <= point[i] <= rec_y[0]:
                        flag_point = True
                        tmp_points.append([point[0], point[i], i])
                    elif rec_x[1] <= point[0] <= rec_x[0] and rec_y[1] <= point[i] <= rec_y[0]:
                        flag_point = True
                        tmp_points.append([point[0], point[i], i])
                    elif rec_x[1] <= point[0] <= rec_x[0] and rec_y[1] >= point[i] >= rec_y[0]:
                        flag_point = True
                        tmp_points.append([point[0], point[i], i])
                    elif rec_x[1] >= point[0] >= rec_x[0] and rec_y[1] >= point[i] >= rec_y[0]:
                        flag_point = True
                        tmp_points.append([point[0], point[i], i])

        if flag_point == True:
            return tmp_points
        else:
            return

    def cross_out_points(self):
        for tmp_point in self.tmp_points:
            self.ax.plot(tmp_point[0], tmp_point[1], 'k.')
        self.canvas.draw()

    def cross_out_del_points(self, tmp_del_list):
        for tmp_del in tmp_del_list:
            self.ax.plot(tmp_del[0], tmp_del[1], marker='.', color='#D3D3D3')
        self.canvas.draw()

root = tk.Tk()
app = PointPlotterApp(root)
root.mainloop()