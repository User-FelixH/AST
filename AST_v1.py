## APG Stunden Tracking - AST v1
## Felix H.
## Dezember 2022, letzte Änderung 04.12.2022
import time
import tkinter as tk
import json
import csv

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
    def __init__(self, p_name, csv_path):
        self.name = p_name
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
        return (self.name.ljust(25) + "\t\nt-Momentan:\t" + time.strftime("%M:%S",time.localtime(self.elapsed_T)) + "\nt-Gesamt:\t\t" + time.strftime("%M:%S",time.localtime(self.Total_T))) #+ str(self.elapsed_T)

    def highlander_toggle(self):
        for p_temp in self.parent_vector:
            if (p_temp != self):
               if(p_temp.active == True):
                   p_temp.deactivate()
            else:
                p_temp.toggle()

    def log_to_csv(self):
        # Date, Duration (h), Task, Comment, User, From, To,
        logdict = {}
        logdict["Date"] = time.strftime("%d.%m.%Y",time.localtime(time.time()))
        logdict["Duration(h)"] = round((self.elapsed_T) / 3600, 3)
        logdict["Task"] = self.name
        if (FINISH_WITH_COMMENT.get() != True):
            logdict["Comment"] = "Kein Kommentar " + str(FINISH_WITH_COMMENT.get())
        else:
            #c_input = tk.Tk()
            #c_input.title("Kommentar/Arbeitsbeschreibung eingeben")
            #c_input.configure(bg = bg_color)
            #c_ok = tk.Button(c_input,text="Ok", command = c_input.destroy)
            #c_ok.pack()
            #c_input.wait_window(c_input)
            #time.sleep(0.2)
            logdict["Comment"] = "Kommentar: " + WORK_COMMENT.get()
        logdict["User"] = user # hier gehört der Code noch aufgebessert - globale User Variable fraglich
        logdict["From"] = time.strftime("%d.%m.%Y %H:%M",time.localtime(self.StartT))
        logdict["To"] = time.strftime("%d.%m.%Y %H:%M",time.localtime(self.CurrentT))
        try:
            with open(self.csv_path, "a") as temp_f:
                fieldnames = logdict.keys()
                writer = csv.DictWriter(temp_f, fieldnames=list(logdict.keys()))
                #writer.writeheader()
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
        p_list = p_list_file.readlines()
        p_list = [p_temp.strip() for p_temp in
                  p_list]  # p_list = ["00_Administration","10_Netzanalysen","20_Projekte","30_Test"]
except:
    with open(plist_path, "w", encoding='utf-8') as p_list_file:
        p_list_file.writelines("P1\nP2\nP3")
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
        p_list_file.writelines("Date, Duration (h), Task, Comment, User, From, To\n")


p_timers = [ZeitObjekt(p_element, tsheet_path) for p_element in p_list]  # from Config fill Timers
[p_temp.set_parent_vector(p_timers) for p_temp in p_timers]  # configure parent Vector

def stop_all():
    for p_temp in p_timers:
        if (p_temp.active) == True:
            p_temp.deactivate()
#
#                                       defining the interface
#
window = tk.Tk()
window.title("AST-v1")
window.configure(bg = "#eef1f2")
FINISH_WITH_COMMENT = tk.IntVar()
WORK_COMMENT = tk.StringVar()
Anzeige = tk.Label(text="Projekt".ljust(25)+
                        "\nt-Momentan:\t00:00\nt-Gesamt:\t\t00:00",
                   fg = fg_color,bg = bg_color)
Anzeige.pack()

def timed_update():
    for p_timer in p_timers:
        p_timer.update()
        if (p_timer.active == True):
            Anzeige.config(text=p_timer.print())
    window.after(500, timed_update)

B_Frame = tk.Frame(window)
B_Frame.configure(bg = bg_color)
B_Frame.pack()
P_Buttons = [tk.Button(B_Frame, text=temp.name, fg=fg_color, command=temp.highlander_toggle) for temp in
             p_timers]
[temp_button.pack(side="left") for temp_button in P_Buttons]
[temp_button.configure(bg = bg_color) for temp_button in P_Buttons]

# Zusatzknöpfe
Stop_Button = tk.Button(B_Frame, text="Stop", command=stop_all, bg = bg_color)
Stop_Button.pack(side="left")
O_Frame = tk.Frame(window)
O_entry = tk.Entry(O_Frame, textvariable = WORK_COMMENT, bg=bg_color,fg=hl_color)
def reset_entry():
    O_entry.delete(0,'end')
    O_entry.pack()
Option_Comment = tk.Checkbutton(O_Frame, variable = FINISH_WITH_COMMENT, text="Mit Kommentar abschliessen", bg = bg_color,fg = fg_color, command = reset_entry)
Option_Comment.pack()
O_Label = tk.Label(O_Frame, text="Kommentar: ",bg=bg_color,fg=fg_color)
O_Label.pack(side="left")
O_entry.pack(side = "left")
O_Frame.pack()
O_Frame.configure(bg = bg_color)
C_Frame = tk.Frame(window)
C_Frame.configure(bg = bg_color)
C_Frame.pack()
#Config_Button = tk.Button(C_Frame, text="Config")
#Report_Button = tk.Button(C_Frame, text="Report")
#Config_Button.pack(side="left")
#Report_Button.pack(side="left")
window.after(500, timed_update)
window.mainloop()
