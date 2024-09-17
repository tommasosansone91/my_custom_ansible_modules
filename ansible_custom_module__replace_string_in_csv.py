#!/usr/bin/python

# task example
#---------------

    # - name: replace dot by comma in money-amount columns of {{ rapporto_finanziario_filename }}
    #   ignore_errors: true  # in case there are no lines
    #   ansible_custom_module__replace_string_in_csv: 
    #     path: "/path/to/file.csv"
    #     columns_to_process: "{{ [ 'ammontare' ] }}"
    #     string_to_be_replaced: "."
    #     string_to_replace_with: ","
    #     delimiter: ";"



from __future__ import (absolute_import, division, print_function)
__metaclass__ = type

from ansible.module_utils.basic import AnsibleModule


def run_module():
    module_args = dict(

        # inputs to the module

        # path of the csv file where to do the replacement
        path = dict(type='str', required=True),

        # list with the titles the columns of the csv where you want to have the replacement done
        columns_to_process = dict(type='list', required=True),

        string_to_be_replaced = dict(type='str', required=True),

        string_to_replace_with = dict(type='str', required=True),

        delimiter = dict(type='str', required=True),

        # the csv must have the first line as header
        
    )

    # this is the output of the playbook for each host
    result = dict(
        changed=False,
        warning_messages=[],
        source_csv_number_of_raw_lines=None,
        source_csv_number_of_lines=None,
        number_of_modified_cells=None,
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

    columns_to_process = module.params['columns_to_process'] 
    # columns_to_order_by = ['idm', 'idc']

    string_to_be_replaced = module.params['string_to_be_replaced'] 

    string_to_replace_with = module.params['string_to_replace_with'] 

    mydelimiter =  module.params['delimiter'] 

    #------------

    # specific import for csv
    import csv, io
    # import operator
    import shutil

    # specific import to manage errors
    import os, traceback




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

    if NOL > 0:

        # just get the columns names, then close the file
        #-----------------------------------------------------
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

        # transform the colum names into a list
        first_dictcolumn = list_of_dictcolumns[0]        
        list_of_column_names = list(first_dictcolumn.keys())
        number_of_columns = len(list_of_column_names)

        # check columns existence
        #------------------------
        column_existence = [ (column_name in list_of_column_names ) for column_name in columns_to_process ]

        if not all(column_existence):
            raise ValueError("File {} does not contains all the columns given in input for processing:\nFile columns names: {}\nInput columns names: {}".format(csv_file_path, list_of_column_names, columns_to_process))

        
        # determine the indexes of the columns to process
        indexes_of_columns_to_process = [i for i, column_name in enumerate(list_of_column_names) if column_name in columns_to_process]

        # print("indexes_of_columns_to_process: ", indexes_of_columns_to_process)

        # build the path of a to-be-generated duplicate file to be used as output
        inputcsv_absname, inputcsv_extension = os.path.splitext(csv_file_path)
        csv_output_file_path = inputcsv_absname + '__output' + inputcsv_extension

        # define the processing function
        def replace_string_in_columns(input_csv, output_csv, indexes_of_columns_to_process, string_to_be_replaced, string_to_replace_with):

            number_of_replacements = 0

            with open(input_csv, 'r', newline='') as infile, open(output_csv, 'w', newline='') as outfile:
                reader = csv.reader(infile, quoting=csv.QUOTE_NONE, delimiter=mydelimiter, quotechar='',escapechar='\\')
                writer = csv.writer(outfile, quoting=csv.QUOTE_NONE, delimiter=mydelimiter, quotechar='',escapechar='\\')
                # writer = csv.writer(outfile, delimiter=mydelimiter, escapechar='\\', quoting=csv.QUOTE_NONE)

                row_index=0

                for row in reader:                

                    for col_index in indexes_of_columns_to_process:

                        # break the processing when empty lines at the end of the file are reached
                        if len(row) == 0:
                            break

                        cell = row[col_index]
                        columns_before = row[:col_index]
                        columns_after = row[(col_index + 1):]

                        # print("col_index: ", col_index)
                        # print("row: ", row)
                        # # print("list_of_cells: ", list_of_cells)
                        # print("cell: ", cell)
                        # # print("columns_before: ", columns_before)
                        # # print("columns_after: ", columns_after)

                        if string_to_be_replaced in cell and row_index != 0:                        
                            # do the substitution in the cell
                            cell = cell.replace(string_to_be_replaced, string_to_replace_with)
                            number_of_replacements = number_of_replacements + 1
                            # print("number_of_replacements: ", number_of_replacements)

                        #     # sew the row up agian
                            row_replaced = columns_before + [ cell ] + columns_after

                            row = row_replaced
                            

                    # write / copy the row in the new file
                    writer.writerow(row)
                    # print("written row: ", row, "index: ", row_index)

                    row_index=row_index+1

            return number_of_replacements 


        # launch the function
        result['number_of_modified_cells'] =  replace_string_in_columns(csv_file_path, csv_output_file_path, indexes_of_columns_to_process, string_to_be_replaced, string_to_replace_with)

        # replace the old csv with the new one
        shutil.copyfile(csv_output_file_path, csv_file_path)
        os.remove(csv_output_file_path)

        if result['number_of_modified_cells'] > 0:
            result['changed'] = True
        else:
            result['changed'] = False
        
    else:

        result['changed'] = False


    result['source_csv_number_of_raw_lines'] = NOL
    result['source_csv_number_of_lines'] = NOL - 1
    #-------------

    module.exit_json(**result)

def main():
    run_module()

if __name__ == '__main__':
    main()
