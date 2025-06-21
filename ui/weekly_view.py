# ui/weekly_view.py
import tkinter as tk
from tkinter import simpledialog, messagebox, filedialog
from datetime import datetime, timedelta, time
from db.database import get_trainings_for_week, add_training, delete_training, update_training, get_trainings_for_month
from models.training import Training
from utils.date_utils import get_week_dates
from export.pdf_exporter import export_trainings_to_pdf

class WeeklyPlanner(tk.Frame):
    def __init__(self, master):
        super().__init__(master)
        self.current_date = datetime.now().date()
        self.init_ui()

    def init_ui(self):
        self.header = tk.Frame(self)
        self.header.pack(fill="x")
        self.prev_btn = tk.Button(self.header, text="<", command=self.prev_week)
        self.prev_btn.pack(side="left")
        self.export_btn = tk.Button(self.header, text="Exporter PDF", command=self.export_pdf)
        self.export_btn.pack(side="left")
        self.next_btn = tk.Button(self.header, text=">", command=self.next_week)
        self.next_btn.pack(side="right")
        self.canvas = tk.Canvas(self)
        self.canvas.pack(fill="both", expand=True)
        self.draw_table()

    def draw_table(self):
        self.canvas.delete("all")
        self.slots = {}
        start_time = time(8, 0)
        end_time = time(22, 0)
        week_dates = get_week_dates(self.current_date)
        slot_height = 40
        slot_width = 120

        for i, date in enumerate(week_dates):
            self.canvas.create_text(80 + i*slot_width, 10, text=date.strftime("%A\n%d/%m"))

        for row, minutes in enumerate(range(8*60, 22*60, 30)):
            t = time(minutes//60, minutes%60)
            self.canvas.create_text(30, 40 + row*slot_height, text=t.strftime("%H:%M"))
            for col, date in enumerate(week_dates):
                x, y = 60 + col*slot_width, 20 + row*slot_height
                rect = self.canvas.create_rectangle(x, y, x+slot_width-10, y+slot_height, fill="white")
                self.canvas.tag_bind(rect, "<Button-1>", lambda e, d=date, t=t: self.add_popup(d, t))
                self.slots[(date, t)] = rect

        self.draw_trainings()

    def draw_trainings(self):
        trainings = get_trainings_for_week(self.current_date)
        for t in trainings:
            col = (t.date.weekday())
            row = ((t.start_time.hour - 8) * 2) + (1 if t.start_time.minute == 30 else 0)
            x, y = 60 + col*120, 20 + row*40
            h = int(((t.end_time.hour - t.start_time.hour) * 2 + (t.end_time.minute - t.start_time.minute)//30) * 40)
            item = self.canvas.create_rectangle(x, y, x+110, y+h, fill="lightblue")
            text = self.canvas.create_text(x+5, y+10, anchor="nw", text=f"{t.category}\n{t.description}")
            self.canvas.tag_bind(item, "<Button-3>", lambda e, tid=t.id: self.delete_training(tid))
            self.canvas.tag_bind(item, "<Double-Button-1>", lambda e, t=t: self.edit_popup(t))

    def add_popup(self, date, start_time):
        category = simpledialog.askstring("Catégorie", "Ex: U15")
        description = simpledialog.askstring("Description", "Ex: Travail physique")
        end_time_str = simpledialog.askstring("Heure de fin", "Format HH:MM")
        try:
            end_hour, end_min = map(int, end_time_str.split(":"))
            end_time = time(end_hour, end_min)
            new_t = Training(category=category, description=description, date=date, start_time=start_time, end_time=end_time)
            add_training(new_t)
            self.draw_table()
        except Exception as e:
            messagebox.showerror("Erreur", str(e))

    def edit_popup(self, training):
        description = simpledialog.askstring("Description", "", initialvalue=training.description)
        category = simpledialog.askstring("Catégorie", "", initialvalue=training.category)
        end_time_str = simpledialog.askstring("Heure de fin", "Format HH:MM", initialvalue=training.end_time.strftime("%H:%M"))
        try:
            end_hour, end_min = map(int, end_time_str.split(":"))
            training.description = description
            training.category = category
            training.end_time = time(end_hour, end_min)
            update_training(training)
            self.draw_table()
        except Exception as e:
            messagebox.showerror("Erreur", str(e))

    def delete_training(self, training_id):
        delete_training(training_id)
        self.draw_table()

    def prev_week(self):
        self.current_date -= timedelta(days=7)
        self.draw_table()

    def next_week(self):
        self.current_date += timedelta(days=7)
        self.draw_table()

    def export_pdf(self):
        year = simpledialog.askinteger("Année", "Ex: 2025")
        month = simpledialog.askinteger("Mois", "Ex: 4")
        category = simpledialog.askstring("Catégorie", "Ex: U15 ou 'Toutes'")
        trainings = get_trainings_for_month(year, month, category)
        filepath = filedialog.asksaveasfilename(defaultextension=".pdf", filetypes=[("PDF files", "*.pdf")])
        if filepath:
            export_trainings_to_pdf(trainings, filepath)
            messagebox.showinfo("Exporté", f"PDF généré : {filepath}")

