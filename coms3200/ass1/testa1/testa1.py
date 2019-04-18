#!/usr/bin/env python3
# COMS3200 a1 test suite
# USAGE: python3 testa1.py

import datetime
import time
import subprocess
import os


class TestFail(Exception):
    """Exception class thrown when a test fails """
    pass


class TestRunner:
    def __init__(self, lines):
        self._lines = lines

    @staticmethod
    def _assert(condition, message=""):
        if not condition:
            raise TestFail(message)

    @staticmethod
    def is_ip(ip):
        return ip.count(".") == 3 and all(i.isdigit() and 0 <= int(i) <= 255 for i in ip.split("."))

    @staticmethod
    def is_port(pt):
        return pt.isdigit() and int(pt) > 1024

    def _test_details_line(self, start, ip, port):
        line = next(self._lines)
        self._assert(line.upper().startswith(start + ":"), "Could not find {} in stdout".format(start.lower()))
        test_ip, test_port = line.upper().lstrip(start + ":").strip().split()
        if str(ip).upper() == "ANY_IP":
            self._assert(self.is_ip(test_ip), "Invalid {} ip addr".format(start.lower()))
        else:
            self._assert(test_ip == str(ip), "Incorrect {} ip addr".format(start.lower()))
        if str(port).upper() == "ANY_PORT":
            self._assert(self.is_port(test_port), "Invalid {} port".format(start.lower()))
        else:
            self._assert(test_port == str(port), "Incorrect {} port".format(start.lower()))

    def test_url(self, url):
        first_line = next(self._lines)
        self._assert(first_line.upper().startswith("URL REQUESTED:"), "Could not find URL in stdout")
        self._assert(first_line.upper().lstrip("URL REQUESTED:").strip() == url.upper(), "Incorrect URL")

    def test_info(self, cli_ip, cli_port, serv_ip, serv_port):
        self._test_details_line("CLIENT", cli_ip, cli_port)
        self._test_details_line("SERVER", serv_ip, serv_port)

    def _test_time(self, test_time, expected_time, type_):
        try:
            print(test_time)
            t_test = datetime.datetime.strptime(test_time, '%d/%m/%Y %H:%M:%S %Z')
        except ValueError:
            print(test_time)
            self._assert(False, "Could not decode timestamp for {}".format(type_.lower()))
            return
        if isinstance(expected_time, str):
            if "ANY" in expected_time:
                return
            t_expected = datetime.datetime.strptime(expected_time, '%d/%m/%Y %H:%M:%S %Z')
            self._assert(abs(t_expected.timestamp() - t_test.timestamp()) <= 60,
                         "Incorrect timestamp for {}".format(type_.lower()))
        else:
            self._assert(abs(time.time() - t_test.timestamp()) <= 60,
                         "Incorrect timestamp for {}".format(type_.lower()))

    def test_dates(self, mod_date, mod_time, time_exists=True):
        self._assert(next(self._lines).strip().upper() == "RETRIEVAL SUCCESSFUL", "Missing \"Retrieval successful\"")
        date_field = " ".join(next(self._lines).strip().split()[2:])
        self._test_time(date_field, time.time(), "access date")
        if time_exists:
            lm_field = " ".join(next(self._lines).strip().split()[2:])
            self._test_time(lm_field, mod_date + " " + mod_time + " AEST", "last modified")
        else:
            self._assert(next(self._lines).strip().upper() == "LAST MODIFIED NOT AVAILABLE",
                         "Missing \"Last modified not available\"")

    def test_https(self):
        self._assert(next(self._lines).strip().upper() == "HTTPS NOT SUPPORTED", "Missing \"HTTPS not supported\"")

    def test_err(self, code):
        self._assert(next(self._lines).strip().upper() == "RETRIEVAL FAILED ({})".format(code),
                     "Incorrect or missing error code")

    def test_redir(self, url, type_):
        self._assert(next(self._lines).upper().strip() == "RESOURCE {} MOVED TO {}".format(type_.upper(), url.upper()))

    def test_file(self, file_name):
        try:
            with open("output." + file_name.split(".")[1] if "." in file_name else "output", "r") as f:
                actual_contents = "".join(f.read().split())
        except FileNotFoundError:
            self._assert(False, "Resource could not be located")
            return
        with open("files/" + file_name, "r") as f:
            expected_contents = "".join(f.read().split())

        self._assert(actual_contents == expected_contents, "Resource output does not match expected output")

    def skip(self, count):
        for i in range(count):
            try:
                next(self._lines)
            except StopIteration:
                pass


