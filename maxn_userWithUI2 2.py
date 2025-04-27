import tkinter as tk
from tkinter import ttk, messagebox
import math
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import matplotlib.pyplot as plt


def calculate_SB(rho, B):
    """
    Calculate blocking (packet lost) Probability (SB) using the M/M/1/B queue model.
    """
    if rho >= 1:
        return 1
    try:
        numerator = math.pow(rho, B) * (1 - rho)
        denominator = 1 - math.pow(rho, B + 1)
        if denominator == 0:  # Prevent division by zero
            return 1
        return numerator / denominator
    except OverflowError:
        return 0  # Handle cases of very small rho


def calculate_metrics(w_max, BW_min, mu, b, SB_max, active_proportion, epsilon=1e-9):
    """
    Calculate metrics: blocking probability and waiting time vs. number of users.
    """
    users = []
    waiting_times = []
    blocking_probs = []

    for n in range(1, 2000):
        lambda_p = (BW_min * 1000000) / 12000
        Lambda = n * active_proportion * lambda_p  # Total arrival rate
        rho = Lambda / mu  # Traffic intensity

        if rho >= 1:  # Ensure stability: rho < 1
            break

        SB = calculate_SB(rho, b)  # Blocking probability
        Lambda_eff = Lambda * (1 - SB)  # Effective arrival rate
        L = Lambda_eff * w_max  # Average number of packets in the system
        W = L / Lambda_eff if Lambda_eff > 0 else float('inf')  # Average waiting time

        if SB <= SB_max + epsilon and W <= w_max + epsilon:
            users.append(n)
            blocking_probs.append(SB)
            waiting_times.append(W)
        else:
            break  # Stop if constraints are violated

    return users, waiting_times, blocking_probs


def calculate_and_display():
    try:
        w_max = float(entry_w_max.get()) / 1000  # Convert ms to seconds
        BW_min = float(entry_BW_min.get())
        if BW_min < 5 or BW_min > 240:
            BW_min = 5
        mu = float(entry_mu.get())
        b = int(entry_b.get())
        SB_max = float(entry_SB_max.get()) / 100  # Convert percentage to fraction
        active_proportion = activity_proportions[activity_combobox.get()]

        # Calculate metrics
        users, waiting_times, blocking_probs = calculate_metrics(w_max, BW_min, mu, b, SB_max, active_proportion)
        result_label.config(text=f"Maximum N number of users: {users[-1] if users else 0}")

        # Show the plot in a separate window
        show_plot(users, waiting_times, blocking_probs)

    except ValueError:
        messagebox.showerror("Invalid Input", "Please enter valid numeric values.")
    except Exception as e:
        messagebox.showerror("Error", str(e))


def show_plot(users, waiting_times, blocking_probs):
    """
    Plot in a separate window.
    """
    # Create a new Tkinter Toplevel window
    plot_window = tk.Toplevel()
    plot_window.title("ECE514 Project - Roommate Wi-Fi Sharing - QoS Metrics Plot")
    plot_window.geometry("900x500")

    # Create the Matplotlib figure and axes
    fig, ax1 = plt.subplots(figsize=(8, 4))

    # Plot waiting time
    ax1.set_xlabel("Number of Users (N)")
    ax1.set_ylabel("Waiting Time (W)", color="tab:blue")
    ax1.plot(users, waiting_times, label="Waiting Time", color="tab:blue")
    ax1.tick_params(axis="y", labelcolor="tab:blue")

    # Plot blocking probability
    ax2 = ax1.twinx()
    ax2.set_ylabel("Blocking Probability (SB)", color="tab:red")
    ax2.plot(users, blocking_probs, label="Blocking Probability", color="tab:red")
    ax2.tick_params(axis="y", labelcolor="tab:red")

    fig.tight_layout()

    # Embed the Matplotlib figure in the Tkinter Toplevel window
    canvas = FigureCanvasTkAgg(fig, master=plot_window)
    canvas.draw()
    canvas.get_tk_widget().pack(side=tk.TOP, fill=tk.BOTH, expand=True)


# Create main application window
root = tk.Tk()
root.title("ECE514 Project - Roommate Wi-Fi Sharing - Maximum Users Calculation")
root.geometry("600x400")

# Input labels and entry fields
tk.Label(root, text="Maximum Waiting Time (W_max) in Milliseconds:").pack(pady=5)
entry_w_max = ttk.Entry(root)
entry_w_max.pack()

tk.Label(root, text="Minimum Bandwidth per User (BW_min) in Mbps:").pack(pady=5)
entry_BW_min = ttk.Entry(root)
entry_BW_min.pack()

tk.Label(root, text="Router’s Capacity in packets per second:(20.000 for IEEE 802.11n Router)").pack(pady=5)
entry_mu = ttk.Entry(root)
entry_mu.pack()

tk.Label(root, text="Buffer Size (B) in packets:").pack(pady=5)
entry_b = ttk.Entry(root)
entry_b.pack()

tk.Label(root, text="Blocking Prob = SB (lost packets when buffer B is full) in %:").pack(pady=5)
entry_SB_max = ttk.Entry(root)
entry_SB_max.pack()

# Activity scenario dropdown
tk.Label(root, text="Select User Activity Scenario (Active State):").pack(pady=5)
activity_proportions = {
    "Web Browsing (3.5%)": 0.035,
    "Gaming (7.4%)": 0.074,
    "Video Streaming (13.6%)": 0.136,
    "General Usage (25%)": 0.25
}
activity_combobox = ttk.Combobox(root, values=list(activity_proportions.keys()), state="readonly")
activity_combobox.set("General Usage (25%)")
activity_combobox.pack()

# Calculate button
calculate_button = ttk.Button(root, text="Calculate N Users", command=calculate_and_display)
calculate_button.pack(pady=20)

# Result display
result_label = tk.Label(root, text="", font=("Helvetica", 12))
result_label.pack(pady=10)

# Run the application
root.mainloop()
