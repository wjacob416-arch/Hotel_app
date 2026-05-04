import tkinter as tk
from tkinter import messagebox, simpledialog
from db import get_connection

root = None

# ──────────────────────────────────────────────────────────
# MANAGER LOGIC (All Requirements 1-9)
# ──────────────────────────────────────────────────────────

def login_action():
    """Req 1: Login"""
    ssn = SSN_entry.get()
    try:
        conn = get_connection()
        cur = conn.cursor()
        cur.execute("SELECT name FROM Managers WHERE SSN = %s", (ssn,))
        result = cur.fetchone()
        if result:
            global manager_name; manager_name = result[0]
            messagebox.showinfo("Success", f"Welcome, {manager_name}!")
            show_manager_menu()
        else: messagebox.showerror("Error", "SSN not found.")
        cur.close(); conn.close()
    except Exception as e: messagebox.showerror("Error", str(e))
 
def register_manager():
    """Req 1: Registration"""
    ssn = simpledialog.askstring("Register", "Enter 9-digit SSN:")
    name = simpledialog.askstring("Register", "Enter Full Name:")
    email = simpledialog.askstring("Register", "Enter Email:")
    if ssn and name and email:
        try:
            conn = get_connection()
            cur = conn.cursor()
            cur.execute("INSERT INTO Managers (SSN, name, email) VALUES (%s, %s, %s)", (ssn, name, email))
            conn.commit(); messagebox.showinfo("Success", "Manager Registered!"); cur.close(); conn.close()
        except Exception as e: messagebox.showerror("Error", str(e))
 
def add_hotel_db():
    """Req 2: Add Hotel"""
    name = simpledialog.askstring("Add Hotel", "Hotel Name:")
    st = simpledialog.askstring("Add Hotel", "Street Name:")
    num = simpledialog.askstring("Add Hotel", "Street Number:")
    city = simpledialog.askstring("Add Hotel", "City:")
    if name and st and num and city:
        try:
            conn = get_connection()
            cur = conn.cursor()
            cur.execute("INSERT INTO Address VALUES (%s,%s,%s) ON CONFLICT DO NOTHING", (st, num, city))
            cur.execute("INSERT INTO Hotel (name, street_name, street_number, city) VALUES (%s,%s,%s,%s)", (name, st, num, city))
            conn.commit(); messagebox.showinfo("Success", "Hotel Added!"); cur.close(); conn.close()
        except Exception as e: messagebox.showerror("Error", str(e))
 
def update_hotel_db():
    """Req 2: Update Hotel"""
    h_id = simpledialog.askinteger("Update Hotel", "Enter Hotel ID:")
    new_name = simpledialog.askstring("Update Hotel", "New Hotel Name:")
    if h_id and new_name:
        try:
            conn = get_connection()
            cur = conn.cursor()
            cur.execute("UPDATE Hotel SET name = %s WHERE hotel_id = %s", (new_name, h_id))
            conn.commit(); messagebox.showinfo("Success", "Hotel Updated!"); cur.close(); conn.close()
        except Exception as e: messagebox.showerror("Error", str(e))
 
def remove_hotel_db():
    """Req 2: Remove Hotel"""
    h_id = simpledialog.askinteger("Remove Hotel", "Enter Hotel ID:")
    if h_id:
        try:
            conn = get_connection()
            cur = conn.cursor()
            cur.execute("DELETE FROM Hotel WHERE hotel_id = %s", (h_id,))
            conn.commit(); messagebox.showinfo("Success", "Hotel Removed!"); cur.close(); conn.close()
        except Exception as e: messagebox.showerror("Error", str(e))
 
def manage_rooms_db():
    """Req 2: Manage Rooms (Add/Remove)"""
    h_id = simpledialog.askinteger("Rooms", "Hotel ID:")
    r_num = simpledialog.askinteger("Rooms", "Room Number:")
    action_input = simpledialog.askstring("Rooms", "Type 'add' or 'remove':")
    if not action_input: return
    action = action_input.lower()
    try:
        conn = get_connection()
        cur = conn.cursor()
        if action == 'add':
            win = simpledialog.askinteger("Rooms", "Number of Windows:")
            yr = simpledialog.askinteger("Rooms", "Renovation Year:")
            acc = simpledialog.askstring("Rooms", "Access Type (elevator/stairs):")
            cur.execute("INSERT INTO Room VALUES (%s,%s,%s,%s,%s)", (h_id, r_num, win, yr, acc))
        else:
            cur.execute("DELETE FROM Room WHERE hotel_id = %s AND room_number = %s", (h_id, r_num))
        conn.commit(); messagebox.showinfo("Success", "Room Updated!"); cur.close(); conn.close()
    except Exception as e: messagebox.showerror("Error", str(e))
 
