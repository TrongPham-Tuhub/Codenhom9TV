import tkinter as tk
from tkinter import ttk, messagebox
import mysql.connector
from student import StudentGUI
from teacher import TeacherGUI
from admin import AdminGUI
import re

class SchoolManagementSystem:
    def __init__(self, master):
        self.master = master
        self.master.title("School Management System")
        self.master.geometry("800x600")
        self.master.configure(bg="#f0f0f0")

        self.db = mysql.connector.connect(
            host="localhost",
            user="root",
            password="",
            database="school_management"
        )
        self.cursor = self.db.cursor()

        self.create_widgets()

    def create_widgets(self):
        # Title
        title_label = tk.Label(self.master, text="School Management System", font=("Arial", 24, "bold"), bg="#f0f0f0", fg="#333333")
        title_label.pack(pady=20)

        # Login Frame
        login_frame = tk.Frame(self.master, bg="#ffffff", padx=20, pady=20)
        login_frame.pack(pady=20)

        tk.Label(login_frame, text="Username:", font=("Arial", 12), bg="#ffffff", fg="#333333").grid(row=0, column=0, sticky="e", padx=5, pady=5)
        self.username_entry = tk.Entry(login_frame, font=("Arial", 12))
        self.username_entry.grid(row=0, column=1, padx=5, pady=5)

        tk.Label(login_frame, text="Password:", font=("Arial", 12), bg="#ffffff", fg="#333333").grid(row=1, column=0, sticky="e", padx=5, pady=5)
        self.password_entry = tk.Entry(login_frame, font=("Arial", 12), show="*")
        self.password_entry.grid(row=1, column=1, padx=5, pady=5)

        login_button = tk.Button(login_frame, text="Login", font=("Arial", 12), command=self.login, bg="#4CAF50", fg="white", activebackground="#45a049")
        login_button.grid(row=2, column=0, columnspan=2, pady=10)

        register_button = tk.Button(login_frame, text="Register", font=("Arial", 12), command=self.show_registration, bg="#2196F3", fg="white", activebackground="#1E88E5")
        register_button.grid(row=3, column=0, columnspan=2)

    def login(self):
        username = self.username_entry.get()
        password = self.password_entry.get()

        if not username or not password:
            messagebox.showerror("Error", "Please enter both username and password.")
            return

        query = "SELECT * FROM users WHERE username = %s AND password = %s"
        self.cursor.execute(query, (username, password))
        user = self.cursor.fetchone()

        if user:
            role = user[3]
            if role == "student":
                StudentGUI(tk.Toplevel(), self.db, user[0])
            elif role == "teacher":
                TeacherGUI(tk.Toplevel(), self.db, user[0])
            elif role == "admin":
                AdminGUI(tk.Toplevel(), self.db, user[0])
        else:
            messagebox.showerror("Error", "Invalid username or password.")

    def show_registration(self):
        registration_window = tk.Toplevel(self.master)
        registration_window.title("Registration")
        registration_window.geometry("400x400")
        registration_window.configure(bg="#f0f0f0")

        tk.Label(registration_window, text="Username:", font=("Arial", 12), bg="#f0f0f0", fg="#333333").grid(row=0, column=0, sticky="e", padx=5, pady=5)
        username_entry = tk.Entry(registration_window, font=("Arial", 12))
        username_entry.grid(row=0, column=1, padx=5, pady=5)

        tk.Label(registration_window, text="Password:", font=("Arial", 12), bg="#f0f0f0", fg="#333333").grid(row=1, column=0, sticky="e", padx=5, pady=5)
        password_entry = tk.Entry(registration_window, font=("Arial", 12), show="*")
        password_entry.grid(row=1, column=1, padx=5, pady=5)

        tk.Label(registration_window, text="Confirm Password:", font=("Arial", 12), bg="#f0f0f0", fg="#333333").grid(row=2, column=0, sticky="e", padx=5, pady=5)
        confirm_password_entry = tk.Entry(registration_window, font=("Arial", 12), show="*")
        confirm_password_entry.grid(row=2, column=1, padx=5, pady=5)

        tk.Label(registration_window, text="Role:", font=("Arial", 12), bg="#f0f0f0", fg="#333333").grid(row=3, column=0, sticky="e", padx=5, pady=5)
        role_var = tk.StringVar()
        role_combobox = ttk.Combobox(registration_window, textvariable=role_var, values=["student", "teacher", "admin"], state="readonly")
        role_combobox.grid(row=3, column=1, padx=5, pady=5)
        role_combobox.set("student")

        tk.Label(registration_window, text="First Name:", font=("Arial", 12), bg="#f0f0f0", fg="#333333").grid(row=4, column=0, sticky="e", padx=5, pady=5)
        first_name_entry = tk.Entry(registration_window, font=("Arial", 12))
        first_name_entry.grid(row=4, column=1, padx=5, pady=5)

        tk.Label(registration_window, text="Last Name:", font=("Arial", 12), bg="#f0f0f0", fg="#333333").grid(row=5, column=0, sticky="e", padx=5, pady=5)
        last_name_entry = tk.Entry(registration_window, font=("Arial", 12))
        last_name_entry.grid(row=5, column=1, padx=5, pady=5)

        tk.Label(registration_window, text="Email:", font=("Arial", 12), bg="#f0f0f0", fg="#333333").grid(row=6, column=0, sticky="e", padx=5, pady=5)
        email_entry = tk.Entry(registration_window, font=("Arial", 12))
        email_entry.grid(row=6, column=1, padx=5, pady=5)

        register_button = tk.Button(registration_window, text="Register", font=("Arial", 12), command=lambda: self.register(
            username_entry.get(),
            password_entry.get(),
            confirm_password_entry.get(),
            role_var.get(),
            first_name_entry.get(),
            last_name_entry.get(),
            email_entry.get(),
            registration_window
        ), bg="#4CAF50", fg="white", activebackground="#45a049")
        register_button.grid(row=7, column=0, columnspan=2, pady=10)

    def register(self, username, password, confirm_password, role, first_name, last_name, email, window):
        if not username or not password or not confirm_password or not first_name or not last_name or not email:
            messagebox.showerror("Error", "Please fill in all fields.")
            return

        if not re.match(r"^[a-zA-Z0-9_]{3,20}$", username):
            messagebox.showerror("Error", "Username must be 3-20 characters long and contain only letters, numbers, and underscores.")
            return

        if len(password) < 6:
            messagebox.showerror("Error", "Password must be at least 6 characters long.")
            return

        if password != confirm_password:
            messagebox.showerror("Error", "Passwords do not match.")
            return

        if not re.match(r"[^@]+@[^@]+\.[^@]+", email):
            messagebox.showerror("Error", "Invalid email address.")
            return

        query = "INSERT INTO users (username, password, role) VALUES (%s, %s, %s)"
        try:
            self.cursor.execute(query, (username, password, role))
            user_id = self.cursor.lastrowid

            if role == "student":
                student_query = "INSERT INTO students (user_id, first_name, last_name) VALUES (%s, %s, %s)"
                self.cursor.execute(student_query, (user_id, first_name, last_name))
            elif role == "teacher":
                teacher_query = "INSERT INTO teachers (user_id, first_name, last_name) VALUES (%s, %s, %s)"
                self.cursor.execute(teacher_query, (user_id, first_name, last_name))
            elif role == "admin":
                admin_query = "INSERT INTO admins (user_id, first_name, last_name, email) VALUES (%s, %s, %s, %s)"
                self.cursor.execute(admin_query, (user_id, first_name, last_name, email))

            self.db.commit()
            messagebox.showinfo("Success", "Registration successful. You can now login.")
            window.destroy()
        except mysql.connector.Error as err:
            messagebox.showerror("Error", f"Registration failed: {err}")

if __name__ == "__main__":
    root = tk.Tk()
    app = SchoolManagementSystem(root)
    root.mainloop()