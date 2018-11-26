from django.shortcuts import render, HttpResponse
from django.contrib.auth.decorators import login_required
from repository import models
from EasyCRM import settings
from easycrmadmin import permission_control
import os, time, json
# Create your views here.


@login_required
@permission_control.check_permission
def my_courses(request):
    """
    学员的课程列表
    :param request:
    :return:
    """
    print('student')
    # print(dir(request.user))
    # obj = request.user.stu_account.profile.enrollment_set.select_related()
    # print("objL", obj)
    # for index in obj:
    #     print(index.id)
    return render(request, "student/student_main_pg.html")


@login_required
@permission_control.check_permission
def my_homeworks(request, eid):
    obj = models.Enrollment.objects.get(id=eid)
    return render(request, 'student/homeworks.html', {'enroll_obj': obj})


@login_required
@permission_control.check_permission
def my_grade(reqeust):
    pass


def get_uploaded_fileinfo(file_dic, upload_dir):
    for filename in os.listdir(upload_dir):
        abs_file_path = '%s/%s' % (upload_dir, filename)
        file_create_time = time.strftime("%Y-%m-%d %H:%M:%S", time.gmtime(os.path.getctime(abs_file_path)))
        file_dic['files'][filename] = {'size': os.path.getsize(abs_file_path) / 1000, 'ctime': file_create_time}


@login_required
@permission_control.check_permission
def my_homework_detail(request, eid, cid):
    """
    最后一点了,想想这里面这么写:
    GET方式: 判断保存作业的文件路径有没有,没有的话创建路径
            确认这个学生是不是有这个节课的上课记录
            有的话获取信息返回,没有的话先给它创建一个（它可以其它方式完成学习啊）
    POST方式: 将学生提交的作业文件写入到对应的文件路径中,简单返回一个结果吧
    :param request:
    :param eid:
    :param cid:
    :return:
    """
    print("my_homework_detail")
    print(eid, cid)
    course_rc_obj = models.CourseRecord.objects.get(id=cid)
    upload_dir = "%s%s%s%s%s%s" % (settings.BASE_HOMEWORK_DIR,
                                   eid,
                                   os.sep,
                                   course_rc_obj.from_class.id,
                                   os.sep,
                                   cid)
    print("上传文件路径:", upload_dir)
    if not os.path.isdir(upload_dir):
        os.makedirs(upload_dir, exist_ok=True)
    response_dic = {'files': {}}
    if request.method == "POST":
        if request.FILES:
            print("upload files:", request.FILES)
            for k, v in request.FILES.items():
                if len(os.listdir(upload_dir)) < 5:
                    with open("%s/%s" % (upload_dir, v.name), 'wb+') as wf:
                        for chunk in v.chunks():
                            wf.write(chunk)
                else:
                    response_dic['error'] = "不能上传超过4个文件"
            get_uploaded_fileinfo(response_dic, upload_dir)
            return HttpResponse(json.dumps(response_dic))

    get_uploaded_fileinfo(response_dic, upload_dir)
    study_rc_obj = models.StudyRecord.objects.filter(student_id=eid, course_record_id=cid)
    print("study_rc_obj:", study_rc_obj)
    if study_rc_obj:
        study_rc_obj = study_rc_obj[0]
    else:
        study_rc_obj = models.StudyRecord(
            student_id=eid,
            course_record_id=cid,
            record='checked',
            score=0
        )
        study_rc_obj.save()

    return render(request, 'student/homework_detail.html',
                  {'study_record_obj': study_rc_obj,
                   'course_record_obj': course_rc_obj,
                   'uploaded_files': response_dic})


@login_required
@permission_control.check_permission
def delete_file(request, eid, cid):
    """
    前端主动删除上传照片
    :param request:
    :param erd: 报名表中的学生ID
    :param cid:课程记录ID
    :return:
    """
    print("delete_file")
    response = {}
    file_info = ""
    if request.method == "POST":
        print(request.POST)  # 会多传一个[]过来，原因暂时未知....
        # print(request.POST.get("filename"))
        course_record_obj = models.CourseRecord.objects.get(id=cid)
        upload_dir = "%s%s/%s/%s" % (settings.BASE_HOMEWORK_DIR,
                                     eid,
                                     course_record_obj.from_class.id,
                                     cid)
        for k in request.POST.lists():
            file_info = json.loads(k[0])

        filename = file_info.get('filename', None)
        file_abs_path = "%s/%s" % (upload_dir, filename.strip())
        if os.path.isfile(file_abs_path):
            os.remove(file_abs_path)
            response['msg'] = "文件 '%s' 已被删除了 " % filename
        else:
            response["error"] = "文件 '%s' 不存在" % filename
    else:
        response['error'] = "only supoort POST method..."
    return HttpResponse(json.dumps(response))
