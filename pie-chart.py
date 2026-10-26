#!/usr/bin/env python3
import tkinter as tk
from tkinter import messagebox
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from matplotlib.patches import Wedge


class FractionApp:

  def __init__(self, root):
    self.root = root
    self.root.title("Fraction Pie Chart Visualizer")
    self.root.geometry("950x700")
    self.root.minsize(750, 520)

    self.fractions = []
    self.is_overlapped = False

    # 1. Top Control Panel
    control_frame = tk.Frame(root, bg="#f0f0f0", pady=14, padx=14)
    control_frame.pack(side=tk.TOP, fill=tk.X)

    tk.Label(
        control_frame,
        text="Fractions:",
        font=("Arial", 12, "bold"),
        bg="#f0f0f0",
    ).pack(side=tk.LEFT, padx=(0, 8))

    self.entry_var = tk.StringVar(value="")
    self.entry = tk.Entry(
        control_frame, textvariable=self.entry_var, width=28, font=("Arial", 12)
    )
    self.entry.pack(side=tk.LEFT, padx=6)
    self.entry.bind("<Return>", lambda event: self.visualize())

    # Buttons 50% bigger
    self.btn_visualize = tk.Button(
        control_frame,
        text="Visualize",
        command=self.visualize,
        bg="#3498db",
        fg="white",
        font=("Arial", 15, "bold"),
        padx=15,
        pady=4,
    )
    self.btn_visualize.pack(side=tk.LEFT, padx=8)

    # Compare Button
    self.btn_overlap = tk.Button(
        control_frame,
        text="Compare",
        command=self.toggle_overlap,
        bg="#e67e22",
        fg="white",
        font=("Arial", 15, "bold"),
        padx=15,
        pady=4,
        state=tk.DISABLED,
    )
    self.btn_overlap.pack(side=tk.LEFT, padx=10)

    # 2. Matplotlib Figure & Canvas Area
    self.fig, self.ax = plt.subplots(figsize=(8, 6))
    self.canvas = FigureCanvasTkAgg(self.fig, master=root)
    self.canvas.get_tk_widget().pack(
        side=tk.TOP, fill=tk.BOTH, expand=True, padx=10, pady=10
    )

    self.show_blank_screen()

  def show_blank_screen(self):
    self.fig.clear()
    ax = self.fig.add_subplot(111)
    ax.axis("off")
    ax.text(
        0.5,
        0.5,
        (
            "Enter fractions above (e.g., 0/4, 2/4, 4/4)\nand click Visualize\n"
            "(Use 'Compare' when comparing 2 or more fractions)"
        ),
        fontsize=13,
        ha="center",
        va="center",
        color="#7f8c8d",
    )
    self.canvas.draw()
    self.btn_overlap.config(state=tk.DISABLED)
    self.is_overlapped = False

  def create_grid(self, num_rows, num_cols):
    """Universally compatible grid creator using add_subplot"""
    self.fig.clear()
    axes = []
    for r in range(num_rows):
      row_axes = []
      for c in range(num_cols):
        plot_num = r * num_cols + c + 1
        ax = self.fig.add_subplot(num_rows, num_cols, plot_num)
        ax.set_aspect("equal")
        row_axes.append(ax)
      axes.append(row_axes)
    return axes

  def visualize(self):
    fraction_str = self.entry_var.get().strip()
    if not fraction_str:
      self.show_blank_screen()
      return

    try:
      parts = fraction_str.split(",")
      parsed = []
      for p in parts:
        p = p.strip()
        if not p:
          continue
        sub_parts = p.split("/")
        if len(sub_parts) != 2:
          raise ValueError(
              f"Invalid format '{p}'. Use 'numerator/denominator'."
          )
        n = int(sub_parts[0].strip())
        d = int(sub_parts[1].strip())
        if d == 0:
          raise ValueError("Denominator cannot be zero.")
        if n < 0:
          raise ValueError("Numerator cannot be negative.")
        parsed.append((n, d))
    except Exception as e:
      messagebox.showerror(
          "Input Error",
          f"Invalid format: {e}\nPlease use format like '0/4, 2/4, 4/4'.",
      )
      return

    if not parsed:
      self.show_blank_screen()
      return

    self.fractions = parsed
    self.is_overlapped = False

    if len(self.fractions) >= 2:
      self.btn_overlap.config(state=tk.NORMAL, text="Compare")
    else:
      self.btn_overlap.config(state=tk.DISABLED, text="Compare")

    try:
      self.render_plot()
    except Exception as e:
      messagebox.showerror("Rendering Error", f"An error occurred while plotting: {e}")

  def toggle_overlap(self):
    if len(self.fractions) < 2:
      return
    self.is_overlapped = not self.is_overlapped
    if self.is_overlapped:
      self.btn_overlap.config(text="Reset View")
    else:
      self.btn_overlap.config(text="Compare")

    try:
      self.render_plot()
    except Exception as e:
      messagebox.showerror("Rendering Error", f"An error occurred while overlaying: {e}")

  def render_plot(self):
    fractions = self.fractions
    num_rows = len(fractions)
    
    # Helper to calculate circles needed (handles 0 numerator gracefully as 1 circle)
    def get_num_circles(n, d):
      return 1 if n == 0 else (n + d - 1) // d

    max_circles = max(get_num_circles(n, d) for n, d in fractions)
    colors = ["#3498db", "#e74c3c", "#2ecc71", "#9b59b6", "#e67e22", "#1abc9c"]

    if self.is_overlapped and len(fractions) >= 2:
      # Multi-Fraction Overlay Mode with complete circles
      max_c = max(get_num_circles(n, d) for n, d in fractions)

      axes_overlap = self.create_grid(1, max_c)
      summary_text = "Comparing: " + ", ".join([f"{n}/{d}" for n, d in fractions])
      self.fig.suptitle(
          summary_text,
          fontsize=12,
          fontweight="bold",
          y=0.96,
      )

      for col_idx in range(max_c):
        ax = axes_overlap[0][col_idx]
        ax.axis("off")

        if col_idx == 0:
          ax.text(
              -1.6,
              0,
              "Overlap\nView",
              fontsize=11,
              fontweight="bold",
              ha="right",
              va="center",
          )

        # Draw each fraction with concentric radii and complete circles
        for i, (n, d) in enumerate(fractions):
          num_c = get_num_circles(n, d)
          if col_idx < num_c:
            filled = min(d, max(0, n - col_idx * d))
            angle_step = 360 / d
            r = max(0.35, 1.0 - (i * 0.15))

            for s_idx in range(d):
              if s_idx < filled:
                face = colors[i % len(colors)]
                alpha = 0.75
              else:
                face = "#f1f2f6"
                alpha = 0.35

              wedge = Wedge(
                  (0, 0),
                  r,
                  s_idx * angle_step,
                  (s_idx + 1) * angle_step,
                  facecolor=face,
                  edgecolor="black",
                  linewidth=0.7,
                  alpha=alpha,
              )
              ax.add_patch(wedge)

        ax.set_xlim(-1.3, 1.3)
        ax.set_ylim(-1.3, 1.3)

    else:
      # Normal Multi-Row Display Mode
      axes = self.create_grid(num_rows, max_circles)
      self.fig.suptitle(
          "Fraction Pie Chart Visualizer",
          fontsize=14,
          fontweight="bold",
          y=0.96,
      )

      for row_idx, (n, d) in enumerate(fractions):
        num_circles_needed = get_num_circles(n, d)
        for col_idx in range(max_circles):
          ax = axes[row_idx][col_idx]
          ax.axis("off")

          if col_idx == 0:
            ax.text(
                -1.6,
                0,
                f"{n}/{d}",
                fontsize=12,
                fontweight="bold",
                ha="right",
                va="center",
            )

          if col_idx < num_circles_needed:
            filled_in_this_circle = min(d, max(0, n - col_idx * d))
            angle_step = 360 / d

            for slice_idx in range(d):
              start_angle = slice_idx * angle_step
              end_angle = (slice_idx + 1) * angle_step
              facecolor = (
                  colors[row_idx % len(colors)]
                  if slice_idx < filled_in_this_circle
                  else "white"
              )
              alpha = 0.9

              wedge = Wedge(
                  center=(0, 0),
                  r=1,
                  theta1=start_angle,
                  theta2=end_angle,
                  facecolor=facecolor,
                  edgecolor="black",
                  linewidth=1.2,
                  alpha=alpha,
              )
              ax.add_patch(wedge)

            ax.set_xlim(-1.3, 1.3)
            ax.set_ylim(-1.3, 1.3)
          else:
            ax.set_xlim(-1.3, 1.3)
            ax.set_ylim(-1.3, 1.3)

    self.fig.tight_layout(rect=[0, 0, 1, 0.95])
    self.canvas.draw()


if __name__ == "__main__":
  root = tk.Tk()
  app = FractionApp(root)
  root.mainloop()