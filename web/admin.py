from django.contrib import admin
from  web.models import Student, Room, StudentInRoom, Teacher, Absent, Subject, TeacherInRoom, StudentAbsent, UserTeacher
# Register your models here.

admin.site.register(Student)
admin.site.register(Room)
admin.site.register(StudentInRoom)
admin.site.register(Teacher)
admin.site.register(Absent)
admin.site.register(Subject)
admin.site.register(TeacherInRoom)
admin.site.register(StudentAbsent)
admin.site.register(UserTeacher)