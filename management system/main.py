# Load Necessary Modules.
import tkinter as tk
from tkinter import ttk, messagebox
import os
import sys
import pandas as pd
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import seaborn as sns
from datetime import datetime
import random
import string

# Load Necessary Flight detail and Flight History File.
# It will create history file, if not found one.
FlightInformationFile = "flights.xlsx"
FlightHistoryFile = "flight_history.xlsx"

# Read flight data Function
def read_flights():
    try:
        df = pd.read_excel(FlightInformationFile)
        return df
    except Exception as e:
        messagebox.showerror("Error", f"Failed to read flight data: {e}")
        return pd.DataFrame()


# Read flight History data Function
def read_flight_history():
    try:
        df_history = pd.read_excel(FlightHistoryFile)
        return df_history
    except Exception as e:
        messagebox.showerror("Error", f"Failed to read flight history data: {e}")
        return pd.DataFrame()

# Display Flight Data
def display_flights():
    global df
    df = read_flights()

    global flight_frame

    if 'flight_frame' in globals():
        flight_frame.destroy()

    flight_frame = tk.Frame(tab_control, bg="#ffffff")
    tab_control.add(flight_frame, text='Flights')

    columns = [
        "Airline Name", "Flight ID", "From Destination", "To Destination", 
        "Scheduled Time", "Status", "Max Seats", "Occupied Seats", "Price"
    ]
    
    tree = ttk.Treeview(flight_frame, columns=columns, show="headings", style="Custom.Treeview")
    
    for col in columns:
        tree.heading(col, text=col)
        tree.column(col, anchor="center", width=120)

    tree.pack(fill="both", expand=True)

    for _, row in df.iterrows():
        scheduled_time = pd.to_datetime(row["Scheduled Time"], unit='s')
        formatted_scheduled_time = scheduled_time.strftime('%Y-%m-%d %H:%M:%S')
        
        flight_info = (
            row["Airline Name"], row["Flight ID"], row["From Destination"],
            row["To Destination"], formatted_scheduled_time,
            row["Status"], row["Max Seats"], row["Occupied Seats"], row["Price"]
        )
        
        tree.insert("", "end", values=flight_info)

# Display flight History
def display_flight_history():
    global df_history
    df_history = read_flight_history()

    global history_frame

    if 'history_frame' in globals():
        history_frame.destroy()

    history_frame = tk.Frame(tab_control, bg="#ffffff")
    tab_control.add(history_frame, text='Flight History')

    columns = [
        "Booking Date", "Airline Name", "Flight ID", "From Destination",
        "To Destination", "Scheduled Time", "Price", "Seat",
        "User Name", "User Address", "User Phone", "User ID"
    ]
    
    tree = ttk.Treeview(history_frame, columns=columns, show="headings", style="Custom.Treeview")
    
    for col in columns:
        tree.heading(col, text=col)
        tree.column(col, anchor="center", width=120)

    # Adding vertical scrollbar
    scrollbar = ttk.Scrollbar(history_frame, orient="vertical", command=tree.yview)
    tree.configure(yscroll=scrollbar.set)
    scrollbar.pack(side="right", fill="y")

    tree.pack(fill="both", expand=True)

    if 'Booking Date' not in df_history.columns:
        tk.Label(history_frame, text="No 'Booking Date' column found in flight history data.", font=('Arial', 12, 'bold'), bg="#ffffff").pack(pady=10)
        return

    max_rows = 200  # Maximum number of rows to display
    row_count = 0
    
    for _, row in df_history.iterrows():
        if row_count >= max_rows:
            break
        booking_date = pd.to_datetime(row["Booking Date"])
        formatted_booking_date = booking_date.strftime('%Y-%m-%d %H:%M:%S')

        scheduled_time = pd.to_datetime(row["Scheduled Time"])
        formatted_scheduled_time = scheduled_time.strftime('%Y-%m-%d %H:%M:%S')

        history_info = (
            formatted_booking_date, row["Airline Name"], row["Flight ID"], row["From Destination"],
            row["To Destination"], formatted_scheduled_time, row["Price"], row["Seat"],
            row["User Name"], row["User Address"], row["User Phone"], row["User ID"]
        )

        tree.insert("", "end", values=history_info)
        row_count += 1

    display_statistics_and_search(history_frame, tree)


