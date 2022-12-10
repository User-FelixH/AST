## APG Stunden Tracking - AST v1
## Felix H.
## Dezember 2022, letzte Änderung 04.12.2022
##
## Offene Aufgaben: Zeitlimit vorsehen, Config Editor
## Erledigt: 08.12.2022 - Vormittag - Projekte in JSON Format strukturieren - Typ, Projekt/Thema, Workpackages, Topics, Visbility
## Erledigt: 08.12.2022 - Nachmittag Reporting Funktion
##
import time
import tkinter as tk
import tkinter.ttk as ttk
import ttkthemes
from tkinter.scrolledtext import ScrolledText
from functools import partial
import json
import csv
import numpy as np
import pandas as pd

bg_color = "#eef1f2"
fg_color = "#243845"
hl_color = "#c14239"

class ZeitObjekt:
   """Zeiterfassungsobjekt für ein Projekt

   Attributes:
       name (str): Projektname
       csv_path (str): Speicherort für csv Logs
       StartT (int): Startzeitpunkt der letzten Aktivierung in Sekunden
       CurrentT (int): Eintrag für den aktuellen Zeitstempel in Sekunden
       elapsed_T (str): Verganene Zeit zwischen Aktivierung und aktuellem Zeitstempel
       Total_T (int): Gezählte Zeit seit Programmstart
       active (bool): Gibt an ob aktuell für dieses Projekt die Zeit erfasst werden soll
       parent_vector (str): Liste aller anderen Projekte

   Methods: To be filled
   """
   def __init__(self, p_element, csv_path):
       self.name = p_element["Name"]
       self.topic = p_element["Topic"]
       self.wps = p_element["Workpackages"]
       self.ilv = p_element["ILV"]
       self.visible = True if (p_element["Visible"]=="True") else False #Objekt nach JSON File
       self.csv_path = csv_path
       self.StartT = 0
       self.CurrentT = 0
       self.elapsed_T = 0
       self.Total_T = 0
       self.active = False
       self.parent_vector = 0

   def set_parent_vector(self, parent_vector):
       self.parent_vector = parent_vector

   def activate(self):
       self.active = True
       self.StartT = time.time()

   def update(self):
       if (self.active == True):
           self.CurrentT = time.time()
           self.elapsed_T = round(self.CurrentT - self.StartT)

   def deactivate(self):
       if (self.active == True):
           self.update()
           self.active = False
           self.Total_T = self.Total_T + self.elapsed_T
           self.log_to_csv()
           self.elapsed_T = 0
           reset_entry()
       else:
           print("Info: check code - deactivate was called for inactive time tracker")

   def toggle(self):
       if (self.active == True):
           self.deactivate()
       else:
           self.activate()

   def print(self):
       return (self.name.ljust(25) + "\t\nt-Momentan:\t" + time.strftime("%H:%M:%S",time.gmtime(self.elapsed_T)) + "\nt-Gesamt:\t" + time.strftime("%H:%M:%S",time.gmtime(self.Total_T))) #+ str(self.elapsed_T)

   def highlander_toggle(self):
       for p_temp in self.parent_vector:
           if (p_temp != self):
              if(p_temp.active == True):
                  p_temp.deactivate()
           else:
               p_temp.toggle()

   def log_to_csv(self):
       #"Date, Duration (h), Topic, Project, Workpackage, Task, Comment, User, From, To,ILV\n")
       logdict = {}
       logdict["Date"] = time.strftime("%d.%m.%Y",time.localtime(time.time()))
       logdict["Duration(h)"] = round((self.elapsed_T) / 3600, 3)
       logdict["Topic"] = self.topic
       logdict["Project"] = self.name
       logdict["Workpackage"] = WORKPACKAGE.get()
       logdict["Task"] = TASK.get()
       if (FINISH_WITH_COMMENT.get() != True):
           logdict["Comment"] = "'-"
       else:
           logdict["Comment"] = "Kommentar: " + WORK_COMMENT.get()
       logdict["User"] = user # hier gehört der Code noch aufgebessert - globale User Variable fraglich
       logdict["From"] = time.strftime("%d.%m.%Y %H:%M",time.localtime(self.StartT))
       logdict["To"] = time.strftime("%d.%m.%Y %H:%M",time.localtime(self.CurrentT))
       logdict["ILV"] = self.ilv
       try:
           with open(self.csv_path, "a") as temp_f:
               t_fieldnames = list(logdict.keys())
               writer = csv.DictWriter(temp_f, fieldnames=t_fieldnames,lineterminator="\r")
               writer.writerow(logdict)
       except:
           print("Error while logging to csv - " + self.csv_path)
       logdict = 0

