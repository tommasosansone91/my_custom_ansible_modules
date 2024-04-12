#!/usr/bin/python

# - name: re-order columns of the csv file
#   ansible_custom_module__reorder_csv_columns:
#     path: "{{ csv__cmpd_path }}"
#     columns_ordered_list: "{{ [ 'id', 'name', 'surname' ] }}"
#     delimiter: ";"

from __future__ import (absolute_import, division, print_function)
__metaclass__ = type

from ansible.module_utils.basic import AnsibleModule


def run_module():
    module_args = dict(

        # inputs to the module

        # path of the csv file to sort
        path = dict(type='str', required=True),

        # list with the titles the columns of the csv in the new order you want them
        columns_ordered_list = dict(type='list', required=True),

        delimiter = dict(type='str', required=True),

        # the csv must have the first line as header
        
    )

    # this is the output of the playbook for each host
    result = dict(
        changed=False,
        warning_messages=[],
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

    columns_ordered_list = module.params['columns_ordered_list'] 
    # columns_ordered_list = ['idm', 'idc']

    mydelimiter =  module.params['delimiter'] 


    # specific for csv and sorting 
    import csv, io, shutil
    import operator
    import os, traceback

    # display the columns titles in the tuple in the order you want them to be sorted.
    # items = (
    #     'id',
    #     'name',
    #     'surname'
    # )

    def file_existence_check(csv_file_path):
        if not os.path.isfile(csv_file_path):
            raise IOError("csv_file_path is not valid or does not exists: {}".format(csv_file_path))


    def columns_existence_check(csv_file_path, columns_to_check, all_columns):

        column_existence = [ (column_name in all_columns ) for column_name in columns_to_check ]

        if not all(column_existence):
            raise ValueError("File {} does not contains all the columns given in input for processing:\nFile columns names: {}\nInput columns names: {}".format(csv_file_path, all_columns, columns_to_check))


    def delimiter_existence_check(csv_file_path, mydelimiter):
        with open(csv_file_path, 'r') as csvfile:
            first_line = csvfile.readline()
            # print("first_line", first_line)
            if mydelimiter not in first_line:
                delimiter_warning_message = "No delimiter found in file first line."
                return delimiter_warning_message 



#----------------------------------------------------------------

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

#----------------------------------------------------------------


    # input checks
    ################

    # check file existence
    file_existence_check(csv_file_path)

    # check columns existence - # check that all the columns existing are in the list of those to be reordered
    columns_existence_check(csv_file_path, columns_ordered_list, list_of_column_names)

    # check the delimiter existence
    delimiter_warning_message = delimiter_existence_check(csv_file_path, mydelimiter)

    if delimiter_warning_message:
        result['warning_messages'].append(delimiter_warning_message)

#------------------------------------------

    # build the path of a to-be-generated duplicate file to be used as output
    inputcsv_absname, inputcsv_extension = os.path.splitext(csv_file_path)
    csv_output_file_path = inputcsv_absname + '__output' + inputcsv_extension


    column_names_list = columns_ordered_list


    with open(csv_file_path, 'r') as infile, open(csv_output_file_path, 'a') as outfile:
        # output dict needs a list for new column ordering
        fieldnames = column_names_list  # this was manually defined as list of strings
        writer = csv.DictWriter(outfile, fieldnames=fieldnames, quoting=csv.QUOTE_NONE, delimiter=mydelimiter, quotechar='',escapechar='\\')
        # reorder the header first
        writer.writeheader()
        for row in csv.DictReader(infile, quoting=csv.QUOTE_NONE, delimiter=mydelimiter, quotechar='',escapechar='\\'):
            # writes the reordered rows to the new file
            writer.writerow(row)



    # with open(csv_file_path, 'r') as infile, open(csv_output_file_path, 'w') as outfile:
    # # in dev there is ansible 2.7, so I cannot use argument newline
    # # with open(csv_file_path, 'r', newline='') as infile, open(csv_output_file_path, 'w', newline='') as outfile:
    #     reader = csv.reader(infile, quoting=csv.QUOTE_NONE, delimiter=mydelimiter, quotechar='',escapechar='\\')
    #     writer = csv.writer(outfile, quoting=csv.QUOTE_NONE, delimiter=mydelimiter, quotechar='',escapechar='\\')

    #     fieldnames = columns_ordered_list  # this was manually defined as list of strings

    #     # reorder the header first
    #     headers = next(reader, None)
    #     writer.writerow(headers)
    #     # reorder the other rows
    #     for row in reader:
    #         # writes the reordered rows to the new file
    #         writer.writerow(row)

        result['changed'] = True
    
    # else:
    #     result['changed'] = False

    # replace the old csv with the new one
    # -> Copy the content of source to destination
    shutil.copyfile(csv_output_file_path, csv_file_path)
    # os.remove(csv_output_file_path) 


    module.exit_json(**result)


def main():
    run_module()

if __name__ == '__main__':
    main()