# Function for Statistics view in admin 
def display_statistics_and_search(parent_frame, tree):
    stats_search_frame = tk.Frame(parent_frame, bg="#ffffff")
    stats_search_frame.pack(side=tk.LEFT, fill="both", expand=True, padx=20, pady=20)

    search_frame = tk.Frame(stats_search_frame, bg="#ffffff")
    search_frame.pack(fill="x", padx=10, pady=10)

    tk.Label(search_frame, text="Search User:", font=('Arial', 12, 'bold'), bg="#ffffff").pack(side=tk.LEFT, padx=10)
    search_entry = tk.Entry(search_frame, font=('Arial', 12))
    search_entry.pack(side=tk.LEFT, padx=10)

    # Search user in UI based on phone number, UserId, User Name
    def search_user():
        search_term = search_entry.get().strip().lower()
        for child in tree.get_children():
            values = tree.item(child, "values")
            if (search_term in values[8].lower()) or (search_term in values[10].lower()) or (search_term in values[11].lower()):
                tree.selection_set(child)
                tree.see(child)
                tree.item(child, tags=("highlight",))
            else:
                tree.detach(child)
        tree.tag_configure("highlight", background="yellow")

    def reset_tree():
        search_entry.delete(0, tk.END)
        display_flight_history()

    search_button = tk.Button(search_frame, text="Search", font=('Arial', 12, 'bold'), bg="#0d6efd", fg="white", command=search_user)
    search_button.pack(side=tk.LEFT, padx=10)

    reset_button = tk.Button(search_frame, text="Reset", font=('Arial', 12, 'bold'), bg="#f44336", fg="white", command=reset_tree)
    reset_button.pack(side=tk.LEFT, padx=10)

    stats_frame = tk.Frame(stats_search_frame, bg="#ffffff")
    stats_frame.pack(fill="both", expand=True, padx=10, pady=20)

    df_history['Booking Date'] = pd.to_datetime(df_history['Booking Date'])
    daily_revenue = df_history.groupby(df_history['Booking Date'].dt.date)['Price'].sum()

    total_bookings = len(df_history)
    total_revenue = df_history["Price"].sum()

    # Display total bookings and total revenue
    tk.Label(stats_frame, text=f"Total Bookings: {total_bookings}", font=('Arial', 12, 'bold'), bg="#ffffff").pack(anchor='nw')
    tk.Label(stats_frame, text=f"Total Revenue: रु {total_revenue}", font=('Arial', 12, 'bold'), bg="#ffffff").pack(anchor='nw')

    graph_frame = tk.Frame(parent_frame, bg="#ffffff")
    graph_frame.pack(side=tk.RIGHT, fill="both", expand=True, padx=20, pady=20)

    canvas = tk.Canvas(graph_frame, bg="white", height=400, width=800)
    canvas.pack(padx=20, pady=20)

    # Draw graph title
    canvas.create_text(400, 30, text="Daily Revenue", font=('Arial', 14, 'bold'))

    # Draw axes
    canvas.create_line(50, 350, 750, 350, fill="black")  # X-axis
    canvas.create_line(50, 350, 50, 50, fill="black")    # Y-axis

    max_revenue = max(daily_revenue)
    scale_factor = 300 / max_revenue  # Scale the graph to fit within the canvas

    # Draw X-axis labels and grid lines
    for i, (date, revenue) in enumerate(daily_revenue.items()):
        x = 50 + (i * (700 / (len(daily_revenue) - 1)))
        if i % 5 == 0:  # Show date label every 5 days
            canvas.create_text(x, 360, text=date.strftime('%b %d'), font=('Arial', 10))
        canvas.create_line(x, 50, x, 350, fill="lightgray")

    # Draw Y-axis labels and grid lines
    for i in range(0, int(max_revenue) + 500, 500):
        y = 350 - (i * scale_factor)
        canvas.create_text(30, y, text=f"रु{i}", font=('Arial', 10))
        canvas.create_line(50, y, 750, y, fill="lightgray")

    # Draw graph
    prev_x, prev_y = 50, 350 - daily_revenue.iloc[0] * scale_factor
    for i, (date, revenue) in enumerate(daily_revenue.items()):
        x = 50 + (i * (700 / (len(daily_revenue) - 1)))
        y = 350 - (revenue * scale_factor)
        canvas.create_line(prev_x, prev_y, x, y, fill="blue")
        canvas.create_oval(x-3, y-3, x+3, y+3, fill="blue", outline="blue")
        canvas.create_text(x, y-10, text=f"रु{revenue:.2f}", font=('Arial', 8), fill="black")
        prev_x, prev_y = x, y

    # Label the graph
    canvas.create_text(400, 370, text="Days", font=('Arial', 12))
    canvas.create_text(20, 200, text="Revenue", font=('Arial', 12), angle=90)

