from datetime import datetime
from django.shortcuts import render
from django.db.models import Count
from django.http import HttpResponse
from .models import Teacher, Subject, Room, StudentInRoom,Absent, TeacherInRoom, StudentAbsent, Student
from .linenotify import sendMessage
# Create your views here.

def index(request):
    '''
    สำหรับการบันทึก กิจกรรม การเข้าเรียนของนักเรียน
    :param request:
    :return:
    '''

    #ค้นหารายชื่อของครูมาทั้งหมด
    teachers = Teacher.objects.all()
    # ค้นหารายชื่อของวิชาที่สอนมาทั้งหมด
    subjects = Subject.objects.all()
    # ค้นหารายชื่อของห้องนักเรียนมาทั้งหมด
    rooms = Room.objects.all()
    # ค้นหารายการ มา/ไม่มาเรียน มาทั้งหมด
    absents = Absent.objects.all()

    #กำหนดค่าตัวแปรให้เป็นช่องว่าไว้ก่อน
    #เวลาที่สอน
    teach_time = ''
    #คาบที่สอน
    time= ''
    # วิชาที่สอน
    subject=''
    # ครูผู้สอน
    teacher=''
    # ห้องเรียน
    room=''
    # รายชื่อนักเรียนที่มา/ไม่มาเรียน
    student_inroom_absent =[]

    # สำหรับการกดปุ่มค้นหาจะให้ทำงาน
    if request.method == 'POST':
        # รับข้อมูล วันที่สอน มาแปลงจากข้อความให้อยู่ในรูป Datetime ตามรูปแบบของ dd/mm/yyyy
        teach_time = request.POST.get('teach_time')
        teach_date = datetime.strptime(teach_time, '%d/%m/%Y')

        # รับข้อมูล คาบที่สอน
        time = request.POST.get('time')
        # รับข้อมูล วิชาที่สอน
        subject = request.POST.get('subject')
        # รับข้อมูล ครูที่สอน
        teacher = request.POST.get('teacher')
        # รับข้อมูล ห้องที่สอน
        room = request.POST.get('room')

        # ค้นหาข้อมูลห้องที่รับมา จากฐานข้อมูลเพื่อให้ได้รายละเอียดมากขึ้น
        room_select = Room.objects.get(pk=room)
        # ค้นหาข้อมูลครูผู้สอนที่รับมา จากฐานข้อมูลเพื่อให้ได้รายละเอียดมากขึ้น
        teacher_select = Teacher.objects.get(pk=teacher)
        # ค้นหาข้อมูลวิชาที่รับมา จากฐานข้อมูลเพื่อให้ได้รายละเอียดมากขึ้น
        subject_select = Subject.objects.get(pk=subject)

        # ค้นหาข้อมูลตามวันที่ ครูผู้สอน คาบ วิชา ห้องที่สอน จาก ข้อมูลครูที่สอนในห้อง
        teacherInRoom = TeacherInRoom.objects.filter(time = time, subject= subject_select, \
                                     teacher=teacher_select, room =room_select,\
                                     teach_date = teach_date).first()

        # ตรวจสอบถ้ายังไม่มีการบันทึกให้ทำการบันทึก
        if teacherInRoom is None:
            # ค้นหาข้อมูลห้องที่รับมา จากฐานข้อมูลเพื่อให้ได้รายละเอียดมากขึ้น
            teacherInRoom = TeacherInRoom(time = time, subject= subject_select, \
                                     teacher=teacher_select, room =room_select,\
                                     teach_date = teach_date)
            teacherInRoom.save()

        # ค้นหารายชื่อนักเรียนในห้องที่ได้เลือกไว้แล้ว
        student_in_room = StudentInRoom.objects.filter(room=room_select).all()
        # เพือนำรายชื่อนักเรียนทั้งหมดในห้อง มาบันทึกลงในตาราง นักเรียนที่มา / ไม่มาเรียนตามกลุ่มที่ได้เลือกไว้
        for inroom in student_in_room:
            # ตรวจสอบ ข้อมูลในตาราง นักเรียนที่มา / ไม่มาเรียน ก่อนว่ามีการบันทึกไว้หรือไม่ถ้ายังไม่มีให้บันทึกใหม่
            student_absent  = StudentAbsent.objects.filter(student = inroom.student, teacherinroom = teacherInRoom).first()

            if student_absent is None:
                # บันทึกนักเรียนกับ รายการครูที่สอนตามข้อมูลที่เลือกไว้
                student_absent = StudentAbsent(student = inroom.student, teacherinroom = teacherInRoom)
                student_absent.save()

            # นำข้อมูลเก็บลงตัวแปร เพื่อนำไปแสดง
            student_inroom_absent.append(student_absent)

    # เตรียมข้อมูลเพื่อนำไปแสดงบนหน้า html
    context = {'teachers': teachers,
               'subjects': subjects,
               'rooms': rooms,
               'absents': absents,
               'teach_time': teach_time,
               'time': time,
               'subject': subject,
               'teacher': teacher,
               'room': room,
               'student_inroom_absent':student_inroom_absent
               }

    return render(request, 'index.html', context)


