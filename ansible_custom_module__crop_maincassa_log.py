#!/usr/bin/python

"""
This script targets a maincassa log and creates a reduced log files that contains information about only the specified transaction.
"""

# task example
#---------------

    # - name: crop the maincassa log
    #   ansible_custom_module__crop_maincassa_log: 
    #     dt:  "{{ dt }}"
    #     idm: "{{ idm }}"
    #     idc: "{{ idc }}"
    #     idt: "{{ idt }}"
    #     cropped_log_filename: "{{ cropped_maincassa_log_filename }}"  # optional
    #     cropped_log_folder_path: "{{ tickets_folder_path }}"
        
    #   register: result


from __future__ import (absolute_import, division, print_function)

__metaclass__ = type

from ansible.module_utils.basic import AnsibleModule

# specific import for this module
import csv, operator
import io
from datetime import datetime
import re

import os, traceback
import subprocess


def run_module():
    module_args = dict(

        # inputs to the module
        #######################

        # ticket key
        dt = dict(type='str', required=True),
        idm = dict(type='str', required=True),
        idc = dict(type='str', required=True),
        idt = dict(type='str', required=True),


        # path of the folder where is the source log
        source_log_folder_path = dict(type='str', required=False, default='/home/vendor/Appli/Trace/cassa'),

        # path of the folder where the cropped log will be saved
        cropped_log_folder_path = dict(type='str', required=True),

        # name of the cropped log
        cropped_log_filename = dict(type='str', required=False, default='default'),



        # the log will be cropped in presence of a starting and ending pattern
        # it is possible to extend (or reduce, negative values) the range of lines that will be captured
        # by adding extra lines before the beginning pattern and after the end pattern
        extra_starting_lines = dict(type='int', required=False, default=50),
        extra_ending_lines = dict(type='int', required=False, default=0),

        
    )

    # this is the output of the playbook for each host
    result = dict(
        log_cropped=False, # did the playbook got to the end and cropped the log?

        source_log_filename=None,
        source_log_path=None,
        source_log_length=None,
        
        next_idt=None,
        ending_pattern_found=False,
        ending_pattern=None,

        next_idt_iteration_count=None,

        lines_log_extremes=None,

        cropped_log_path=None,
        cropped_log_length=None,
        cropped_log_size=None,
        
    )

    # options which state syntax rules for calling the module
    module = AnsibleModule(
        argument_spec=module_args,
        supports_check_mode=True
    )

    # # this snippet was to access the file at indicated path, search a astring and retrun true if it was found
    # with open(module.params['path'], 'r') as f:    
    #     for line in f.readlines():
    #         if module.params['search_string'] in line:
    #             result['found_lines'] =  result['found_lines'] + line
    #             result['found'] = True

    # # define the output of the playbook for each hosts, according to what happens into the play
    # result['changed'] = False



    # get params input
    ####################

    # go get them from module_args

    # dt = '2023-08-11'
    # idm = '10'
    # idc = '4'
    # idt= '6144'

    # cropped_log_folder_path = '/home/vendor/var/log/scontrini_AM'

    dt = module.params['dt']
    idm = module.params['idm']
    idc = module.params['idc']
    idt = module.params['idt']

    source_log_folder_path = module.params['source_log_folder_path']
    cropped_log_folder_path = module.params['cropped_log_folder_path']

    cropped_log_filename = module.params['cropped_log_filename']

    extra_starting_lines = module.params['extra_starting_lines']
    extra_ending_lines = module.params['extra_ending_lines']


    # input processing
    ####################

    dt_compressed = dt.replace("-","")

    # log filenames
    #---------------

    source_log_filename = 'maincassa-{}.tra'.format(dt)
    # source_log_filename='maincassa-2023-08-11.tra'
    source_log_path = os.path.join(source_log_folder_path, source_log_filename)

    if cropped_log_filename == 'default':        
        cropped_log_filename = 'maincassa_transazione_pdv{idm}_c{idc}_{dt_compressed}_idt{idt}.tra'.format(
            **{
                "idm": idm, 
                "idc": idc, 
                "dt_compressed": dt_compressed, 
                "idt": idt
                }
            )

    cropped_log_path = os.path.join(cropped_log_folder_path, cropped_log_filename)

    # patterns to select the beginning and end of the crop
    #-------------------------------------------------------

    target_ticket_pattern = "'receiptNumber': {}".format(idt)

    next_idt = int(idt) + 1
    next_ticket_pattern = "'receiptNumber': {}".format(next_idt)


    # execution
    ###############

    # check existence of folder input and output
    if not os.path.isdir(source_log_folder_path):
        raise IOError("source_log_folder_path is not valid or does not exists: {}".format(source_log_folder_path))

    if not os.path.isdir(cropped_log_folder_path):
        raise IOError("cropped_log_folder_path is not valid or does not exists: {}".format(cropped_log_folder_path))

    if not os.path.isfile(source_log_path):
        raise IOError("source_log_path is not valid or does not exists: {}".format(source_log_path))
        

    # count source log lines
    source_log_length = sum(1 for _ in io.open(source_log_path, "r",  encoding="ISO-8859-1"))

    # check presence of the starting and ending pattern in the source log.
    # make a while loop incrementing next idt if next idt is not in log

    # define Python user-defined exceptions
    class PatternNotFoundInFile(Exception):
        "Raised when the searched pattern is not in the searched file."
        pass

    # check existence of starting pattern
    with io.open(source_log_path, "r",  encoding="ISO-8859-1") as source_log_file:
        if target_ticket_pattern not in source_log_file.read():
            raise PatternNotFoundInFile("Cannot find target_ticket_pattern \n{}\n in file {} .".format(target_ticket_pattern, source_log_path))

    ending_pattern = next_ticket_pattern

    # check existence of ending pattern
    with io.open(source_log_path, "r",  encoding="ISO-8859-1") as source_log_file:

        # if not ending_pattern in source_log_file.read():
            # raise PatternNotFoundInFile("Cannot find ending_pattern \n{}\n in file {} .".format(ending_pattern, source_log_path))

        next_idt_iteration_count=0
        next_idt_iteration_count_max = 100
        ending_pattern_found = True  # assumption

        while ending_pattern not in source_log_file.read():

            # cannot reach the next ticket pattern after x iterations
            if next_idt_iteration_count > next_idt_iteration_count_max:
                for line in source_log_file:
                    pass
                last_line = line
                ending_pattern = last_line
                ending_pattern_found = False
                break
        
            # go to next idt
            next_idt = next_idt + 1
            ending_pattern = "'receiptNumber': {}".format(next_idt)
            next_idt_iteration_count = next_idt_iteration_count + 1

    # determine the indexes where the starting and ending pattern appear
    with io.open(source_log_path, "r",  encoding="ISO-8859-1") as source_log_file:

        lines_indexes = list()   

        for index, line in enumerate(source_log_file.readlines()):
            if ending_pattern in line:
                line_before_new_ticket_pattern__index = index - 1
                lines_indexes.append(line_before_new_ticket_pattern__index)
                break
            elif target_ticket_pattern in line:
                lines_indexes.append(index)
            else:
                pass
                # this line does not contain any idt ticket pattern - it is totally fine, the log is plenty of them

    lines_log_extremes = [ 
        max( 0, lines_indexes[0] - extra_starting_lines ), 
        min( lines_indexes[-1] + extra_ending_lines, source_log_length )
        ]

    # cropped_log_length = lines_log_extremes[1] - lines_log_extremes[0]
    # print(cropped_log_length)


    # copy lines of source log to cropped log where the lines are between the computed indexes 
    cropped_log_file = io.open(cropped_log_path, "w",  encoding="ISO-8859-1")

    with io.open(source_log_path, "r",  encoding="ISO-8859-1") as source_log_file: 
        for index, line in enumerate(source_log_file.readlines()):
            if index >= lines_log_extremes[0] and index <= lines_log_extremes[1] :
                cropped_log_file.write(line)

    cropped_log_file.close()

    
    # define success for cropping log:
    class cropped_log_info:
        def __init__(self, cropped_log_path, source_log_path):

            self.exists = os.path.isfile(cropped_log_path)
            if not self.exists:
                raise IOError("cropped_log_path is not valid or does not exists: {}".format(cropped_log_path))

            self.cropped_log_size = os.path.getsize(cropped_log_path)  

            self.cropped_log_length = sum(1 for _ in io.open(cropped_log_path, "r",  encoding="ISO-8859-1"))
            source_log_length = sum(1 for _ in io.open(source_log_path, "r",  encoding="ISO-8859-1"))
            
            self.is_non_zero_file = os.path.getsize(cropped_log_path) > 0 # bytes

            self.is_shorter_than_source_log = self.cropped_log_length < source_log_length
            
            self.is_ok = self.exists and self.is_non_zero_file and self.is_shorter_than_source_log


    cropped_log_info = cropped_log_info(cropped_log_path, source_log_path)



    # results update:
    #-----------------

    result['log_cropped'] = cropped_log_info.is_ok  # did the playbook got to the end and cropped the log?

    result['source_log_filename'] = source_log_filename
    result['source_log_path'] = source_log_path
    result['source_log_length'] = source_log_length

    result['next_idt'] = next_idt
    result['ending_pattern_found'] = ending_pattern_found
    result['ending_pattern'] = ending_pattern

    result['next_idt_iteration_count'] = next_idt_iteration_count

    result['lines_log_extremes'] = lines_log_extremes

    result['cropped_log_path'] = cropped_log_path
    result['cropped_log_length'] = cropped_log_info.cropped_log_length
    result['cropped_log_size'] = cropped_log_info.cropped_log_size


    module.exit_json(**result)


def main():
    run_module()

if __name__ == '__main__':
    main()
