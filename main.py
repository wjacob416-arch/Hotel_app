import tkinter as tk
from tkinter import messagebox
import client_dashboard
import manager_dashboard


def show_role_menu():
    for widget in root.winfo_children():
        widget.destroy()

    root.title("UIC Hotel System")
    root.geometry("420x220")

    tk.Label(root, text="UIC Hotel System", font=("Arial", 16, "bold")).pack(pady=20)
    tk.Label(root, text="Choose how you want to log in:", font=("Arial", 11)).pack(pady=5)
    tk.Label(root, text="Version 1.1 — new unified launcher", font=("Arial", 9), fg="gray").pack(pady=2)

    button_frame = tk.Frame(root)
    button_frame.pack(pady=15)

    tk.Button(button_frame, text="Client Login", width=18, command=load_client_app).grid(row=0, column=0, padx=10)
    tk.Button(button_frame, text="Manager Login", width=18, command=load_manager_app).grid(row=0, column=1, padx=10)

    tk.Button(root, text="Quit", command=root.destroy, width=12).pack(pady=6)
    tk.Button(root, text="Help", command=show_help, width=12).pack(pady=2)


def show_help():
    messagebox.showinfo(
        "UIC Hotel Launcher",
        "Select Client Login or Manager Login to open the appropriate dashboard.\n\n" \
        "This launcher now has a small help button and version label."
    )


def load_client_app():
    root.destroy()
    client_dashboard.run_client_app()


def load_manager_app():
    root.destroy()
    manager_dashboard.run_manager_app()


def main():
    global root
    root = tk.Tk()
    show_role_menu()
    root.mainloop()


if __name__ == "__main__":
    main()
