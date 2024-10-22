import tkinter as tk
from tkinter import ttk, messagebox
import mysql.connector

class AdminGUI:
    def __init__(self, master, db, user_id):
        self.master = master
        self.master.title("Admin Dashboard")
        self.master.geometry("800x600")
        self.master.configure(bg="#f0f0f0")

        self.db = db
        self.cursor = db.cursor()
        self.user_id = user_id

        self.create_widgets()

    def create_widgets(self):
        # Title
        title_label = tk.Label(self.master, text="Admin Dashboard", font=("Arial", 24, "bold"), bg="#f0f0f0", fg="#333333")
        title_label.pack(pady=20)

        # Notebook for different sections
        style = ttk.Style()
        style.configure("TNotebook", background="#f0f0f0")
        style.configure("TNotebook.Tab", background="#e0e0e0", padding=[10, 5])
        style.map("TNotebook.Tab", background=[("selected", "#ffffff")])

        notebook = ttk.Notebook(self.master)
        notebook.pack(pady=10, padx=10, expand=True, fill="both")

        # Personal Information Tab
        personal_info_frame = ttk.Frame(notebook)
        notebook.add(personal_info_frame, text="Personal Information")
        self.show_personal_info(personal_info_frame)

        # Student Management Tab
        student_frame = ttk.Frame(notebook)
        notebook.add(student_frame, text="Student Management")
        self.show_student_management(student_frame)

        # Grade Management Tab
        grade_frame = ttk.Frame(notebook)
        notebook.add(grade_frame, text="Grade Management")
        self.show_grade_management(grade_frame)

        # Account Management Tab
        account_frame = ttk.Frame(notebook)
        notebook.add(account_frame, text="Account Management")
        self.show_account_management(account_frame)

    def show_personal_info(self, frame):
        query = """
        SELECT a.first_name, a.last_name, a.email
        FROM admins a
        JOIN users u ON a.user_id = u.id
        WHERE u.id = %s
        """
        self.cursor.execute(query, (self.user_id,))
        admin_info = self.cursor.fetchone()

        if admin_info:
            info_frame = tk.Frame(frame, bg="#ffffff",padx=20, pady=20)
            info_frame.pack(pady=20, padx=20, fill="both", expand=True)

            tk.Label(info_frame, text="Personal Information", font=("Arial", 16, "bold"), bg="#ffffff", fg="#333333").pack(pady=(0, 10))
            tk.Label(info_frame, text=f"Name: {admin_info[0]} {admin_info[1]}", font=("Arial", 12), bg="#ffffff", fg="#333333").pack(pady=5)
            tk.Label(info_frame, text=f"Email: {admin_info[2]}", font=("Arial", 12), bg="#ffffff", fg="#333333").pack(pady=5)
        else:
            tk.Label(frame, text="No personal information available.", font=("Arial", 12), fg="#333333").pack(pady=5)

    def show_student_management(self, frame):
        # Create a frame for the student table
        table_frame = ttk.Frame(frame)
        table_frame.pack(pady=10, padx=10, expand=True, fill="both")

        # Create the student table
        columns = ("ID", "First Name", "Last Name", "Class", "Date of Birth")
        tree = ttk.Treeview(table_frame, columns=columns, show="headings")
        for col in columns:
            tree.heading(col, text=col)
        tree.pack(side="left", expand=True, fill="both")

        # Add a scrollbar
        scrollbar = ttk.Scrollbar(table_frame, orient="vertical", command=tree.yview)
        scrollbar.pack(side="right", fill="y")
        tree.configure(yscrollcommand=scrollbar.set)

        # Function to load students
        def load_students():
            tree.delete(*tree.get_children())
            query = "SELECT id, first_name, last_name, class, date_of_birth FROM students"
            self.cursor.execute(query)
            for student in self.cursor.fetchall():
                tree.insert("", "end", values=student)

        # Load initial data
        load_students()

        # Create a frame for buttons
        button_frame = ttk.Frame(frame)
        button_frame.pack(pady=10)

        # Add Student button
        add_button = tk.Button(button_frame, text="Add Student", command=self.add_student_window, bg="#4CAF50", fg="white", activebackground="#45a049")
        add_button.pack(side="left", padx=5)

        # Edit Student button
        edit_button = tk.Button(button_frame, text="Edit Student", command=lambda: self.edit_student_window(tree), bg="#2196F3", fg="white", activebackground="#1E88E5")
        edit_button.pack(side="left", padx=5)

        # Delete Student button
        delete_button = tk.Button(button_frame, text="Delete Student", command=lambda: self.delete_student(tree), bg="#F44336", fg="white", activebackground="#D32F2F")
        delete_button.pack(side="left", padx=5)

    def add_student_window(self):
        add_window = tk.Toplevel(self.master)
        add_window.title("Add Student")
        add_window.geometry("300x250")
        add_window.configure(bg="#f0f0f0")

        tk.Label(add_window, text="First Name:", bg="#f0f0f0", fg="#333333").pack(pady=5)
        first_name_entry = tk.Entry(add_window)
        first_name_entry.pack(pady=5)

        tk.Label(add_window, text="Last Name:", bg="#f0f0f0", fg="#333333").pack(pady=5)
        last_name_entry = tk.Entry(add_window)
        last_name_entry.pack(pady=5)

        tk.Label(add_window, text="Class:", bg="#f0f0f0", fg="#333333").pack(pady=5)
        class_entry = tk.Entry(add_window)
        class_entry.pack(pady=5)

        tk.Label(add_window, text="Date of Birth (YYYY-MM-DD):", bg="#f0f0f0", fg="#333333").pack(pady=5)
        dob_entry = tk.Entry(add_window)
        dob_entry.pack(pady=5)

        def save_student():
            first_name = first_name_entry.get()
            last_name = last_name_entry.get()
            class_name = class_entry.get()
            dob = dob_entry.get()

            if first_name and last_name and class_name and dob:
                query = "INSERT INTO students (first_name, last_name, class, date_of_birth) VALUES (%s, %s, %s, %s)"
                try:
                    self.cursor.execute(query, (first_name, last_name, class_name, dob))
                    self.db.commit()
                    messagebox.showinfo("Success", "Student added successfully")
                    add_window.destroy()
                    self.show_student_management(self.master.children["!notebook"].children["!frame3"])
                except mysql.connector.Error as err:
                    messagebox.showerror("Error", f"An error occurred: {err}")
            else:
                messagebox.showerror("Error", "All fields are required")

        save_button = tk.Button(add_window, text="Save", command=save_student, bg="#4CAF50", fg="white", activebackground="#45a049")
        save_button.pack(pady=10)

    def edit_student_window(self, tree):
        selected_item = tree.selection()
        if not selected_item:
            messagebox.showerror("Error", "Please select a student to edit")
            return

        student_id = tree.item(selected_item)['values'][0]
        query = "SELECT * FROM students WHERE id = %s"
        self.cursor.execute(query, (student_id,))
        student = self.cursor.fetchone()

        edit_window = tk.Toplevel(self.master)
        edit_window.title("Edit Student")
        edit_window.geometry("300x250")
        edit_window.configure(bg="#f0f0f0")

        tk.Label(edit_window, text="First Name:", bg="#f0f0f0", fg="#333333").pack(pady=5)
        first_name_entry = tk.Entry(edit_window)
        first_name_entry.insert(0, student[2])
        first_name_entry.pack(pady=5)

        tk.Label(edit_window, text="Last Name:", bg="#f0f0f0", fg="#333333").pack(pady=5)
        last_name_entry = tk.Entry(edit_window)
        last_name_entry.insert(0, student[3])
        last_name_entry.pack(pady=5)

        tk.Label(edit_window, text="Class:", bg="#f0f0f0", fg="#333333").pack(pady=5)
        class_entry = tk.Entry(edit_window)
        class_entry.insert(0, student[4])
        class_entry.pack(pady=5)

        tk.Label(edit_window, text="Date of Birth (YYYY-MM-DD):", bg="#f0f0f0", fg="#333333").pack(pady=5)
        dob_entry = tk.Entry(edit_window)
        dob_entry.insert(0, student[5])
        dob_entry.pack(pady=5)

        def update_student():
            first_name = first_name_entry.get()
            last_name = last_name_entry.get()
            class_name = class_entry.get()
            dob = dob_entry.get()

            if first_name and last_name and class_name and dob:
                query = "UPDATE students SET first_name = %s, last_name = %s, class = %s, date_of_birth = %s WHERE id = %s"
                try:
                    self.cursor.execute(query, (first_name, last_name, class_name, dob, student_id))
                    self.db.commit()
                    messagebox.showinfo("Success", "Student updated successfully")
                    edit_window.destroy()
                    self.show_student_management(self.master.children["!notebook"].children["!frame3"])
                except mysql.connector.Error as err:
                    messagebox.showerror("Error", f"An error occurred: {err}")
            else:
                messagebox.showerror("Error", "All fields are required")

        update_button = tk.Button(edit_window, text="Update", command=update_student, bg="#2196F3", fg="white", activebackground="#1E88E5")
        update_button.pack(pady=10)

    def delete_student(self, tree):
        selected_item = tree.selection()
        if not selected_item:
            messagebox.showerror("Error", "Please select a student to delete")
            return

        student_id = tree.item(selected_item)['values'][0]
        confirm = messagebox.askyesno("Confirm Deletion", "Are you sure you want to delete this student?")
        if confirm:
            query = "DELETE FROM students WHERE id = %s"
            try:
                self.cursor.execute(query, (student_id,))
                self.db.commit()
                messagebox.showinfo("Success", "Student deleted successfully")
                self.show_student_management(self.master.children["!notebook"].children["!frame3"])
            except mysql.connector.Error as err:
                messagebox.showerror("Error", f"An error occurred: {err}")

    def show_grade_management(self, frame):
        # Create a frame for the grade table
        table_frame = ttk.Frame(frame)
        table_frame.pack(pady=10, padx=10, expand=True, fill="both")

        # Create the grade table
        columns = ("Student ID", "Student Name", "Subject", "Grade")
        tree = ttk.Treeview(table_frame, columns=columns, show="headings")
        for col in columns:
            tree.heading(col, text=col)
        tree.pack(side="left", expand=True, fill="both")

        # Add a scrollbar
        scrollbar = ttk.Scrollbar(table_frame, orient="vertical", command=tree.yview)
        scrollbar.pack(side="right", fill="y")
        tree.configure(yscrollcommand=scrollbar.set)

        # Function to load grades
        def load_grades():
            tree.delete(*tree.get_children())
            query = """
            SELECT s.id, CONCAT(s.first_name, ' ', s.last_name) AS student_name, sub.name, g.grade
            FROM students s
            JOIN grades g ON s.id = g.student_id
            JOIN subjects sub ON g.subject_id = sub.id
            ORDER BY s.id, sub.name
            """
            self.cursor.execute(query)
            for grade in self.cursor.fetchall():
                tree.insert("", "end", values=grade)

        # Load initial data
        load_grades()

        # Create a frame for buttons
        button_frame = ttk.Frame(frame)
        button_frame.pack(pady=10)

        # Edit Grade button
        edit_button = tk.Button(button_frame, text="Edit Grade", command=lambda: self.edit_grade_window(tree), bg="#2196F3", fg="white", activebackground="#1E88E5")
        edit_button.pack(side="left", padx=5)

    def edit_grade_window(self, tree):
        selected_item = tree.selection()
        if not selected_item:
            messagebox.showerror("Error", "Please select a grade to edit")
            return

        student_id, student_name, subject, current_grade = tree.item(selected_item)['values']

        edit_window = tk.Toplevel(self.master)
        edit_window.title("Edit Grade")
        edit_window.geometry("300x200")
        edit_window.configure(bg="#f0f0f0")

        tk.Label(edit_window, text=f"Student: {student_name}", bg="#f0f0f0", fg="#333333").pack(pady=5)
        tk.Label(edit_window, text=f"Subject: {subject}", bg="#f0f0f0", fg="#333333").pack(pady=5)

        tk.Label(edit_window, text="New Grade:", bg="#f0f0f0", fg="#333333").pack(pady=5)
        grade_entry = tk.Entry(edit_window)
        grade_entry.insert(0, current_grade)
        grade_entry.pack(pady=5)

        def update_grade():
            new_grade = grade_entry.get()
            if new_grade:
                try:
                    new_grade = float(new_grade)
                    query = """
                    UPDATE grades g
                    JOIN subjects s ON g.subject_id = s.id
                    SET g.grade = %s
                    WHERE g.student_id = %s AND s.name = %s
                    """
                    self.cursor.execute(query, (new_grade, student_id, subject))
                    self.db.commit()
                    messagebox.showinfo("Success", "Grade updated successfully")
                    edit_window.destroy()
                    self.show_grade_management(self.master.children["!notebook"].children["!frame4"])
                except ValueError:
                    messagebox.showerror("Error", "Grade must be a number")
                except mysql.connector.Error as err:
                    messagebox.showerror("Error", f"An error occurred: {err}")
            else:
                messagebox.showerror("Error", "Grade is required")

        update_button = tk.Button(edit_window, text="Update", command=update_grade, bg="#2196F3", fg="white", activebackground="#1E88E5")
        update_button.pack(pady=10)

    def show_account_management(self, frame):
        # Create a frame for the account table
        table_frame = ttk.Frame(frame)
        table_frame.pack(pady=10, padx=10, expand=True, fill="both")

        # Create the account table
        columns = ("ID", "Username", "Role")
        tree = ttk.Treeview(table_frame, columns=columns, show="headings")
        for col in columns:
            tree.heading(col, text=col)
        tree.pack(side="left", expand=True, fill="both")

        # Add a scrollbar
        scrollbar = ttk.Scrollbar(table_frame, orient="vertical", command=tree.yview)
        scrollbar.pack(side="right", fill="y")
        tree.configure(yscrollcommand=scrollbar.set)

        # Function to load accounts
        def load_accounts():
            tree.delete(*tree.get_children())
            query = "SELECT id, username, role FROM users"
            self.cursor.execute(query)
            for account in self.cursor.fetchall():
                tree.insert("", "end", values=account)

        # Load initial data
        load_accounts()

        # Create a frame for buttons
        button_frame = ttk.Frame(frame)
        button_frame.pack(pady=10)

        # Add Account button
        add_button = tk.Button(button_frame, text="Add Account", command=self.add_account_window, bg="#4CAF50", fg="white", activebackground="#45a049")
        add_button.pack(side="left", padx=5)

        # Edit Account button
        edit_button = tk.Button(button_frame, text="Edit Account", command=lambda: self.edit_account_window(tree), bg="#2196F3", fg="white", activebackground="#1E88E5")
        edit_button.pack(side="left", padx=5)

        # Delete Account button
        delete_button = tk.Button(button_frame, text="Delete Account", command=lambda: self.delete_account(tree), bg="#F44336", fg="white", activebackground="#D32F2F")
        delete_button.pack(side="left", padx=5)

    def add_account_window(self):
        add_window = tk.Toplevel(self.master)
        add_window.title("Add Account")
        add_window.geometry("300x250")
        add_window.configure(bg="#f0f0f0")

        tk.Label(add_window, text="Username:", bg="#f0f0f0", fg="#333333").pack(pady=5)
        username_entry = tk.Entry(add_window)
        username_entry.pack(pady=5)

        tk.Label(add_window, text="Password:", bg="#f0f0f0", fg="#333333").pack(pady=5)
        password_entry = tk.Entry(add_window, show="*")
        password_entry.pack(pady=5)

        tk.Label(add_window, text="Role:", bg="#f0f0f0", fg="#333333").pack(pady=5)
        role_var = tk.StringVar(add_window)
        role_var.set("student")  # default value
        role_option = tk.OptionMenu(add_window, role_var, "student", "teacher", "admin")
        role_option.pack(pady=5)

        def save_account():
            username = username_entry.get()
            password = password_entry.get()
            role = role_var.get()

            if username and password:
                query = "INSERT INTO users (username, password, role) VALUES (%s, %s, %s)"
                try:
                    self.cursor.execute(query, (username, password, role))
                    self.db.commit()
                    messagebox.showinfo("Success", "Account added successfully")
                    add_window.destroy()
                    self.show_account_management(self.master.children["!notebook"].children["!frame5"])
                except mysql.connector.Error as err:
                    messagebox.showerror("Error", f"An error occurred: {err}")
            else:
                messagebox.showerror("Error", "Username and password are required")

        save_button = tk.Button(add_window, text="Save", command=save_account, bg="#4CAF50", fg="white", activebackground="#45a049")
        save_button.pack(pady=10)

    def edit_account_window(self, tree):
        selected_item = tree.selection()
        if not selected_item:
            messagebox.showerror("Error", "Please select an account to edit")
            return

        account_id = tree.item(selected_item)['values'][0]
        query = "SELECT * FROM users WHERE id = %s"
        self.cursor.execute(query, (account_id,))
        account = self.cursor.fetchone()

        edit_window = tk.Toplevel(self.master)
        edit_window.title("Edit Account")
        edit_window.geometry("300x250")
        edit_window.configure(bg="#f0f0f0")

        tk.Label(edit_window, text="Username:", bg="#f0f0f0", fg="#333333").pack(pady=5)
        username_entry = tk.Entry(edit_window)
        username_entry.insert(0, account[1])
        username_entry.pack(pady=5)

        tk.Label(edit_window, text="New Password (leave blank to keep current):", bg="#f0f0f0", fg="#333333").pack(pady=5)
        password_entry = tk.Entry(edit_window, show="*")
        password_entry.pack(pady=5)

        tk.Label(edit_window, text="Role:", bg="#f0f0f0", fg="#333333").pack(pady=5)
        role_var = tk.StringVar(edit_window)
        role_var.set(account[3])  # current role
        role_option = tk.OptionMenu(edit_window, role_var, "student", "teacher", "admin")
        role_option.pack(pady=5)

        def update_account():
            username = username_entry.get()
            password = password_entry.get()
            role = role_var.get()

            if username:
                if password:
                    query = "UPDATE users SET username = %s, password = %s, role = %s WHERE id = %s"
                    params = (username, password, role, account_id)
                else:
                    query = "UPDATE users SET username = %s, role = %s WHERE id = %s"
                    params = (username, role, account_id)

                try:
                    self.cursor.execute(query, params)
                    self.db.commit()
                    messagebox.showinfo("Success", "Account updated successfully")
                    edit_window.destroy()
                    self.show_account_management(self.master.children["!notebook"].children["!frame5"])
                except mysql.connector.Error as err:
                    messagebox.showerror("Error", f"An error occurred: {err}")
            else:
                messagebox.showerror("Error", "Username is required")

        update_button = tk.Button(edit_window, text="Update", command=update_account, bg="#2196F3", fg="white", activebackground="#1E88E5")
        update_button.pack(pady=10)

    def delete_account(self, tree):
        selected_item = tree.selection()
        if not selected_item:
            messagebox.showerror("Error", "Please select an account to delete")
            return

        account_id = tree.item(selected_item)['values'][0]
        confirm = messagebox.askyesno("Confirm Deletion", "Are you sure you want to delete this account?")
        if confirm:
            query = "DELETE FROM users WHERE id = %s"
            try:
                self.cursor.execute(query, (account_id,))
                self.db.commit()
                messagebox.showinfo("Success", "Account deleted successfully")
                self.show_account_management(self.master.children["!notebook"].children["!frame5"])
            except mysql.connector.Error as err:
                messagebox.showerror("Error", f"An error occurred: {err}")