class TestBlock:
    def __init__(self, id_, url):
        self._id = id_
        self._tests = []
        self._url = url
        self._lang = "py"

    def set_lang(self, lang):
        self._lang = lang

    def add(self, test):
        self._tests.append(test)
        return self

    def run(self):
        if self._lang == "py":
            if os.name == "nt":
                cmd = ["python", "assign1.py", self._url]
            else:
                cmd = ["python3.6", "assign1.py", self._url]
        elif self._lang == "java":
            cmd = ["java", "Assign1", self._url]
        elif self._lang == "c":
            cmd = ["./assign1", self._url]
        else:
            raise RuntimeError
        with subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE) as proc:
            out = proc.stdout.read().decode("UTF-8")
            err = proc.stderr.read().decode("UTF-8")
        if len(err) > 0:
            print("TEST {} | FAIL | {}".format(str(self._id).zfill(2), self._url))
            print("  Error thrown while executing program\n")
            return

        tr = TestRunner(i for i in out.split("\n"))
        upto = "a"
        toprint = ""
        final = True

        for test in self._tests:
            desc = test[0]
            if desc == "skip":
                tr.skip(int(test[1]))
                continue
            test_name = test[1]
            test_args = test[2:]
            result, message = self.run_single(test_name, test_args, tr)
            final = final and result
            if self._id < 10:
                toprint += " " * 5
            else:
                toprint += " " * 4
            toprint += str(self._id) + upto + " | "
            if result:
                toprint += "PASS | " + desc + "\n"
            else:
                toprint += "FAIL | " + desc + "\n"
                if message is not None:
                    toprint += " " * 7
                    toprint += message + "\n"
            upto = chr(ord(upto) + 1)
        toprint = "TEST {} | {} | {}\n".format(str(self._id).zfill(2), "PASS" if final else "FAIL", self._url) \
                  + toprint
        print(toprint)

    @staticmethod
    def run_single(name, args, tr):
        method = getattr(tr, name)
        try:
            method(*args)
        except TestFail as e:
            return False, e.args[0] if len(e.args) > 0 else None
        except StopIteration:
            return False, "Unexpected end of stdout"
        except:
            return False, "Unhandled exception in test script"
        return True, ""


def find_assignment_files():
    if os.path.isfile("./assign1.py"):
        print("Found main file assign1.py")
        return "py"
    elif os.path.isfile("./makefile") or os.path.isfile("./Makefile"):
        print("Found makefile")
        try:
            subprocess.check_output(["make"])
            if os.path.isfile("./Assign1.class"):
                print("Found class file Assign1.class")
                return "java"
            elif os.path.isfile("./assign1"):
                print("Found binary assign1")
                return "c"
            else:
                print("No executable file found after calling make - cannot test")
        except subprocess.CalledProcessError:
            print("Error thrown while executing makefile - cannot test")
    print("No assignment file or makefile found - cannot test")


