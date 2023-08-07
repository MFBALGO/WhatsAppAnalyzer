import re
from datetime import datetime
import pandas as pd
import unicodedata
from dateutil.parser import parse

# Regular expression pattern to match lines in the chat history
pattern = r"\[(\d{4}-\d{1,2}-\d{1,2}, \d{1,2}:\d{1,2}:\d{1,2} [AP]M)\] ([^:]+): (.*)"


def read_chat(file_path):
    with open(file_path, 'r', encoding='utf-8') as file:
        messages = []
        current_message = None
        for line in file:
            line = line.strip().replace('‎', '')  # decode the line from bytes to string
            #print(f'Parsing line: {line}')
            match = re.match(r'\[(.*?)\] (.*?): (.*)', line)
            if match:
                date_str, user, message = match.groups()
                user = clean_username(user)
                for fmt in ('%m/%d/%y, %I:%M:%S %p', '%d/%m/%Y, %I:%M:%S %p', '%Y-%m-%d, %I:%M:%S %p'):
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
        message_df = pd.DataFrame(messages)
        message_df.to_csv("message_df.csv", index=False)
        return message_df




def clean_username(username):
    return ''.join(ch for ch in username if unicodedata.category(ch)[0]!="C")






