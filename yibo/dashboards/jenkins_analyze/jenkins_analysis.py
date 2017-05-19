# -*- coding: utf-8 -*-
import jenkins as jen
from pymongo import MongoClient
import re
import time

from models import BuildsResult

def write_log(msg):
    with open('/tmp/analyze.log', 'a') as fd:
        fd.write(msg)

class DBCon(object):
    def __init__(self,
                 host="mongodb.cpt.com", #200.200.177.11
                 user="root",
                 password="root",
                 port=27017,
                 db_name="jenkins",
                 collection_name="job"
                 ):
        self.client = MongoClient(host, int(port))
        self.db = self.client[db_name]
        self.collection = self.db[collection_name]


class BaseBuildsAnalysis(object):
    def __init__(self, jenkins_url, username=None, password=None):
        self.jenkins_url = jenkins_url
        self.jenkins = jen.Jenkins(self.jenkins_url, username, password)
        self.jobs = self.jenkins.get_jobs()
        self.db_con = DBCon(db_name="jenkins", collection_name="builds")
        self.collection = self.db_con.collection

    def _get_build_nums(self, builds):
        build_nums = []
        if builds is None:
            return build_nums

        for build in builds:
            build_nums.append(build["number"])
        return build_nums

    def analyze(self, job_names=[]):
        for job in self.jobs:
            # get the job info
            job_name = job["name"]
            if job_name not in job_names:
                continue
            job_info = self.jenkins.get_job_info(job_name)

            #get the build nums
            last_build = job_info["lastBuild"]
            last_build_num = last_build.get("number", 0)
            build_nums = []
            # the builds in job_info only return 100 builds
            # if last_build is not None:
                # builds = job_info["builds"]
                # build_nums = self._get_build_nums(builds)
            # else:
            #    build_nums = [0]
            if last_build_num != 0:
                build_nums = range(1, last_build_num + 1)
            else:
                build_nums = [0]

            # analyze the builds
            nums_not_in_db = self.get_not_analysis_builds(job_name, build_nums)
            builds_result = self._analyze(job_name, nums_not_in_db)

            #if name == "testx":
            #    import pdb
            #    pdb.set_trace()

    def get_not_analysis_builds(self, job_name, build_nums):
        """
        Get the build numbers which are not analuyzed

        :param job_name: the name of job in jenkins
        :param build_nums: the list of the build number
        :return: list of the build nums which are not analyzed
        """
        
        builds_in_db = self.db_con.collection.find({"job_name":job_name})
        
        build_nums_in_db = []
        for build in builds_in_db:
            build_num = build["build_num"]
            build_nums_in_db.append(build_num)

        nums_not_in = []
        for num in build_nums:
            if num in build_nums_in_db:
                continue
            else:
                nums_not_in.append(num)

        return nums_not_in

    def _success_percent(self, success_count, total_count):
        success_percent = 0.0
        if total_count != 0:
            success_percent = success_count * 100.0 / total_count
        success_percent = float("%0.2f" % success_percent)
        return success_percent

    def _fail_percent(self, failed_count, total_count):
        return self._success_percent(failed_count, total_count)     
    
    def _skip_percent(self, skip_count, total_count):
        return self._success_percent(skip_count, total_count)

    def _not_run_reason(self, content):
        """
        :param content: the output of the build
        """
        reason = "unknown reason"
        #FATAL: channel is already closed
        #hudson.remoting.ChannelClosedException: channel is already closed
        #could not install deps [-r/opt/ceilometer/requirements.txt, -r/opt/ceilometer/test-requirements.txt]
        
        slave_channel_close_error_reg = "FATAL:\s+channel\s+is\s+already\s+closed"
        java_io_exception_reg = "Connection\s+was\s+broken:\s+java\.io\.EOFException"
        downloading_error_reg = "could\s+not\s+install\sdeps"
        downloadings = re.findall(downloading_error_reg, content)

        if len(downloadings) >= 1:
            return "install deps failed"
        if re.search(slave_channel_close_error_reg, content):
            return "channel closed before job finished error"
        elif re.search(java_io_exception_reg, content):
            return "only Connection was broken"
        return reason


