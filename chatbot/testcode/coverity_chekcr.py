import threading
import subprocess
from xml2markdown import parser

project_path = '/home/nahyeon/prototype/project/coverity_test'
coverity_path = '/home/nahyeon/prototype/project/coverity_test/build/reports/jacoco/test/jacocoTestReport.xml'

class CMD():
    CD_PROJECT = f'cd {project_path}'
    BUILD = 'gradle clean build'
    TEST = 'gradle test'

class CoverityChecker(threading.Thread):
    def __init__(self):
        pass
    
    def build(self):
        pass
    def test(self):
        pass
    def parse_build_result(self):
        pass
    def parse_coverity_result(self):
        return parse()
    def run(self):
        pass
    