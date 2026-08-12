class Course:

    _id_counter = 1

    def __init__(self, name):
        self.course_id = Course._id_counter
        Course._id_counter += 1

        self.name = name
        self.grades = {}
        self.enrolled_students = []

    def __str__(self):
        return f'Course_ID: {self.course_id}, Name: {self.name}, Enrolled_Students: {self.enrolled_students}'

    def __repr__(self):
        return f'Course_ID: {self.course_id}, Name: {self.name}, Enrolled_Students: {self.enrolled_students}'

    def enroll_student(self, student_name: str) -> None:
        if student_name not in self.enrolled_students:
            self.enrolled_students.append(student_name)
            print(f'Student {student_name} has been enrolled in {self.name}')
        else:
            print(f'Student {student_name} is already enrolled in {self.name}')
            
            
    def remove_student(self, student_name: str) -> None:
        if student_name in self.enrolled_students:
            self.enrolled_students.remove(student_name)
            print(f'Student {student_name} has been removed from {self.name}')
        else:
            print(f'Student {student_name} is not enrolled in {self.name}')