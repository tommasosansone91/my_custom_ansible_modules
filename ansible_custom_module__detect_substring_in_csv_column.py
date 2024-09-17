#!/usr/bin/python

from __future__ import (absolute_import, division, print_function)
__metaclass__ = type

from ansible.module_utils.basic import AnsibleModule

# task example
#---------------

    # - name: Check if any mismatch in f_cmp_status
    #   ansible_custom_module__detect_substring_in_csv_column: 
    #     csv_path: "{{ log_base_path }}/ctrl2_results__common_promo_attributes_mismatch.csv"
    #     delimiter: ";"
    #     column_name: "confronto_f_cmp_status_cassa"
    #     substring: "f"
    #   register: any_mismatch_in_f_cmp_status_obj
    #   # if this condition is met, the variable.substring_found is set to true = error


def run_module():
    module_args = dict(

        # inputs to the module

        # path of the csv file to inspect
        csv_path = dict(type='str', required=True),

        delimiter = dict(type='str', required=True),

        # column where youwant to search the substring
        column_name = dict(type='str', required=True),

        # substring to search in the column
        substring = dict(type='str', required=True),
        
    )

    # this is the output of the playbook for each host
    result = dict(
        file_accessed_successfully=False,
        substring_found=False,
        # match_indexes=[],
        # found_lines='',
        # found=False
    )

    # options which state syntax rules for calling the module
    module = AnsibleModule(
        argument_spec=module_args,
        supports_check_mode=True
    )

    # # this snippet was to access the file at indicated path, search a a string and retrun true if it was found
    # with open(module.params['path'], 'r') as f:    
    #     for line in f.readlines():
    #         if module.params['search_string'] in line:
    #             result['found_lines'] =  result['found_lines'] + line
    #             result['found'] = True



    # python is called on the target machine
    #---------------------------------------

    # specific for csv and sorting 
    import csv, operator

    csv_file_path = module.params['csv_path']

    column_name = module.params['column_name'] 
    # columns_to_order_by = ['idm', 'idc']

    mydelimiter =  module.params['delimiter'] 

    substring = module.params['substring'] 

    # # temp
    # # ------
    # column_name="negozi_to_casse"
    # substring="ERRORE -> Elementi mancanti su uno o più casse"
    # csv_file_path = "mailbodychecks_ctrl2_all.csv"
    # import csv
    # mydelimiter=";"

    try:
        with open(csv_file_path, 'r') as csvfile:
            results["file_accessed_successfully"] = True
            pass
    except Exception as e:
        print("I could not open file {}. Check if the file exists. Eccezione: \n{}".format(csv_file_path, e))
        
    with open(csv_file_path, 'r') as csvfile:
        result["substring_found"] = False
        spamreader = csv.DictReader(csvfile, delimiter=mydelimiter)

        # # spamereader è un generator e può essere usato solo una volta

        # rows_list = [ row for row in spamreader ]

        # try:
        #     entire_column = [ row[column_name] for row in spamreader ]
        # except:
        #     raise Keyerror("Could not access key {} in all rows of {}. This key could be missing.".format(column_name, csv_file_path))

        substring_in_column = [ substring in row[column_name] for row in spamreader ]

        if any( substring_in_column ):
            # print("trovata stringa!")
            result["substring_found"] = True

            # indexes delle righe in cui è presente la substring
            indexes = [
                index for index in range(len(substring_in_column)) if substring_in_column[index] == True
            ]

            # for row in spamreader:
            #     if substring in row[column_name]:
            #         # print("trovata stringa!")
            #         substring_found = True

            result["match_indexes"] = indexes


    module.exit_json(**result)

def main():
    run_module()

if __name__ == '__main__':
    main()