# load config and initialize all timers
f = open('./Settings/config.json')
config = json.load(f)
user = config["user"]
plist_path = config["plist_path"]
tsheet_path = config["tsheet_path"]

try:
   with open(plist_path, "r", encoding='utf-8') as p_list_file:
       p_overview = json.load(p_list_file)
       p_list = p_overview["Projects"] #p_list = [p_temp["Name"] for p_temp in p_list1]
       Aufgaben = p_overview["Tasks"]
except:
    p_list = ["P1", "P2", "P3"]

try:
   with open(tsheet_path, "r", encoding='utf-8') as p_list_file:
       t_header = p_list_file.readline()
       if (t_header == "## Timesheet-Header --- do not delete"):
           print("Timesheet appears available")
except:
   print("There appears to be an error when trying to load the timesheet")
   with open(tsheet_path, "w", encoding='utf-8') as p_list_file:
       p_list_file.writelines("##Timesheet-Header --- do not delete\n")
       p_list_file.writelines("Date,Duration (h),Topic,Project,Workpackage,Task,Comment,User,From,To,ILV\n")


p_timers = [ZeitObjekt(p_element, tsheet_path) for p_element in p_list]  # from Config fill Timers
[p_temp.set_parent_vector(p_timers) for p_temp in p_timers]  # configure parent Vector

def eval_timesheet(path):
    timesheet = pd.read_csv(path,skiprows=1,dayfirst=True,parse_dates=[0])
    #timesheet["Month"] = timesheet.Date.month
    df_topic = timesheet[["Date", "Duration (h)", "Topic"]]
    df_topic.insert(1,"Month",pd.DatetimeIndex(df_topic.Date).month)
    df_topic = df_topic[["Month", "Topic","Duration (h)"]].groupby(["Month","Topic"]).sum().transpose()
    #print(df_topic)

    df_project = timesheet[["Date", "Duration (h)", "Project","ILV"]]
    df_project.insert(1,"Month",pd.DatetimeIndex(df_project.Date).month)
    df_project = df_project[df_project.ILV ==True]
    df_project = df_project[["Month", "Project", "Duration (h)"]].groupby(["Month", "Project"]).sum().transpose()

    OutTk = tk.Toplevel()  # tk.Tk()# arc ... theme="equilux"
    OutFrame = ttk.Frame(OutTk)
    OutFrame.pack()
    st = ScrolledText(OutFrame, width=90, height=20)
    st.tag_configure('color', foreground=fg_color, background=bg_color)
    st.insert(tk.END, "Nach Thema fuer Gruppe:\n")
    st.insert(tk.END, df_topic.to_csv(),"color")
    st.insert(tk.END, "\n\nNach Projekt für Stundenmeldung:\n")
    st.insert(tk.END, df_project.to_csv(), "color")
    st.configure(state='disabled')
    st.pack(fill=tk.BOTH, side=tk.LEFT, expand=True)


def stop_all():
   for p_temp in p_timers:
       if (p_temp.active) == True:
           p_temp.deactivate()
   WP_Select.delete(0, 'end')
   Task_Select.delete(0,'end')


#defining the interface
root = ttkthemes.ThemedTk(theme="equilux") #tk.Tk()# arc ... theme="equilux"
window = ttk.Frame(root)
window.pack()
style = ttk.Style()
style.configure("TFrame", background="#243845", foreground = "#b4d0e0")
style.configure("TLabel", background="#243845",foreground = "#b4d0e0")
style.configure("TEntry", background="#243845",foreground = "#b4d0e0")
style.configure("TCombobox", background="#243845",foreground = "#b4d0e0")
style.configure("TCheckbutton", background="#243845",foreground = "#b4d0e0")
style.configure("TButton", background="#243845",foreground="#b4d0e0",padding=(10, 10))
style.configure("Line.TSeparator", bg="red",fg="blue")
style.configure("TScrolledtext", background="#243845", foreground = "#b4d0e0")
style.map('TButton',foreground=[('pressed', '#243845'),('active', '#c6463c')]) # foreground =
root.title("Schnell und einfach Projektstunden tracken")

