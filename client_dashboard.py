import tkinter as tk
from tkinter import messagebox, simpledialog
from db import get_connection
from utils import validate_email, date_range_valid, calculate_total_cost


client_email = ""
client_name = ""
root = None


def login_action():
    global client_email, client_name
    email = email_entry.get()

    if not validate_email(email):
        messagebox.showerror("Error", "Invalid email.")
        return

    try:
        conn = get_connection()
        cur = conn.cursor()
        cur.execute("SELECT name FROM Client WHERE email = %s", (email,))
        result = cur.fetchone()

        if result:
            client_email = email
            client_name = result[0]
            messagebox.showinfo("Success", "Welcome, " + client_name + "!")
            show_client_menu()
        else:
            messagebox.showerror("Error", "Client not found. Please register first.")

        cur.close()
        conn.close()
    except Exception as e:
        messagebox.showerror("Error", str(e))


def register_client():
    name = simpledialog.askstring("Register", "Enter Full Name:")
    email = simpledialog.askstring("Register", "Enter Email:")

    if name and email:
        if not validate_email(email):
            messagebox.showerror("Error", "Invalid email.")
            return
        try:
            conn = get_connection()
            cur = conn.cursor()
            cur.execute("INSERT INTO Client (email, name) VALUES (%s, %s)", (email, name))
            conn.commit()
            messagebox.showinfo("Success", "Client Registered!")
            cur.close()
            conn.close()
        except Exception as e:
            messagebox.showerror("Error", str(e))


def add_address():
    st = simpledialog.askstring("Address", "Street Name:")
    num = simpledialog.askstring("Address", "Street Number:")
    city = simpledialog.askstring("Address", "City:")

    if st and num and city:
        try:
            conn = get_connection()
            cur = conn.cursor()
            cur.execute("INSERT INTO Address VALUES (%s,%s,%s) ON CONFLICT DO NOTHING", (st, num, city))
            cur.execute("""INSERT INTO Client_Address (email, street_name, street_number, city)
                           VALUES (%s,%s,%s,%s)""", (client_email, st, num, city))
            conn.commit()
            messagebox.showinfo("Success", "Address Added!")
            cur.close()
            conn.close()
        except Exception as e:
            messagebox.showerror("Error", str(e))


def view_addresses():
    try:
        conn = get_connection()
        cur = conn.cursor()
        cur.execute("""SELECT street_number, street_name, city
                       FROM Client_Address
                       WHERE email = %s""", (client_email,))
        res = cur.fetchall()
        output = "\n".join([f"{r[0]} {r[1]}, {r[2]}" for r in res])
        messagebox.showinfo("My Addresses", output if res else "No addresses found.")
        cur.close()
        conn.close()
    except Exception as e:
        messagebox.showerror("Error", str(e))


def add_credit_card():
    card = simpledialog.askstring("Credit Card", "Card Number:")
    st = simpledialog.askstring("Billing Address", "Street Name:")
    num = simpledialog.askstring("Billing Address", "Street Number:")
    city = simpledialog.askstring("Billing Address", "City:")

    if card and st and num and city:
        try:
            conn = get_connection()
            cur = conn.cursor()
            cur.execute("INSERT INTO Address VALUES (%s,%s,%s) ON CONFLICT DO NOTHING", (st, num, city))
            cur.execute("""INSERT INTO Credit_Card (card_number, email, street_name, street_number, city)
                           VALUES (%s,%s,%s,%s,%s)""", (card, client_email, st, num, city))
            conn.commit()
            messagebox.showinfo("Success", "Credit Card Added!")
            cur.close()
            conn.close()
        except Exception as e:
            messagebox.showerror("Error", str(e))


def view_hotels():
    try:
        conn = get_connection()
        cur = conn.cursor()
        cur.execute("SELECT hotel_id, name, street_number, street_name, city FROM Hotel ORDER BY city, name")
        res = cur.fetchall()
        output = "\n".join([f"ID {r[0]}: {r[1]} - {r[2]} {r[3]}, {r[4]}" for r in res])
        messagebox.showinfo("Hotels", output if res else "No hotels found.")
        cur.close()
        conn.close()
    except Exception as e:
        messagebox.showerror("Error", str(e))


def search_hotels_by_city():
    city = simpledialog.askstring("Hotels", "Enter City:")
    if city:
        try:
            conn = get_connection()
            cur = conn.cursor()
            cur.execute("""SELECT hotel_id, name, street_number, street_name, city
                           FROM Hotel WHERE LOWER(city) = LOWER(%s)
                           ORDER BY name""", (city,))
            res = cur.fetchall()
            output = "\n".join([f"ID {r[0]}: {r[1]} - {r[2]} {r[3]}, {r[4]}" for r in res])
            messagebox.showinfo("Search Results", output if res else "No hotels found.")
            cur.close()
            conn.close()
        except Exception as e:
            messagebox.showerror("Error", str(e))


