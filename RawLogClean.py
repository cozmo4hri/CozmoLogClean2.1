"""
author: Bishakha Chaudhury
location: Social Brains in action Lab

This program reads the Daslog from cozmo and cleans it to present records in
time-stamped format with only the Anki's custom entries and data being presnted in
pipe separated format
"""


import json
import os
from datetime import datetime, timedelta
import sys


from record import DailyData


def read_input_log (log_file_path):
    """
    Collects the json log entries into a list
    @log_file_path: the path to the file to read
    @returns: entries in the log file as a list
    """
    log_data = []
    file_pointer =  open(log_file_path, 'r')
    file_data = file_pointer.read()
    file_pointer.close()
    raw_data = file_data.split('},{')
    total_lines = len(raw_data)
    count = 1
    error_line = 0
    for raw_line in raw_data:
        #print("%s" % raw_line)
        #print(">>>>>>>>>>>>>>>>>>")
        if not raw_line.startswith('{'):
            raw_line = '{' + raw_line
            
        if total_lines==count:
            # remove trailing ',' from last line
            raw_line = raw_line[:-1]
        elif raw_line[-1] != '}':
            raw_line= raw_line + '}'
        
        count += 1
        try:
            log_data.append(json.loads(raw_line))
            #print("%s" % log_data[-1])
            #print("-------------------------")
        except:
            # Sacrifice the problematic logline
            # but record that this line we could not read
            log_data.append(None)
            error_line += 1
    #print("There were %d error lines" % error_line)
    return log_data
    
def clean_log_data(log_data):
    """
    Extracts from each line of the log file the essential fields into a dictionary and put its the dictionary into a list :
    timestamp, The key for the last entry, the value for the last entry, the data entry associated with the line
    
    @param log_data: the log data lines in the file
    @returns : a list of essential information  dictionary. Each dictionary item contains 
                {'TimeStamp': '',     # timestamp of entry
                 'Key': '',           # key giving the information about the entry event
                 'Value': '',         # value for the entry event
                 'Data': ''}          # data associated with the entry event
    """    
    entry_list = []
    for log_line in log_data:
        entry = {'TimeStamp': '',
                 'Key': '',
                 'Value': '',
                 'Data': ''}
        for key,value in log_line.items():
            if key == '$ts':
                ts_epoch = float(value) / 1000.0

                entry['TimeStamp'] = datetime.fromtimestamp(ts_epoch).strftime('%Y-%m-%d %H:%M:%S')
                entry['TimeStamp'] += ' , ' + str(int((ts_epoch-int(ts_epoch))*1000))
            elif not key.startswith('$'):
                entry['Key'] = key
                entry['Value'] = value
            elif key == '$data':
                entry['Data'] = value
                
        entry_list.append(entry)                        
            
    return entry_list

def sort_logs_by_time(log_dir):
    """
    sort logs by time creation time
    @param log_dir: The log directory whose files are to be
    @returns : the log file path list sorted by time 
    """
    file_paths_in_dir = [os.path.join(log_dir, 
                                      filename) for filename in 
                                                    os.listdir(log_dir)]
    file_stats_details = [(os.stat(file_path).st_mtime, file_path) 
                                            for file_path in file_paths_in_dir]
    sorted_log_files = sorted(file_stats_details)
    return sorted_log_files
        
def get_usage_details(log_dir):    
    """
    Gets the relevant entries from all log files in into a dictionary
    @param log_dir: the directory in which all the log files are present
    @returns : the essential information from all log files sorted by time as a list
    """
    usage_log = {}
    clean_log = []
    session_record = None
    
    # sort all files by creation time
    sorted_log_file_path = sort_logs_by_time(log_dir)
    
    for fdate, fpath in sorted_log_file_path:
        if not os.path.isfile(fpath):
            # Don't want to get into directories
            continue
        #print("%s" % fpath)
        
        try:
            # read each log file
            log_data = read_input_log(fpath)
            
            # Read the essential entries from the log file and collect into a list
            # At the end all entries from all files will be collected in this list
            clean_log = clean_log + clean_log_data(log_data)
        except:
            print("Issue in %s" % fpath)
            raise
    return clean_log
    

if __name__ == "__main__":
    
    if len(sys.argv) < 2:
        try:
            #CHANGE THIS DIRECTORY
            usage_log = get_usage_details("C:/Users/Laptop/Documents/CozmoLogs")
        except:
            print("Check that you have provided the log directory correctly")
    else:
        # Or provide log directory at commandline
        log_dir = sys.argv[1]
        try:
            #CHANGE THIS DIRECTORY
            usage_log = get_usage_details(log_dir)
        except:
            print("Incorrect log directory : %s " % log_dir)
    
    # print out the essential entry as pipe(|) separated entries.
    # This could be put in a csv. Chosen  '|' separator as there are ',' in the log entries.
    for use_line in usage_log:
        print("%s|%s|%s|%s" % (use_line['TimeStamp'],use_line['Key'],use_line['Value'],use_line['Data']))
    

                