#!/usr/bin/python

import sys
import re
import getopt

#C language string element analyser, concerned with 
#'\', '\x', '"'
SN_ENUM_INIT = 0
SN_ENUM_FOUND_SLASH = 1
SN_ENUM_NORMAL_STR = 2
class line_ele:
    def __init__(self, line, line_no = None):
        self.line_ana = []
        self.line_no = line_no
        if not line:
            return
        str_state = SN_ENUM_INIT
        tmp_ele = ""
        for i in range(0, len(line)):
            if line[i] == '\\':
                if str_state == SN_ENUM_INIT:
                    tmp_ele = line[i]
                    str_state = SN_ENUM_FOUND_SLASH
                elif str_state == SN_ENUM_NORMAL_STR:
                    self.line_ana.append(tmp_ele)
                    tmp_ele = line[i]
                    str_state = SN_ENUM_FOUND_SLASH
                elif str_state == SN_ENUM_FOUND_SLASH:
                    tmp_ele = tmp_ele + line[i]
                    self.line_ana.append(tmp_ele)
                    str_state = SN_ENUM_INIT
                else:
                    raise "unexpected stat machine"
            elif line[i] == '"':
                if str_state == SN_ENUM_INIT:
                    self.line_ana.append(line[i])
                elif str_state == SN_ENUM_FOUND_SLASH:
                    tmp_ele = tmp_ele + line[i]
                    self.line_ana.append(tmp_ele)
                    str_state = SN_ENUM_INIT
                elif str_state == SN_ENUM_NORMAL_STR:
                    self.line_ana.append(tmp_ele)
                    self.line_ana.append(line[i])
                    str_state = SN_ENUM_INIT
                else:
                    raise "unexpected state machine"
            else:
                if str_state == SN_ENUM_INIT:
                    tmp_ele = line[i]
                    str_state = SN_ENUM_NORMAL_STR 
                elif str_state == SN_ENUM_FOUND_SLASH:
                    tmp_ele = tmp_ele + line[i]
                    self.line_ana.append(tmp_ele)
                    str_state = SN_ENUM_INIT
                elif str_state == SN_ENUM_NORMAL_STR:
                    tmp_ele = tmp_ele + line[i]
                else:
                    raise "unexpect state machine"
        if str_state != SN_ENUM_INIT:
            self.line_ana.append(tmp_ele)

def get_string_from_line(line_e, instr):
    tmp_str = ""
    tmp_str_list = []
    for ele in line_e.line_ana:
        if ele != '"':
            if instr:
                tmp_str = tmp_str + ele
        else:
            if instr:
                tmp_str_list.append(tmp_str)
                tmp_str = ""
                instr = False
            else:
                instr = True
    if instr:
        tmp_str_list.append(tmp_str)
    return tmp_str_list, instr

#return a list
#[(line_no, string), ...]
def read_in_strings(file_name):
    line_list = []
    str_list = []
    with open(file_name, "r") as fh:
        line_no = 0
        for line in fh.readlines():
            line_no = line_no + 1
            line_e = line_ele(line[:-2], line_no)
            line_list.append(line_e)
    instr = False
    for line in line_list:
        line_str_list, instr = get_string_from_line(line, instr)
        if len(line_str_list) == 0:
            continue
        for line_str in line_str_list:
            str_list.append((line.line_no, line_str))
    return str_list

def precheck_delete_chinese(line):
    zhRe = re.compile(u'[\u4e00-\u9fa5]+')
    if zhRe.search(line[1].decode('utf-8')):
        return False
    return True

def pre_check(string_list):
    for line in string_list:
        if not precheck_delete_chinese(line):
            string_list.remove(line)

def check_file(fname, outfile_handle=None):
    #Read in file, and analyse string-list in it
    strl = read_in_strings(fname)
    if len(strl) == 0:
        return 0
    pre_check(strl)
    for line in strl:
        #do spelling check, and print error
        if not outfile_handle:
            print("line %d: [%s]" %(line[0], line[1]))

def print_help_info():
    print '''
Usage: %s [argument] [file...]      check specified file(s)'s spelling
Argument:
    [-h|--help]                     Print help info
    [-o|--output=<file-name>]       Specified output filename
''' % (sys.argv[0])
   

#Script begin...
try:
    opts, files = getopt.getopt(sys.argv[1:], "ho:", ["output=", "help"])
except getopt.GetoptError:
    print "Get invalid option"
    print_help_info()
    exit(1)

g_outfile = None

#Read in arguments
if len(opts) != 0:
    for ele in opts:
        if ele[0] == '-h' or ele[0] == '--help':
            print_help_info()
            exit(0)
        if ele[0] == '-o' or ele[0] == '--output':
            if len(ele) != 2:
                print "Cannot find output file"
                print_help_info()
                exit(1)
            g_outfile = ele[1]
            continue

#Read in files
if len(files) == 0:
    print "Cannot get check file(s)"
    print_help_info()
    exit(1)

ofh = None
if g_outfile:
    ofh = open(g_outfile, "a")
for fname in files:
    check_file(fname, ofh)
