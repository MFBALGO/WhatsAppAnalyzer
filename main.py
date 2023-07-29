from flask import Flask, request, render_template
import data_analyzer
import plotter
import chat_parser
import time


app = Flask(__name__)

@app.route('/', methods=['GET', 'POST'])
def upload_file():
    if request.method == 'POST':
        f = request.files['file']
        results = data_analyzer.analyze_chat(f)  # replace with your actual function

        # Generate a unique identifier
        identifier = str(int(time.time()))
        plotter.plot_results(results, identifier)

        return render_template('results.html', results=results.__dict__, identifier=identifier)  # pass the results to the template
    return render_template('upload.html')

# @app.route("/", methods=["GET", "POST"])
# def upload_file():
#     if request.method == "POST":
#         file = request.files["file"]
#         if file:
#             file.save("chat.txt")
#             chat = chat_parser.parse_chat("chat.txt")
#             results = data_analyzer.analyze_chat(chat)
#
#             # Generate a unique identifier
#             identifier = str(int(time.time()))
#
#             plotter.plot_results(results, identifier)
#
#             return render_template("results.html", results=results, identifier=identifier)
#     return render_template("upload.html")


@app.after_request
def add_header(response):
    response.headers['Cache-Control'] = 'no-store'
    return response


if __name__ == '__main__':
    app.run(debug=True)