# Display graph based info 
def display_visualizations_popup():
    global df_history
    df_history = read_flight_history()

    if df_history.empty:
        messagebox.showerror("Error", "No flight history data available for visualization.")
        return

    if 'Booking Date' not in df_history.columns:
        messagebox.showerror("Error", "No 'Booking Date' column found in flight history data.")
        return

    popup = tk.Toplevel(root)
    popup.title("Visualizations")
    popup.geometry("1200x600")
    popup.config(bg="#e0e0e0")

    df_history['Booking Date'] = pd.to_datetime(df_history['Booking Date'])
    df_history.set_index('Booking Date', inplace=True)
    monthly_revenue = df_history['Price'].resample('MS').sum()

    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(14, 7))

    monthly_revenue.plot(kind='line', color='b', ax=ax1)
    ax1.set_title('Monthly Booking Trend')
    ax1.set_ylabel('Total Revenue')
    ax1.set_xlabel('Month')

    sns.countplot(y='To Destination', data=df_history, order=df_history['To Destination'].value_counts().index, ax=ax2)
    ax2.set_title('Number of Flights by Destination')
    ax2.set_ylabel('Destination')
    ax2.set_xlabel('Number of Flights')

    fig.tight_layout()

    canvas = FigureCanvasTkAgg(fig, master=popup)
    canvas.draw()
    canvas.get_tk_widget().pack(fill='both', expand=True)

# Edit flight function for User Role
def edit_flight(whichUser):
    global button_frame
    if 'button_frame' in globals():
        button_frame.destroy()

    button_frame = tk.Frame(root, bg="#d1e7dd")
    button_frame.pack(side=tk.BOTTOM, fill="x", pady=10)

    flight_id_label = tk.Label(button_frame, text="Enter Flight ID to Edit:", bg="#d1e7dd", font=('Arial', 10))
    flight_id_label.pack(side=tk.LEFT, padx=10)
    
    flight_id_entry = tk.Entry(button_frame, font=('Arial', 10))
    flight_id_entry.pack(side=tk.LEFT, padx=10)

    def edit_button_click():
        flight_id = flight_id_entry.get().strip()
        
        if whichUser != "admin":
            tk.messagebox.showerror("Permission Denied", "You must be an admin to edit flight data.")
            return

        flight_data = df[df["Flight ID"] == flight_id]

        if not flight_data.empty:
            edit_frame = tk.Frame(root, bg="#fff3cd")
            edit_frame.pack(fill="both", expand=True)
            
            flight_row = flight_data.iloc[0]
            fields = ["Airline Name", "From Destination", "To Destination", 
                      "Scheduled Time", "Status", "Max Seats", "Occupied Seats", "Price"]
            
            entries = {}
            for idx, field in enumerate(fields):
                label = tk.Label(edit_frame, text=f"{field}:", bg="#fff3cd", font=('Arial', 10))
                label.grid(row=idx, column=0, padx=10, pady=5, sticky="w")
                
                entry = tk.Entry(edit_frame, width=30, font=('Arial', 10))
                
                if field == "Scheduled Time":
                    scheduled_time = pd.to_datetime(flight_row[field], unit='s')
                    formatted_scheduled_time = scheduled_time.strftime('%Y-%m-%d %H:%M:%S')
                    entry.insert(0, formatted_scheduled_time)
                else:
                    entry.insert(0, str(flight_row[field]))
                entry.grid(row=idx, column=1, padx=10, pady=5)
                entries[field] = entry

            def save_info():
                for field, entry in entries.items():
                    new_value = entry.get().strip()
                    try:
                        if field == "Scheduled Time":
                            try:
                                parsed_time = pd.to_datetime(new_value, format='%Y-%m-%d %H:%M:%S')
                                new_value = int(parsed_time.timestamp())
                            except ValueError:
                                raise ValueError(f"Invalid date format for {field}. Expected format: YYYY-MM-DD HH:MM:SS")
                        elif field in ["Max Seats", "Occupied Seats", "Price"]:
                            new_value = int(new_value)
                        df.loc[df["Flight ID"] == flight_id, field] = new_value
                    except ValueError as ve:
                        print(f"Error updating field {field}: {ve}")
                        tk.messagebox.showerror("Error", f"Invalid input for {field}: {ve}")
                        return
                    except Exception as e:
                        print(f"Error updating field {field}: {e}")
                        tk.messagebox.showerror("Error", f"Unexpected error: {e}")
                        return
                
                try:
                    df.to_excel(FlightInformationFile, index=False)
                except Exception as e:
                    tk.messagebox.showerror("Error", f"Failed to save data: {e}")
                    return

                edit_frame.destroy()
                display_flights()

            save_button = tk.Button(edit_frame, text="Save Info", command=save_info, bg="#0d6efd", fg="white", font=('Arial', 10))
            save_button.grid(row=len(fields), column=1, pady=10)

        else:
            tk.messagebox.showerror("Error", "Flight ID not found")

    edit_button = tk.Button(button_frame, text="Edit Flight", command=edit_button_click, bg="#0d6efd", fg="white", font=('Arial', 10))
    edit_button.pack(side=tk.LEFT, padx=10)


