import tkinter as tk
from tkinter import ttk, messagebox, font
import numpy as np

# ── AHP math ──────────────────────────────────────────────────────────────────

class Transformer:

    RI = {
        1: 0.00, 2: 0.00, 3: 0.58, 4: 0.90, 5: 1.12,
        6: 1.24, 7: 1.32, 8: 1.41, 9: 1.45, 10: 1.49,
        11: 1.51, 12: 1.48, 13: 1.56, 14: 1.57, 15: 1.59, 16: 1.62,
    }

    def normalize_matrix(self, matrix):
        m = matrix.T.copy()
        for i in range(len(m)):
            s = m[i].sum()
            if s != 0:
                m[i] /= s
        return m.T

    def define_weights(self, matrix):
        return [row.mean() for row in matrix]

    def consistency_rate(self, matrix):
        n = len(matrix)
        norm = self.normalize_matrix(matrix)
        eigvals = np.linalg.eig(matrix)[0]
        nmax = float(max(eigvals.real))
        ci = (nmax - n) / (n - 1) if n > 1 else 0.0
        ri = self.RI.get(n, 1.0)
        cr = ci / ri if ri != 0 else 0.0
        print(cr)
        return nmax, ci, cr


# ── GUI ───────────────────────────────────────────────────────────────────────

ACCENT   = "#2563EB"   # blue-600
BG       = "#F9FAFB"   # gray-50
SURFACE  = "#FFFFFF"
BORDER   = "#E5E7EB"   # gray-200
TEXT     = "#111827"   # gray-900
MUTED    = "#6B7280"   # gray-500
DIAG_BG  = "#F3F4F6"   # gray-100
GOOD     = "#16A34A"   # green-600
WARN     = "#D97706"   # amber-600
BAD      = "#DC2626"   # red-600

MONO = ("Courier New", 11)


