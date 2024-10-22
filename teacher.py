import tkinter as tk
from tkinter import ttk, messagebox
import mysql.connector

class TeacherGUI:
    def __init__(self, master, db, user_id):
        self.master = master
        self.master.title("Teacher Dashboard")
        self.master.geometry("800x600")
        self.master.configure(bg="#f0f0f0")

        self.db = db
        self.cursor = db.cursor()
        self.user_id = user_id

        self.create_widgets()

    def create_widgets(self):
        # Title
        title_label = tk.Label(self.master, text="Teacher Dashboard", font=("Arial", 24, "bold"), bg="#f0f0f0", fg="#333333")
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

        # Schedule Tab
        schedule_frame = ttk.Frame(notebook)
        notebook.add(schedule_frame, text="Schedule")
        self.show_schedule(schedule_frame)

        # Student List Tab
        student_list_frame = ttk.Frame(notebook)
        notebook.add(student_list_frame, text="Student List")
        self.show_student_list(student_list_frame)

        # Grades Tab
        grades_frame = ttk.Frame(notebook)
        notebook.add(grades_frame, text="Grades")
        self.show_grades(grades_frame)

    def show_personal_info(self, frame):
        query = """
        SELECT t.first_name, t.last_name, t.subject
        FROM teachers t
        JOIN users u ON t.user_id = u.id
        WHERE u.id = %s
        """
        self.cursor.execute(query, (self.user_id,))
        teacher_info = self.cursor.fetchone()

        if teacher_info:
            info_frame = tk.Frame(frame, bg="#ffffff", padx=20, pady=20)
            info_frame.pack(pady=20, padx=20, fill="both", expand=True)

            tk.Label(info_frame, text="Personal Information", font=("Arial", 16, "bold"), bg="#ffffff", fg="#333333").pack(pady=(0, 10))
            tk.Label(info_frame, text=f"Name: {teacher_info[0]} {teacher_info[1]}", font=("Arial", 12), bg="#ffffff", fg="#333333").pack(pady=5)
            tk.Label(info_frame, text=f"Subject: {teacher_info[2]}", font=("Arial", 12), bg="#ffffff", fg="#333333").pack(pady=5)
        else:
            tk.Label(frame, text="No personal information available.", font=("Arial", 12), fg="#333333").pack(pady=5)

    def show_schedule(self, frame):
        query = """
        SELECT s.name, sc.class, sc.day_of_week, sc.start_time, sc.end_time
        FROM schedule sc
        JOIN subjects s ON sc.subject_id = s.id
        JOIN teachers t ON sc.teacher_id = t.id
        JOIN users u ON t.user_id = u.id
        WHERE u.id = %s
        ORDER BY FIELD(sc.day_of_week, 'Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday'), sc.start_time
        """
        self.cursor.execute(query, (self.user_id,))
        schedule = self.cursor.fetchall()

        if schedule:
            tree = ttk.Treeview(frame, columns=("Subject", "Class", "Day", "Start Time", "End Time"), show="headings")
            tree.heading("Subject", text="Subject")
            tree.heading("Class", text="Class")
            tree.heading("Day", text="Day")
            tree.heading("Start Time", text="Start Time")
            tree.heading("End Time", text="End Time")
            tree.pack(pady=10, padx=10, expand=True, fill="both")

            for item in schedule:
                tree.insert("", "end", values=item)
        else:
            tk.Label(frame, text="No schedule available.", font=("Arial", 12), fg="#333333").pack(pady=5)

    def show_student_list(self, frame):
        query = """
        SELECT DISTINCT s.id, s.first_name, s.last_name, s.class
        FROM students s
        JOIN schedule sc ON s.class = sc.class
        JOIN teachers t ON sc.teacher_id = t.id
        JOIN users u ON t.user_id = u.id
        WHERE u.id = %s
        ORDER BY s.class, s.last_name, s.first_name
        """
        self.cursor.execute(query, (self.user_id,))
        students = self.cursor.fetchall()

        if students:
            tree = ttk.Treeview(frame, columns=("ID", "First Name", "Last Name", "Class"), show="headings")
            tree.heading("ID", text="ID")
            tree.heading("First Name", text="First Name")
            tree.heading("Last Name", text="Last Name")
            tree.heading("Class", text="Class")
            tree.pack(pady=10, padx=10, expand=True, fill="both")

            for student in students:
                tree.insert("", "end", values=student)
        else:
            tk.Label(frame, text="No students available.", font=("Arial", 12), fg="#333333").pack(pady=5)

    def show_grades(self, frame):
        # Create a frame for the subject selection
        subject_frame = ttk.Frame(frame)
        subject_frame.pack(pady=10, padx=10, fill="x")

        tk.Label(subject_frame, text="Select Subject:", font=("Arial", 12), fg="#333333").pack(side="left", padx=(0, 10))
        subject_var = tk.StringVar()
        subject_combobox = ttk.Combobox(subject_frame, textvariable=subject_var, state="readonly")
        subject_combobox.pack(side="left")

        # Create a frame for the grade table
        table_frame = ttk.Frame(frame)
        table_frame.pack(pady=10, padx=10, expand=True, fill="both")

        # Create the grade table
        columns = ("Student ID", "First Name", "Last Name", "Class", "Grade")
        tree = ttk.Treeview(table_frame, columns=columns, show="headings")
        for col in columns:
            tree.heading(col, text=col)
        tree.pack(side="left", expand=True, fill="both")

        # Add a scrollbar
        scrollbar = ttk.Scrollbar(table_frame, orient="vertical", command=tree.yview)
        scrollbar.pack(side="right", fill="y")
        tree.configure(yscrollcommand=scrollbar.set)

        # Function to update the grade table
        def update_grade_table(*args):
            tree.delete(*tree.get_children())
            subject = subject_var.get()
            if subject:
                query = """
                SELECT s.id, s.first_name, s.last_name, s.class, g.grade
                FROM students s
                LEFT JOIN grades g ON s.id = g.student_id
                JOIN subjects sub ON g.subject_id = sub.id
                JOIN schedule sc ON s.class = sc.class AND sub.id = sc.subject_id
                JOIN teachers t ON sc.teacher_id = t.id
                JOIN users u ON t.user_id = u.id
                WHERE u.id = %s AND sub.name = %s
                ORDER BY s.class, s.last_name, s.first_name
                """
                self.cursor.execute(query, (self.user_id, subject))
                grades = self.cursor.fetchall()

                for grade in grades:
                    tree.insert("", "end", values=grade)

        # Function to save the updated grades
        def save_grades():
            for item in tree.get_children():
                values = tree.item(item, "values")
                student_id, grade = values[0], values[4]
                if grade:
                    query = """
                    INSERT INTO grades (student_id, subject_id, grade)
                    SELECT %s, id, %s FROM subjects WHERE name = %s
                    ON DUPLICATE KEY UPDATE grade = %s
                    """
                    self.cursor.execute(query, (student_id, grade, subject_var.get(), grade))
            self.db.commit()
            messagebox.showinfo("Success", "Grades saved successfully.")

        # Bind the update function to the subject selection
        subject_var.trace("w", update_grade_table)

        # Populate the subject combobox
        query = """
        SELECT DISTINCT s.name
        FROM subjects s
        JOIN schedule sc ON s.id = sc.subject_id
        JOIN teachers t ON sc.teacher_id = t.id
        JOIN users u ON t.user_id = u.id
        WHERE u.id = %s
        """
        self.cursor.execute(query, (self.user_id,))
        subjects = [row[0] for row in self.cursor.fetchall()]
        subject_combobox["values"] = subjects

        # Add a save button
        save_button = tk.Button(frame, text="Save Grades", command=save_grades, bg="#4CAF50", fg="white", activebackground="#45a049")
        save_button.pack(pady=10)

        # Enable editing of the Grade column
        def on_double_click(event):
            item = tree.selection()[0]
            column = tree.identify_column(event.x)
            if column == "#5":  # Grade column
                tree.edit(item, column)

        tree.bind("<Double-1>", on_double_click)