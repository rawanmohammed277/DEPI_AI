class Student:
    _id_counter = 1 # class atribute
    def __init__(self,name):
        self.student_id= Student._id_counter
        Student._id_counter +=1
        self.name = name
        self.grades={}
        self.enrolled_courses =[]
        
    def __str__(self):
        return f'Student ID: {self.student_id}, Name: {self.name}, Grades: {self.grades}, Courses: {self.enrolled_courses}'
    
    def __repr__(self) -> str:
        return f'Student ID: {self.student_id}, Name: {self.name}'
    
    def add_grades(self,course_id, grade):
        if not  0<=grade<=100 :
            raise ValueError("Grade must be between 0 and 100")
        self.grades[course_id] = grade
        
    def enrolleed_courses(self,course):
        if course in self.enrolled_courses:
            raise ValueError("student already enrolled in this course")
        else:
            self.enrolled_courses.append(course)

        