class TempestBuildsAnalysis(BaseBuildsAnalysis):
    def __init__(self, jenkins_url, username=None, password=None, job_names=[]):
        super(TempestBuildsAnalysis, self).__init__(jenkins_url, username, password)
        self.job_names = job_names

    def get_model_info(self, job_name, build_num=0):
        """
        Get the model info of the build_nums

        :param job_name: the name of the job
        :param build_nums: the builds's number of the job
        :return models_infos: a list of models_info which are got from self._models_info function
        """

        models_info = {}
        try:
            output = self.jenkins.get_build_console_output(job_name, build_num)
            lines = output.split("\n")
            testcases = self._all_testcases(lines)
            models_info = self._models_info(testcases)
        except jen.NotFoundException:
            models_info ={
                "job_name": job_name,
                "build_num": build_num,
                "models": {},
                "reason": "NotFoundException"
            }

        return models_info

    def get_build_info(self, job_name, build_num=0):
        query = {"job_name": job_name, "build_num": build_num}
        builds_result = BuildsResult()
        builds = builds_result.find(query=query)
        if (builds.count < 1):
            return None
        build = builds[0]
        return build

    def get_model_info_html(self, job_name, build_num=0):
        model_info = self.get_model_info(job_name, build_num)
        known_info = model_info.get("known")
        if known_info is None:
            return None

        build = self.get_build_info(job_name, build_num)
        if not build:
            raise Exception("job_name(%s)-build_num(%d), get build info "
                            "failed!" % (job_name, build_num))

        body = '<html><body bgcolor="#E6EFA">'

        header_table = '<table width="1000" border="0" cellspacing="0" ' \
                       'cellpadding="4">'

        header_table = header_table + '<tr bgcolor="#F0FFFF" height="20" ' \
                    'style="font-size:14px">'

        header = "<td>构建</td>" + \
                "<td>Version</td>" + \
                "<td>包号</td>" + \
                "<td>耗时</td>" + \
                "<td>结果</td>" + \
                "<td>原因</td>" + \
                "<td>成功</td>" + \
                "<td>跳过数</td>" + \
                "<td>失败</td>" + \
                "<td>用例数</td>" + \
                "<td>超时20s</td>"

        if not isinstance(header, unicode):
            header = header.decode('utf-8')

        success_percent = build["success_percent"] + build["skip_percent"]
        duration = build["duration"] / 1000
        duration_sec = int(duration % 60)
        duration_min = int(duration / 60)

        header_table = header_table + header
        header_table = header_table + '</tr>'
        info ="<tr><td>%d</td><td>%s</td><td>%d</td><td>%dm%ds</td><td>%s" \
              "</td" \
              "><td>%s</td><td>%s</td><td>%d</td><td>%d</td><td>%d</td><td" \
              ">%d</td></tr>" % (build["build_num"], build["sf_version"],
                            build["package_version"], duration_min,
                            duration_sec, build["result"],
                            build["not_run_reason"], success_percent,
                            build["skip_count"], build["fail_percent"],
                            build["total_count"], build["timeout_count"])

        if not isinstance(info, unicode):
            info = info.decode('utf-8')

        header_table = header_table + info + '</table>'

        mod_info = '<br />模块详情信息如下：'

        if not isinstance(mod_info, unicode):
            mod_info = mod_info.decode('utf-8')

        str = '<table width="1000" border="0" cellspacing="0" cellpadding="4">'
        if not isinstance(str, unicode):
            str = str.decode('utf-8')
        str = str + '<tr bgcolor="#CECFAD" height="20" ' \
                    'style="font-size:14px">'

        cur_str = '<td>模块</td>' + '<td>用例数</td>' + \
              '<td>成功数</td>' \
              + '<td>失败数</td>' + '<td>跳过数</td>'
        if not isinstance(cur_str, unicode):
            write_log("+++sf, unicode 2")
            cur_str = cur_str.decode('utf-8')
        str = str + cur_str
        str = str + '</tr>'
        keys =  known_info.keys()
        keys.sort()
        for p in keys:
            count = known_info[p]["count"]
            success_count = known_info[p]["success"]
            fail_count = known_info[p]["fail"]
            skip_count = known_info[p]["skip"]

            str = str + "<tr>"
            str = str + "<td>%s</td><td>%d</td><td>%d</td><td>%d</td><td>%d" \
                        "</td>" % (p, count, success_count, fail_count, skip_count)

            str = str + "</tr>"
        str = str + '</table>'

        xiangqing = '<br /><br />*官网数据<a href="http://www.cpt.com:8004/jenkins_analyze" \
                             "/">详情>></a>'

        if not isinstance(xiangqing, unicode):
            xiangqing = xiangqing.decode('utf-8')

        sub_info = '<br /><br /><font color="#dd0000">订阅请发送：</font>' \
                   'http://www.cpt.com:8004/jenkins_analyze/sub_email?id' \
                   '=90503，90503换成你的工号'
        unsub_info = '<br /><font color="#dd0000">退订请发送：</font>' \
                       'http://www.cpt.com:8004/jenkins_analyze/unsub_email' \
                     '?id=90503，90503换成你的工号'
        ad_info = '<br /><br /><font ' \
                  'color="#00dddd"><strong>广告招商中---欢迎您的加盟。</font>' \
                  '</strong>请发送email：90503@sangfor.com'

        if not isinstance(sub_info, unicode):
            sub_info = sub_info.decode('utf-8')
        if not isinstance(unsub_info, unicode):
            unsub_info = unsub_info.decode('utf-8')
        if not isinstance(ad_info, unicode):
            ad_info = ad_info.decode('utf-8')

        body = body + header_table + mod_info + str + xiangqing + sub_info + \
               unsub_info + ad_info
        body = body + "</body></html>"
        return body

    def get_testcases_name(self, job_name, build_num=0, result="FAILED"):
        testcase_name = ""
        try:
            build_num = int(build_num)
            output = self.jenkins.get_build_console_output(job_name, build_num)
            lines = output.split("\n")
            testcases = self._all_testcases(lines)
            names = self._fail_testcases_name(testcases, result)
            testcase_name = "[job name]:%s\n" % job_name
            testcase_name += "[build num]:%s\n" % build_num
            testcase_name += "[names]:\n%s" % "\n".join(names)

        except jen.NotFoundException:
            testcase_name =  "[job name]:%s\n" % job_name
            testcase_name += "[build num]:%s\n" % build_num
            testcase_name += "[names]:NONE\n"
            testcase_name += "reason:NotFoundException"

        return testcase_name

    def _models_info(self, testcases):
        """
        Get the models info of the testcases

        :param testcases:the testcases info which are
        got from _all_testcases function
        :return models: a dict, the strustrue is as follows:
            {
                "known":{# the model already known and their count, 
                    "tempest.api.compute": {
                        "count": 1,
                        "success": 2,
                        "fail": 3
                    },
                    #the key is model name, the value is count of all/succ/fail
                    "tempest.api.network": {},
                    ...
                }, 
                "unkonwn":[# the testcases which belong to no models known
                    "tempest.api",
                    "tempest.cmd.xxx.xxx",
                    ....
                ]
            }
        """
        models = {}
        unknown_models = []
        for testcase in testcases:
            testcase_name = testcase["name"]

            if re.search("^tempest\.api", testcase_name):
                temp = re.findall("tempest\.api\.[0-9a-zA-Z_]*",
                                  testcase_name)
                if len(temp) == 1:
                    model = temp[0]
                    if models.has_key(model):
                        models[model]["count"] += 1
                    else:
                        models[model] = {}
                        models[model]["count"] = 1
                        models[model]["success"] = 0
                        models[model]["fail"] = 0
                        models[model]["skip"] = 0
                        models[model]['fail_cast'] = []

                    result = testcase["result"]
                    if result == "ok":
                        models[model]["success"] += 1
                    elif result == "SKIPPED":
                        models[model]["skip"] += 1
                    else:
                        models[model]["fail"] += 1
                        models[model]['fail_cast'].append(testcase['testcase'])
                else:
                    unknown_models.append(testcase_name)
            elif re.search("^tempest\.sf_scenario", testcase_name):
                temp = re.findall("tempest\.sf_scenario",
                                  testcase_name)
                if len(temp) == 1:
                    model = temp[0]
                    if models.has_key(model):
                        models[model]["count"] += 1
                    else:
                        models[model] = {}
                        models[model]["count"] = 1
                        models[model]["success"] = 0
                        models[model]["fail"] = 0
                        models[model]["skip"] = 0
                        models[model]['fail_cast'] = []

                    result = testcase["result"]
                    if result == "ok":
                        models[model]["success"] += 1
                    elif result == "SKIPPED":
                        models[model]["skip"] += 1
                    else:
                        models[model]["fail"] += 1
                        models[model]['fail_cast'].append(testcase['testcase'])
                else:
                    unknown_models.append(testcase_name)
            else:
                unknown_models.append(testcase_name)
        models_info = {
            "known": models,
            "unkwon": unknown_models
        }
        return models_info

    def _analyze(self, job_name, nums_not_in_db):
        for num in nums_not_in_db:
            b_info = {}
            try:
                b_info = self.jenkins.get_build_info(job_name, num)
            except jen.NotFoundException:
                build_info = {
                    "jenkins_url": b_info.get("url"),
                    "job_name": job_name,
                    "build_num": num,
                    "result": "Unkown",
                    "not_run_reason": "DeleteBuilds",
                    "total_count": 0,
                    "success_count": 0,
                    "failed_count": 0,
                    "skip_count": 0,
                    "success_percent": 0,
                    "fail_percent": 0,
                    "skip_percent": 0,
                    "timeout_count": 0,
                    "build_time": 0,
                    "duration": 0
                }
                self.collection.insert_one(build_info)
                continue

            building = b_info["building"]
            if building:
                continue

            build_time = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(int(b_info["timestamp"]/1000)))#b_info["timestamp"]
            duration = b_info["duration"]
            output = self.jenkins.get_build_console_output(job_name, num)
            lines = output.split("\n")
            
            testcases = self._all_testcases(lines)
            success_count = self._success_testcase_count(testcases)
            skip_count = self._skip_testcase_count(testcases)
            #failed_count = self._failed_testcase_count(lines)
            failed_count = self._fail_testcase_count(testcases)
            total_count = success_count + failed_count + skip_count
            success_percent = self._success_percent(success_count, total_count)
            fail_percent = self._fail_percent(failed_count, total_count)
            skip_percent = self._skip_percent(skip_count, total_count)
            timeout_count = self._timeout_count(testcases)
            package_version = self._package_version(lines)
            sf_version = self._sf_version(lines)

            result = ""
            not_run_reason = ""
            if success_percent + skip_percent >=100:
                result = "PASSED"
            elif total_count == 0:
                result = "NotRun"
                not_run_reason = self._not_run_reason(output) 
            else:
                result = "FAILED"

            build_info = {
                "jenkins_url": b_info["url"],
                "job_name": job_name,
                "build_num": num,
                "result":result,
                "not_run_reason": not_run_reason,
                "total_count": total_count,
                "success_count": success_count,
                "failed_count": failed_count,
                "skip_count": skip_count,
                "success_percent": success_percent,
                "fail_percent": fail_percent,
                "skip_percent": skip_percent,
                "timeout_count": timeout_count,
                "build_time": build_time,
                "duration": duration,
                "package_version": package_version,
                "sf_version": sf_version
            }

            self.collection.insert_one(build_info)

    def _not_run_reason(self, output):
        not_run_reason = "Unkown"
        flag = "deploy openstack faild"
        creat_node_fail_flag = "create node faild"
        if flag in output:
            not_run_reason = "deploy failed"
        elif creat_node_fail_flag in "create node faild":
            not_run_reason = "create node failed"
        return not_run_reason

    def _success_testcase_count(self, testcases, ret="ok"):
        count = 0
        if testcases is None:
            count = 0
        for testcase in testcases:
            if testcase["result"] == ret:
                count += 1
        return count


    def _skip_testcase_count(self, testcases, ret="SKIPPED"):
        return self._success_testcase_count(testcases, ret)

    def _fail_testcase_count(self, testcases, ret="FAILED"):
        return self._success_testcase_count(testcases, ret)

    def _success_testcases_name(self, testcases, ret="ok"):
        testcases_name = []
        for testcase in testcases:
            if testcase["result"] == ret:
                testcases_name.append(testcase["name"])

        return testcases_name

    def _fail_testcases_name(self, testcases, ret="FAILED"):
        return self._success_testcases_name(testcases, ret)

    # discarded
    def _failed_testcase_count(self, content):
        """
        :param content: a list, lines of output
        """

        failed_count = 0

        # The flag is -> 'Failed 1 tests - output below:'
        reg = re.compile("Failed\s+[0-9]+\s+tests\s+-\s+output\s+below:")
        for line in content:
            if reg.search(line):
                failed_count = re.findall("[0-9]+", line)[0]
                break
        if failed_count is None:
            failed_count = 0
        else:
            failed_count = int(failed_count)
        return failed_count

    def _all_testcases(self, content):
        """
        :param content: a list, lines of output
        """
        testcases = []


        for line in content:
            testcase_name_reg = "tempest[0-9a-zA-Z._]+"
            testcase_time_reg = "\[[0-9.s]+\]"
            testcase_result_reg = "\.{3}\s*"
            skip_flag = "SKIPPED"
            fail_flag = "FAILED"
            ok_flag = "ok"
            reg = re.compile("^\{[0-9]+\}\s+(setUpClass)?\s*(\()?%s(\))?\s+(%s)?\s*%s(%s|%s|%s)*" % 
                (testcase_name_reg, testcase_time_reg, testcase_result_reg, skip_flag, fail_flag, ok_flag))

            testcase_time = None
            testcase_name = None
            testcase_result = None
            testcase_skip_reason = None
            
            if reg.search(line):
                testcase_name = re.findall(testcase_name_reg, line)[0]
                
                testcase_result = re.split(testcase_result_reg, line)
                testcase_result = testcase_result[-1].replace("\n", "")
                if skip_flag in testcase_result:
                    testcase_time = 0.0
                    testcase_skip_reason = re.split(skip_flag, testcase_result)[-1]
                    testcase_skip_resaon = re.sub("^:", "", testcase_skip_reason)
                    testcase_result = skip_flag
                elif fail_flag in testcase_result:
                    testcase_time = re.findall(testcase_time_reg, line)[0]
                    testcase_time = re.sub("[\[\]s]", "", testcase_time)
                else:
                    testcase_time = re.findall(testcase_time_reg, line)[0]
                    testcase_time = re.sub("[\[\]s]", "", testcase_time)
                    
                testcase_info = {
                    "name": testcase_name,
                    "exec_time": testcase_time,
                    "result": testcase_result,
                    "skip_reason": testcase_skip_reason,
                    "testcase": line,
                }
                testcases.append(testcase_info)

        return testcases

    def _timeout_count(self, testcases, standard_time=20):
        timeout_count = 0
        if testcases is None:
            return timeout_count
        for testcase in testcases:
            exec_time = 0
            if testcase["exec_time"] is not None and exec_time >= standard_time:
                timeout_count += 1
        return timeout_count

    def _total_time(self, content):
        pass

    def _package_version(self, lines):
        package_version = 0
        for line in lines:
            if "[SANGFOR_PACKAGE_BUILD_VERSION]" in line:
                package_version = line.split(
                    "[SANGFOR_PACKAGE_BUILD_VERSION]")[-1]
                package_version = int(package_version)
                break
        return package_version

    def _sf_version(self, lines):
        sf_version = ""
        for line in lines:
            if "[SANGFOR_VERSION]" in line:
                sf_version = line.split("[SANGFOR_VERSION]")[-1]
                sf_version = re.sub("\n", "", sf_version)
                break

        return sf_version


