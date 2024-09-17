#!/usr/bin/python


# task example
#---------------

    # - name: inspect logs of myservice to ascertain its status
    #   ansible_custom_module__detect_service_crash_from_logs: 
        # service_name: "myservice"
        # service_logs_folder_path: "/home/orka/var/log/myservice"
        # service_logs_filename_pattern: "myservice"
        # number_of_log_files_to_analyze: 2
        # list_of_patterns_indicating_service_crashed: ["Cannot assign requested address"]
        # list_of_patterns_indicating_service_working: ["BURN request idbonint .* idcli .*"]


        # pattern_indicating_service_crashed: "Cannot assign requested address"
        # pattern_indicating_service_working: "BURN request idbonint .* idcli .*"


from __future__ import (absolute_import, division, print_function)
__metaclass__ = type

from ansible.module_utils.basic import AnsibleModule

def run_module():
    
    # define the parameters of the module

    module_args = dict(

        # inputs to the module
        #----------------------

        # file containing theoutput of the analysis in json output
        # output_file_path = dict(type='str', required=False),

        # name of the service
        service_name = dict(type='str', required=True),

        # path of the folder containing the logs of the service
        service_logs_folder_path = dict(type='str', required=True),

        # pattern grouping the logs of the service in the folder indicater upwards
        service_logs_filename_pattern = dict(type='str', required=True),

        # number of most recent log files to analyze, other logs will be ignored
        number_of_log_files_to_analyze = dict(type='int', required=True),

        # line of log indicating the server occurred into an error
        list_of_patterns_indicating_service_crashed = dict(type='list', required=True),

        # line of log indicating the server does its main task
        list_of_patterns_indicating_service_working = dict(type='list', required=True),
        
    )

    # this is the output of the playbook for each host
    result = dict(
        # file_accessed_successfully=False,
        # substring_found=False,
        # match_indexes=[],
        # found_lines='',
        # found=False
    )

    # options which state syntax rules for calling the module
    module = AnsibleModule(
        argument_spec=module_args,
        supports_check_mode=True
    )


    # python is called on the target machine
    ##########################################

    # get inputs params as base variables
    #-------------------------------------

    # file containing theoutput of the analysis in json output
    # output_file_path = module.params['']

    # name of the service
    service_name= module.params['service_name']

    # path of the folder containing the logs of the service
    service_logs_folder_path = module.params['service_logs_folder_path']

    # pattern grouping the logs of the service in the folder indicater upwa
    service_logs_filename_pattern = module.params['service_logs_filename_pattern']

    # number of most recent log files to analyze, other logs will be ignore
    number_of_log_files_to_analyze = module.params['number_of_log_files_to_analyze']

    # line of log indicating the server occurred into an error
    list_of_patterns_indicating_service_crashed = module.params['list_of_patterns_indicating_service_crashed']

    # line of log indicating the server does its main task
    list_of_patterns_indicating_service_working = module.params['list_of_patterns_indicating_service_working']


    # specific import for module operations 
    #----------------------------------------

    import sys
    import os
    import traceback
    import json

    import datetime

    import re

    import copy


    # define constant variables
    #--------------------------------

    WORKING_STATUS = "working"
    CRASHED_STATUS = "crashed"
    UNDETERMINED_STATUS = "cannot say"

    # define functions
    #-----------------

    class DetectServiceCrashFromLogs():

        def __init__(
            self, 
            service_name, 
            service_logs_folder_path, 
            service_logs_filename_pattern, 
            number_of_log_files_to_analyze, 
            list_of_patterns_indicating_service_crashed, 
            list_of_patterns_indicating_service_working ):

            # output_file_path=None            
            
            self.service_name = service_name
            self.service_logs_folder_path = service_logs_folder_path 
            self.service_logs_filename_pattern = service_logs_filename_pattern 
            self.number_of_log_files_to_analyze = number_of_log_files_to_analyze 
            self.list_of_patterns_indicating_service_crashed = list_of_patterns_indicating_service_crashed
            self.list_of_patterns_indicating_service_working = list_of_patterns_indicating_service_working
            # self.output_file_path = output_file_path


        def preliminary_checks(self):

            if not os.path.exists(self.service_logs_folder_path):
                raise Exception("logs directory does not exists")

            if self.number_of_log_files_to_analyze  <= 0:
                raise Exception("number_of_log_files_to_analyze must be greater than 0")

            if not self.list_of_patterns_indicating_service_crashed:
                raise Exception("list_of_patterns_indicating_service_crashed is void")

            if not self.list_of_patterns_indicating_service_working:
                raise Exception("list_of_patterns_indicating_service_working is void")

            # warn if there are wildcards different than * in the element of list of patterns
            # they will be interpreted as regex and not as char to exact match


        @staticmethod
        def track_string_positions_in_file(file_path, pattern):
            
            with open(file_path, 'r') as myfile:
                content = myfile.read().decode('utf-8')
                
            matches = re.finditer(pattern, content)

            positions = [match.start() for match in matches]

            if not positions:
                print("pattern {} not found in file {}".format(pattern, file_path))

            return positions


        def ascertain_service_status_from_logfile(
            self,
            log_path, 
            list_of_patterns_indicating_service_working, 
            list_of_patterns_indicating_service_crashed
            ):

            #-----------------------

            # # lookup the error pattern and eventually its position.
            # # if no pattern is found, then the service status is ok
            # positions_of_service_crashed_patterns = self.track_string_positions_in_file(log_path, service_crashed_pattern)

            # positions_of_service_working_patterns = self.track_string_positions_in_file(log_path, service_working_pattern)

            #-----------------------

            # multistirng logic

            # lookup the error pattern and eventually its position.
            # if no pattern is found, then the service status is ok

            positions_of_service_crashed_patterns = list()

            for service_crashed_pattern in list_of_patterns_indicating_service_crashed:

                thispattern_positions_of_service_crashed_patterns = self.track_string_positions_in_file(log_path, service_crashed_pattern)

                positions_of_service_crashed_patterns = positions_of_service_crashed_patterns + thispattern_positions_of_service_crashed_patterns


            positions_of_service_working_patterns = list()

            for service_working_pattern in list_of_patterns_indicating_service_working:

                thispattern_positions_of_service_working_patterns = self.track_string_positions_in_file(log_path, service_working_pattern)

                positions_of_service_working_patterns = positions_of_service_working_patterns + thispattern_positions_of_service_working_patterns

                
            if positions_of_service_working_patterns and not positions_of_service_crashed_patterns:
                service_status = WORKING_STATUS

            elif not positions_of_service_working_patterns and positions_of_service_crashed_patterns:
                service_status = CRASHED_STATUS

            elif not positions_of_service_working_patterns and not positions_of_service_crashed_patterns:
                service_status = UNDETERMINED_STATUS
                return service_status

            elif positions_of_service_working_patterns and positions_of_service_crashed_patterns:

                # reordering should not be necessary, but
                # in multipattern logic, yes, sorting is necessary


                positions_of_service_crashed_patterns = list(set(positions_of_service_crashed_patterns))
                positions_of_service_working_patterns = list(set(positions_of_service_working_patterns))

                positions_of_service_crashed_patterns.sort()
                positions_of_service_working_patterns.sort()

                position_of_last_occurrence_of_service_crashed_pattern = positions_of_service_crashed_patterns[-1]
                position_of_last_occurrence_of_service_working_pattern = positions_of_service_working_patterns[-1]

                # if the last pattern is the working one, then the service works
                # if the last pattern is the crash one, then the service has crashed

                if position_of_last_occurrence_of_service_crashed_pattern > position_of_last_occurrence_of_service_working_pattern:
                    service_status = CRASHED_STATUS

                elif position_of_last_occurrence_of_service_crashed_pattern < position_of_last_occurrence_of_service_working_pattern:
                    service_status = WORKING_STATUS

                else:
                    raise Exception("code should never get here")

            return service_status


        def get_relevant_logs(self):

            all_files_data = list()
            
            for element in os.listdir(self.service_logs_folder_path):
                file_path = os.path.join(self.service_logs_folder_path, element)
                if os.path.isfile(file_path):
                    timestamp = os.path.getmtime(file_path)
                    last_modified_date = datetime.datetime.fromtimestamp(timestamp)
                    all_files_data.append(
                        {
                        'last_modified_date': last_modified_date,
                        'log_file_path': file_path
                        }
                    )

            # select only files that are logs of the service - recognition based on logs filename pattern
            service_log_files_data = [
                element for element in all_files_data 
                if self.service_logs_filename_pattern in element['log_file_path']
                ]

            service_log_files_data.sort(key=lambda x: x['last_modified_date'], reverse=True)

            self.relevant_service_log_files_data = service_log_files_data[:self.number_of_log_files_to_analyze]

            # self.analyzed_service_log_files_data = relevant_service_log_files_data[:]  # deepcopy


        def ascertain_service_status_in_logs(self):

            self.analyzed_service_log_files_data = list()

            for log_file_data in self.relevant_service_log_files_data:

                # new dict
                analyzed_log_file_data = copy.deepcopy(log_file_data)
                
                log_path = analyzed_log_file_data['log_file_path']

                # get the status of the service from log file (for each file)
                service_status = self.ascertain_service_status_from_logfile(
                    log_path, 
                    self.list_of_patterns_indicating_service_working, 
                    self.list_of_patterns_indicating_service_crashed
                    )

                # add the detected service status to the new dict 
                analyzed_log_file_data['detected_service_status'] = service_status

                # append the new dict to new list self.analyzed_service_log_files_data
                self.analyzed_service_log_files_data.append(analyzed_log_file_data)


        def ascertain_service_latest_status(self):

            # reordering should not be necessary, but

            self.analyzed_service_log_files_data.sort(key=lambda x: x['last_modified_date'], reverse=True)

            self.service_latest_status = self.analyzed_service_log_files_data[0]['detected_service_status']

            if self.service_latest_status == UNDETERMINED_STATUS:

                for log_data in self.analyzed_service_log_files_data:

                    if log_data['detected_service_status'] == CRASHED_STATUS:
                        self.service_latest_status = CRASHED_STATUS
                        break
                    elif log_data['detected_service_status'] == WORKING_STATUS:
                        self.service_latest_status = WORKING_STATUS
                        break
                    elif log_data['detected_service_status'] == UNDETERMINED_STATUS:
                        pass
                    else:
                        raise Exception("code should never get here")


        # def print_log_analysis_data(self)
            # pass

        # def dump_log_analysis_data_to_file(self):
        #     with open(self.output_file_path, 'w') as output_file:
        #         json.dump(self.analyzed_service_log_files_data, output_file)


        # runs all the functions in order, 
        # eventually runs command 'out from the functions'
        def run(self):
            self.preliminary_checks()
            self.get_relevant_logs()
            self.ascertain_service_status_in_logs()
            self.ascertain_service_latest_status()


            # # return results as print or dumps them into a file
            # # according to the not given or iven path of output file

            # if self.output_file_path:
            #     self.dump_log_analysis_data_to_file()
            # else:
            #     self.print_log_analysis_data()


    # body of run_module
    #-----------------------

    # isntantiate class 
    analysis = DetectServiceCrashFromLogs(
        service_name,
        service_logs_folder_path,
        service_logs_filename_pattern,
        number_of_log_files_to_analyze,
        list_of_patterns_indicating_service_crashed,
        list_of_patterns_indicating_service_working
    )

    analysis.run()
    

    result['analyzed_service_log_files_data'] = analysis.analyzed_service_log_files_data

    result['service_latest_status'] = analysis.service_latest_status
 

#-------------

    module.exit_json(**result)

def main():
    run_module()

if __name__ == '__main__':
    main()

    

    
