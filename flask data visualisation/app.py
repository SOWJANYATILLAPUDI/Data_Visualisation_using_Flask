import plotly.graph_objects as go
from flask import Flask, render_template, request, redirect, url_for
import pandas as pd
from pymongo import MongoClient

app = Flask(__name__)
client = MongoClient('mongodb://localhost:27017/')
db = client['data_db']


@app.route('/')
def index():
    return render_template('index.html')

@app.route('/form', methods=['GET', 'POST'])
def form():
    if request.method == 'POST':
        # Save the data to MongoDB
        data = {col: request.form[col] for col in request.form}
        db.form_data.insert_one(data)

        

    return render_template('form.html')

@app.route('/excel', methods=['GET', 'POST'])
def excel():
    if request.method == 'POST':
        # Read the uploaded Excel file and save the data to MongoDB
        file = request.files['file']
        if file.filename.endswith('.xlsx'):
            data_df = pd.read_excel(file)
            data = data_df.to_dict(orient='records')
            db.excel_data.insert_many(data)
    return render_template('excel.html')

@app.route('/piechart')
def piechart():
    # Fetch data from MongoDB for pie charts
    data = list(db.form_data.find({}, {'_id': 0}))

    # Create a list to store pie chart HTML
    piechart = []

    # Create a pie chart for each column
    for column in data[0]:
        column_counts = {item[column] for item in data if item[column]}
        labels = list(column_counts)
        values = [len([item for item in data if item[column] == label]) for label in labels]
        fig = go.Figure(data=[go.Pie(labels=labels, values=values)])
        piechart_html = fig.to_html(full_html=False)
        piechart.append(piechart_html)

    return render_template('piechart.html', piechart=piechart)


if __name__ == '__main__':
    app.run(debug=True)
