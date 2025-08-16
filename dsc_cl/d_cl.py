import os
import shutil
import time
import threading
import tkinter as tk
from tkinter import filedialog, messagebox, ttk, simpledialog
from datetime import datetime
from send2trash import send2trash  # pip install send2trash

BG = "#bfbfbf"
BTN = "#d9d9d9"
BTN_FG = "#222222"
BTN_ACT = "#bfbfbf"
BTN_ACT_FG = "#111111"
LBOX_BG = "#e3e3e3"
LBOX_FG = "#222222"
FONT = "MS Sans Serif"
F_SIZE = 10
MONTHS = [1, 3, 6, 12, 24, 36]

class MultiSelDrop(tk.Toplevel):
    def __init__(self, parent, opts, selected, cb):
        super().__init__(parent)
        self.title("Select file types")
        self.configure(bg=BG)
        self.cb = cb
        self.geometry("260x330")
        self.resizable(False, False)
        self.lbox = tk.Listbox(self, selectmode=tk.MULTIPLE, bg=LBOX_BG, fg=LBOX_FG,
                               font=(FONT, F_SIZE), bd=2, relief="sunken")
        self.lbox.pack(fill=tk.BOTH, expand=True, padx=10, pady=16)
        for opt in opts:
            self.lbox.insert(tk.END, opt)
        for idx, val in enumerate(opts):
            if val in selected:
                self.lbox.selection_set(idx)
        tk.Button(self, text="Done", command=self.done,
                  font=(FONT, F_SIZE), fg=BTN_FG, bg=BTN, activebackground=BTN_ACT,
                  activeforeground=BTN_ACT_FG, relief="raised", borderwidth=2).pack(pady=8)
    def done(self):
        sel = [self.lbox.get(i) for i in self.lbox.curselection()]
        self.cb(sel or ["All files"])
        self.destroy()