def view_rooms():
    h_id = simpledialog.askinteger("Rooms", "Hotel ID:")
    if h_id:
        try:
            conn = get_connection()
            cur = conn.cursor()
            cur.execute("""SELECT h.name, r.room_number, r.windows, r.year, r.access_type
                           FROM Hotel h, Room r
                           WHERE h.hotel_id = r.hotel_id AND h.hotel_id = %s
                           ORDER BY r.room_number""", (h_id,))
            res = cur.fetchall()
            output = "\n".join([f"{r[0]} Room {r[1]}: {r[2]} windows, renovated {r[3]}, {r[4]}" for r in res])
            messagebox.showinfo("Rooms", output if res else "No rooms found.")
            cur.close()
            conn.close()
        except Exception as e:
            messagebox.showerror("Error", str(e))


def available_rooms():
    city = simpledialog.askstring("Available Rooms", "City:")
    start = simpledialog.askstring("Available Rooms", "Start Date (YYYY-MM-DD):")
    end = simpledialog.askstring("Available Rooms", "End Date (YYYY-MM-DD):")

    if not city or not start or not end:
        return
    if not date_range_valid(start, end):
        messagebox.showerror("Error", "Invalid date range.")
        return

    try:
        conn = get_connection()
        cur = conn.cursor()
        cur.execute("""SELECT h.hotel_id, h.name, r.room_number, r.windows, r.year, r.access_type
                       FROM Hotel h, Room r
                       WHERE h.hotel_id = r.hotel_id
                       AND LOWER(h.city) = LOWER(%s)
                       AND NOT EXISTS (
                           SELECT * FROM Booking b
                           WHERE b.hotel_id = r.hotel_id
                           AND b.room_number = r.room_number
                           AND daterange(b.start_date, b.end_date, '[]') && daterange(%s::date, %s::date, '[]')
                       )
                       ORDER BY h.name, r.room_number""", (city, start, end))
        res = cur.fetchall()
        output = "\n".join([f"Hotel ID {r[0]} - {r[1]} Room {r[2]} ({r[5]})" for r in res])
        messagebox.showinfo("Available Rooms", output if res else "No available rooms.")
        cur.close()
        conn.close()
    except Exception as e:
        messagebox.showerror("Error", str(e))


def book_room():
    h_id = simpledialog.askinteger("Book Room", "Hotel ID:")
    room = simpledialog.askinteger("Book Room", "Room Number:")
    start = simpledialog.askstring("Book Room", "Start Date (YYYY-MM-DD):")
    end = simpledialog.askstring("Book Room", "End Date (YYYY-MM-DD):")
    price = simpledialog.askfloat("Book Room", "Price Per Day:")

    if not h_id or not room or not start or not end or price is None:
        return
    if not date_range_valid(start, end):
        messagebox.showerror("Error", "Invalid date range.")
        return

    try:
        conn = get_connection()
        cur = conn.cursor()

        # check room exists first so error message is nicer
        cur.execute("SELECT * FROM Room WHERE hotel_id = %s AND room_number = %s", (h_id, room))
        existing_room = cur.fetchone()
        if not existing_room:
            messagebox.showerror("Error", "Room does not exist.")
            cur.close()
            conn.close()
            return

        cur.execute("""INSERT INTO Booking (email, hotel_id, room_number, start_date, end_date, price_per_day)
                       VALUES (%s,%s,%s,%s,%s,%s)""", (client_email, h_id, room, start, end, price))
        conn.commit()
        total = calculate_total_cost(start, end, price)
        messagebox.showinfo("Success", f"Booking Added! Total cost: ${total}")
        cur.close()
        conn.close()
    except Exception as e:
        messagebox.showerror("Error", str(e))


def view_bookings():
    try:
        conn = get_connection()
        cur = conn.cursor()
        cur.execute("""SELECT b.booking_id, h.name, h.city, b.room_number,
                              b.start_date, b.end_date, b.price_per_day
                       FROM Booking b, Hotel h
                       WHERE b.hotel_id = h.hotel_id AND b.email = %s
                       ORDER BY b.start_date DESC""", (client_email,))
        res = cur.fetchall()
        output = "\n".join([f"Booking {r[0]}: {r[1]} ({r[2]}) Room {r[3]}, {r[4]} to {r[5]}, ${r[6]}/day" for r in res])
        messagebox.showinfo("My Bookings", output if res else "No bookings found.")
        cur.close()
        conn.close()
    except Exception as e:
        messagebox.showerror("Error", str(e))


def cancel_booking():
    b_id = simpledialog.askinteger("Cancel Booking", "Booking ID:")
    if b_id:
        try:
            conn = get_connection()
            cur = conn.cursor()
            cur.execute("DELETE FROM Booking WHERE booking_id = %s AND email = %s", (b_id, client_email))
            conn.commit()
            messagebox.showinfo("Success", "Booking cancelled if it existed.")
            cur.close()
            conn.close()
        except Exception as e:
            messagebox.showerror("Error", str(e))


