from flask import Flask, request, render_template
from data_analyzer import DataAnalyzer
import plotter
import chat_parser
import time
import os

app = Flask(__name__)

@app.route('/', methods=['GET', 'POST'])
def upload_file():
    if request.method == 'POST':
        # Parsing the chat to a df
        f = request.files['file']
        identifier = str(int(time.time()))
        file_path = os.path.join('uploads', f'{f.filename}_{identifier}.txt')
        f.save(file_path)  # Save the file temporarily

        message_df = chat_parser.read_chat(file_path)
        print(message_df)
        # Check user count
        all_users = message_df['user'].unique()
        user_cap = 50  # Adjust as needed
        if len(all_users) > user_cap:
            return render_template('select_users.html', users=all_users, file_path=file_path)  # Pass the file path

        # Analysis
        analyzed_results = DataAnalyzer(message_df, all_users)

        # Generate a unique identifier for plots then plot
        identifier = str(int(time.time()))
        plotter.plot_results(analyzed_results, identifier)

        return render_template('results.html', results=analyzed_results.__dict__, identifier=identifier)  # pass the results to the template

    return render_template('upload.html')


@app.after_request
def add_header(response):
    response.headers['Cache-Control'] = 'no-store'
    return response

@app.route('/select_users', methods=['POST'])
def select_users():
    users_to_include = request.form.getlist('users_to_include')
    file_path = request.form['file_path']  # Retrieve the file path from form data
    message_df = chat_parser.read_chat(file_path)  # Read from the saved file

    # Analysis
    analyzed_results = DataAnalyzer(message_df, users_to_include)

    # Generate a unique identifier for plots then plot
    identifier = str(int(time.time()))
    plotter.plot_results(analyzed_results, identifier)
    return render_template('results.html', results=analyzed_results.__dict__, identifier=identifier)

@app.route('/select_users_page')
def select_users_page():
    users = get_users()  # Retrieve the list of users from your data
    return render_template('select_users.html', users=users)


if __name__ == '__main__':
    app.run(debug=True, port=80, host="0.0.0.0")
