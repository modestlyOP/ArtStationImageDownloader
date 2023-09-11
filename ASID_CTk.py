import customtkinter
from tkinter import filedialog
from tkinter import StringVar
from tkinter import IntVar
import os
from platform import system as os_type
import subprocess
import re

# system settings:
customtkinter.set_appearance_mode("system")
customtkinter.set_default_color_theme("green")
## font settings:
HEADER = ('Roboto', 18)
REGULAR = ('Roboto', 12)
TERMINAL_WIN = ('Consolas', 12)
TERMINAL_NIX = ('Nimbus Mono L', 12)

class MainFrame(customtkinter.CTkFrame):
    def __init__(self, master, **kwargs):
        super().__init__(master, **kwargs)
        self.tbvw_mainTabview = Tabview(master=self, height=150, width=625, command=self.clearSelectedPath)
        self.tbvw_mainTabview.grid(row=0, column=0, padx=10, pady=10)

    # clear previously selected storage directory (logically), which should clear visually represented information in turn
    def clearSelectedPath(self):
        self.tbvw_mainTabview.STORE_PATH.set("")

class OutFrame(customtkinter.CTkFrame):
    def __init__(self, master, **kwargs):
        super().__init__(master, **kwargs)
        self.txtbx_out = customtkinter.CTkTextbox(master=self, wrap="char", height=150, width=625, state="disabled")
        self.lbl_header = customtkinter.CTkLabel(master=self, text="Output", font=HEADER)
        self.lbl_header.grid(row=0, column=0, pady=(10, 0), padx=10, sticky="w")
        self.txtbx_out.grid(row=1, column=0, padx=10, pady=10)

        if os_type() == 'Windows':
            self.txtbx_out.configure(font=TERMINAL_WIN)
        elif os_type() == 'Linux':
            self.txtbx_out.configure(font=TERMINAL_NIX)
        else:
            self.txtbx_out.configure(font=("Arial", 12))

