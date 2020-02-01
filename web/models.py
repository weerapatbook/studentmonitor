from django.db import models
from django.contrib.auth.models import User
from enum import Enum
# Create your models here.


class IntegerRangeField(models.IntegerField):
    def __init__(self, verbose_name=None, name=None, min_value=None, max_value=None, **kwargs):
        self.min_value, self.max_value = min_value, max_value
        models.IntegerField.__init__(self, verbose_name, name, **kwargs)
    def formfield(self, **kwargs):
        defaults = {'min_value': self.min_value, 'max_value':self.max_value}
        defaults.update(kwargs)
        return super(IntegerRangeField, self).formfield(**defaults)




class Student(models.Model):
    '''
    เก็บข้อมูลรายชื่อนักเรียน
    first_name ชื่อนักเรียน
    last_name นามสกุลนักเรียน
    code รหัสนักเรียน
    sex เพศ
    '''
    class SexChoiceEnum(Enum):
        male = '1'
        fremale = '2'

        @classmethod
        def choices(cls):
            return tuple((i.value, i.name) for i in cls)

    first_name = models.CharField(max_length=200,blank=True, null=True)
    last_name =  models.CharField(max_length=200,blank=True, null=True)
    code = models.CharField(max_length=200,blank=True, null=True)
    sex  = models.CharField(max_length=1, choices=SexChoiceEnum.choices(),blank=True, null=True)

    def __str__(self):
        return r"%s %s" %(self.first_name, self.last_name)

class Room (models.Model):
    '''
    เก็บข้อมูลห้องเรียนชั้นนักเรียน
    name ชื่อห้องเรียนชั้นนักเรียน
    description รายละเอียด
    '''
    name = models.CharField(max_length=200,blank=True, null=True)
    description = models.CharField(max_length=200,blank=True, null=True)
    line_access_token = models.CharField(max_length=255, blank=True, null=True)
    classroom = IntegerRangeField(min_value=1, max_value=6 , default=1, blank=True, null=True)
    room = IntegerRangeField(min_value=1, max_value=6, default=1, blank=True, null=True)
    def __str__(self):
        return r"%s" %(self.name)

class Teacher(models.Model):
    '''
    เก็บข้อมูลรายชื่อนักเรียน
    name ชื่อครู
    description รายละเอียด
    telephone เบอร์โทร
    '''
    name = models.CharField(max_length=200,blank=True, null=True)
    description = models.CharField(max_length=200,blank=True, null=True)
    telephone = models.CharField(max_length=200,blank=True, null=True)

    def __str__(self):
        return r"%s" %(self.name)

class Absent(models.Model):
    '''
    เก็บข้อมูลการมา / ไม่มา เรียน และต้องการให้ส่ง ไปยัง line message หรือไม่
    name ชื่อรายการ มา / ไม่มาเรียน
    description รายละเอียด
    send_alert ส่ง หรือ ไม่ส่ง ถ้าเป็น True ให้ส่งไปยัง line message, False ไม่ต้องส่ง
    '''
    name = models.CharField(max_length=200,blank=True, null=True)
    description = models.CharField(max_length=200,blank=True, null=True)
    send_alert = models.BooleanField(default=False,blank=True, null=True)
    def __str__(self):
        return r"%s" %(self.name)

class Subject(models.Model):
    '''
    เก็บข้อมูลวิชาที่มีการสอน
    name ชื่อวิชา
    description รายละเอียด
    '''
    name = models.CharField(max_length=200,blank=True, null=True)
    description = models.CharField(max_length=200,blank=True, null=True)

    def __str__(self):
        return r"%s" %(self.name)

class StudentInRoom(models.Model):
    '''
    เก็บข้อมูลห้องเรียน กับรายชื่อนักเรียน
    room ห้องเรียน
    student  ชื่อนักเรียน
    current_year ประจำปี พ.ศ.
    '''
    room = models.ForeignKey(Room, on_delete=models.CASCADE,blank=True, null=True )
    student = models.ForeignKey(Student, on_delete=models.CASCADE,blank=True, null=True )
    current_year = models.IntegerField(blank=True, null=True,default=2561)
    def __str__(self):
        return r"%s (%s)" %(self.room, self.student)


class TeacherInRoom(models.Model):
    '''
    เก็บข้อมูล เงื่อนไข ของ วันที่สอน คาบ ครู วิชา ห้องเรียน เพื่อให้สามารถระบุนักเรียน
    teach_date วันที่สอน
    time คาบที่สอน
    subject วิชาที่สอน
    teacher ครูที่สอน
    room ห้องที่สอน
    '''
    teach_date = models.DateField(blank=True, null=True)
    time = models.CharField(max_length=200,blank=True, null=True)
    subject = models.ForeignKey(Subject, on_delete=models.CASCADE, blank=True, null=True)
    teacher = models.ForeignKey(Teacher, on_delete=models.CASCADE, blank=True, null=True)
    room = models.ForeignKey(Room, on_delete=models.CASCADE,blank=True, null=True )



    def __str__(self):
        return r"%s %s (%s)" % (self.teach_date, self.subject, self.teacher)

class StudentAbsent(models.Model):
    '''
    เก็บข้อมูลรายชื่อนักเรียนที่มา / ไม่มา ตามเงื่อนไขของ วันที่สอน คาบ ครู วิชา ห้องเรียน
    teacherinroom เงื่อนไขของ วันที่สอน คาบ ครู วิชา ห้องเรียน
    student ชื่อนักเรียน
    absent สถานะการมา / ไม่มาเรียน
    '''
    teacherinroom = models.ForeignKey(TeacherInRoom, on_delete=models.CASCADE, blank=True, null=True)
    student = models.ForeignKey(Student, on_delete=models.CASCADE, blank=True, null=True)
    absent = models.ForeignKey(Absent, on_delete=models.CASCADE, blank=True, null=True)

    def __str__(self):
        return r"%s %s" % (self.student, self.absent)

class UserTeacher(models.Model):
    '''
    เก็บ user เชื่อมกับ ตาราง Teacher
    '''
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    teacher = models.ForeignKey(Teacher, on_delete=models.CASCADE, blank=True, null=True)

    def __str__(self):
        return r"%s %s" % (self.user.username, self.teacher)