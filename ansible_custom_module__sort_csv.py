#!/usr/bin/python

    # - name: sort the aggregated ticketregister 
    #   ansible_custom_module__sort_csv: 
    #     path: "{{ aggregated_ticketregister_path }}"
    #     # columns_to_order_by: [dt, padded_idm, idc, idt]
    #     columns_to_order_by: "{{ ['dt', 'padded_idm', 'idc', 'idt'] }}"
    #     delimiter: ';'

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

        # the csv must have the first line as header
        
    )

    # this is the output of the playbook for each host
    result = dict(
        changed=False,
        warning_messages=[],
        source_csv_number_of_raw_lines=None,
        source_csv_number_of_lines=None,
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

    csv_file_path = module.params['path']

    columns_to_order_by = module.params['columns_to_order_by'] 
    # columns_to_order_by = ['idm', 'idc']

    mydelimiter =  module.params['delimiter'] 


    # specific for csv and sorting 
    import csv, io
    import operator
    import os, traceback

    # display the columns titles in the tuple in the order you want them to be sorted.
    # items = (
    #     'giorno',
    #     'orario',
    #     'idm',
    #     'idc'
    # )


    # check file existence
    if not os.path.isfile(csv_file_path):
        raise IOError("csv_file_path is not valid or does not exists: {}".format(csv_file_path))

    # check the delimiter existence
    with open(csv_file_path, 'r') as csvfile:
        first_line = csvfile.readline()
        # print("first_line", first_line)
        if mydelimiter not in first_line:
            delimiter_warning_message = "No delimiter found in file first line."
            result['warning_messages'].append(delimiter_warning_message)

    # count the lines in the source file
    NOL = sum(1 for _ in io.open(csv_file_path, "r"))

    # print("NOL:", NOL)

    # if NOL = 0 -> void file
    # if NOL = 1 -> header-only file

    if NOL > 1:

        # just get the columns names, then close the file
        with open(csv_file_path, 'r') as csvfile:
            columnslist = csv.DictReader(csvfile, delimiter=mydelimiter)      
            list_of_dictcolumns = []
            # loop to iterate through the rows of csv
            for row in columnslist:
                # adding the first row
                list_of_dictcolumns.append(row)
                # breaking the loop after the
                # first iteration itself
                break  

        # print("list_of_dictcolumns", list_of_dictcolumns)  

        first_dictcolumn = list_of_dictcolumns[0]        
        list_of_column_names = list(first_dictcolumn.keys())

        # print("list_of_column_names", list_of_column_names)

        # read the file
        with open(csv_file_path, 'r') as csvfile:
            spamreader = csv.DictReader(csvfile, delimiter=mydelimiter)

            # print("columns_to_order_by", columns_to_order_by)

            # check columns existence
            column_existence = [ (column_name in list_of_column_names ) for column_name in columns_to_order_by ]

            # print(column_existence)

            if not all(column_existence):
                raise ValueError("File {} does not contains all the columns given in input for sorting:\nFile columns names: {}\nInput columns names: {}".format(csv_file_path, list_of_column_names, columns_to_order_by))


            items = tuple ( columns_to_order_by ) 
            sortedlist = sorted(spamreader, key=operator.itemgetter(*items), reverse=False)


        # the same csv gets overwritten

        with open(csv_file_path, 'w') as f:
            # titles of the new csv that gets generated with the sorted data coming from the previous one        
            writer = csv.DictWriter(f, fieldnames=list_of_column_names, delimiter=mydelimiter)  # my excel reads ; as column separator for CSVs
            writer.writeheader()
            for row in sortedlist:
                writer.writerow(row)
                
        result['changed'] = True
    
    else:
        result['changed'] = False


    result['source_csv_number_of_raw_lines'] = NOL
    result['source_csv_number_of_lines'] = NOL - 1

    module.exit_json(**result)

def main():
    run_module()

if __name__ == '__main__':
    main()
