# my_custom_ansible_modules
Public repo to share my custom ansible modules.<br>
All the modules work well, as long as it is not indicated differently in this file.

## Install

### architecture n°1

inside the folder `playbooks`,<br>
create a new directory called `custom_ansible_modules`,<br>
and place the custom modules inside it.

Then in your `ansible.cfg` file add the following snippet

    [defaults]
    library = /path/to/ansible_project/playbooks/common/ansible_custom_modules/


```
playbooks
├── tool_1
│   ├── templates
│   │   └── ...
│   ├── vars
│   │   └── ...
│   └── playbook_1.yml
├── tool_2
|   └── ...
└── tool_3
|   └── ...
└── common
    ├── vars
    |   └── ...
    ├── plays
    |   └── ...
    ├── ansible_custom_modules
        ├── ansible_custom_module_1.py
        └── ansible_custom_module_2.py
```

### architecture n°2 (not recommended)

In the same directory where is the playbook .yml file that uses that custom module,<br>
create a new directory called `library`,<br>
and place the custom modules inside it.

```
playbooks
├── tool_1
│   ├── library
│   │   ├── ansible_custom_module_1.py
│   │   └── ansible_custom_module_2.py
│   ├── templates
│   │   └── ...
│   ├── vars
│   │   └── ...
│   └── playbook_1.yml
├── tool_2
│   ├── library
│   │   ├── ansible_custom_module_1.py
│   │   ├── ansible_custom_module_2.py
│   │   └── ansible_custom_module_3.py
└── tool_3
    └── ...
```

## How to write the tasks

Every module has at its top some comments indicating how to write the task that uses that module.

## Ansible documentation on custom modules

https://docs.ansible.com/ansible/latest/dev_guide/developing_modules_general.html

## Information on single modules

#### ansible_custom_module__delete_rows_from_csv.py
has a bug and must be fixed. maybe is related to the delimiter
