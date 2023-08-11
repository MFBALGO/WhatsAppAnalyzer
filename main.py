from flask import Flask, request, render_template
from data_analyzer import DataAnalyzer
import plotter
import chat_parser
import time
import os
import logging
from logging.handlers import RotatingFileHandler


app = Flask(__name__)
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 16 MB

formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')

handler = RotatingFileHandler('app.log', maxBytes=10000, backupCount=3)
handler.setFormatter(formatter)
handler.setLevel(logging.INFO)

app.logger.addHandler(handler)

logging.basicConfig(filename='app.log', level=logging.INFO)

@app.route('/', methods=['GET', 'POST'])
def upload_file():
    identifier = str(int(time.time()))

    def allowed_file(filename):
        ALLOWED_EXTENSIONS = {'txt'}
        return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

    if request.method == 'POST':
        # Preparing file
        f = request.files['file']

        if not f:
            app.logger.warning("No file selected for upload")
            return render_template("400.html", error_message="Select a file before uploading"), 400

        if not allowed_file(f.filename):
            app.logger.warning(f"Unsupported file upload attempt: {f.filename}")
            return render_template("400.html", error_message="Unsupported file upload attempt, ensure it's a valid format (.txt)"), 400

        # Process the file
        file_path = os.path.join('uploads', f'{f.filename}_{identifier}.txt')

        try:
            f.save(file_path) # Save the file temporarily
        except Exception as e:
            app.logger.error(f"Error saving uploaded file: {e}")
            return render_template("500.html", error_message="Error saving uploaded file"), 500

        # Parsing the chat to a df
        try:
            message_df = chat_parser.read_chat(file_path)
        except Exception as e:
            app.logger.error(f"Error parsing the chat: {e}")
            return render_template("400.html", error_message="Unable to process the uploaded chat.\n"
                                                             "Will analyze logs and fix"), 400

        # Check user count
        all_users = message_df['user'].unique()
        user_cap = 50  # Adjust as needed
        if len(all_users) > user_cap:
            app.logger.info(f"Chat has {len(all_users)} users, exceeding the cap of {user_cap}. Redirecting to user selection.")
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


@app.errorhandler(500)
def internal_server_error(e):
    app.logger.error(f"Server Error: {e}")
    return render_template('500.html'), 500


@app.errorhandler(400)
def no_selected_file(e):
    return render_template("400.html"), 400


if __name__ == '__main__':
    app.run(debug=False, port=8000, host="0.0.0.0")