# Here are the sample tests for the first assignment
TESTS = [
    TestBlock(1, "http://hob.uqcloud.net/coms3200/a1/test1.txt")
        .add(("Test URL", "test_url", "http://hob.uqcloud.net/coms3200/a1/test1.txt"))
        .add(("Test client/server info", "test_info", "ANY_IP", "ANY_PORT", "ANY_IP", "80"))
        .add(("Test dates", "test_dates", "15/03/2019", "19:00:57"))
        .add(("Test file output", "test_file", "test1.txt")),

    TestBlock(2, "http://hob.uqcloud.net/coms3200/a1/test2.js")
        .add(("Test URL", "test_url", "http://hob.uqcloud.net/coms3200/a1/test2.js"))
        .add(("Test client/server info", "test_info", "ANY_IP", "ANY_PORT", "ANY_IP", "80"))
        .add(("Test dates", "test_dates", "16/03/2019", "11:49:44"))
        .add(("Test file output", "test_file", "test2.js")),

    TestBlock(3, "http://hob.uqcloud.net/coms3200/a1/test3.css")
        .add(("Test URL", "test_url", "http://hob.uqcloud.net/coms3200/a1/test3.css"))
        .add(("Test client/server info", "test_info", "ANY_IP", "ANY_PORT", "ANY_IP", "80"))
        .add(("Test dates", "test_dates", "15/03/2019", "11:39:56"))
        .add(("Test file output", "test_file", "test3.css")),

    TestBlock(4, "http://hob.uqcloud.net/coms3200/a1/test4")
        .add(("Test URL", "test_url", "http://hob.uqcloud.net/coms3200/a1/test4"))
        .add(("Test client/server info", "test_info", "ANY_IP", "ANY_PORT", "ANY_IP", "80"))
        .add(("Test dates", "test_dates", "15/03/2019", "19:11:47"))
        .add(("Test file output", "test_file", "test4")),

    TestBlock(5, "http://hob.uqcloud.net/coms3200/a1/test5.html")
        .add(("Test URL", "test_url", "http://hob.uqcloud.net/coms3200/a1/test5.html"))
        .add(("Test client/server info", "test_info", "ANY_IP", "ANY_PORT", "ANY_IP", "80"))
        .add(("Test dates", "test_dates", "18/03/2019", "18:50:45"))
        .add(("Test file output", "test_file", "test5.html")),

    TestBlock(9, "http://hob.uqcloud.net/coms3200/a1/test9.txt")
        .add(("Test URL", "test_url", "http://hob.uqcloud.net/coms3200/a1/test9.txt"))
        .add(("Test client/server info", "test_info", "ANY_IP", "ANY_PORT", "ANY_IP", "80"))
        .add(("Test dates", "test_dates", "03/03/2019", "10:31:00"))
        .add(("Test file output", "test_file", "test9.txt")),

    TestBlock(11, "https://uq.edu.au/")
        .add(("Test URL", "test_url", "https://uq.edu.au/"))
        .add(("Test HTTPS", "test_https")),

    TestBlock(12, "http://hob.uqcloud.net/missing")
        .add(("Test URL", "test_url", "http://hob.uqcloud.net/missing"))
        .add(("Test client/server info", "test_info", "ANY_IP", "ANY_PORT", "ANY_IP", "80"))
        .add(("Test error code", "test_err", "404")),

    TestBlock(17, "http://hob.uqcloud.net/coms3200/a1/test17/")
        .add(("Test URL", "test_url", "http://hob.uqcloud.net/coms3200/a1/test17/"))
        .add(("Test client/server info", "test_info", "ANY_IP", "ANY_PORT", "ANY_IP", "80"))
        .add(("Test redirection to /coms3200/redir/test17.json", "test_redir", "http://hob.uqcloud.net/coms3200/redir/test17.json", "TEMPORARILY"))
        .add(("Test client/server info after redirection", "test_info", "ANY_IP", "ANY_PORT", "ANY_IP", "80"))
        .add(("Test dates", "test_dates", "15/03/2019", "13:51:40"))
        .add(("Test file output", "test_file", "test17.json")),

    TestBlock(18, "http://hob.uqcloud.net/coms3200/a1/test18/")
        .add(("Test URL", "test_url", "http://hob.uqcloud.net/coms3200/a1/test18/"))
        .add(("Test client/server info", "test_info", "ANY_IP", "ANY_PORT", "ANY_IP", "80"))
        .add(("Test redirection to HTTPS", "test_redir", "https://hob.uqcloud.net/coms3200/a1/test18/", "PERMANENTLY"))
        .add(("Test HTTPS", "test_https")),

    TestBlock(19, "http://hob.uqcloud.net/coms3200/a1/test19/")
        .add(("Test URL", "test_url", "http://hob.uqcloud.net/coms3200/a1/test19/"))
        .add(("Test client/server info 1", "test_info", "ANY_IP", "ANY_PORT", "ANY_IP", "80"))
        .add(("Test redirection to /next/", "test_redir", "http://hob.uqcloud.net/next/", "PERMANENTLY"))
        .add(("Test client/server info 2", "test_info", "ANY_IP", "ANY_PORT", "ANY_IP", "80"))
        .add(("Test redirection to /uhoh", "test_redir", "http://hob.uqcloud.net/uhoh", "TEMPORARILY"))
        .add(("Test client/server info 3", "test_info", "ANY_IP", "ANY_PORT", "ANY_IP", "80"))
        .add(("Test error code", "test_err", "404")),

]


def main():
    lang = find_assignment_files()
    if lang is None:
        return
    for test in TESTS:
        test.set_lang(lang)
        test.run()

if __name__ == "__main__":
    main()
