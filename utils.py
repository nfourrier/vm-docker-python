import threading
import pandas as pd
import numpy as np
import datetime as dt
import random
import pprint

import platform
import sys
import os
import subprocess
from subprocess import Popen, PIPE, call
from collections import defaultdict
import __main__

vmPrefix = ' -- '
is_py2 = sys.version[0] == '2'
if is_py2:
    import Queue as queue
else:
    import queue as queue

class vm(object):
    def __init__(self, machine='default'):
        self.machine = machine
        self.newCmd = ['docker-machine','ssh',machine,'\n']
        self.cmd = self.newCmd
        self.imagesList = self.imagesList()
        self.b_shell = False

    def run(self):
        print('{} running command ...'.format(vmPrefix))
        p = Popen(self.cmd, stdin=PIPE, stdout=PIPE, stderr=PIPE, shell=self.b_shell)
        error = 0
        while(p.poll() == None):
            A = p.stdout.readline()
            # print('stdout',len(A))
            B = p.stderr
            if(len(A) > 0):
                print(str(A))
        # print(B)
        for line in B:
            error = 1
            print(line)
        # while(p.poll()==None):
        #     B = p.stderr.readline()
        #     # print('stderr',len(B))
        #     if(len(B) > 0):
        #         error = 1
        #         print(str(B))

        if(error==0):
            print('{} end running command with success'.format(vmPrefix))
        else:
            print('{} end running command FAIL'.format(vmPrefix))

                # p = call(self.cmd, stdin=PIPE, stdout=None, stderr=PIPE, shell=self.b_shell)
        # if(p==0):
        #     print('{} end running command with success'.format(vmPrefix))
        # else:
        #     print('{} end running command FAIL'.format(vmPrefix))
        self.cmd = self.newCmd

    def command(self,inp):
        self.cmd = self.cmd + inp.split(" ") + ['\n']

    def isValid(self,container):
        return (container in self.imagesList)

    def imagesList(self):
        proc = subprocess.Popen(self.cmd+['docker',"images",'\n','exit'],
                        stdin=None,
                        stdout=subprocess.PIPE,
                        stderr=subprocess.PIPE,
                        )
        stdout_value, stderr_value = proc.communicate()
        return str(stdout_value)
        # p = call(self.cmd+['docker',"images",'\n','exit'], stdin=PIPE, stdout=PIPE, stderr=PIPE)

    def command_anaconda(self,pyScript,py=None):
        if(isinstance(py,type(None))):
            self.cmd = 'python {}'.format(pyScript)
        else:
            self.cmd = 'activate {} & python -u {}'.format(py,pyScript)
            # self.cmd = ['activate',py,'&','python',pyScript]
        self.b_shell = True

    def command_docker(self,container,pyScript,compiler='python'):
        if(not self.isValid(container)):
            print('{} invalid container name'.format(vmPrefix))
            sys.exit()
        print(os.getcwd())


        path = os.path.dirname(os.path.realpath(__main__.__file__))
        path = os.getcwd()

        # path = os.path.realpath(os.path.join(os.getcwd(), os.path.dirname(__file__)))
        if platform.system().lower().startswith("windows"):
            CACHE_FILE_FOLDER = os.environ['USERPROFILE']
            path = path.replace(CACHE_FILE_FOLDER,os.path.join('//c/Users',os.environ["USERNAME"]))
            path = path.replace('\\','/')
            path = path.replace(CACHE_FILE_FOLDER,os.path.join('//c/Users',os.environ["USERNAME"]))
            path = path.replace('\\','/')

        else:
            CACHE_FILE_FOLDER = os.environ.get("HOME")
        print(path)
        path = path.replace(CACHE_FILE_FOLDER,os.path.join('//c/Users',os.environ["USERNAME"]))
        path = path.replace('\\','/')
        print(path)
        pyScript = pyScript.replace('\\','/')
        print(pyScript)
        # print('//c/Users/myUsername/Documents/myCurrentWorkingFolder')/
        self.cmd = self.cmd + [
            'docker', 'run',
            '-v', '{}:/tmp'.format(path),
            # '-v', '//c/Users/myUsername/Documents/myCurrentWorkingFolder:/tmp',
            '-w', '/tmp',
            '-it',
            container,
            # 'python '+'testos.py',
            '{} {}'.format(compiler,pyScript),
            '\n',
            'exit',
            '\n',
            'docker', 'rm',
            '-v',
            '$(docker ps -a -q -f status=exited)'
        ]
        print(self.cmd)
        self.b_shell = False