class DiskCleaner:
    def __init__(self, root):
        self.root = root
        self.root.title("Disk Cleaner")
        self.root.configure(bg=BG)
        self.root.minsize(560, 480)
        self.scan_running = False
        self.scan_thread = None
        self.stop_scan = threading.Event()
        self.file_types = [
            "All files", ".tmp", ".log", ".bak", ".cache",
            ".jpg", ".png", ".txt", ".pdf", ".exe"
        ]
        self.selected_types = ["All files"]
        self.junk_ext = ['.tmp', '.log', '.bak', '.cache', '.ds_store', '.thumb', '.temp']
        self.files = []
        self.f_hash = {}
        self.min_size = tk.IntVar(value=0)
        self.months = tk.IntVar(value=1)
        self.folders = []
        self.start_time = 0

        self.root.grid_columnconfigure(0, weight=1)
        self.root.grid_columnconfigure(1, weight=1)
        self.root.grid_rowconfigure(5, weight=1)

        # Menu
        menu = tk.Menu(self.root)
        helpmenu = tk.Menu(menu, tearoff=0)
        helpmenu.add_command(label="About", command=self.show_about)
        helpmenu.add_command(label="Instructions", command=self.show_help)
        menu.add_cascade(label="Help", menu=helpmenu)
        self.root.config(menu=menu)

        # Progress
        self.pb = ttk.Progressbar(root, orient=tk.HORIZONTAL, mode='determinate')
        self.pb.grid(row=0, column=0, columnspan=3, sticky='ew', padx=12, pady=(14, 2))
        self.pb.grid_remove()
        style = ttk.Style()
        style.theme_use('clam')
        style.configure("TProgressbar", troughcolor=BG, background=BTN,
                        bordercolor=BG, thickness=16)

        # Status
        self.status = tk.Label(root, text="", anchor='w', bg=BG, fg=BTN_FG,
                              font=(FONT, F_SIZE))
        self.status.grid(row=1, column=0, columnspan=3, sticky='ew', padx=12, pady=(0, 10))
        self.status.grid_remove()

        # Scan folders
        folder_fr = tk.Frame(root, bg=BG)
        folder_fr.grid(row=2, column=0, columnspan=3, pady=(0,2), sticky='ew')
        self.folder_lbl = tk.Label(folder_fr, text="Folders:", font=(FONT, F_SIZE), bg=BG, anchor='w')
        self.folder_lbl.pack(side='left', padx=10)
        tk.Button(folder_fr, text="Add folder", command=self.add_folder,
                  font=(FONT, F_SIZE), fg=BTN_FG, bg=BTN, activebackground=BTN_ACT,
                  activeforeground=BTN_ACT_FG, relief="raised", borderwidth=2).pack(side='left', padx=5)
        tk.Button(folder_fr, text="Add Recent", command=self.add_recent,
                  font=(FONT, F_SIZE), fg=BTN_FG, bg=BTN, activebackground=BTN_ACT,
                  activeforeground=BTN_ACT_FG, relief="raised", borderwidth=2).pack(side='left')
        tk.Button(folder_fr, text="Show disk usage", command=self.show_usage,
                  font=(FONT, F_SIZE), fg=BTN_FG, bg=BTN, activebackground=BTN_ACT,
                  activeforeground=BTN_ACT_FG, relief="raised", borderwidth=2).pack(side='left', padx=5)

        # Filters
        filter_fr = tk.Frame(root, bg=BG)
        filter_fr.grid(row=3, column=0, columnspan=3, sticky='ew', pady=(0,6))
        self.scan_btn = tk.Button(filter_fr, text="Scan folder", width=14, command=self.toggle_scan,
                                 font=(FONT, F_SIZE), fg=BTN_FG, bg=BTN, activebackground=BTN_ACT,
                                 activeforeground=BTN_ACT_FG, relief="raised", borderwidth=2)
        self.scan_btn.grid(row=0, column=0, padx=5, pady=5)
        self.pause_btn = tk.Button(filter_fr, text="Pause", width=7, command=self.toggle_pause,
                                 font=(FONT, F_SIZE), fg=BTN_FG, bg=BTN, activebackground=BTN_ACT,
                                 activeforeground=BTN_ACT_FG, relief="raised", borderwidth=2, state=tk.DISABLED)
        self.pause_btn.grid(row=0, column=1, padx=5, pady=5)
        self.filter_btn = tk.Button(filter_fr, text="All files ▼", width=14,
                                   font=(FONT, F_SIZE), fg=BTN_FG, bg=BTN, activebackground=BTN_ACT,
                                   activeforeground=BTN_ACT_FG, relief="raised", borderwidth=2,
                                   command=self.show_filter)
        self.filter_btn.grid(row=0, column=2, padx=5)
        tk.Label(filter_fr, text="Older than:", font=(FONT, F_SIZE), bg=BG, fg=BTN_FG).grid(row=0, column=3, padx=2)
        self.month_menu = tk.OptionMenu(filter_fr, self.months, *MONTHS)
        self.month_menu.config(width=5, font=(FONT, F_SIZE), fg=BTN_FG, bg=BTN,
                               activebackground=BTN_ACT, activeforeground=BTN_ACT_FG)
        self.month_menu.grid(row=0, column=4, padx=2)
        tk.Label(filter_fr, text="Min size (MB):", font=(FONT, F_SIZE), bg=BG, fg=BTN_FG).grid(row=0, column=5, padx=8)
        self.min_entry = tk.Entry(filter_fr, textvariable=self.min_size, width=6)
        self.min_entry.grid(row=0, column=6, padx=2)

        # Sort buttons
        sort_fr = tk.Frame(root, bg=BG)
        sort_fr.grid(row=4, column=0, columnspan=3, sticky='ew', pady=2)
        tk.Label(sort_fr, text="Sort by:", font=(FONT, F_SIZE), bg=BG).pack(side='left')
        tk.Button(sort_fr, text="Name", command=self.sort_name, font=(FONT, F_SIZE), bg=BTN).pack(side='left')
        tk.Button(sort_fr, text="Size", command=self.sort_size, font=(FONT, F_SIZE), bg=BTN).pack(side='left')
        tk.Button(sort_fr, text="Date", command=self.sort_date, font=(FONT, F_SIZE), bg=BTN).pack(side='left')

        # Action buttons
        action_fr = tk.Frame(root, bg=BG)
        action_fr.grid(row=6, column=0, columnspan=3, pady=2, sticky='ew')
        action_fr.grid_columnconfigure(0, weight=1)
        action_fr.grid_columnconfigure(1, weight=1)
        self.junk_btn = tk.Button(action_fr, text="Configure junk file types", width=30,
                                  command=self.set_junk, font=(FONT, F_SIZE), fg=BTN_FG, bg=BTN,
                                  activebackground=BTN_ACT, activeforeground=BTN_ACT_FG, relief="raised", borderwidth=2)
        self.junk_btn.grid(row=0, column=0, padx=14, pady=9, sticky='ew')
        self.del_btn = tk.Button(action_fr, text="Delete selected", width=22,
                                 command=self.delete_files, font=(FONT, F_SIZE), fg=BTN_FG, bg=BTN,
                                 activebackground=BTN_ACT, activeforeground=BTN_ACT_FG, relief="raised", borderwidth=2)
        self.del_btn.grid(row=0, column=1, padx=14, pady=9, sticky='ew')

        # File list and info
        self.lbox = tk.Listbox(root, selectmode=tk.EXTENDED, bg=LBOX_BG, fg=LBOX_FG,
                               font=(FONT, F_SIZE), bd=2, highlightbackground=BG, relief="sunken")
        self.lbox.grid(row=7, column=0, columnspan=3, padx=18, pady=(4,0), sticky='nsew')
        self.lbox.bind("<<ListboxSelect>>", self.show_info)
        scroll = tk.Scrollbar(root, command=self.lbox.yview)
        scroll.grid(row=7, column=3, sticky='ns', pady=(4,0))
        self.lbox.config(yscrollcommand=scroll.set)
        self.info_lbl = tk.Label(
            root, text="File info", font=(FONT, F_SIZE), bg=BG, fg=BTN_FG, anchor="w")
        self.info_lbl.grid(row=8, column=0, columnspan=3, sticky='ew', padx=14, pady=4)

        # Copyright
        tk.Label(root, text="© 2025 Siddhansh Srivastava.", font=(FONT, 9),
                 fg=BTN_FG, bg=BG).grid(row=9, column=0, columnspan=4, pady=10)

    def show_about(self):
        messagebox.showinfo(
            "About Disk Cleaner",
            "Disk Cleaner\nBy Siddhansh Srivastava\n\nFeatures:\n- Safe deletion\n- Recycle Bin support\n- Sorting and Filtering\n- Multi-folder scan\n- About/Help"
        )

    def show_help(self):
        messagebox.showinfo(
            "Instructions",
            "1. Add folder(s) to scan.\n2. Select file type(s) and timeframe.\n3. Use sort/filter for easier preview.\n4. Pause/resume scan as needed.\n5. Select files to delete safely (Recycle Bin)."
        )
    def show_filter(self):
        MultiSelDrop(self.root, self.file_types, self.selected_types, self.set_filter)
    def set_filter(self, sel):
        self.selected_types = sel
        self.filter_btn.config(text=", ".join(sel).title() + " ▼")

    def set_junk(self):
        current = ", ".join(self.junk_ext)
        response = simpledialog.askstring(
            "Configure Junk File Types",
            "Extensions (comma separated):\nCurrent: "+current)
        if response is not None:
            self.junk_ext = [
                e.strip().lower() if e.strip().startswith('.') else '.'+e.strip().lower()
                for e in response.split(",") if e.strip()
            ]
            messagebox.showinfo("Junk Types Updated", "New junk extensions:\n" + ", ".join(self.junk_ext))

    def add_folder(self):
        fld = filedialog.askdirectory()
        if fld:
            self.folders.append(fld)
            self.folder_lbl.config(text="Folders:\n" + "\n".join(self.folders))
    def add_recent(self):
        recent = os.path.expanduser(r"~\AppData\Roaming\Microsoft\Windows\Recent")
        self.folders.append(recent)
        self.folder_lbl.config(text="Folders:\n" + "\n".join(self.folders))
    def show_usage(self):
        folder = self.folders[0] if self.folders else 'C:\\'
        total, used, free = shutil.disk_usage(folder)
        messagebox.showinfo("Disk Usage",
            f"Total: {total//(1024**3)} GB\nUsed: {used//(1024**3)} GB\nFree: {free//(1024**3)} GB")

    def toggle_scan(self):
        if not self.scan_running:
            if not self.folders:
                messagebox.showwarning("Scan", "Add a folder first!")
                return
            self.scan_running = True
            self.start_time = time.time()
            self.scan_btn.config(text="Stop Scan", bg=BTN_ACT, fg=BTN_ACT_FG)
            self.pause_btn.config(state=tk.NORMAL)
            self.pb.grid()
            self.status.grid()
            self.status.config(text="Scanning...")
            self.files.clear()
            self.f_hash.clear()
            self.lbox.delete(0, 'end')
            self.pb['value'] = 0
            self.stop_scan.clear()
            self.scan_thread = threading.Thread(target=self.scan_folders)
            self.scan_thread.start()
            self.root.after(100, self.check_thread)
        else:
            self.stop_scan.set()
            self.status.config(text="Stopping scan...")

    def toggle_pause(self):
        if self.pause_btn['text'] == "Pause":
            self.stop_scan.set()
            self.pause_btn.config(text="Resume")
            self.status.config(text="Paused.")
        else:
            self.stop_scan.clear()
            self.start_time = time.time()
            self.scan_thread = threading.Thread(target=self.scan_folders)
            self.scan_thread.start()
            self.root.after(100, self.check_thread)
            self.pause_btn.config(text="Pause")
            self.status.config(text="Resuming...")

    def check_thread(self):
        if self.scan_thread and self.scan_thread.is_alive():
            self.root.after(100, self.check_thread)
        else:
            self.scan_running = False
            self.scan_btn.config(text="Scan folder", bg=BTN, fg=BTN_FG)
            self.pause_btn.config(state=tk.DISABLED, text="Pause")
            if self.stop_scan.is_set():
                self.status.config(text="Scan stopped by user")
            else:
                self.status.config(text=f"Scan complete. {len(self.files)} files found.")
            self.show_results()
            self.pb.grid_remove()
            self.status.grid_remove()

    def scan_folders(self):
        file_count = 0
        for folder in self.folders:
            for _, _, files in os.walk(folder):
                file_count += len(files)
        if file_count == 0:
            self.root.after(0, lambda: self.status.config(text="No files found."))
            return
        processed = 0
        self.start_time = time.time()
        for folder in self.folders:
            for dirpath, _, files in os.walk(folder):
                if self.stop_scan.is_set():
                    return
                for fname in files:
                    if self.stop_scan.is_set():
                        return
                    fpath = os.path.join(dirpath, fname)
                    processed += 1
                    elapsed = time.time() - self.start_time
                    fps = processed / elapsed if elapsed > 0 else 0
                    percent = processed / file_count * 100
                    self.root.after(0, self.pb.step, percent - self.pb['value'])
                    self.root.after(0, self.status.config, {"text": f"Scanning: {processed}/{file_count} | {fps:.1f} files/s | {int(elapsed)}s"})
                    fhash = self.get_hash(fpath)
                    if not fhash:
                        continue
                    self.f_hash.setdefault(fhash, []).append(fpath)
        dupes, junks = [], []
        for paths in self.f_hash.values():
            if len(paths) > 1:
                dupes += paths
            else:
                fp = paths[0]
                ext = os.path.splitext(fp)[1].lower()
                if ext in self.junk_ext:
                    junks.append(fp)
        self.files = list(set(dupes + junks))

    def get_hash(self, path, sz=1024*1024):
        h = hashlib.sha256()
        try:
            with open(path, 'rb') as f:
                while chunk := f.read(sz):
                    h.update(chunk)
        except Exception:
            return None
        return h.hexdigest()

    def show_results(self):
        self.lbox.delete(0, 'end')
        min_sz = self.min_size.get() * 1024 * 1024
        filtered = [fp for fp in self.files if os.path.isfile(fp) and os.path.getsize(fp) >= min_sz]
        if not filtered:
            self.lbox.insert('end', "No duplicate or junk files found.")
            return
        self.lbox.insert('end', "=== Duplicate and Junk Files Found ===")
        for fp in filtered:
            self.lbox.insert('end', fp)

    def sort_name(self):
        self.files.sort(key=lambda x: os.path.basename(x).lower())
        self.show_results()
    def sort_size(self):
        self.files.sort(key=lambda x: os.path.getsize(x) if os.path.isfile(x) else 0, reverse=True)
        self.show_results()
    def sort_date(self):
        self.files.sort(key=lambda x: os.path.getmtime(x) if os.path.isfile(x) else 0, reverse=True)
        self.show_results()

    def show_info(self, event=None):
        sel = self.lbox.curselection()
        if not sel:
            self.info_lbl.config(text="File info")
            return
        idx = sel[0]
        fp = self.lbox.get(idx)
        if os.path.isfile(fp):
            size = os.path.getsize(fp) / (1024*1024)
            mtime = datetime.fromtimestamp(os.path.getmtime(fp)).strftime("%Y-%m-%d %H:%M:%S")
            self.info_lbl.config(text=f"{os.path.basename(fp)} | {size:.2f} MB | Modified: {mtime}")
        else:
            self.info_lbl.config(text=fp)

    def delete_files(self):
        sel_indices = self.lbox.curselection()
        if not sel_indices:
            messagebox.showinfo("Select files", "Select file(s) to delete from the list.")
            return
        sel_files = [self.lbox.get(i) for i in sel_indices if os.path.isfile(self.lbox.get(i))]
        # Time filter
        months = self.months.get()
        now = time.time()
        cutoff = now - months * 30 * 24 * 3600
        age_files = [f for f in sel_files if os.path.getmtime(f) < cutoff]
        if not age_files:
            messagebox.showinfo("No Files", "No files match selected filter and age.")
            return
        sample = "\n".join(os.path.basename(f) for f in age_files[:10])
        more = f"\n...and {len(age_files) - 10} more." if len(age_files) > 10 else ""
        confirm = messagebox.askyesno("Confirm Delete",
                                      f"About to delete {len(age_files)} files older than {months} month(s):\n{sample}{more}\n\nThis cannot be undone. Continue?")
        if not confirm:
            return
        errors = []
        for fp in age_files:
            try:
                send2trash(fp)
                with open("deleted_files_log.txt", "a", encoding="utf-8") as logf:
                    logf.write(f"{datetime.now().isoformat()} | {fp}\n")
            except Exception as e:
                errors.append(f"{fp}: {e}")
        if errors:
            messagebox.showwarning("Errors", "Some files could not be deleted:\n\n" + "\n".join(errors))
        else:
            messagebox.showinfo("Done", "Files moved to Recycle Bin successfully.")
        self.show_results()

if __name__ == "__main__":
    root = tk.Tk()
    app = DiskCleaner(root)
    root.mainloop()