def savestudentabsent(request):
    '''
    บันทึหข้อมูลนักเรียนที่มา หรือไม่มาตามที่ครูได้เลือกไวเ
    :param request:
    :return:
    '''
    if request.method == 'POST':
        print(request.POST)
        student_inroom = request.POST.getlist('student_inroom')
        absent = request.POST.getlist('absent')

        #ตรวจสอบว่ามีการบันทึกไว้หรือไว้ โดยตรวจสอบกับ promary key ข้องตารางถ้ามีให้ทำการ update
        #ในเงื่อนไขนี้จะต้องมีข้อมูลอยู่แล้ว เพราะได้มีการเพิ่ม (Insert) ข้อมุลไว้ก่อนหน้านี้
        for i in range(0, len(absent)):

            studentAbsent = StudentAbsent.objects.get(pk=student_inroom[i])
            std_absent = Absent.objects.get(pk=absent[i])
            if studentAbsent:
                #ทำการบันทึก การมา/ไม่มา ของนักเรียน
                studentAbsent.absent = std_absent
                studentAbsent.save()

                # ส่งข้อมูลของนักเรียนและ ชื่อครู วันที่ คาบ สถานะการมา ไปยัง line
                if std_absent.send_alert :
                    message = "นักเรียน %s ในวิชา %s คาบเรียน %s ของครู %s วันที่ %s สถานะ %s" \
                    %(studentAbsent.student, studentAbsent.teacherinroom.subject,
                      studentAbsent.teacherinroom.time,
                      studentAbsent.teacherinroom.teacher,
                      studentAbsent.teacherinroom.teach_date,
                      studentAbsent.absent)

                    sendMessage(message)
            else:
                print("error : update")
    context = {
               }

    return render(request, 'save.html', context)

def report_index(request):
    '''
    รายงาน จำนวนนักเรียนแยกชาย หญิง ตามประเภทการมา/ไม่มาเรียน ตามช่วงเวลา
    :param request:
    :return:
    '''
    # กำหมดค่าเวลา เริ่ม และ สิ้นสุดเป็นวันนี้ (ใช้กรณีตั้งต้น)
    start_teach_time = datetime.now().strftime("%d/%m/%Y")
    stop_teach_time = datetime.now().strftime("%d/%m/%Y")
    show_absent = []
    data_male = []
    data_fremale = []
    # หาประเภทของการมา/ไม่มา เรียน ทั้งหมด
    absent = Absent.objects.all()

    # นำเฉพาะชื่อมาแสดงในรายงาน
    for abs in absent:
        show_absent.append(abs.name)

    # สำหรับการกด แสดงรายงาน
    if request.method == 'POST':
        print(request.POST)

        # รับวันที่เริ่มต้น
        start_teach_time = request.POST.get('start_teach_time')
        # รับวันที่สิ้นสุด
        stop_teach_time = request.POST.get('stop_teach_time')

        # กรณีไม่ได้เลือกวันที่เริ่มต้นไว้ ให้กำหมดค่าเริ่ต้นเป็นวันนี้
        if len(start_teach_time) == 0:
            start_teach_time = datetime.now().strftime("%d/%m/%Y")

        # กรณีไม่ได้เลือกวันที่สิ้นสุดไว้ ให้กำหมดค่าเริ่ต้นเป็นวันนี้
        if len(stop_teach_time) == 0:
            stop_teach_time = datetime.now().strftime("%d/%m/%Y")

        # แปลงวันที่ในรูปข้อความ ให้อยู่ในรูป Datetime
        start_time = datetime.strptime(start_teach_time + ' 00:00:00', '%d/%m/%Y %H:%M:%S')
        stop_time = datetime.strptime(stop_teach_time + ' 23:59:59', '%d/%m/%Y %H:%M:%S')

        # ทำการหา จำนวนนักเรียน ชาย หญิง จาก รูปแบบการ มา / ไม่มาเรียน และวันที่
        for abs in absent:
            male = StudentAbsent.objects.filter(teacherinroom__teach_date__range=(start_time, stop_time),  absent = abs, student__sex = Student.SexChoiceEnum.male.value).count()
            fremale = StudentAbsent.objects.filter(teacherinroom__teach_date__range=(start_time, stop_time),  absent=abs, student__sex=Student.SexChoiceEnum.fremale.value).count()
            print("%s : %s , %s " % (abs, male, fremale))
            data_male.append(male)
            data_fremale.append(fremale)
    # เตรียมข้อมูลเพื่อนำไปแสดงบนหน้า html
    context = { 'start_teach_time': start_teach_time,
                'stop_teach_time': stop_teach_time,
                'show_absent': show_absent,
                'data_male': data_male,
                'data_fremale': data_fremale
                }
    return render(request, 'report_index.html', context)


