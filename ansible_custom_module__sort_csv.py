#!/usr/bin/python

# THIS WORKS FINE
# yet it could be possible to make the module read columns_names from the csv given in input, without passing the variable as input

    # - name: order the columns of prova.csv
    #   ansible_custom_module__sort_csv: 
    #     path: "{{ data_base_path }}/prova.csv"
    #     columns_names: "{{ [ 'negozio', 'cassa', 'codice_pagamento', 'pagamento', 'ammontare' ] }}"
    #     columns_to_order_by: "{{ [ 'negozio', 'cassa', 'codice_pagamento' ] }}"
      
    #   register: csv_content
    #   run_once: yes
    
    

from __future__ import (absolute_import, division, print_function)
__metaclass__ = type

from ansible.module_utils.basic import AnsibleModule

# specific for csv and sorting 
import csv, operator


def run_module():
    module_args = dict(

        # inputs to the module

        # path of the csv file to sort
        path = dict(type='str', required=True),

        # list with the titles of all the columns of the csv
        columns_names = dict(type='list', required=True),

        # list with the titles the columns of the csv you want it ordered them by
        columns_to_order_by = dict(type='list', required=True),
        
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

    csv_file_path = module.params['path']

    fieldnames = module.params['columns_names']
    # fieldnames = ['idm', 'idc', 'giorno', 'orario']

    items = tuple ( module.params['columns_to_order_by'] )  

    # display the columns titles in the tuple in the order you want them to be sorted.
    # items = (
    #     'giorno',
    #     'orario',
    #     'idm',
    #     'idc'
    # )

    with open(csv_file_path, 'r') as csvfile:
        spamreader = csv.DictReader(csvfile, delimiter=";")
        sortedlist = sorted(spamreader, key=operator.itemgetter(*items), reverse=False)

    # the same csv gets overwritten

    with open(csv_file_path, 'w') as f:
        # titles of the new csv that gets generated with the sorted data coming from the previous one        
        writer = csv.DictWriter(f, fieldnames=fieldnames, delimiter=";")  # my excel reads ; as column separator for CSVs
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