class Tabview(customtkinter.CTkTabview):
    def __init__(self, master, **kwargs):
        super().__init__(master, **kwargs)
        self.STORE_PATH = StringVar(master=self, value="")
        self.STORE_UNAME = StringVar(master=self, value="")
        self.STORE_URL = StringVar(master=self, value="")
        self.STORE_MAXPRJ = IntVar(master=self, value=50)
        self.STORE_MAXPRJ_STR = StringVar(master=self, value=f"Fetch first {self.STORE_MAXPRJ.get()} projects")

        ### tabview elements ###
        #### scrape from likes page ####
        self.tab_LP = self.add("Likes Page")
        self.btn_selectPathLP = customtkinter.CTkButton(master=self.tab_LP, text="Select Storage\nPath", font=REGULAR, width=15, command=lambda: self.pathSelectDialog(self.ent_storepathLP))
        self.lbl_storepathLP = customtkinter.CTkLabel(master=self.tab_LP, text="Write to:", font=REGULAR)
        self.ent_storepathLP = customtkinter.CTkEntry(master=self.tab_LP, textvariable=self.STORE_PATH, font=REGULAR, width=250, state="readonly")
        self.lbl_username = customtkinter.CTkLabel(master=self.tab_LP, text="Username:", font=REGULAR)
        self.ent_username = customtkinter.CTkEntry(master=self.tab_LP, textvariable=self.STORE_UNAME, font=REGULAR, width=150)
        self.btn_runLP = customtkinter.CTkButton(master=self.tab_LP, text="Run", font=REGULAR, width=15, command=lambda: self.master.master.runProcessMgr(slctn=0))
        ##### slider that controls max number of projects to scan #####
        self.frm_prjMax = customtkinter.CTkFrame(master=self.tab_LP, width=250, height=50)
        self.lbl_prjMax_title = customtkinter.CTkLabel(master=self.frm_prjMax, textvariable=self.STORE_MAXPRJ_STR, font=REGULAR)
        # self.lbl_prjMax_title = customtkinter.CTkLabel(master=self.frm_prjMax, text=f"Fetch first {self.STORE_MAXPRJ.get()} projects")
        # self.after(500, self.updateNumPrj)
        self.sldr_prjMax = customtkinter.CTkSlider(master=self.frm_prjMax, from_=1, to=50, number_of_steps=50, variable=self.STORE_MAXPRJ, command=self.updateNumPrj)
        self.lbl_prjMax_min = customtkinter.CTkLabel(master=self.frm_prjMax, text=self.sldr_prjMax.cget("from_"), font=REGULAR)
        self.lbl_prjMax_max = customtkinter.CTkLabel(master=self.frm_prjMax, text=self.sldr_prjMax.cget("to"), font=REGULAR)
        ##### element placement #####
        self.btn_selectPathLP.grid(row=1, column=0, padx=10, pady=10)
        self.lbl_storepathLP.grid(row=0, column=1, padx=10, sticky="s")
        self.ent_storepathLP.grid(row=1, column=1, padx=10, pady=(0, 10))
        self.lbl_username.grid(row=0, column=2, padx=10, sticky="s")
        self.ent_username.grid(row=1, column=2, padx=10, pady=(0, 10))
        self.btn_runLP.grid(row=1, column=3, padx=10, pady=(0, 10))
        self.frm_prjMax.grid(row=2, columnspan=4, padx=10, pady=10)
        self.lbl_prjMax_title.grid(row=0, columnspan=3, padx=5, pady=5)
        self.sldr_prjMax.grid(row=1, column=1, padx=5, pady=5)
        self.lbl_prjMax_min.grid(row=1, column=0, pady=5, padx=15, sticky="e")
        self.lbl_prjMax_max.grid(row=1, column=2, pady=5, padx=15, sticky="w")
        #### scrape from project page ####
        self.tab_SP = self.add("Single Project")
        self.btn_selectPathSP = customtkinter.CTkButton(master=self.tab_SP, text="Select Storage\nPath", font=REGULAR, width=15, command=lambda: self.pathSelectDialog(self.ent_storepathSP))
        self.lbl_storepathSP = customtkinter.CTkLabel(master=self.tab_SP, text="Write to:", font=REGULAR)
        self.ent_storepathSP = customtkinter.CTkEntry(master=self.tab_SP, textvariable=self.STORE_PATH, font=REGULAR, width=250, state="readonly")
        self.lbl_url = customtkinter.CTkLabel(master=self.tab_SP, text="URL:", font=REGULAR)
        self.ent_url = customtkinter.CTkEntry(master=self.tab_SP, textvariable=self.STORE_URL, font=REGULAR, width=150)
        self.btn_runSP = customtkinter.CTkButton(master=self.tab_SP, text="Run", font=REGULAR, width=15, command=lambda: self.master.master.runProcessMgr(slctn=1))
        self.btn_selectPathSP.grid(row=1, column=0, padx=10, pady=10)
        self.lbl_storepathSP.grid(row=0, column=1, padx=5, sticky="s")
        self.ent_storepathSP.grid(row=1, column=1, padx=10, pady=(0, 10))
        self.lbl_url.grid(row=0, column=2, padx=5, sticky="s")
        self.ent_url.grid(row=1, column=2, padx=10, pady=(0, 10))
        self.btn_runSP.grid(row=1, column=3, padx=10, pady=(0, 10))

    def pathSelectDialog(self, ent):
        selectedFolder = filedialog.askdirectory()
        self.STORE_PATH.set(selectedFolder)

    def updateNumPrj(self, val):
        # val is automatically passed by the command param, when this function is used as a callback
        self.STORE_MAXPRJ_STR.set(f"Fetch the first {int(val)} projects")
        return int(val)