# Book flight Function for User Role
def book_flight(whichUser):
    global button_frame
    if 'button_frame' in globals():
        button_frame.destroy()

    button_frame = tk.Frame(root, bg="#d1e7dd")
    button_frame.pack(side=tk.BOTTOM, fill="x", pady=10)

    flight_id_label = tk.Label(button_frame, text="Enter Flight ID to Book:", bg="#d1e7dd", font=('Arial', 10))
    flight_id_label.pack(side=tk.LEFT, padx=10)
    
    flight_id_entry = tk.Entry(button_frame, font=('Arial', 10))
    flight_id_entry.pack(side=tk.LEFT, padx=10)

    def book_button_click():
        flight_id = flight_id_entry.get().strip()

        flight_data = df[df["Flight ID"] == flight_id]

        if flight_data.empty:
            messagebox.showerror("Error", "Flight ID not found")
            return

        flight_status = flight_data.iloc[0]["Status"]

        if flight_status not in ["Ongoing", "Rescheduled"]:
            messagebox.showerror("Error", "This flight has been cancelled.")
            return

        button_frame.destroy()

        flight_info_frame = tk.Frame(root, bg="white")
        flight_info_frame.pack(fill="both", expand=True, padx=10, pady=10)

        columns = [
            "Airline Name", "Flight ID", "From Destination", "To Destination", 
            "Scheduled Time", "Status", "Max Seats", "Occupied Seats", "Price"
        ]
        
        for col, column_name in enumerate(columns):
            label = tk.Label(flight_info_frame, text=column_name, font=('Arial', 8, 'bold'), 
                            borderwidth=1, relief="solid", width=15, anchor="w", bg="#f2f2f2")
            label.grid(row=0, column=col, padx=3, pady=3, sticky="nsew")

        flight_row = flight_data.iloc[0]
        scheduled_time = pd.to_datetime(flight_row["Scheduled Time"], unit='s')
        formatted_scheduled_time = scheduled_time.strftime('%Y-%m-%d %H:%M:%S')

        flight_info = (
            flight_row["Airline Name"], flight_row["Flight ID"], flight_row["From Destination"],
            flight_row["To Destination"], formatted_scheduled_time, flight_row["Status"],
            flight_row["Max Seats"], flight_row["Occupied Seats"], flight_row["Price"]
        )

        for col, value in enumerate(flight_info):
            label = tk.Label(flight_info_frame, text=value, font=('Arial', 8), 
                            borderwidth=1, relief="solid", width=15, anchor="w", bg="white")
            label.grid(row=1, column=col, padx=3, pady=3, sticky="nsew")

        for col in range(len(columns)):
            flight_info_frame.grid_columnconfigure(col, weight=1, uniform="equal")

        user_info_frame = tk.Frame(root, bg="white")
        user_info_frame.pack(fill="both", expand=True, padx=10, pady=10)

        user_name_label = tk.Label(user_info_frame, text="Name:", bg="white", font=('Arial', 10))
        user_name_label.grid(row=0, column=0, padx=10, pady=5, sticky="w")
        user_name_entry = tk.Entry(user_info_frame, font=('Arial', 10))
        user_name_entry.grid(row=0, column=1, padx=10, pady=5)

        user_address_label = tk.Label(user_info_frame, text="Address:", bg="white", font=('Arial', 10))
        user_address_label.grid(row=1, column=0, padx=10, pady=5, sticky="w")
        user_address_entry = tk.Entry(user_info_frame, font=('Arial', 10))
        user_address_entry.grid(row=1, column=1, padx=10, pady=5)

        user_phone_label = tk.Label(user_info_frame, text="Phone Number:", bg="white", font=('Arial', 10))
        user_phone_label.grid(row=2, column=0, padx=10, pady=5, sticky="w")
        user_phone_entry = tk.Entry(user_info_frame, font=('Arial', 10))
        user_phone_entry.grid(row=2, column=1, padx=10, pady=5)

        user_id_label = tk.Label(user_info_frame, text="Valid ID Card:", bg="white", font=('Arial', 10))
        user_id_label.grid(row=3, column=0, padx=10, pady=5, sticky="w")
        user_id_entry = tk.Entry(user_info_frame, font=('Arial', 10))
        user_id_entry.grid(row=3, column=1, padx=10, pady=5)

        def continue_booking():
            user_name = user_name_entry.get().strip()
            user_address = user_address_entry.get().strip()
            user_phone = user_phone_entry.get().strip()
            user_id = user_id_entry.get().strip()
            
            user_info = (user_name, user_address, user_phone, user_id)

            if not user_name or not user_address or not user_phone or not user_id:
                messagebox.showerror("Error", "Please fill out all fields.")
                return
            
            generate_booking_pass(flight_info, user_info, whichUser, flight_info_frame, user_info_frame)

        def cancel_booking():
            flight_info_frame.destroy()
            user_info_frame.destroy()
            book_flight(whichUser)

        continue_button = tk.Button(user_info_frame, text="Continue Booking", command=continue_booking, bg="#0d6efd", fg="white", font=('Arial', 10))
        continue_button.grid(row=4, column=1, padx=10, pady=10)

        cancel_button = tk.Button(user_info_frame, text="Cancel", command=cancel_booking, bg="#f44336", fg="white", font=('Arial', 10))
        cancel_button.grid(row=4, column=0, padx=10, pady=10)

    book_button = tk.Button(button_frame, text="Book Flight", command=book_button_click, bg="#0d6efd", fg="white", font=('Arial', 10))
    book_button.pack(side=tk.LEFT, padx=10)