class UnittestBuildsAnalysis(BaseBuildsAnalysis):
    def __init__(self,
                 jenkins_url,
                 username=None,
                 password=None,
                 job_names=[]):
        super(UnittestBuildsAnalysis, self).__init__(
            jenkins_url,
            username,
            password
        )
        self.job_names = job_names

    def _analyze(self, job_name, nums_not_in_db):
        for num in nums_not_in_db:
            b_info = {}
            try:
                b_info = self.jenkins.get_build_info(job_name, num)
            except jen.NotFoundException:
                build_info = {
                    "jenkins_url": b_info.get("url"),
                    "job_name": job_name,
                    "build_num": num,
                    "result": "Unkown",
                    "not_run_reason": "DeleteBuilds",
                    "total_count": 0,
                    "success_count": 0,
                    "skip_count": 0,
                    "failed_count": 0,
                    "success_percent": 0,
                    "fail_percent": 0,
                    "skip_percent": 0,
                    "maxtime": 0,
                    "total_time": 0,
                    "build_time": 0,
                    "duration": 0
                }
                self.collection.insert_one(build_info)
                continue

            building = b_info["building"]
            if building:
                continue
            build_time = time.strftime(
                "%Y-%m-%d %H:%M:%S",
                time.localtime(int(b_info["timestamp"]/1000)))
            duration = b_info["duration"]
            output = self.jenkins.get_build_console_output(job_name, num)
            results = self._get_results(output)
            
            result = results["result"]
            not_run_reason = results["not_run_reason"]
            total_count = results["total_count"]
            skip_count = results["skip_count"]
            failed_count = results["failed_count"]
            success_count = total_count - failed_count - skip_count
            maxtime = results["maxtime"]
            total_time = results["total_time"]
  
            success_percent = self._success_percent(success_count, total_count)
            fail_percent = self._fail_percent(failed_count, total_count)
            skip_percent = self._skip_percent(skip_count, total_count)
            

            build_info = {
                    "jenkins_url": b_info["url"],
                    "job_name": job_name,
                    "build_num": num,
                    "result": result,
                    "not_run_reason": not_run_reason,
                    "total_count": total_count,
                    "success_count": success_count,
                    "skip_count": skip_count,
                    "failed_count": failed_count,
                    "success_percent": success_percent,
                    "fail_percent": fail_percent,
                    "skip_percent": skip_percent,
                    "maxtime": maxtime,
                    "total_time": total_time,
                    "build_time": build_time,
                    "duration": duration
            }
            self.collection.insert_one(build_info)

    def _get_results(self, content):
        lines = content.split("\n")
        results ={}
        result = "NotRun"
        not_run_reason = ""
        total_count = 0
        skip_count = 0
        failed_count = 0
        maxtime = 0
        total_time = 0

        # Ran 66 tests in 0.426s
        # FAILED (id=0, failures=6, skips=614)
        # PASSED (id=0, skips=1)
        count_time_reg = "^Ran\s+[0-9]+\s+tests\s+in\s+[0-9.]+s"
        failures_reg = "failures=[0-9]+"
        skips_reg = "skips=[0-9]+"
        result_reg = \
            "^(FAILED|PASSED){1}\s*\(id=[0-9]+(,\s+)?(%s)?(,\s+)?(%s)?\)" %\
            (failures_reg, skips_reg)
        slowest_testcase_flag_reg = "Slowest\s+Tests.*Test id"

        for line in lines:
            if re.search(count_time_reg, line):
                temp = re.split("tests\s+in", line)
                total_count = re.findall("[0-9.]+", temp[0])[0]
                total_count = int(total_count)
                total_time = re.sub("[s\s]", "", temp[1])

            if re.search(result_reg, line):
                if re.search("PASSED", line):
                    result = "PASSED"
                if re.search("FAILED", line):
                    result = "FAILED"
                if re.search(failures_reg, line):
                    failed_count = re.findall(failures_reg, line)[0]
                    failed_count = failed_count.split("=")[-1]
                    failed_count = int(failed_count)
                if re.search(skips_reg, line):
                    skip_count = re.findall(skips_reg, line)[0]
                    skip_count = skip_count.split("=")[-1]
                    skip_count = int(skip_count)

        if result is "NotRun":
            not_run_reason = self._not_run_reason(content)

        if re.search(slowest_testcase_flag_reg, content):
            slowest_test_cases = re.split()(
                slowest_testcase_flag_reg, content
            )[-1]
            maxtime = self._testcase_timeout(slowest_test_cases)
        results = {
            "result": result, 
            "not_run_reason": not_run_reason,
            "total_count": total_count,
            "skip_count": skip_count,
            "failed_count": failed_count,
            "maxtime": maxtime,
            "total_time": total_time
        }

        return results

    def _testcase_timeout(self, slowest_test_cases):
        """
        :param conent: part of the output of the build
        """
        lines = slowest_test_cases.split("\n")
        slowest_testcase_reg = "\s+[0-9.]+$"
        maxtime = 0
        for line in lines:
            if re.search(slowest_testcase_reg, line):
                testcase_time = re.findall(slowest_testcase_reg, line)[0]
                if maxtime < float(testcase_time):
                    maxtime = float(testcase_time)

        return maxtime


