#!/usr/bin/python

from __future__ import (absolute_import, division, print_function)
__metaclass__ = type

from ansible.module_utils.basic import AnsibleModule


def run_module():
    module_args = dict(

        # inputs to the module

        # path of the csv file to sort
        path = dict(type='str', required=True),

        # list with the titles the columns of the csv you want it ordered them by
        columns_to_order_by = dict(type='list', required=True),

        delimiter = dict(type='str', required=True),
        
    )

    # this is the output of the playbook for each host
    result = dict(
        changed=False,
        # found_lines='',
        # found=False
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

    # python is calledon the target machine
    #---------------------------------------

    # specific for csv and sorting 
    import csv, operator

    csv_file_path = module.params['path']

    columns_to_order_by = module.params['columns_to_order_by'] 
    # columns_to_order_by = ['idm', 'idc']

    mydelimiter =  module.params['delimiter'] 

    

    # display the columns titles in the tuple in the order you want them to be sorted.
    # items = (
    #     'giorno',
    #     'orario',
    #     'idm',
    #     'idc'
    # )

    items = tuple ( columns_to_order_by ) 

    with open(csv_file_path, 'r') as csvfile:
        spamreader = csv.DictReader(csvfile, delimiter=mydelimiter)
        sortedlist = sorted(spamreader, key=operator.itemgetter(*items), reverse=False)

    # just get the columns names, then close the file
    with open(csv_file_path, 'r') as csvfile:
        columnslist = csv.DictReader(csvfile, delimiter=mydelimiter)      
        list_of_column_names = []
        # loop to iterate through the rows of csv
        for row in columnslist:
            # adding the first row
            list_of_column_names.append(row)
            # breaking the loop after the
            # first iteration itself
            break            
        list_of_column_names = list_of_column_names[0]        
        list_of_column_names = list(list_of_column_names.keys())

    # the same csv gets overwritten

    with open(csv_file_path, 'w') as f:
        # titles of the new csv that gets generated with the sorted data coming from the previous one        
        writer = csv.DictWriter(f, fieldnames=list_of_column_names, delimiter=mydelimiter)  # my excel reads ; as column separator for CSVs
        writer.writeheader()
        for row in sortedlist:
            writer.writerow(row)

        # the csv gets overwritten, so there are changes on the host machine
        result['changed'] = True

    module.exit_json(**result)

def main():
    run_module()

if __name__ == '__main__':
    main()