# Also update and increase the seat by one.
def update_occupied_seat(flight_info, df, flight_history_file=FlightInformationFile):
    flight_id = flight_info[1]
    max_seats = flight_info[6]
    occupied_seats = flight_info[7]
    
    if occupied_seats < max_seats:
        new_occupied_seats = occupied_seats + 1
        df.loc[df["Flight ID"] == flight_id, "Occupied Seats"] = new_occupied_seats
        
        df.to_excel(flight_history_file, index=False)

        display_flights()
    else:
        messagebox.showwarning("No Available Seats", "No seats available on this flight.")

# Generate Booking Pass and save it to history file.
def generate_booking_pass(flight_info, user_info, whichUser, flight_info_frame, user_info_frame):
    def reset_to_booking_ui():
        flight_info_frame.destroy()
        user_info_frame.destroy()
        booking_pass_window.destroy()
        update_occupied_seat(flight_info, df)
        book_flight(whichUser)

    booking_pass_window = tk.Toplevel(root)
    booking_pass_window.title("Booking Pass")
    booking_pass_window.geometry("800x400")
    booking_pass_window.config(bg="#e0e0e0")

    header_label = tk.Label(booking_pass_window, text="Booking Pass", font=('Arial', 16, 'bold'), bg="#e0e0e0")
    header_label.pack(pady=10)

    details_frame = tk.Frame(booking_pass_window, bg="white", relief="solid", borderwidth=2)
    details_frame.pack(fill="both", expand=True, padx=20, pady=20)

    random_seat = f"{random.choice(string.ascii_uppercase[:6])}{random.randint(1, 30)}"

    left_frame = tk.Frame(details_frame, bg="white")
    left_frame.grid(row=0, column=0, padx=10, pady=10, sticky="nw")

    flight_label = tk.Label(left_frame, text="Flight Information", font=('Arial', 12, 'bold'), bg="white")
    flight_label.pack(anchor="w", pady=5)

    booking_date = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    for label_text, value in [
        ("Date", booking_date),
        ("Airline Name", flight_info[0]),
        ("Flight ID", flight_info[1]),
        ("From Destination", flight_info[2]),
        ("To Destination", flight_info[3]),
        ("Scheduled Time", flight_info[4]),
        ("Price", flight_info[8]),
        ("Seat", random_seat)
    ]:
        tk.Label(left_frame, text=f"{label_text}: {value}", font=('Arial', 10), bg="white", anchor="w").pack(anchor="w", padx=10)

    right_frame = tk.Frame(details_frame, bg="white")
    right_frame.grid(row=0, column=1, padx=10, pady=10, sticky="ne")

    user_label = tk.Label(right_frame, text="User Information", font=('Arial', 12, 'bold'), bg="white")
    user_label.pack(anchor="w", pady=5)

    for label_text, value in [
        ("Name", user_info[0]),
        ("Address", user_info[1]),
        ("Phone Number", user_info[2]),
        ("Valid ID Card", user_info[3])
    ]:
        tk.Label(right_frame, text=f"{label_text}: {value}", font=('Arial', 10), bg="white", anchor="w").pack(anchor="w", padx=10)

    def save_booking_pass():
        flight_history_file = FlightHistoryFile

        try:
            df_history = pd.read_excel(flight_history_file)
        except FileNotFoundError:
            df_history = pd.DataFrame(columns=["Booking Date", "Airline Name", "Flight ID", "From Destination",
                                               "To Destination", "Scheduled Time", "Price", "Seat", 
                                               "User Name", "User Address", "User Phone", "User ID"])

        new_booking = {
            "Booking Date": booking_date,
            "Airline Name": flight_info[0],
            "Flight ID": flight_info[1],
            "From Destination": flight_info[2],
            "To Destination": flight_info[3],
            "Scheduled Time": flight_info[4],
            "Price": flight_info[8],
            "Seat": random_seat,
            "User Name": user_info[0],
            "User Address": user_info[1],
            "User Phone": user_info[2],
            "User ID": user_info[3]
        }

        df_history = df_history._append(new_booking, ignore_index=True)

        df_history.to_excel(flight_history_file, index=False)

        messagebox.showinfo("Booking Success", "Your booking has been confirmed! A booking pass has been generated.")

        reset_to_booking_ui()

    button_frame = tk.Frame(booking_pass_window, bg="#e0e0e0")
    button_frame.pack(fill="x", pady=10)

    save_button = tk.Button(button_frame, text="Save Booking Pass", font=('Arial', 12, 'bold'),
                            command=save_booking_pass, bg="#4CAF50", fg="white", relief="solid", width=20)
    save_button.pack(side="left", padx=50)

    cancel_button = tk.Button(button_frame, text="Cancel", font=('Arial', 12, 'bold'),
                              command=reset_to_booking_ui, bg="#f44336", fg="white", relief="solid", width=20)
    cancel_button.pack(side="right", padx=50)

