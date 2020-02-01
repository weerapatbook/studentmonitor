    for abs in absent:
        show_absent.append(abs.name)

    if request.method == 'POST':
        print(request.POST)

        start_teach_time = request.POST.get('start_teach_time')
        stop_teach_time = request.POST.get('stop_teach_time')

        if len(start_teach_time) == 0:
            start_teach_time = datetime.now().strftime("%d/%m/%Y")

        if len(stop_teach_time) == 0:
            stop_teach_time = datetime.now().strftime("%d/%m/%Y")

        start_time = datetime.strptime(start_teach_time + ' 00:00:00', '%d/%m/%Y %H:%M:%S')
        stop_time = datetime.strptime(stop_teach_time + ' 23:59:59', '%d/%m/%Y %H:%M:%S')

        for abs in absent:
            male = StudentAbsent.objects.filter(teacherinroom__teach_date__range=(start_time, stop_time),  absent = abs, student__sex = Student.SexChoiceEnum.male.value).count()
            fremale = StudentAbsent.objects.filter(teacherinroom__teach_date__range=(start_time, stop_time),  absent=abs, student__sex=Student.SexChoiceEnum.fremale.value).count()
            print("%s : %s , %s " % (abs, male, fremale))
            data_male.append(male)
            data_fremale.append(fremale)
    context = { 'start_teach_time': start_teach_time,
                'stop_teach_time': stop_teach_time,
                'show_absent': show_absent,
                'data_male': data_male,
                'data_fremale': data_fremale
                }
    return render(request, 'report_index.html', context)