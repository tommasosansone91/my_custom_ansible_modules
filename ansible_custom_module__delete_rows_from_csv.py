#!/usr/bin/python

# THIS HAS SOME BUGS



from __future__ import (absolute_import, division, print_function)
__metaclass__ = type

from ansible.module_utils.basic import AnsibleModule


# imports specific for this playbook:
#---------------------------------------

# reading and writing the csv
import os
import csv

# this is to allow the insertion of datetime method inside the python condition in the playbook"
from datetime import datetime

# module config
#-----------------


def run_module():
    module_args = dict(

        # inputs to the module

        # path of the csv file to sort
        path = dict(type='str', required=True),

        # list with the titles the columns of the csv you want it ordered them by
        python_condition = dict(type='str', required=True),

        # list with the titles of the columns appearing in the python condition
        columns_involved_in_condition = dict(type='list', required=True),
        
    )

    # this is the output of the playbook for each host
    result = dict(
        changed=False,
        rows_parsed=0,
        rows_excepted=0,
        rows_deleted=0,
        rows_untouched=0,
        exception_in_eval=[]
    )

    # options which state syntax rules for calling the module
    module = AnsibleModule(
        argument_spec=module_args,
        supports_check_mode=True
    )


    #---------------------------------------
    # python is called on the target machine
    #---------------------------------------

    # load inputs form playbook
    #---------------------------

    csv_input_file_path = module.params['path']

    python_condition = module.params['python_condition'] 

    columns_involved_in_condition = module.params['columns_involved_in_condition'] 
    

    # input processing
    # ------------------
    
    # here the columns involved are sorted in order of decreasing length of their title,
    # otherwise, if one column title contains another, the substitution of one column will affect also columns which contains that string
    # "where idt > 9000 and dt = '2022-11-23'" --> "where row[0]t > 9000 and row[0] = '2022-11-23'"
    columns_involved_in_condition = sorted(columns_involved_in_condition, key=lambda x: (-len(x), x))


    # execution
    #------------

    dir_path, input_csv_filename = os.path.split(csv_input_file_path)

    csv_output_filename = "filtered_output.csv"
    csv_output_file_path = os.path.join(dir_path, csv_output_filename)

    # just get the columns names, then close the file
    with open(csv_input_file_path, 'r') as csvfile:
        columnslist = csv.DictReader(csvfile, delimiter=";")      
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


    # read csv content
    with open(csv_input_file_path,"r+") as r, open(csv_output_file_path,"w", newline='') as f:  # newline is only to avoid line brak between rows on windows (testing)
    # pass the file object to reader() to get the reader object
        reader = csv.reader(r, delimiter=";")
        writer = csv.writer(f, delimiter=";")
        # Iterate over each row in the csv using reader object

        #---------

        # associate the column name to the column position
        ic_indexes = [ list_of_column_names.index(element) for element in columns_involved_in_condition ]
        # involved columns indexes

        variablefilled_python_condition = (python_condition + '.')[:-1]  
        # this is a workaround to do the copy on a string. 
        # see https://stackoverflow.com/a/24804471/7658051


        # substitute that column name with row[index] in the string before eval
        for i in range(len(columns_involved_in_condition)): 
            variablefilled_python_condition =  variablefilled_python_condition.replace( columns_involved_in_condition[i], "row[" + str(ic_indexes[i]) + "]")

        print(python_condition)
        print(variablefilled_python_condition)

        #--------

        # write down the header
        for row in reader:
            writer.writerow(row)
            break
        
        # in the following cycle, skip the headers, otherwise the first comparison will be done on columns names
        next(reader, None)  
    

        for row in reader:

            try:

                if eval(variablefilled_python_condition):    
                        # if   row[0] == '06-06-2022' and <= '08-06-2022'    :   
                        # if   day >= '06-06-2022' and day <= '08-06-2022'    :  
                                    
                        result["rows_deleted"]+=1
                        # skip the writing of the current row
                        # "delete the line if the condition is met"
                        
                else:
                    writer.writerow(row)
                    result["rows_untouched"]+=1

            except Exception as e:
                
                result["rows_excepted"]+=1


                dict_error_data = {}
                dict_error_data["row"] = row
                dict_error_data["variablefilled_python_condition"] = variablefilled_python_condition
                dict_error_data["list_of_column_names"] = list_of_column_names
                dict_error_data["columns_involved_in_condition"] = columns_involved_in_condition
                dict_error_data["ic_indexes"] = ic_indexes

                result["exception_in_eval"].append(dict_error_data)
                
                
                
            result["rows_parsed"]+=1


    # remove the file in excess
    os.remove(csv_input_file_path)
    os.rename(csv_output_file_path, csv_input_file_path)


    if result['rows_deleted'] > 0:
        # the csv gets overwritten, so there are changes on the host machine
        result['changed'] = True
    else:
        result['changed'] = False


    #  export result
    module.exit_json(**result)


def main():
    run_module()

if __name__ == '__main__':
    main()
