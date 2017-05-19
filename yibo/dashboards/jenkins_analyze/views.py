# -*- coding: utf-8 -*-

from django.http import HttpResponse
from django.shortcuts import render
import json
from models import BuildsResult
from models import Email
from jenkins_analyze.jenkins_analysis import TempestBuildsAnalysis
from jenkins_analyze.jenkins_analysis import UnittestBuildsAnalysis
from jenkins_analyze.jenkins_analysis import Pep8BuildsAnalysis
import exceptions
import re
import jenkins as jen
import email_send


# Create your views here.
def index(request):

    return render(
        request,
        "tables.html",
    )


def write_log(msg):
    with open('/tmp/analyze.log', 'a') as fd:
        fd.write(msg)


def builds(request):
    job_name = "tempest_run"
    params = request.GET
    job_name = params["job_name"] or "tempest_run"

    limit = int(params.get("limit", 10))
    if limit == 0:
        limit = 10

    page = int(params.get("page", 1))
    skip = (page-1) * limit

    builds_result = BuildsResult()
    query = {"job_name": job_name}
    total_count = builds_result.count(query)
    builds = builds_result.find(query, skip, limit)
    builds_list = []
    for build in builds:
        build["_id"] = "%s" % build["_id"]
        builds_list.append(build)

    resp = {
        "code": 0,
        "msg": "ok",
        "builds": builds_list,
        "total_count": total_count,
        "limit": limit
    }

    response = HttpResponse(json.dumps(resp), content_type="application/json")
    return response


def jobs(request):
    builds_result = BuildsResult()
    jobs = builds_result.jobs()
    jobs_list = []
    jenkins_url = "http://dev.ci.cpt.com:8080"
    username = None
    password = None
    job_names = []
    client = jen.Jenkins(jenkins_url, username, password)
    for job in jobs:
        new_job = {}
        try:
            job_info = client.get_job_info(job)
        except Exception:
            continue
        new_job["description"] = job_info["description"]
        new_job["job_name"] = job
        jobs_list.append(new_job)
    resp = {
        "code": 0,
        "msg": "ok",
        "jobs": jobs_list
    }
    response = HttpResponse(json.dumps(resp), content_type="application/json")
    return response


def sub_email(request):
    params = request.GET
    id = params.get("id")
    if id == None:
        raise exceptions.AttributeError, "id is None"

    email_db = Email()
    email_db.sub_email(id)

    resp = {
        "code": 0,
        "msg": "ok",
    }
    response = HttpResponse(json.dumps(resp), content_type="application/json")
    return response


def unsub_email(request):
    params = request.GET
    id = params.get("id")
    if id == None:
        raise exceptions.AttributeError, "id is None"

    email_db = Email()
    email_db.unsub_email(id)

    resp = {
        "code": 0,
        "msg": "ok",
    }
    response = HttpResponse(json.dumps(resp), content_type="application/json")
    return response

def notify_by_email(request):
    params = request.GET
    job_name = params.get("job_name", "physical_smoke_tempest_run")
    build_num = params.get("build_num", None)
    jenkins_url = "http://dev.ci.cpt.com:8080"

    if job_name is None or build_num is None:
        return HttpResponse(json.dumps([]), content_type="application/json")
    if not re.search("tempest", job_name):
        raise exceptions.AttributeError, "job_name error"
    if not re.search("^[0-9]+$", build_num):
        raise exceptions.AttributeError, "build_num is not numbers"
    build_num = int(build_num)

    tempest = TempestBuildsAnalysis(jenkins_url)
    msg = "ok"
    try:
        info_html = tempest.get_model_info_html(job_name, build_num)
    except Exception as ex:
        msg = ex
        resp = {
            "code": 0,
            "msg": msg,
        }
        response = HttpResponse(json.dumps(resp), content_type="application/json")
        return response

    build_info = tempest.get_build_info(job_name, build_num)
    if not build_num:
        msg = "job_name(%s)-build_num(%d), get build info " \
              "failed!" % (job_name, build_num)
        resp = {
            "code": 0,
            "msg": msg,
        }
        response = HttpResponse(json.dumps(resp), content_type="application/json")
        return response

    sub = "冒烟结果展示（包号（%s）- %s)"
    sub = sub.decode('utf-8')
    sub = sub % (build_info["package_version"], build_info["sf_version"])

    email_db = Email()
    email_db.find()
    mailto_list = ["%s@sangfor.com" % one['id'] for one in email_db.find()]
    write_log("+++sf, mailto_list = %s"% mailto_list)

    if mailto_list:
        email_send.send_html_email(mailto_list=mailto_list, sub=sub,
                                   msg=info_html)

    resp = {
        "code": 0,
        "msg": "ok",
    }
    response = HttpResponse(json.dumps(resp), content_type="application/json")
    return response

def tempest_models_info(request):
    """
    Get the testcases's info of each model
    :param request:
    :return:
    """
    params = request.GET
    job_name = params.get("job_name", "physical_smoke_tempest_run")
    build_num = params.get("build_num", None)
    jenkins_url = "http://dev.ci.cpt.com:8080"

    if job_name is None or build_num is None:
        return HttpResponse(json.dumps([]), content_type="application/json")
    if not re.search("tempest", job_name):
        raise exceptions.AttributeError, "job_name error"
    if not re.search("^[0-9]+$", build_num):
        raise exceptions.AttributeError, "build_num is not numbers"
    build_num = int(build_num)

    tempest = TempestBuildsAnalysis(jenkins_url)
    model_info = tempest.get_model_info(job_name, build_num)
    
    resp = {
        "code": 0,
        "msg": "ok",
        "model_info": model_info
    }
    response = HttpResponse(json.dumps(resp), content_type="application/json")
    return response


def tempest_test_cases(request):
    params = request.GET
    job_name = params.get("job_name", "tempest_run")
    build_num = params.get("build_num", None)
    result = params.get("result", "FAILED")

    jenkins_url = "http://dev.ci.cpt.com:8080"

    if job_name is None or build_num is None:
        return HttpResponse(json.dumps([]), content_type="application/json")
    if not re.search("tempest", job_name):
        raise exceptions.AttributeError, "job_name error"
    if not re.search("^[0-9]+$", build_num):
        raise exceptions.AttributeError, "build_num is not numbers"

    tempest = TempestBuildsAnalysis(jenkins_url)
    test_cases = tempest.get_testcases_name(job_name, build_num, result)

    response = HttpResponse(test_cases, content_type="application/text")
    return response


def update_results(request):
    jenkins_url = "http://dev.ci.cpt.com:8080"
    username = None
    password = None
    job_names = []
    client = jen.Jenkins(jenkins_url, username, password)
    jobs = client.get_jobs()
    for job in jobs:
        job_names.append(job["name"])

    for job_name in job_names:
        jenkins = None
        if re.search("tempest_run$", job_name):
            jenkins = TempestBuildsAnalysis(jenkins_url)
        elif re.search("ut_run$", job_name):
            jenkins = UnittestBuildsAnalysis(jenkins_url)
        elif re.search("pep8_run$", job_name):
            jenkins = Pep8BuildsAnalysis(jenkins_url)
        else:
            continue

        jenkins.analyze([job_name])
        resp = {
            "code": 0,
            "msg": "ok"
        }
    response = HttpResponse(json.dumps(resp), content_type="application/json")
    return response


def latest_package_version(request):
    builds_result = BuildsResult()
    build = builds_result.latest_pkg_nums()
    package_version = build["package_version"]
    resp = {
        "code": 0,
        "msg": "ok",
        "package_version": package_version
    }
    response = HttpResponse(json.dumps(resp), content_type="application/json")
    return response