class ArtStationDownloader(customtkinter.CTk):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # app frame settings:
        self.title("ArtStation Image Downloader")
        self.resizable(width=False, height=False)

        # GUI elements #
        ## foundation elements ##
        self.frm_mainFrame = MainFrame(master=self)
        self.frm_outFrame = OutFrame(master=self)

        # element placement #
        ## foundation elements ##
        self.frm_mainFrame.pack(fill="both", expand=True, side="top")
        self.frm_outFrame.pack(fill="both", expand=True, side="bottom")

    # update txtbx_out (output textbox) with given text
    def writeOutputMsg(self, text, form='normal'):
        self.frm_outFrame.txtbx_out.configure(state="normal")
        self.frm_outFrame.txtbx_out.delete("1.0", "end")
        self.frm_outFrame.txtbx_out.insert(customtkinter.INSERT, text, form)
        self.update_idletasks()
        self.frm_outFrame.txtbx_out.tag_config('error', foreground='red')  # format text to red color if form is 'error'
        self.frm_outFrame.txtbx_out.configure(state="disabled")

    # def writeOutputScript(self, process):
    #     self.frm_outFrame.txtbx_out.configure(state="normal")
    #     self.frm_outFrame.txtbx_out.delete("1.0", "end")
    #     self.frm_outFrame.txtbx_out.insert(customtkinter.END, str(process))
    #     self.update_idletasks()
    #     self.frm_outFrame.txtbx_out.configure(state="disabled")
    #
    # def runScrapeLP(self, path, username):
    #     with subprocess.Popen(["node", "likespagedownloader.js", str(path), str(username)], shell=False, stdout=subprocess.PIPE, encoding="utf-8") as p:
    #         for line in p.stdout:
    #             self.update_idletasks()
    #             print(line)
    #             return line
    #
    # def runScrapeSP(self, path, link):
    #     with subprocess.Popen(["node", "singleprojectdownloader.js", str(path), str(link)], shell=False, stdout=subprocess.PIPE, encoding="utf-8") as p:
    #         for line in p.stdout:
    #             self.frm_outFrame.txtbx_out.insert(customtkinter.END, str(line))
    #             self.frm_outFrame.txtbx_out.update_idletasks()
    #             print(line)

    # check inputs, run external scripts if all good
    def runProcessMgr(self, slctn):
        # slctn <- tab selected (0, 1, ...), counting from left to right
        storepath = self.frm_mainFrame.tbvw_mainTabview.STORE_PATH.get()
        uname = self.frm_mainFrame.tbvw_mainTabview.STORE_UNAME.get()
        url = self.frm_mainFrame.tbvw_mainTabview.STORE_URL.get()
        maxPrj = int(self.frm_mainFrame.tbvw_mainTabview.STORE_MAXPRJ.get())
        output = ""

        # error checks:
        ##storage path valid? (not blank, does exist)
        if ((storepath == "") or not os.path.exists(storepath)):
            e = "Error: Storage path invalid"
            self.writeOutputMsg(e, 'error')
            return
        try:
            if (slctn == 0):
                ##username valid? (no special chars, not blank/space)
                if ((re.compile(r"[<>/{}[\]~`%]").search(uname) or (uname == "") or (uname == " "))):
                    e = "Error: Username invalid"
                    self.writeOutputMsg(e, 'error')
                    return
                else:
                    # scrape from given Likes page
                    # p = subprocess.check_output(f"node likespagedownloader.js {storepath} {uname}")
                    # output = p.decode("utf-8")
                    # self.writeOutputScript(self.runScrapeLP(storepath, uname))
                    self.frm_outFrame.txtbx_out.configure(state="normal")
                    self.frm_outFrame.txtbx_out.delete("1.0", "end")
                    with subprocess.Popen(["node", "likespagedownloader.js", str(storepath), str(uname), str(maxPrj)], shell=False, stdout=subprocess.PIPE, encoding="utf-8") as p:
                        for line in p.stdout:
                            self.frm_outFrame.txtbx_out.insert(customtkinter.END, line)
                            self.update_idletasks()
                            print(line)

                    self.frm_outFrame.txtbx_out.configure(state="disabled")
            elif (slctn == 1):
                ##project url valid? (not blank/space, starts with actual https url)
                if ((url == "") or (url == " ") or not (url.startswith("https://www.artstation.com/artwork/"))):
                    print(url)
                    e = "Error: URL invalid"
                    self.writeOutputMsg(e, 'error')
                    return
                else:
                    # scrape from given project page
                    self.frm_outFrame.txtbx_out.configure(state="normal")
                    self.frm_outFrame.txtbx_out.delete("1.0", "end")
                    # p = subprocess.check_output(f"node singleprojectdownloader.js {storepath} {url}")
                    # output = p.decode("utf-8")
                    with subprocess.Popen(["node", "singleprojectdownloader.js", str(storepath), str(url)], shell=False, stdout=subprocess.PIPE, encoding="utf-8") as p:
                        for line in p.stdout:
                            self.frm_outFrame.txtbx_out.insert(customtkinter.END, str(line))
                            self.frm_outFrame.txtbx_out.update_idletasks()
                            print(line)
                    self.frm_outFrame.txtbx_out.configure(state="disabled")
            # self.writeOutput(output)
        except (subprocess.SubprocessError, subprocess.CalledProcessError):
            e = "Something went wrong. Ensure both inputs exist."
            self.writeOutputMsg(e, 'error')


if __name__ == "__main__":
    app = ArtStationDownloader()
    app.mainloop()
