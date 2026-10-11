"""AuraCoord Standalone Graphical User Interface.
Runs standalone using standard library Tkinter.
"""

import sys
import tkinter as tk
from tkinter import ttk, messagebox
from auracoord.converter import parse_any_coordinate, format_result


class AuraCoordGui:
    def __init__(self, root: tk.Tk):
        self.root = root
        self.root.title("AuraCoord | Sovereign Military Coordinate Converter")
        self.root.geometry("640x480")
        self.root.minsize(580, 420)
        self.root.configure(bg="#0f172a")

        self._build_ui()

    def _build_ui(self):
        style = ttk.Style()
        style.theme_use("clam")

        # Header
        header_frame = tk.Frame(self.root, bg="#1e293b", padx=16, pady=12)
        header_frame.pack(fill="x")

        title_label = tk.Label(
            header_frame,
            text="AURACOORD GEODETIC CONVERTER",
            font=("Segoe UI", 14, "bold"),
            fg="#38bdf8",
            bg="#1e293b",
        )
        title_label.pack(side="left")

        sub_label = tk.Label(
            header_frame,
            text="WGS84 · MGRS · UTM · DMS",
            font=("Segoe UI", 9),
            fg="#94a3b8",
            bg="#1e293b",
        )
        sub_label.pack(side="right", pady=4)

        # Input Frame
        input_frame = tk.Frame(self.root, bg="#0f172a", padx=16, pady=16)
        input_frame.pack(fill="x")

        prompt_label = tk.Label(
            input_frame,
            text="Enter Coordinate (DD, DMS, or MGRS):",
            font=("Segoe UI", 10, "bold"),
            fg="#f8fafc",
            bg="#0f172a",
        )
        prompt_label.pack(anchor="w")

        entry_row = tk.Frame(input_frame, bg="#0f172a")
        entry_row.pack(fill="x", pady=6)

        self.input_var = tk.StringVar(value="38.8895, -77.0353")
        self.entry = tk.Entry(
            entry_row,
            textvariable=self.input_var,
            font=("Consolas", 11),
            bg="#1e293b",
            fg="#38bdf8",
            insertbackground="#38bdf8",
            relief="flat",
        )
        self.entry.pack(side="left", fill="x", expand=True, ipady=4, padx=(0, 8))
        self.entry.bind("<Return>", lambda e: self.convert())

        convert_btn = tk.Button(
            entry_row,
            text="Convert",
            command=self.convert,
            font=("Segoe UI", 10, "bold"),
            bg="#0284c7",
            fg="#ffffff",
            activebackground="#0369a1",
            relief="flat",
            padx=16,
        )
        convert_btn.pack(side="right")

        # Results Frame
        self.results_frame = tk.Frame(self.root, bg="#1e293b", padx=16, pady=16)
        self.results_frame.pack(fill="both", expand=True, padx=16, pady=8)

        self.output_vars = {}
        fields = [
            ("Detected Format", "detectedFormat"),
            ("Decimal Degrees (DD)", "dd"),
            ("Degrees Minutes Seconds (DMS)", "dms"),
            ("Degrees Decimal Minutes (DDM)", "ddm"),
            ("Military Grid Ref (MGRS)", "mgrs"),
            ("Universal Transverse Mercator (UTM)", "utm"),
        ]

        for i, (label_text, key) in enumerate(fields):
            row = tk.Frame(self.results_frame, bg="#1e293b")
            row.pack(fill="x", pady=4)

            lbl = tk.Label(
                row,
                text=label_text + ":",
                font=("Segoe UI", 9, "bold"),
                fg="#94a3b8",
                bg="#1e293b",
                width=32,
                anchor="w",
            )
            lbl.pack(side="left")

            val_var = tk.StringVar(value="--")
            self.output_vars[key] = val_var
            val_lbl = tk.Label(
                row,
                textvariable=val_var,
                font=("Consolas", 10),
                fg="#e2e8f0",
                bg="#1e293b",
                anchor="w",
            )
            val_lbl.pack(side="left", fill="x", expand=True)

        # Initial trigger
        self.convert()

    def convert(self):
        text = self.input_var.get().strip()
        res = parse_any_coordinate(text)
        if not res:
            messagebox.showerror(
                "Coordinate Parsing Error",
                f"Could not parse coordinate '{text}'.\nExpected formats:\n- DD: 38.8895, -77.0353\n- DMS: 38°53'22.2\"N 77°02'07.1\"W\n- MGRS: 18SUJ2345067890",
            )
            return

        self.output_vars["detectedFormat"].set(res.get("detectedFormat", "--"))
        self.output_vars["dd"].set(f"{res['latitude']}, {res['longitude']}")
        self.output_vars["dms"].set(res.get("dms", "--"))
        self.output_vars["ddm"].set(res.get("ddm", "--"))
        self.output_vars["mgrs"].set(res.get("mgrs", "--"))
        self.output_vars["utm"].set(res.get("utm", "--"))


def main():
    root = tk.Tk()
    app = AuraCoordGui(root)
    root.mainloop()


if __name__ == "__main__":
    main()
