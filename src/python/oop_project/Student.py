class Student:
    
    _id_counter= 1
    
    def __init__(self, name):
        self.student_id= Student._id_counter
        Student._id_counter +=1
        self.name= name
        self.grades= {}
        self.enrolled_courses= []
        
    def __str__(self):
        return f'Student_ID: {self.student_id}, Name: {self.name}, Grade: {self.grades}'

    def add_grades(self,course_id, grade):
        if not  0<=grade<=100 :
            raise ValueError("Grade must be between 0 and 100")
        self.grades[course_id] = grade
        
    def enrolleed_courses(self,course):
        if course in self.enrolled_courses:
            raise ValueError("student already enrolled in this course")
        else:
            self.enrolled_courses.append(course)