def leave_review():
    h_id = simpledialog.askinteger("Review", "Hotel ID:")
    rating = simpledialog.askinteger("Review", "Rating 0-10:")
    msg = simpledialog.askstring("Review", "Message:")

    if h_id and rating is not None:
        if rating < 0 or rating > 10:
            messagebox.showerror("Error", "Rating must be 0 to 10.")
            return
        try:
            conn = get_connection()
            cur = conn.cursor()
            cur.execute("SELECT 1 FROM Booking WHERE email=%s AND hotel_id=%s", (client_email, h_id))
            if not cur.fetchone():
                messagebox.showerror("Error", "You can only review hotels you have stayed at.")
                cur.close(); conn.close()
                return
            cur.execute("INSERT INTO Review (hotel_id, email, message, rating) VALUES (%s,%s,%s,%s)",
                        (h_id, client_email, msg, rating))
            conn.commit()
            messagebox.showinfo("Success", "Review Added!")
            cur.close(); conn.close()
        except Exception as e:
            messagebox.showerror("Error", str(e))


def view_reviews():
    h_id = simpledialog.askinteger("Reviews", "Hotel ID:")
    if h_id:
        try:
            conn = get_connection()
            cur = conn.cursor()
            cur.execute("""SELECT c.name, r.rating, r.message
                           FROM Review r, Client c
                           WHERE r.email = c.email AND r.hotel_id = %s
                           ORDER BY r.review_id DESC""", (h_id,))
            res = cur.fetchall()
            output = "\n".join([f"{r[0]} rated {r[1]}/10: {r[2]}" for r in res])
            messagebox.showinfo("Reviews", output if res else "No reviews found.")
            cur.close()
            conn.close()
        except Exception as e:
            messagebox.showerror("Error", str(e))


def show_client_menu():
    for widget in root.winfo_children():
        widget.destroy()

    tk.Label(root, text="CLIENT DASHBOARD", font=("Arial", 14, "bold")).pack(pady=10)
    tk.Label(root, text=f"User: {client_name}", fg="blue").pack()

    frame = tk.Frame(root)
    frame.pack(pady=10)
    L = tk.Frame(frame)
    L.pack(side="left", padx=15)
    R = tk.Frame(frame)
    R.pack(side="right", padx=15)

    tk.Label(L, text="CLIENT INFO", font=("Arial", 10, "bold")).pack(pady=3)
    tk.Button(L, text="Add Address", command=add_address, width=22).pack(pady=2)
    tk.Button(L, text="View Addresses", command=view_addresses, width=22).pack(pady=2)
    tk.Button(L, text="Add Credit Card", command=add_credit_card, width=22).pack(pady=2)

    tk.Label(L, text="HOTELS", font=("Arial", 10, "bold")).pack(pady=8)
    tk.Button(L, text="View Hotels", command=view_hotels, width=22).pack(pady=2)
    tk.Button(L, text="Search Hotels by City", command=search_hotels_by_city, width=22).pack(pady=2)
    tk.Button(L, text="View Rooms", command=view_rooms, width=22).pack(pady=2)
    tk.Button(L, text="Available Rooms", command=available_rooms, width=22).pack(pady=2)

    tk.Label(R, text="BOOKINGS", font=("Arial", 10, "bold")).pack(pady=3)
    tk.Button(R, text="Book Room", command=book_room, width=22).pack(pady=2)
    tk.Button(R, text="View My Bookings", command=view_bookings, width=22).pack(pady=2)
    tk.Button(R, text="Cancel Booking", command=cancel_booking, width=22).pack(pady=2)

    tk.Label(R, text="REVIEWS", font=("Arial", 10, "bold")).pack(pady=8)
    tk.Button(R, text="Leave Review", command=leave_review, width=22).pack(pady=2)
    tk.Button(R, text="View Reviews", command=view_reviews, width=22).pack(pady=2)

    tk.Button(root, text="Logout", command=show_login, width=15).pack(pady=10)


def show_login():
    global email_entry
    for widget in root.winfo_children():
        widget.destroy()

    tk.Label(root, text="UIC Hotel Client", font=("Arial", 14, "bold")).pack(pady=10)
    tk.Label(root, text="Enter Client Email:").pack(pady=10)
    email_entry = tk.Entry(root, width=30)
    email_entry.pack()
    tk.Button(root, text="Login", command=login_action, width=15).pack(pady=5)
    tk.Button(root, text="Register New Client", command=register_client, width=22).pack(pady=5)


def create_client_app(main_root):
    global root
    root = main_root
    root.title("UIC Hotel Client")
    root.geometry("600x520")
    show_login()


def run_client_app():
    local_root = tk.Tk()
    create_client_app(local_root)
    local_root.mainloop()


if __name__ == "__main__":
    run_client_app()