def report_table(request):
    '''
    รายงาน จำนวนนักเรียนแยกชาย หญิง ตามประเภทการมา/ไม่มาเรียน ตามช่วงเวลา
    :param request:
    :return:
    '''

    # กำหมดค่าเวลา เริ่ม และ สิ้นสุดเป็นวันนี้ (ใช้กรณีตั้งต้น)
    start_teach_time = datetime.now().strftime("%d/%m/%Y")
    stop_teach_time = datetime.now().strftime("%d/%m/%Y")

    data_student_in_room = []
    total_abs = {}
    room_select= ''
    subject_select=''
    # หาประเภทของการมา/ไม่มา เรียน ทั้งหมด
    absent = Absent.objects.all()
    room = Room.objects.all()
    subject = Subject.objects.all()






    # สำหรับการกด แสดงรายงาน
    if request.method == 'POST':
        print(request.POST)

        # รับวันที่เริ่มต้น
        start_teach_time = request.POST.get('start_teach_time')
        # รับวันที่สิ้นสุด
        stop_teach_time = request.POST.get('stop_teach_time')

        room_select = request.POST.get('room_select')
        subject_select = request.POST.get('subject_select')
        print("room_select : %s" %(room_select))
        print("subject_select : %s" % (subject_select))
        # กรณีไม่ได้เลือกวันที่เริ่มต้นไว้ ให้กำหมดค่าเริ่ต้นเป็นวันนี้
        if len(start_teach_time) == 0:
            start_teach_time = datetime.now().strftime("%d/%m/%Y")

        # กรณีไม่ได้เลือกวันที่สิ้นสุดไว้ ให้กำหมดค่าเริ่ต้นเป็นวันนี้
        if len(stop_teach_time) == 0:
            stop_teach_time = datetime.now().strftime("%d/%m/%Y")

        # แปลงวันที่ในรูปข้อความ ให้อยู่ในรูป Datetime
        start_time = datetime.strptime(start_teach_time + ' 00:00:00', '%d/%m/%Y %H:%M:%S')
        stop_time = datetime.strptime(stop_teach_time + ' 23:59:59', '%d/%m/%Y %H:%M:%S')

        # หานักเรียนที่อยู่ในห้องที่เลือก
        students = StudentInRoom.objects.filter(room = room_select).all()


        for stu in students:
            tmpstudent = stu.student

            student_abs = []
            for abs in absent:
                abs_count = StudentAbsent.objects.filter(teacherinroom__teach_date__range=(start_time, stop_time),
                                                    teacherinroom__subject=subject_select,
                                                    teacherinroom__room=room_select,
                                                    student = tmpstudent,
                                                    absent=abs).count()

                count_abs = total_abs.get(abs.id,None)
                if count_abs == None:
                    count_abs = 0

                count_abs = count_abs + abs_count
                total_abs[abs.id] = count_abs

                student_abs.append({'abs_id' : abs.id, 'abs_name': abs.name, 'count': abs_count})



            data_student_in_room.append( {'stu_id' : tmpstudent.id, 'stu_name': tmpstudent, 'abs' : student_abs})


        print ('%s' %(total_abs))


    # เตรียมข้อมูลเพื่อนำไปแสดงบนหน้า html
    context = { 'start_teach_time': start_teach_time,
                'stop_teach_time': stop_teach_time,

                'room' : room , 'subject': subject, 'absent':absent,
                'room_select': room_select, 'subject_select': subject_select,
                'data_student_in_room' : data_student_in_room,'total_abs':total_abs
                }
    return render(request, 'report_table.html', context)