def remove_client_db():
    """Req 3: Remove Client"""
    email = simpledialog.askstring("Remove Client", "Enter Client Email:")
    if email:
        try:
            conn = get_connection()
            cur = conn.cursor()
            cur.execute("DELETE FROM Client WHERE email = %s", (email,))
            conn.commit(); messagebox.showinfo("Success", "Client Removed!"); cur.close(); conn.close()
        except Exception as e: messagebox.showerror("Error", str(e))
 
def view_top_k():
    """Req 4: Top-K Clients by Bookings"""
    k = simpledialog.askinteger("Top-K", "Enter value for K:")
    if k:
        try:
            conn = get_connection()
            cur = conn.cursor()
            cur.execute("""SELECT c.name, c.email, COUNT(b.booking_id) 
                FROM Client c, Booking b WHERE c.email = b.email 
                GROUP BY c.name, c.email 
                ORDER BY COUNT(b.booking_id) DESC LIMIT %s""", (k,))
            res = cur.fetchall()
            output = "\n".join([f"{r[0]} ({r[1]}): {r[2]} bookings" for r in res])
            messagebox.showinfo(f"Top {k} Clients", output if res else "No data."); cur.close(); conn.close()
        except Exception as e: messagebox.showerror("Error", str(e))
 
def view_room_stats():
    """Req 5: All Rooms with Number of Bookings"""
    try:
        conn = get_connection()
        cur = conn.cursor()
        cur.execute("""SELECT h.name, r.room_number,
            (SELECT COUNT(*) FROM Booking b WHERE b.hotel_id = r.hotel_id AND b.room_number = r.room_number)
            FROM Hotel h, Room r WHERE h.hotel_id = r.hotel_id""")
        res = cur.fetchall()
        output = "\n".join([f"{r[0]} Room {r[1]}: {r[2]} bookings" for r in res])
        messagebox.showinfo("Room Stats", output if res else "No rooms."); cur.close(); conn.close()
    except Exception as e: messagebox.showerror("Error", str(e))
 
def hotel_stats():
    """Req 6: Hotel Name, Total Bookings, Avg Rating"""
    try:
        conn = get_connection()
        cur = conn.cursor()
        cur.execute("""SELECT h.name,
            (SELECT COUNT(*) FROM Booking b WHERE b.hotel_id = h.hotel_id),
            (SELECT AVG(r.rating) FROM Review r WHERE r.hotel_id = h.hotel_id)
            FROM Hotel h""")
        res = cur.fetchall()
        output = "\n".join([f"{r[0]}: {r[1]} bookings, Rating: {round(r[2],1) if r[2] else 'N/A'}" for r in res])
        messagebox.showinfo("Hotel Stats", output if res else "No hotels."); cur.close(); conn.close()
    except Exception as e: messagebox.showerror("Error", str(e))
 
def clients_by_city():
    """Req 7: Clients in C1 who booked in C2"""
    c1 = simpledialog.askstring("Search", "Client Home City (C1):")
    c2 = simpledialog.askstring("Search", "Hotel City (C2):")
    if c1 and c2:
        try:
            conn = get_connection()
            cur = conn.cursor()
            cur.execute("""SELECT DISTINCT c.name, c.email FROM Client c, Client_Address ca, Booking b, Hotel h
                WHERE c.email = ca.email AND c.email = b.email AND b.hotel_id = h.hotel_id
                AND ca.city = %s AND h.city = %s""", (c1, c2))
            res = cur.fetchall()
            output = "\n".join([f"{r[0]} ({r[1]})" for r in res])
            messagebox.showinfo("Results", output if res else "No matches."); cur.close(); conn.close()
        except Exception as e: messagebox.showerror("Error", str(e))
 
