import os
import subprocess
import re
import tkinter as tk
from tkinter import ttk
from tkinter import scrolledtext
from tkinter import filedialog

class ArtStationImageDownloader(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("ArtStation Image Downloader")
        self.resizable(width=False, height=False)
        self.style = ttk.Style(self)
        self.style.theme_use(ttk.Style().theme_names()[1])

        ## initialize "global" vars used by UI elements ##
        self.STORE_PATH = tk.StringVar(master=self, value="")
        self.STORE_UNAME = tk.StringVar(master=self, value="")
        self.STORE_URL = tk.StringVar(master=self, value="")

        ## GUI elements ##
        ### foundation elements ##
        self.frm_mainFrame = ttk.Frame(master=self, name='mainFrame')
        self.ntbk_mainNotebook = ttk.Notebook(master=self.frm_mainFrame, name='mainNotebook')
        self.lblfrm_outFrame = ttk.LabelFrame(master=self, text="Output", relief=tk.SOLID, name='outputFrame')
        self.txtbx_out = tk.scrolledtext.ScrolledText(master=self.lblfrm_outFrame, wrap=tk.WORD, height=15, width=self.ntbk_mainNotebook['width'], state="disabled", relief=tk.FLAT, name='outputBox')
        ### notebook elements ###
        #### scrape from likes page ####
        self.frm_likespageFrame = tk.Frame(master=self.ntbk_mainNotebook, width= 150, height=60, name='likespageFrame')
        self.btn_selectPathLP = ttk.Button(master=self.frm_likespageFrame, text="Select Storage\nPath", width=15, command=lambda: self.pathSelectDialog(self.ent_storepathLP), name='btn_selectpath')
        self.lbl_storepathLP = ttk.Label(master=self.frm_likespageFrame, text="Write to:")
        self.ent_storepathLP = ttk.Entry(master=self.frm_likespageFrame, width=25, textvariable=self.STORE_PATH, state="readonly", name='ent_storepath')
        self.lbl_username = ttk.Label(master=self.frm_likespageFrame, text="Username:")
        self.ent_username = ttk.Entry(master=self.frm_likespageFrame, width=25, name='ent_username')
        self.btn_runLP = ttk.Button(master=self.frm_likespageFrame, text="Run", width=15, name='btn_run', command=lambda: self.runScript(slctn=0))
        #### scrape from single project ####
        self.frm_singleprojFrame = tk.Frame(master=self.ntbk_mainNotebook, width=150, height=60, name='singleprojectFrame')
        self.btn_selectPathSP = ttk.Button(master=self.frm_singleprojFrame, text="Select Storage\nPath", width=15, command=lambda:self.pathSelectDialog(self.ent_storepathSP))
        self.lbl_storepathSP = ttk.Label(master=self.frm_singleprojFrame, text="Write to:")
        self.ent_storepathSP = ttk.Entry(master=self.frm_singleprojFrame, width=25, textvariable=self.STORE_PATH, state="readonly", name='ent_storepath')
        self.lbl_url = ttk.Label(master=self.frm_singleprojFrame, text="URL:")
        self.ent_url = ttk.Entry(master=self.frm_singleprojFrame, width=25, name='ent_url')
        self.btn_runSP = ttk.Button(master=self.frm_singleprojFrame, text="Run", width=15, name='btn_run', command=lambda: self.runScript(slctn=1))

        ## element placement ##
        ### foundation elements ###
        self.frm_mainFrame.pack(fill=tk.BOTH, expand=True, side=tk.TOP)
        self.ntbk_mainNotebook.grid(row=0, column=0, padx=10, pady=10)
        self.lblfrm_outFrame.pack(fill=tk.BOTH, expand=True, side=tk.BOTTOM)
        self.txtbx_out.pack(fill=tk.BOTH, expand=True)
        ### tab in ntbk_mainNotebook - scrape from likes page ###
        self.frm_likespageFrame.pack(fill=tk.BOTH, expand=True)
        self.ntbk_mainNotebook.add(self.frm_likespageFrame, text='Likes Page')
        self.btn_selectPathLP.grid(row=0, column=0, padx=10, pady=10)
        self.lbl_storepathLP.grid(row=0, column=1, padx=5, pady=5, sticky="N")
        self.ent_storepathLP.grid(row=0, column=1, padx=10, pady=10)
        self.lbl_username.grid(row=0, column=2, padx=5, pady=5, sticky="N")
        self.ent_username.grid(row=0, column=2, padx=10, pady=10)
        self.btn_runLP.grid(row=0, column=3, padx=10, pady=10)
        ### tab in ntbk_mainNotebook - scrape from single project ###
        self.frm_singleprojFrame.pack(fill=tk.BOTH, expand=True)
        self.ntbk_mainNotebook.add(self.frm_singleprojFrame, text='Single Project')
        self.btn_selectPathSP.grid(row=0, column=0, padx=10, pady=10)
        self.lbl_storepathSP.grid(row=0, column=1, padx=5, pady=5, sticky="N")
        self.ent_storepathSP.grid(row=0, column=1, padx=10, pady=10)
        self.lbl_url.grid(row=0, column=2, padx=5, pady=5, sticky="N")
        self.ent_url.grid(row=0, column=2, padx=10, pady=10)
        self.btn_runSP.grid(row=0, column=3, padx=10, pady=10)

        #bind ntbk_mainNotebook's tab-changing event to a function that clears the selected storage directory:
        self.ntbk_mainNotebook.bind('<<NotebookTabChanged>>', self.clearSelectedPath)

    #open prompt for storage path selection
    def pathSelectDialog(self, ent):
        selectedFolder = filedialog.askdirectory()
        self.STORE_PATH.set(selectedFolder)

    #
    def clearSelectedPath(self, event):
        self.STORE_PATH.set("")

    def writeOutput(self, text, form='normal'):
        self.txtbx_out.config(state="normal")
        self.txtbx_out.delete("1.0", "end")
        self.txtbx_out.insert(tk.INSERT, text, form)
        self.txtbx_out.tag_config('error', foreground='red')
        self.txtbx_out.config(state="disabled")

    def runScript(self, slctn):
        storepath = self.STORE_PATH.get()
        self.STORE_UNAME.set(self.ent_username.get())
        uname = self.STORE_UNAME.get()
        self.STORE_URL.set(self.ent_url.get())
        url = self.STORE_URL.get()
        output = ""

        #error checks:
        if ((storepath == "") or not os.path.exists(storepath)):
            # print("storage path invalid...")         #debug print
            e = "Error: Storage path invalid"
            self.writeOutput(e, 'error')
            return
        try:
            if(slctn == 0):
                if((re.compile(r"[<>/{}[\]~`%]").search(uname) or (uname == "") or (uname == " "))):
                    e = "Error: Username invalid"
                    self.writeOutput(e, 'error')
                    return
                else:
                    # default selection: scrape from likes page
                    p = subprocess.check_output(f"node likespagedownloader.js {storepath} {uname}")
                    output = p.decode("utf-8")
            elif (slctn == 1):
                if((url == "") or (url == " ") or not (url.startswith("https://www.artstation.com/artwork/"))):
                    e = "Error: URL invalid"
                    self.writeOutput(e, 'error')
                    return
                else:
                    #alt selection: scrape from given project page
                    p = subprocess.check_output(f"node singleprojectdownloader.js {storepath} {url}")
                    output = p.decode("utf-8")
            #print(output)           #debug print
            self.writeOutput(output)
        except (subprocess.SubprocessError, subprocess.CalledProcessError):
            e = "Something went wrong. Ensure inputs exist."
            self.writeOutput(e, 'error')





if __name__ == "__main__":
    app = ArtStationImageDownloader()
    app.mainloop()