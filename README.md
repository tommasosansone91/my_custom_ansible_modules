# my_custom_ansible_modules
Public repo to share my custom ansible modules.<br>
All the modules work well, as long as it is not indicated differently in this file.

## Install

In the same directory where is the playbook .yml file that uses that custom module,<br>
create a new directory called `library`,<br>
and place the custom modules inside it.

## How to write the task to call the custom modules

Every module has at its top some comments indicating how to write the task that usaes that module.

### ansible_custom_module__delete_rows_from_csv.py
has a bug and must be fixed. maybe is related to the delimiter

## Ansible documentation on custom modules

https://docs.ansible.com/ansible/latest/dev_guide/developing_modules_general.html