class Pep8BuildsAnalysis(BaseBuildsAnalysis):
    def __init__(self,
                 jenkins_url,
                 username=None,
                 password=None,
                 job_names=[]):
        super(Pep8BuildsAnalysis, self).__init__(
            jenkins_url, username, password)
        self.job_names = job_names

    def _analyze(self, job_name, nums_not_in_db):
        for num in nums_not_in_db:
            b_info = {}
            try:
                b_info = self.jenkins.get_build_info(job_name, num)
                #write_log("+++sf, pep8 %s" % b_info)
            except jen.NotFoundException:
                build_info = {
                    "jenkins_url": b_info.get("url"),
                    "job_name": job_name,
                    "build_num": num,
                    "result": "Unkown",
                    "not_run_reason": "DeleteBuilds",
                    "check_failed_count": 0,
                    "build_time": 0,
                    "duration": 0
                }
                self.collection.insert_one(build_info)
                continue

            building = b_info["building"]
            if building:
                continue
            build_time = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(int(b_info["timestamp"]/1000)))#b_info["timestamp"]
            duration = b_info["duration"]
            output = self.jenkins.get_build_console_output(job_name, num)
            results = self._get_result(output)
            result = results["result"]
            not_run_reason = results["not_run_reason"]
            check_failed_count = results["check_failed_count"]
            build_info = {
                    "jenkins_url": b_info["url"],
                    "job_name": job_name,
                    "build_num": num,
                    "result": result,
                    "not_run_reason": not_run_reason,
                    "check_failed_count": check_failed_count,
                    "build_time": build_time,
                    "duration": duration
                }
            self.collection.insert_one(build_info)

    def _get_result(self, content):
        # pep8: commands succeeded
        # pep8: commands failed
        lines = content.split("\n")
        results ={}
        result = "NotRun"
        not_run_reason = ""
        failed_count = 0

        pep8_success_reg = "pep8:\s+commands\s+succeeded"
        pep8_fail_reg = "pep8:\s+commands\s+failed"

        if re.search(pep8_success_reg, content):
            result = "PASSED"
        if re.search(pep8_fail_reg, content):
            result = "FAILED"
            failed_count = self._get_failed_count(lines)
        if result is "NotRun":
            not_run_reason = self._not_run_reason(content)

        results = {
            "result": result, 
            "not_run_reason": not_run_reason,
            "check_failed_count": failed_count
        }

        return results

    def _get_failed_count(self, lines):
        # "     ^     "
        failed_reg = "^\s*\^\s*$"
        count = 0
        for line in lines:
            if re.search(failed_reg, line):
                count += 1

        return count
        

jenkins_url = "http://dev.ci.cpt.com:8080"
username = None
password = None
job_names = []

"""
jenkins = jen.Jenkins(jenkins_url, username, password)
jobs = jenkins.get_jobs()
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
"""


# jenkins = TempestBuildsAnalysis(jenkins_url)
# job_names = ["tempest_run"]

# jenkins = UnittestBuildsAnalysis(jenkins_url)
# job_names = ["python-cplogclient_ut_run"]
# job_names = ["cplog_ut_run"]

# jenkins = Pep8BuildsAnalysis(jenkins_url)
# job_names = ["cplog_pep8_run"]
# job_names = ["ceilometer_pep8_run"]
# job_names = ["bjdevapi_pep8_run"]
# jenkins.analyze([job_name])

"""
job_name = "physical_smoke_tempest_run"
tempest = TempestBuildsAnalysis(jenkins_url)
model_info = tempest.get_model_info(job_name, [121])
import pdb
pdb.set_trace()
print "ok"
"""
