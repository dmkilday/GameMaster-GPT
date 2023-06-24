import os
import sys
import re
from datetime import datetime
strip_colors = True

def has_colors():
    if strip_colors:
        return False
        
    if ((os.getenv("CLICOLOR","1") != "0" and sys.stdout.isatty()) or
        os.getenv("CLICOLOR_FORCE","0") != "0"):
        return True
    else:
        return False
        
        
# Checks to see if a string is a dice roll in the format #d# (e.g. 1d20)
def is_roll(user_msg):
	
	ret_val = False

	# Check to see if the string ends with d# (e.g. d20)
	match = re.search('d\d+$', user_msg)
	
	# If there is a match, grap the values before and after the d
	if match:
		die = user_msg.split("d")
		
		# Check if the value before the d is blank or a number. 
		if (die[0]=="" or die[0].isnumeric()):
			retVal = True

	return ret_val
    
def is_ooc(user_msg):
    ret_val = False
    match = re.search('^ooc(\/clear)?\s+', user_msg)
    if match:
        return True
    else:
        return False
        
def is_integer(n):
    try:
        float(n)
    except ValueError:
        return False
    else:
        return float(n).is_integer()
    
def color_print(source):
    if not has_colors():
        source = re.sub(r'\033\[(\d|;)+?m', '', source)
    print(source)

def read_file(file_path):
    with open(file_path, 'r') as file:
        file_contents = file.read()
    
    return file_contents

def get_duration(start_datetime, end_datetime):
    duration = end_datetime - start_datetime
    seconds = duration.total_seconds()
    return seconds

def write_file(file_name, data):
    file = open(get_file_path(file_name),"w")
    file.write(data)
    file.close()

def write_file_nd(file_name, data):
    file = open(file_name,"w")
    file.write(data)
    file.close()
    
def get_file_path(file_name):
    return "data/" + file_name