def logout():
    # Restart the script to simulate a logout
    python = sys.executable
    os.execl(python, python, *sys.argv)


def admin_activity(whichUser):
    def switch_to_edit():
        if 'history_frame' in globals():
            history_frame.destroy()
        if 'button_frame' in globals():
            button_frame.destroy()
        display_flights()
        edit_flight(whichUser)

    def switch_to_history():
        if 'flight_frame' in globals():
            flight_frame.destroy()
        if 'button_frame' in globals():
            button_frame.destroy()
        display_flight_history()

    menu_frame = tk.Frame(root, bg="#e0e0e0")
    menu_frame.pack(side=tk.TOP, fill="x")

    edit_button = tk.Button(menu_frame, text="Edit Flight Data", command=switch_to_edit, bg="#0d6efd", fg="white", font=('Arial', 10, 'bold'))
    edit_button.pack(side=tk.LEFT, padx=10, pady=10)

    history_button = tk.Button(menu_frame, text="View Flight History", command=switch_to_history, bg="#0d6efd", fg="white", font=('Arial', 10, 'bold'))
    history_button.pack(side=tk.LEFT, padx=10, pady=10)

    visualize_button = tk.Button(menu_frame, text="Visualize Data", command=display_visualizations_popup, bg="#0d6efd", fg="white", font=('Arial', 10, 'bold'))
    visualize_button.pack(side=tk.LEFT, padx=10, pady=10)

    logout_button = tk.Button(menu_frame, text="Logout", command=logout, bg="#f44336", fg="white", font=('Arial', 10, 'bold'))
    logout_button.pack(side=tk.RIGHT, padx=10, pady=10)

    switch_to_edit()