def problematic_hotels():
    """Req 8: Problematic Chicago Hotels"""
    try:
        conn = get_connection()
        cur = conn.cursor()
        cur.execute("""SELECT h.name FROM Hotel h WHERE h.city = 'Chicago'
            AND (SELECT AVG(rating) FROM Review WHERE hotel_id = h.hotel_id) < 2
            AND 2 <= (SELECT COUNT(DISTINCT b.email) FROM Booking b WHERE b.hotel_id = h.hotel_id
            AND b.email NOT IN (SELECT email FROM Client_Address WHERE city = 'Chicago'))""")
        res = cur.fetchall()
        messagebox.showinfo("Problematic Hotels", "\n".join([r[0] for r in res]) if res else "None found."); cur.close(); conn.close()
    except Exception as e: messagebox.showerror("Error", str(e))
 
def client_spending():
    """Req 9: Client Spending Report"""
    try:
        conn = get_connection()
        cur = conn.cursor()
        cur.execute("""SELECT c.name, SUM(b.price_per_day * (b.end_date - b.start_date))
            FROM Client c, Booking b WHERE c.email = b.email GROUP BY c.name ORDER BY 2 DESC""")
        res = cur.fetchall()
        output = "\n".join([f"{r[0]}: ${r[1]}" for r in res])
        messagebox.showinfo("Spending Report", output if res else "No data."); cur.close(); conn.close()
    except Exception as e: messagebox.showerror("Error", str(e))
 
# ──────────────────────────────────────────────────────────
# UI
# ──────────────────────────────────────────────────────────
 
def show_manager_menu():
    for widget in root.winfo_children(): widget.destroy()
    tk.Label(root, text="MANAGER DASHBOARD", font=("Arial", 14, "bold")).pack(pady=10)
    tk.Label(root, text=f"User: {manager_name}", fg="blue").pack()
    frame = tk.Frame(root); frame.pack(pady=10)
    L = tk.Frame(frame); L.pack(side="left", padx=15)
    R = tk.Frame(frame); R.pack(side="right", padx=15)
 
    tk.Label(L, text="MANAGEMENT", font=("Arial", 10, "bold")).pack(pady=3)
    tk.Button(L, text="Add Hotel",      command=add_hotel_db,    width=22).pack(pady=2)
    tk.Button(L, text="Update Hotel",   command=update_hotel_db, width=22).pack(pady=2)
    tk.Button(L, text="Remove Hotel",   command=remove_hotel_db, width=22).pack(pady=2)
    tk.Button(L, text="Manage Rooms",   command=manage_rooms_db, width=22).pack(pady=2)
    tk.Button(L, text="Remove Client",  command=remove_client_db,width=22).pack(pady=2)
 
    tk.Label(R, text="REPORTS", font=("Arial", 10, "bold")).pack(pady=3)
    tk.Button(R, text="Top-K Clients",       command=view_top_k,          width=22).pack(pady=2)
    tk.Button(R, text="Room Booking Stats",  command=view_room_stats,     width=22).pack(pady=2)
    tk.Button(R, text="Hotel Stats",         command=hotel_stats,         width=22).pack(pady=2)
    tk.Button(R, text="Clients by City",     command=clients_by_city,     width=22).pack(pady=2)
    tk.Button(R, text="Problematic Hotels",  command=problematic_hotels,  width=22).pack(pady=2)
    tk.Button(R, text="Client Spending",     command=client_spending,     width=22).pack(pady=2)
    tk.Button(root, text="Back to Launcher", command=return_to_main, width=15).pack(pady=10)
 
def return_to_main():
    root.destroy()
    import main
    main.main()


def create_manager_app(main_root):
    global root
    root = main_root
    root.title("UIC Hotel Manager")
    root.geometry("580x500")
    tk.Label(root, text="Enter Manager SSN:").pack(pady=10)
    global SSN_entry
    SSN_entry = tk.Entry(root, width=30)
    SSN_entry.pack()
    tk.Button(root, text="Login", command=login_action, width=15).pack(pady=5)
    tk.Button(root, text="Register New Manager", command=register_manager, width=22).pack(pady=5)
    tk.Button(root, text="Back to Launcher", command=return_to_main, width=22).pack(pady=5)


def run_manager_app():
    local_root = tk.Tk()
    create_manager_app(local_root)
    local_root.mainloop()


if __name__ == "__main__":
    run_manager_app()