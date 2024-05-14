from flask import Flask, render_template, request, redirect, url_for
import os

app = Flask(__name__)
basedir = os.path.abspath(os.path.dirname(__file__))
todo_file = os.path.join(basedir, "todo_list.txt")

todo_list = []

# load the to-do list from a file
try:
    with open(todo_file, "r") as file:
        for line in file:
            todo_list.append(line.strip())
except FileNotFoundError:
    # ignore the error if the file does not exist, simply start with an empty list
    print("No saved items found") 

@app.route("/")
def index():
    return render_template("index.html", todo_list=todo_list)

if __name__ == "__main__":
    app.run(debug=True)