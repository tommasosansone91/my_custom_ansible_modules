#!/usr/bin/python

"""
This module appends csv 1 to csv 2.
if it is decleared that the appending csv has header,
it skips the first line, which is assumed to be the header.
"""

from __future__ import (absolute_import, division, print_function)
__metaclass__ = type

from ansible.module_utils.basic import AnsibleModule

# specific for csv and sorting 
import csv, operator, datetime


def run_module():
    module_args = dict(

        # inputs to the module

        # path of the csv file to be updated with the new csv
        path_of_csv_to_be_updated = dict(type='str', required=True),

        # path of the csv file to be appended
        path_of_csv_to_be_appended = dict(type='str', required=True),

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

    path_csv_updating = module.params['path_of_csv_to_be_updated']

    path_csv_appending = module.params['path_of_csv_to_be_appended']

    appending_hasHeader = module.params['header']


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
                print(row)

        with open(path_csv_updating, 'r') as reader:
            row_count_after = sum(1 for row in reader)        

        if row_count_before < row_count_after:
            result['changed'] = True
            # print("changed!")
        else:
            print("Please note: No changes have been made after appending {} to {}. \n{} rows before vs {} rows after.".format(path_csv_appending, path_csv_updating, row_count_before, row_count_after))

    except Exception as e:
        print('Exception occurred while trying to append {} to {}\n{}'.format(path_csv_appending, path_csv_updating, e))

        module.exit_json(**result)

def main():
    run_module()

if __name__ == '__main__':
    main()
