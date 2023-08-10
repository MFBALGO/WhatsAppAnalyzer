import re
from datetime import datetime
import pandas as pd
import unicodedata


def clean_username(username):
    return ''.join(ch for ch in username if unicodedata.category(ch)[0] != "C")


import re
from datetime import datetime
import pandas as pd
import unicodedata

def clean_username(username):
    return ''.join(ch for ch in username if unicodedata.category(ch)[0] != "C")

def read_chat(file_path):
    with open(file_path, 'r', encoding='utf-8') as file:
        messages = []
        current_message = None
        for line in file:
            line = line.strip().replace('\u202f', '').replace('\u200e', '')

            # Handling system messages
            if "Messages and calls are end-to-end encrypted" in line:
                date_match = re.match(r'(\[?\d{1,4}[-/]\d{1,2}[-/]\d{1,4},? \d{1,2}:\d{1,2}(:\d{1,2})? ?[APap][Mm]?\]?)', line)
                if date_match:
                    date_str = date_match.group(1)
                    date_parsed = False
                    for fmt in ('%m/%d/%y, %I:%M:%S %p', '%d/%m/%Y, %I:%M:%S %p', '%Y-%m-%d, %I:%M:%S %p', '%m/%d/%Y, %I:%M %p', '%d/%m/%Y, %I:%M%p', '%m/%d/%y, %I:%M:%S%p', '%d/%m/%Y, %I:%M:%Sp', '%Y-%m-%d, %I:%M:%Sp', '%m/%d/%Y, %I:%Mp', '%d/%m/%Y, %I:%Mp'):
                        try:
                            date = datetime.strptime(date_str.replace('[', '').replace(']', ''), fmt)
                            date_parsed = True
                            break
                        except ValueError:
                            continue
                    if date_parsed:
                        messages.append({"date": date, "user": "System", "message": line.split('-')[1].strip()})
                    continue

            match = re.match(r'(\[?\d{1,4}[-/]\d{1,2}[-/]\d{1,4},? \d{1,2}:\d{1,2}(:\d{1,2})? ?[APap][Mm]?\]?) ?-? ([^:]+): (.*)', line)
            if match:
                date_str, _, user, message = match.groups()
                user = clean_username(user.strip())
                date_parsed = False
                for fmt in ('%m/%d/%y, %I:%M:%S %p', '%d/%m/%Y, %I:%M:%S %p', '%Y-%m-%d, %I:%M:%S %p', '%m/%d/%Y, %I:%M %p', '%d/%m/%Y, %I:%M%p', '%m/%d/%y, %I:%M:%S%p', '%d/%m/%Y, %I:%M:%Sp', '%Y-%m-%d, %I:%M:%Sp', '%m/%d/%Y, %I:%Mp', '%d/%m/%Y, %I:%Mp'):
                    try:
                        date = datetime.strptime(date_str.replace('[', '').replace(']', ''), fmt)
                        date_parsed = True
                        break
                    except ValueError:
                        continue
                if date_parsed:
                    if current_message:
                        messages.append(current_message)
                    current_message = {"date": date, "user": user, "message": message}
            elif current_message:
                current_message["message"] += '\n' + line
        if current_message:
            messages.append(current_message)
        message_df = pd.DataFrame(messages)
        message_df.to_csv("parsed_output.csv", index=False)
        return message_df


# if __name__ == "__main__":
#     file_path = input("Enter the path to the chat file: ")
#     parsed_df = read_chat(file_path)
#     parsed_df.to_excel("parsed_output.xlsx", index=False)
#     print("Parsed messages have been saved to 'parsed_output.xlsx'.")
