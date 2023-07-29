import re
from datetime import datetime
import pandas as pd
import unicodedata
from dateutil.parser import parse

# Regular expression pattern to match lines in the chat history
pattern = r"\[(\d+\/\d+\/\d+, \d+:\d+:\d+ [APM]+)\] ([^:]+): (.*)"



def read_chat(file):
    messages = []
    current_message = None
    for line in file:
        line = line.decode('utf-8').strip()  # decode the line from bytes to string
        #print(f'Parsing line: {line}')
        match = re.match(r'\[(.*?)\] (.*?): (.*)', line)
        if match:
            date_str, user, message = match.groups()
            user = clean_username(user)
            for fmt in ('%m/%d/%y, %I:%M:%S %p', '%d/%m/%Y, %I:%M:%S %p'):
                try:
                    date = datetime.strptime(date_str, fmt)
                    break
                except ValueError:
                    continue
            else:
                print(f'Error parsing date: {date_str}')
                continue
            if current_message:
                messages.append(current_message)
            current_message = {"date": date, "user": user, "message": message}
        elif current_message:
            current_message["message"] += '\n' + line
        else:
            print(f'Error parsing line: {line}')
    if current_message:
        messages.append(current_message)
    return pd.DataFrame(messages)




def clean_username(username):
    return ''.join(ch for ch in username if unicodedata.category(ch)[0]!="C")






# def parse_chat(file):
#     # Initialize an empty list
#     data = []
#
#     # Read the file
#     for line in file:
#         try:
#             # Search for the pattern
#             match = re.search(pattern, line.decode('utf-8'))
#             if match:
#                 # Extract the timestamp, user, and message from the line
#                 timestamp_str, user, message = match.groups()
#
#                 # Convert the timestamp string to a datetime object
#                 timestamp = parse_date(timestamp_str)
#
#                 # Add the data to the list
#                 data.append({'Timestamp': timestamp, 'User': user, 'Message': message})
#         except Exception as e:
#             print(f"Error parsing line: {e}")
#
#     # Convert the list to a DataFrame
#     df = pd.DataFrame(data)
#
#     return df
