#!/usr/bin/python

"""
This module appends a list of csv to csv 2.
if it is decleared that the appending csv has header,
it skips the first line, which is assumed to be the header.
"""

from __future__ import (absolute_import, division, print_function)
__metaclass__ = type

from ansible.module_utils.basic import AnsibleModule


def run_module():
    module_args = dict(

        # inputs to the module

        # path of the csv file to be updated with the new csv
        path_of_csv_to_be_updated = dict(type='str', required=True),

        # path of the csv files to be appended
        directory_of_csvs_to_be_appended = dict(type='str', required=True),

        # common pattern in filename of the csv files to be appended
        filename_common_pattern_of_csvs_to_be_appended = dict(type='str', required=True),

        # declares if the csv to be appended has the header
        header = dict(type='bool', required=True),
        
    )

    # this is the output of the playbook for each host
    result = dict(
        changed=False,
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


    # python is called on the target machine
    #---------------------------------------

    # specific import for this module
    import csv, operator
    import datetime
    import re

    import os, traceback
    import subprocess

    # get params input

    path_csv_updating = module.params['path_of_csv_to_be_updated']

    dir_all_csv_appending = module.params['directory_of_csvs_to_be_appended']

    filename_pattern = module.params['filename_common_pattern_of_csvs_to_be_appended']

    appending_hasHeader = module.params['header']

    # execution
    #--------------

    # check filename_pattern input is not injection
    # protection form injection [^a-zA-Z0-9^*_-] detect char which are no letter numbers - / _ and *
    bad_pattern = re.compile("[^a-zA-Z0-9^*_\/-]")

    if  bad_pattern.match(filename_pattern):
        print("Invalid input! Execution aborted!\n'filename_common_pattern_of_csvs_to_be_appended' can only contain number, letters, dash, underscore and asterisk.\nYou gave me: {}".format(filename_pattern))
        exit(1)

    # check file path input is not injection
    # protection form injection [^a-zA-Z0-9^_-] detect char which are no letter numbers - / and _
    bad_pattern = re.compile("[^a-zA-Z0-9^._\/-]")

    if  bad_pattern.match(dir_all_csv_appending):
        print("Invalid input! Execution aborted!\n'directory_of_csvs_to_be_appended' can only contain number, letters, dash and underscore.\nYou gave me: {}".format(dir_all_csv_appending))
        exit(1)       

    if  bad_pattern.match(path_csv_updating):
        print("Invalid input! Execution aborted!\n'path_of_csv_to_be_updated' can only contain number, letters, dash and underscore.\nYou gave me: {}".format(path_csv_updating))
        exit(1)   

    # create find bash command

    # e.g.
    # """ find . -maxdepth 0 -name '*test2*' """
    # lista_test=$(find . -maxdepth 1 -name "*test2*")

    find_command = "find"
    find_arguments = [ dir_all_csv_appending, "-maxdepth", "1", "-name", "*{}*".format(filename_pattern) ]    

    # launch the bash commands and get the list fo files
    # subprocess.run(["ls", "-l"])  # doesn't capture output

    # supported only by python 3.5
    # find_result = subprocess.run([find_command] + find_arguments, capture_output=True, text=True)

    # workaround to for python2
    find_process = subprocess.Popen([find_command] + find_arguments, stdout=subprocess.PIPE)
    find_result, _ = find_process.communicate()
    find_result = find_result.decode("utf-8")

    try:
        # for python 3.5+
        # list_of_relpaths_appending_csvs = find_result.stdout.strip().split("\n") 

        list_of_relpaths_appending_csvs = find_result.strip().split("\n")
        
        if path_csv_updating in list_of_relpaths_appending_csvs:
            list_of_relpaths_appending_csvs.remove(path_csv_updating)
        
        list_of_relpaths_appending_csvs.sort()



    except Exception as e:
        raise Exception("Exception when extraction the find results:\nfind_result: \n{}\n\nfind result type:{}".format(find_result, type(find_result) ))



    # append sequentially each csv
    for path_csv_appending in list_of_relpaths_appending_csvs:

        try:
            with open(path_csv_updating, 'r') as reader:
                row_count_before = sum(1 for row in reader)

            with open(path_csv_appending, 'r') as reader, open(path_csv_updating, 'a') as writer:
                # print(reader)

                if appending_hasHeader:
                    # The line will skip the first row of the csv file (Header row)
                    next(reader)


                for row in reader:
                    writer.write(row)
                    # print("Appending {}: Added row: {}".format(path_csv_appending, row))

            with open(path_csv_updating, 'r') as reader:
                row_count_after = sum(1 for row in reader)        

            if row_count_before < row_count_after:
                result['changed'] = True
                # print("changed!")
            else:
                print("Please note: No changes have been made after appending {} to {}. \n{} rows before vs {} rows after.".format(path_csv_appending, path_csv_updating, row_count_before, row_count_after))

        except Exception as e:
            print('Exception occurred while trying to append {} to {}\n{}\nTraceback:\n{}'.format(path_csv_appending, path_csv_updating, e, traceback.format_exc()))

    module.exit_json(**result)

def main():
    run_module()

if __name__ == '__main__':
    main()