#TK Vars
WORKPACKAGE = tk.StringVar()
TASK = tk.StringVar()
FINISH_WITH_COMMENT = tk.IntVar()
WORK_COMMENT = tk.StringVar()

#Layout u. TK Funktionen
Ueberschrift = ttk.Label(window,text="Time Tracking",font=("Arial", 20))
Ueberschrift.pack()
Anzeige = ttk.Label(window,text="Projekt".ljust(25) + "\nt-Momentan:\t00:00:00\nt-Gesamt:\t00:00:00", pad = 5)
Anzeige.pack()

def timed_update():
   for p_timer in p_timers:
       p_timer.update()
       if (p_timer.active == True):
           Anzeige.config(text=p_timer.print())
   window.after(500, timed_update)

def hl_toggle(p_name):
    for p_temp in p_timers:
        if (p_temp.name) == p_name:
            p_temp.highlander_toggle()
            WP_Select.delete(0,'end')
            Task_Select.delete(0,'end')
            WP_Select['values'] = p_temp.wps
            Task_Select['values'] = Aufgaben

First_Seperator = ttk.Separator(window, orient = "vertical", style="Line.TSeparator")
First_Seperator.pack(fill='x')

# Projektbezogene Buttons
B_Frame = ttk.Frame(window, pad=5)
B_Frame.configure()
B_Frame.pack()
P_Buttons = [ttk.Button(B_Frame, text=temp.name, command=partial(hl_toggle, temp.name)) for temp in p_timers if temp.visible==True]
[temp_button.pack(side="left") for temp_button in P_Buttons]
Stop_Button = ttk.Button(B_Frame, text="Stop", command=stop_all)
Stop_Button.pack(side="left")

Second_Seperator = ttk.Separator(window, orient="vertical", style="Line.TSeparator")
Second_Seperator.pack(fill='x')

# Auswahlmenues
M_Frame = ttk.Frame(window, pad=5)
M_Frame.configure()
M_Frame.pack()
WP_label = ttk.Label(M_Frame, text="Arbeitspaket: ", pad=5)
WP_label.pack(side="left")
WP_Select = ttk.Combobox(M_Frame, textvariable=WORKPACKAGE)
WP_Select.pack(side="left")
Task_label = ttk.Label(M_Frame, text="Aufgabentyp:", pad=5)
Task_label.pack(side="left")
Task_Select = ttk.Combobox(M_Frame, textvariable=TASK)
Task_Select.pack(side="left")


#Third_Separator = ttk.Separator(window, orient = "vertical", style="Line.TSeparator")
#Third_Separator.pack(fill='x')

# Options-menue
O_Frame = ttk.Frame(window)
O_entry = ttk.Entry(O_Frame, textvariable = WORK_COMMENT, style = "TEntry", width = 50)
O_entry.config(state="disabled")
def reset_entry():
   O_entry.delete(0,'end')
   O_entry.pack()
   if (FINISH_WITH_COMMENT.get() == True):
       O_entry.config(state="enabled")
   else:
       O_entry.config(state="disabled")
Option_Comment = ttk.Checkbutton(O_Frame, variable = FINISH_WITH_COMMENT, text="mit Kommentar: ", command = reset_entry)
Option_Comment.pack(side="left")
O_entry.pack(side = "left")
O_Frame.pack()

Fourth_Separator = ttk.Separator(window, orient = "vertical", style="Line.TSeparator")
Fourth_Separator.pack(fill='x')

#Comments and more
C_Frame = ttk.Frame(window)
C_Frame.pack()
C_Label = ttk.Label(C_Frame,text="Einstellungen: ", pad = 5)
C_Label.pack(side="left", fill="x")
#Config_Button = ttk.Button(C_Frame, text="Config")
#Config_Button.pack(side="left")
Report_Button = ttk.Button(C_Frame, text="Report", command = partial(eval_timesheet, tsheet_path))
Report_Button.pack(side="left")
window.after(500, timed_update)
window.mainloop()