class AHPApp(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("AHP Matrix Calculator")
        self.configure(bg=BG)
        self.resizable(True, True)
        self.minsize(640, 520)

        self.transformer = Transformer()
        self.n = 3                # matrix dimension
        self.names = [f"C{i+1}" for i in range(self.n)]
        # upper-triangle entries  (i < j)  stored as StringVar
        self.cell_vars: dict[tuple[int,int], tk.StringVar] = {}

        self._build_ui()
        self._rebuild_matrix_frame()

    # ── layout ────────────────────────────────────────────────────────────────

    def _build_ui(self):
        # ── header
        hdr = tk.Frame(self, bg=ACCENT, padx=20, pady=14)
        hdr.pack(fill="x")
        tk.Label(hdr, text="AHP Consistency Calculator", bg=ACCENT,
                 fg="white", font=("Helvetica", 15, "bold")).pack(side="left")

        # ── toolbar
        bar = tk.Frame(self, bg=BG, padx=16, pady=10)
        bar.pack(fill="x")
        self._btn(bar, "+ Add criterion", self._add_criterion).pack(side="left", padx=(0,6))
        self._btn(bar, "− Remove criterion", self._remove_criterion).pack(side="left", padx=(0,6))
        self._btn(bar, "⟳ Reset", self._reset_values, outline=True).pack(side="left", padx=(0,6))
        self._btn(bar, "▶  Calculate", self._calculate,
                  bg=ACCENT, fg="white").pack(side="right")

        # ── scrollable canvas for the matrix
        outer = tk.Frame(self, bg=BG, padx=16, pady=4)
        outer.pack(fill="both", expand=True)

        tk.Label(outer, text="Pairwise comparison matrix",
                 bg=BG, fg=MUTED, font=("Helvetica", 11)).pack(anchor="w", pady=(0,6))

        self.canvas_frame = tk.Frame(outer, bg=BG)
        self.canvas_frame.pack(fill="both", expand=True)

        self.mat_canvas = tk.Canvas(self.canvas_frame, bg=BG, highlightthickness=0)
        sb_x = ttk.Scrollbar(self.canvas_frame, orient="horizontal",
                              command=self.mat_canvas.xview)
        sb_y = ttk.Scrollbar(self.canvas_frame, orient="vertical",
                              command=self.mat_canvas.yview)
        self.mat_canvas.configure(xscrollcommand=sb_x.set,
                                  yscrollcommand=sb_y.set)
        sb_x.pack(side="bottom", fill="x")
        sb_y.pack(side="right",  fill="y")
        self.mat_canvas.pack(side="left", fill="both", expand=True)

        self.mat_inner = tk.Frame(self.mat_canvas, bg=BG)
        self.mat_window = self.mat_canvas.create_window(
            (0, 0), window=self.mat_inner, anchor="nw")
        self.mat_inner.bind("<Configure>", self._on_frame_resize)

        # ── results panel
        res_outer = tk.Frame(self, bg=BG, padx=16, pady=10)
        res_outer.pack(fill="x")
        tk.Frame(res_outer, bg=BORDER, height=1).pack(fill="x", pady=(0,10))
        tk.Label(res_outer, text="Consistency metrics",
                 bg=BG, fg=MUTED, font=("Helvetica", 11)).pack(anchor="w", pady=(0,8))

        cards = tk.Frame(res_outer, bg=BG)
        cards.pack(fill="x")

        self.lbl_nmax = self._metric_card(cards, "λ max (nmax)", "—")
        self.lbl_nmax.pack(side="left", padx=(0,10))

        self.lbl_ci = self._metric_card(cards, "CI", "—")
        self.lbl_ci.pack(side="left", padx=(0,10))

        self.lbl_cr = self._metric_card(cards, "CR", "—")
        self.lbl_cr.pack(side="left")

        self.lbl_verdict = tk.Label(res_outer, text="",
                                    bg=BG, font=("Helvetica", 12, "bold"))
        self.lbl_verdict.pack(anchor="w", pady=(10,0))

    def _btn(self, parent, text, cmd, bg=SURFACE, fg=TEXT, outline=False):
        relief = "flat"
        b = tk.Button(parent, text=text, command=cmd, bg=bg, fg=fg,
                      font=("Helvetica", 10), padx=10, pady=5,
                      relief=relief, bd=0, cursor="hand2",
                      activebackground=DIAG_BG, activeforeground=TEXT)
        b.configure(highlightbackground=BORDER, highlightthickness=1)
        return b

    def _metric_card(self, parent, label, initial):
        frame = tk.Frame(parent, bg=DIAG_BG, padx=20, pady=12,
                         relief="flat", bd=0)
        frame.config(highlightbackground=BORDER, highlightthickness=1)
        tk.Label(frame, text=label, bg=DIAG_BG, fg=MUTED,
                 font=("Helvetica", 10)).pack(anchor="w")
        val_lbl = tk.Label(frame, text=initial, bg=DIAG_BG,
                           fg=TEXT, font=("Helvetica", 20, "bold"))
        val_lbl.pack(anchor="w")
        # return the value label so we can update it
        return val_lbl

    def _on_frame_resize(self, event):
        self.mat_canvas.configure(scrollregion=self.mat_canvas.bbox("all"))

    # ── matrix grid ───────────────────────────────────────────────────────────

    def _rebuild_matrix_frame(self):
        for w in self.mat_inner.winfo_children():
            w.destroy()

        n = self.n
        CELL_W = 88
        HEADER_W = 88

        # top-left corner blank
        self._corner_label(self.mat_inner, 0, 0)

        # column name headers (editable)
        for j in range(n):
            frame = tk.Frame(self.mat_inner, bg=DIAG_BG,
                             width=CELL_W, height=34,
                             highlightbackground=BORDER, highlightthickness=1)
            frame.grid(row=0, column=j+1, sticky="nsew", padx=1, pady=1)
            frame.grid_propagate(False)
            entry = tk.Entry(frame, font=("Helvetica", 10, "bold"),
                             bg=DIAG_BG, fg=ACCENT, bd=0,
                             justify="center", width=9)
            entry.insert(0, self.names[j])
            entry.pack(expand=True, fill="both", padx=2, pady=2)
            idx = j
            entry.bind("<FocusOut>", lambda e, i=idx: self._update_name(e, i))
            entry.bind("<Return>",   lambda e, i=idx: self._update_name(e, i))

        # rows
        for i in range(n):
            # row label
            lbl_f = tk.Frame(self.mat_inner, bg=DIAG_BG,
                              width=HEADER_W, height=34,
                              highlightbackground=BORDER, highlightthickness=1)
            lbl_f.grid(row=i+1, column=0, sticky="nsew", padx=1, pady=1)
            lbl_f.grid_propagate(False)
            tk.Label(lbl_f, text=self.names[i], bg=DIAG_BG, fg=ACCENT,
                     font=("Helvetica", 10, "bold")).pack(expand=True)

            for j in range(n):
                if i == j:
                    # diagonal — fixed "1"
                    f = tk.Frame(self.mat_inner, bg=DIAG_BG,
                                 width=CELL_W, height=34,
                                 highlightbackground=BORDER, highlightthickness=1)
                    f.grid(row=i+1, column=j+1, sticky="nsew", padx=1, pady=1)
                    f.grid_propagate(False)
                    tk.Label(f, text="1", bg=DIAG_BG, fg=MUTED,
                             font=MONO).pack(expand=True)

                elif i < j:
                    # upper triangle — editable
                    key = (i, j)
                    if key not in self.cell_vars:
                        self.cell_vars[key] = tk.StringVar(value="1")
                    var = self.cell_vars[key]

                    f = tk.Frame(self.mat_inner, bg=SURFACE,
                                 width=CELL_W, height=34,
                                 highlightbackground=BORDER, highlightthickness=1)
                    f.grid(row=i+1, column=j+1, sticky="nsew", padx=1, pady=1)
                    f.grid_propagate(False)
                    e = tk.Entry(f, textvariable=var, font=MONO,
                                 bg=SURFACE, fg=TEXT, bd=0,
                                 justify="center", width=9)
                    e.pack(expand=True, fill="both", padx=2, pady=2)
                    e.bind("<FocusIn>",  lambda ev: ev.widget.configure(bg="#EFF6FF"))
                    e.bind("<FocusOut>", lambda ev: ev.widget.configure(bg=SURFACE))

                else:
                    # lower triangle — mirrored, read-only display
                    key = (j, i)
                    if key not in self.cell_vars:
                        self.cell_vars[key] = tk.StringVar(value="1")
                    var = self.cell_vars[key]

                    f = tk.Frame(self.mat_inner, bg=DIAG_BG,
                                 width=CELL_W, height=34,
                                 highlightbackground=BORDER, highlightthickness=1)
                    f.grid(row=i+1, column=j+1, sticky="nsew", padx=1, pady=1)
                    f.grid_propagate(False)
                    lbl = tk.Label(f, bg=DIAG_BG, fg=MUTED, font=MONO)
                    lbl.pack(expand=True)

                    # live-update mirrored label
                    def _refresh(name, idx_, widget):
                        try:
                            v = self._parse_value(self.cell_vars[idx_].get())
                            widget.configure(text=self._reciprocal_label(v))
                        except Exception:
                            widget.configure(text="?")

                    var.trace_add("write",
                        lambda *_, k=key, w=lbl: _refresh(None, k, w))
                    _refresh(None, key, lbl)

        # column/row sizing
        self.mat_inner.columnconfigure(0, minsize=HEADER_W)
        for c in range(1, n+1):
            self.mat_inner.columnconfigure(c, minsize=CELL_W)
        for r in range(n+1):
            self.mat_inner.rowconfigure(r, minsize=34)

    def _corner_label(self, parent, row, col):
        f = tk.Frame(parent, bg=BG, width=88, height=34)
        f.grid(row=row, column=col, padx=1, pady=1)
        f.grid_propagate(False)

    def _update_name(self, event, idx):
        self.names[idx] = event.widget.get() or f"C{idx+1}"
        self._rebuild_matrix_frame()

    # ── toolbar actions ───────────────────────────────────────────────────────

    def _add_criterion(self):
        if self.n >= 16:
            messagebox.showwarning("Limit", "Maximum 16 criteria supported.")
            return
        self.n += 1
        self.names.append(f"C{self.n}")
        self._rebuild_matrix_frame()

    def _remove_criterion(self):
        if self.n <= 2:
            messagebox.showwarning("Limit", "Minimum 2 criteria required.")
            return
        # remove vars involving last criterion
        removed = [k for k in self.cell_vars if self.n-1 in k]
        for k in removed:
            del self.cell_vars[k]
        self.n -= 1
        self.names = self.names[:self.n]
        self._rebuild_matrix_frame()

    def _reset_values(self):
        for v in self.cell_vars.values():
            v.set("1")
        for lbl in (self.lbl_nmax, self.lbl_ci, self.lbl_cr):
            lbl.configure(text="—", fg=TEXT)
        self.lbl_verdict.configure(text="")

    # ── fraction helpers ──────────────────────────────────────────────────────

    @staticmethod
    def _parse_value(raw: str) -> float:
        """Parse a cell string into a positive float.
        Accepts: integers (3), decimals (0.333), fractions (1/7, 3/2).
        Raises ValueError with a friendly message on bad input.
        """
        raw = raw.strip()
        if not raw:
            raise ValueError("Empty cell — please enter a value.")
        if "/" in raw:
            parts = raw.split("/")
            if len(parts) != 2:
                raise ValueError(f"Cannot parse fraction: '{raw}'")
            num_s, den_s = parts
            try:
                num, den = float(num_s.strip()), float(den_s.strip())
            except ValueError:
                raise ValueError(f"Cannot parse fraction: '{raw}'")
            if den == 0:
                raise ValueError("Denominator cannot be zero.")
            v = num / den
        else:
            try:
                v = float(raw)
            except ValueError:
                raise ValueError(f"Cannot parse value: '{raw}'")
        if v <= 0:
            raise ValueError(f"Values must be positive (got '{raw}').")
        return v

    @staticmethod
    def _reciprocal_label(v: float) -> str:
        """Return a clean label for 1/v.
        If v is a recognisable integer (1–16), show '1/N'.
        If 1/v is a recognisable integer, show that integer.
        Otherwise show decimal rounded to 4 places.
        """
        if v == 0:
            return "?"
        recip = 1.0 / v
        # v is an integer → show 1/N
        if abs(v - round(v)) < 1e-9 and round(v) >= 1:
            n = int(round(v))
            return "1" if n == 1 else f"1/{n}"
        # 1/v is an integer → show that integer
        if abs(recip - round(recip)) < 1e-9 and round(recip) >= 1:
            return str(int(round(recip)))
        return f"{recip:.4f}"

    # ── calculate ─────────────────────────────────────────────────────────────

    def _build_np_matrix(self):
        n = self.n
        m = np.ones((n, n))
        for i in range(n):
            for j in range(i+1, n):
                raw = self.cell_vars[(i, j)].get()
                v = self._parse_value(raw)
                m[i][j] = v
                m[j][i] = 1.0 / v
        return m

    def _calculate(self):
        try:
            matrix = self._build_np_matrix()
        except Exception as ex:
            messagebox.showerror("Invalid input", str(ex))
            return

        nmax, ci, cr = self.transformer.consistency_rate(matrix)

        self.lbl_nmax.configure(text=f"{nmax:.10f}", fg=TEXT)
        self.lbl_ci.configure(text=f"{ci:.10f}", fg=TEXT)

        cr_color = GOOD if cr < 0.1 else (WARN if cr < 0.2 else BAD)
        # show full precision + percentage
        self.lbl_cr.configure(text=f"{cr:.10f}  ({cr*100:.4f}%)", fg=cr_color)

        if cr < 0.1:
            verdict = f"✓  Consistent  (CR < 0.10) CR = {cr}"
            vcolor = GOOD
        elif cr < 0.2:
            verdict = f"⚠  Marginally consistent  (CR < 0.20) CR = {cr}"
            vcolor = WARN
        else:
            verdict = f"✗  Inconsistent  (CR ≥ 0.20) — review judgments CR = {cr}"
            vcolor = BAD

        self.lbl_verdict.configure(text=verdict, fg=vcolor)


# ── entry point ───────────────────────────────────────────────────────────────

if __name__ == "__main__":
    app = AHPApp()
    app.mainloop()