def user_activity(whichUser):
    display_flights()
    book_flight(whichUser)

    logout_button = tk.Button(root, text="Logout", command=logout, bg="#f44336", fg="white", font=('Arial', 10, 'bold'))
    logout_button.pack(side=tk.BOTTOM, padx=10, pady=10)

# Login Function
def login(username_entry, password_entry, frame):
    username = username_entry.get()
    password = password_entry.get()

    for widget in user_frame.winfo_children():
        if isinstance(widget, tk.Label) and widget.cget("fg") == "red":
            widget.destroy()

    if username == "user" and password == "user":
        user_frame.destroy()
        admin_frame.destroy()
        user_activity("user")
    elif username == "admin" and password == "admin":
        user_frame.destroy()
        admin_frame.destroy()
        admin_activity("admin")
    else:
        if frame == "admin":
            error_label = tk.Label(admin_frame, text="Invalid credentials!", fg="red", bg="#f8d7da", font=('Arial', 10))
            error_label.grid(row=3, columnspan=2, pady=5)
        elif frame == "user":
            error_label = tk.Label(user_frame, text="Invalid credentials!", fg="red", bg="#f8d7da", font=('Arial', 10))
            error_label.grid(row=3, columnspan=2, pady=5)

# The important function to create login UI
def create_login_ui():
    global user_frame, admin_frame, root, tab_control
    root = tk.Tk()
    root.title("Flight Management System")
    root.config(bg="#e0e0e0")
    
    tab_control = ttk.Notebook(root)
    tab_control.pack(expand=1, fill="both")
    
    user_frame = tk.Frame(root, bg="#d1e7dd")
    user_frame.pack(side=tk.LEFT, padx=50, pady=50)
    
    tk.Label(user_frame, text="Username:", bg="#d1e7dd", font=('Arial', 12, 'bold')).grid(row=0, column=0, padx=10, pady=5)
    username_entry = tk.Entry(user_frame, font=('Arial', 12))
    username_entry.grid(row=0, column=1, padx=10, pady=5)
    
    tk.Label(user_frame, text="Password:", bg="#d1e7dd", font=('Arial', 12, 'bold')).grid(row=1, column=0, padx=10, pady=5)
    password_entry = tk.Entry(user_frame, show="*", font=('Arial', 12))
    password_entry.grid(row=1, column=1, padx=10, pady=5)
    
    login_button = tk.Button(
        user_frame,
        text="Login",
        command=lambda: login(username_entry, password_entry, "user"),
        bg="#0d6efd", fg="white", font=('Arial', 12, 'bold')
    )
    login_button.grid(row=2, columnspan=2, pady=10)
    
    admin_frame = tk.Frame(root, bg="#f8d7da")
    admin_frame.pack(side=tk.RIGHT, padx=50, pady=50)
    
    tk.Label(admin_frame, text="Admin Username:", bg="#f8d7da", font=('Arial', 12, 'bold')).grid(row=0, column=0, padx=10, pady=5)
    admin_username_entry = tk.Entry(admin_frame, font=('Arial', 12))
    admin_username_entry.grid(row=0, column=1, padx=10, pady=5)
    
    tk.Label(admin_frame, text="Admin Password:", bg="#f8d7da", font=('Arial', 12, 'bold')).grid(row=1, column=0, padx=10, pady=5)
    admin_password_entry = tk.Entry(admin_frame, show="*", font=('Arial', 12))
    admin_password_entry.grid(row=1, column=1, padx=10, pady=5)
    
    admin_login_button = tk.Button(
        admin_frame,
        text="Login",
        command=lambda: login(admin_username_entry, admin_password_entry, "admin"),
        bg="#0d6efd", fg="white", font=('Arial', 12, 'bold')
    )
    admin_login_button.grid(row=2, columnspan=2, pady=10)
    
    root.mainloop()


if __name__ == "__main__":
    create_login_ui()
else:
    print("This function Does not have Return Value.")