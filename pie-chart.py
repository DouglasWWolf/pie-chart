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
    self.root.geometry("850x650")
    self.root.minsize(700, 500)

    # 1. Top Control Panel (Entry field and Button)
    control_frame = tk.Frame(root, bg="#f0f0f0", pady=12, padx=12)
    control_frame.pack(side=tk.TOP, fill=tk.X)

    tk.Label(
        control_frame,
        text="Fractions (comma-separated):",
        font=("Arial", 11, "bold"),
        bg="#f0f0f0",
    ).pack(side=tk.LEFT, padx=(0, 8))

    # Start with an empty entry field
    self.entry_var = tk.StringVar(value="")
    self.entry = tk.Entry(
        control_frame, textvariable=self.entry_var, width=32, font=("Arial", 11)
    )
    self.entry.pack(side=tk.LEFT, padx=5)
    # Allow pressing 'Enter' to submit
    self.entry.bind("<Return>", lambda event: self.visualize())

    self.btn = tk.Button(
        control_frame,
        text="Visualize",
        command=self.visualize,
        bg="#3498db",
        fg="white",
        font=("Arial", 10, "bold"),
        padx=12,
        pady=2,
    )
    self.btn.pack(side=tk.LEFT, padx=10)

    # Helper instruction label
    tk.Label(
        control_frame,
        text="(Type fractions & press Enter)",
        font=("Arial", 9, "italic"),
        fg="#666666",
        bg="#f0f0f0",
    ).pack(side=tk.LEFT, padx=5)

    # 2. Matplotlib Figure & Canvas Area
    self.fig, self.ax = plt.subplots(figsize=(8, 6))
    self.canvas = FigureCanvasTkAgg(self.fig, master=root)
    self.canvas.get_tk_widget().pack(
        side=tk.TOP, fill=tk.BOTH, expand=True, padx=10, pady=10
    )

    # Initially display a blank plot with instructions
    self.show_blank_screen()

  def show_blank_screen(self):
    self.fig.clear()
    ax = self.fig.add_subplot(111)
    ax.axis("off")
    ax.text(
        0.5,
        0.5,
        "Enter fractions above (e.g., 3/5, 6/10, 5/3)\nand click Visualize",
        fontsize=14,
        ha="center",
        va="center",
        color="#7f8c8d",
    )
    self.canvas.draw()

  def visualize(self):
    fraction_str = self.entry_var.get().strip()

    if not fraction_str:
      self.show_blank_screen()
      return

    # Parse fractions directly without auto-simplifying
    try:
      parts = fraction_str.split(",")
      fractions = []
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
        fractions.append((n, d))
    except Exception as e:
      messagebox.showerror(
          "Input Error",
          f"Invalid format: {e}\nPlease use format like '3/5, 6/10'.",
      )
      return

    if not fractions:
      self.show_blank_screen()
      return

    # Clear previous plot
    self.fig.clear()

    num_rows = len(fractions)
    max_circles = max((n + d - 1) // d for n, d in fractions)

    # Setup axes grid
    axes = self.fig.subplots(
        num_rows, max_circles, squeeze=False, subplot_kw={"aspect": "equal"}
    )

    self.fig.suptitle(
        "Fraction Pie Chart Visualizer",
        fontsize=14,
        fontweight="bold",
        y=0.96,
    )

    for row_idx, (n, d) in enumerate(fractions):
      num_circles_needed = (n + d - 1) // d

      for col_idx in range(max_circles):
        ax = axes[row_idx, col_idx]
        ax.axis("off")

        # Place fraction label to the left of the first column
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

        # Draw circles if needed
        if col_idx < num_circles_needed:
          filled_in_this_circle = min(d, max(0, n - col_idx * d))
          angle_step = 360 / d

          for slice_idx in range(d):
            start_angle = slice_idx * angle_step
            end_angle = (slice_idx + 1) * angle_step

            # Blue for filled, white for empty
            if slice_idx < filled_in_this_circle:
              facecolor = "#3498db"
              alpha = 0.9
            else:
              facecolor = "white"
              alpha = 1.0

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