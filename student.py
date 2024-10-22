import tkinter as tk
from tkinter import ttk

class StudentGUI:
    def __init__(self, master, db, user_id):
        self.master = master
        self.master.title("Student Dashboard")
        self.master.geometry("800x600")
        self.master.configure(bg="#f0f0f0")

        self.db = db
        self.cursor = db.cursor()
        self.user_id = user_id

        self.create_widgets()

    def create_widgets(self):
        # Title
        title_label = tk.Label(self.master, text="Student Dashboard", font=("Arial", 24, "bold"), bg="#f0f0f0", fg="#333333")
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

        # Grades Tab
        grades_frame = ttk.Frame(notebook)
        notebook.add(grades_frame, text="Grades")
        self.show_grades(grades_frame)

        # Schedule Tab
        schedule_frame = ttk.Frame(notebook)
        notebook.add(schedule_frame, text="Schedule")
        self.show_schedule(schedule_frame)

    def show_personal_info(self, frame):
        query = """
        SELECT s.first_name, s.last_name, s.date_of_birth, s.class
        FROM students s
        JOIN users u ON s.user_id = u.id
        WHERE u.id = %s
        """
        self.cursor.execute(query, (self.user_id,))
        student_info = self.cursor.fetchone()

        if student_info:
            info_frame = tk.Frame(frame, bg="#ffffff", padx=20, pady=20)
            info_frame.pack(pady=20, padx=20, fill="both", expand=True)

            tk.Label(info_frame, text="Personal Information", font=("Arial", 16, "bold"), bg="#ffffff", fg="#333333").pack(pady=(0, 10))
            tk.Label(info_frame, text=f"Name: {student_info[0]} {student_info[1]}", font=("Arial", 12), bg="#ffffff", fg="#333333").pack(pady=5)
            tk.Label(info_frame, text=f"Date of Birth: {student_info[2]}", font=("Arial", 12), bg="#ffffff", fg="#333333").pack(pady=5)
            tk.Label(info_frame, text=f"Class: {student_info[3]}", font=("Arial", 12), bg="#ffffff", fg="#333333").pack(pady=5)
        else:
            tk.Label(frame, text="No personal information available.", font=("Arial", 12), fg="#333333").pack(pady=5)

    def show_grades(self, frame):
        query = """
        SELECT s.name, g.grade
        FROM grades g
        JOIN subjects s ON g.subject_id = s.id
        JOIN students st ON g.student_id = st.id
        JOIN users u ON st.user_id = u.id
        WHERE u.id = %s
        """
        self.cursor.execute(query, (self.user_id,))
        grades = self.cursor.fetchall()

        if grades:
            tree = ttk.Treeview(frame, columns=("Subject", "Grade"), show="headings")
            tree.heading("Subject", text="Subject")
            tree.heading("Grade", text="Grade")
            tree.pack(pady=10, padx=10, expand=True, fill="both")

            for grade in grades:
                tree.insert("", "end", values=grade)
        else:
            tk.Label(frame, text="No grades available.", font=("Arial", 12), fg="#333333").pack(pady=5)

    def show_schedule(self, frame):
        query = """
        SELECT s.name, t.first_name, t.last_name, sc.day_of_week, sc.start_time, sc.end_time
        FROM schedule sc
        JOIN subjects s ON sc.subject_id = s.id
        JOIN teachers t ON sc.teacher_id = t.id
        JOIN students st ON sc.class = st.class
        JOIN users u ON st.user_id = u.id
        WHERE u.id = %s
        ORDER BY FIELD(sc.day_of_week, 'Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday'), sc.start_time
        """
        self.cursor.execute(query, (self.user_id,))
        schedule = self.cursor.fetchall()

        if schedule:
            tree = ttk.Treeview(frame, columns=("Subject", "Teacher", "Day", "Start Time", "End Time"), show="headings")
            tree.heading("Subject", text="Subject")
            tree.heading("Teacher", text="Teacher")
            tree.heading("Day", text="Day")
            tree.heading("Start Time", text="Start Time")
            tree.heading("End Time", text="End Time")
            tree.pack(pady=10, padx=10, expand=True, fill="both")

            for item in schedule:
                tree.insert("", "end", values=(item[0], f"{item[1]} {item[2]}", item[3], item[4], item[5]))
        else:
            tk.Label(frame, text="No schedule available.", font=("Arial", 12), fg="#333333").pack(pady=5)