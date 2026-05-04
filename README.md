# Hotel Management System (Relational Database)
A complete Python and PostgreSQL application developed for **CS 480: Database Systems**. This system manages a hotel ecosystem with distinct role-based functionality, focusing on data integrity and complex relational querying.

## 🛠 Tech Stack
*   **Database:** PostgreSQL
*   **Language:** Python
*   **Database Driver:** Psycopg2
*   **GUI:** Tkinter (Desktop Application)

## 🏗 System Architecture
This application implements a normalized relational schema to handle complex business requirements:
*   **Role-Based Access Control (RBAC):** Separate logic and dashboards for **Managers** (SSN-based login) and **Clients** (Email-based login).
*   **Data Integrity:** Implementation of non-overlapping date-range constraints to prevent double-booking of hotel rooms.
*   **Relational Entities:** Manages relationships between Clients, Managers, Hotels, Rooms, Bookings, Reviews, and Credit Cards.

## 🚀 Key Features

### Manager Operations
*   **Inventory Control:** Insert, remove, and update hotel and room records.
*   **Advanced Analytics:** 
    *   **Top-K Reporting:** Identify top-K clients based on booking frequency.
    *   **Financial Audits:** Report total client spending and average hotel ratings.
    *   **Location Intelligence:** Identify "problematic" local Chicago hotels based on ratings and guest demographics.

### Client Operations
*   **Smart Search:** Search for available rooms across specific date intervals.
*   **Booking System:** Manual room selection and **Automatic Booking** which suggests alternative hotels if a request is unavailable.
*   **Profile Management:** Support for multiple addresses and billing-specific credit cards.

## 💻 How to Run

1.  **Initialize Database:**
    Create a Postgres database and run the schema script:
    ```bash
    psql -d hotel_db -f hotel_schema.sql
    ```
2.  **Configure Connection:**
    Update `db.py` with your local credentials:
    ```python
    DB_CONFIG = {
        "host": "localhost",
        "user": "your_username",
        "password": "your_password",
        "dbname": "hotel_db"
    }
    ```
3.  **Launch App:**
    ```bash
    python manager_dashboard.py  # For Manager Access
    python client_dashboard.py   # For Client Access
    ```

## 📁 Project Structure
*   `hotel_schema.sql`: SQL DDL script for table creation, keys, and constraints.
*   `db.py`: Database wrapper utilizing **parameterized queries** for SQL injection protection.
*   `manager_dashboard.py`: Manager-side logic and statistical reporting.
*   `client_dashboard.py`: Client registration, room searching, and booking logic.
