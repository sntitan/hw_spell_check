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

def get_string_from_line(line_str, instr):
    tmp_str = ""
    tmp_str_list = []
    line_e = line_ele(line_str)
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
def analyse_string(file_lines):
    str_list = []
    instr = False
    for line in file_lines:
        line_str_list, instr = get_string_from_line(line[1], instr)
        if len(line_str_list) == 0:
            continue
        for line_str in line_str_list:
            str_list.append((line[0], line_str))
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

SN_CPOS_EN_CODE = 0
SN_CPOS_EN_COMMENT = 1
include_re = re.compile("[\s]*#include[\s]+(\"|<)[\w/\.]+(\"|>)")
cppcomment_re = re.compile(".*?//.*")
ccomment_begin_re = re.compile(".*?/\*")
ccomment_end_re = re.compile(".*?\*/")
#line[in]: line string
#pos[in]: line pos, SN_CPOS_EN
#return: line_without_comments, pos
def preanalyse_oneline(line, pos):
    if pos == SN_CPOS_EN_CODE:
        #delete include statement
        if include_re.match(line):
            return "", SN_CPOS_EN_CODE
        #delete cpp-style comment
        if cppcomment_re.match(line):
            slash_pos = line.find('//')
            if slash_pos != 0:
                return preanalyse_oneline(line[:slash_pos], SN_CPOS_EN_CODE)
            else:
                return "", SN_CPOS_EN_CODE
        #Deal with line with c-style comment
        if ccomment_begin_re.match(line):
            line_without_comments = ""
            cc_beginpos = line.find("/*")
            if cc_beginpos != 0:
                line_without_comments = line[:cc_beginpos]
            if ccomment_end_re.match(line[cc_beginpos:]):
                line_without_comments = line_without_comments + " "
                cc_endpos = line.find("*/")
                tmpline, pos = preanalyse_oneline(line[cc_endpos+2:], SN_CPOS_EN_CODE)
                return line_without_comments + tmpline, pos
            else:
                return line_without_comments, SN_CPOS_EN_COMMENT

        return line, SN_CPOS_EN_CODE
    elif pos == SN_CPOS_EN_COMMENT:
        if ccomment_end_re.match(line):
            cc_endpos = line.find("*/")
            return preanalyse_oneline(line[cc_endpos+2:], SN_CPOS_EN_CODE)
        else:
            return "", SN_CPOS_EN_COMMENT
    else:
        raise "Unknown line pos"

#pre-analyse, delete include, comments
def pre_analyse(filebuff):
    fline = []
    line_no = 0
    pos = SN_CPOS_EN_CODE
    for line in filebuff.splitlines():
        line_no = line_no + 1
        tmpline, pos = preanalyse_oneline(line, pos)
        if len(tmpline) != 0:
            fline.append((line_no, tmpline))
    return fline


def check_file(fname, outfile_handle=None):
    #Read in file
    filebuff = None
    with open(fname, "r") as fh:
        filebuff = fh.read()
    file_lines = pre_analyse(filebuff)

    print("DEBUG: pre_analyse:")
    for line in file_lines:
        print("line %d: [%s]" %(line[0], line[1]))

    #analyse string-list in it
    strl = analyse_string(file_lines)
    if len(strl) == 0:
        return 0
    
    print("DEBUG: analyse:")
    for line in strl:
        print("line %d: [%s]" %(line[0], line[1]))

    pre_check(strl)

    print("DEBUG: after pre_check:")
    for line in strl:
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
