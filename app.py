import os
from flask import Flask, render_template, request
import pandas as pd
import plotly.express as px

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = 'uploads'

# Ensure the uploads directory exists at the start
if not os.path.exists(app.config['UPLOAD_FOLDER']):
    os.makedirs(app.config['UPLOAD_FOLDER'])

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/upload', methods=['POST'])
def upload_file():
    if 'file' not in request.files:
        return "No file part"
    file = request.files['file']
    if file.filename == '':
        return "No selected file"
    if file:
        file_path = os.path.join(app.config['UPLOAD_FOLDER'], file.filename)
        file.save(file_path)
        global df
        df = pd.read_csv(file_path)
        columns = df.columns.tolist()
        return render_template('select_columns.html', columns=columns)

@app.route('/plot', methods=['POST'])
def plot():
    x_axis = request.form.getlist('x_axis')
    y_axis = request.form.getlist('y_axis')
    chart_type = request.form['chart_type']
    colors = request.form.getlist('colors')  # Get the list of selected colors

    # Create the plot based on the selected chart type
    if chart_type == 'bar':
        fig = px.bar(df, x=x_axis[0] if len(x_axis) == 1 else None, y=y_axis, title="Bar Chart")
    elif chart_type == 'line':
        fig = px.line(df, x=x_axis[0] if len(x_axis) == 1 else None, y=y_axis, title="Line Chart")
    elif chart_type == 'scatter':
        fig = px.scatter(df, x=x_axis[0] if len(x_axis) == 1 else None, y=y_axis, title="Scatter Plot")
    elif chart_type == 'pie':
        if len(x_axis) == 1 and len(y_axis) == 1:
            fig = px.pie(df, names=x_axis[0], values=y_axis[0], title="Pie Chart")
        else:
            return "Pie charts require exactly one column for both X and Y axes."

    # Apply colors to each series if specified
    for i, color in enumerate(colors):
        if i < len(fig.data):  # Ensure color assignment is within bounds
            fig.data[i].marker.color = color

    graph_html = fig.to_html(full_html=False)
    return render_template('plot.html', graph_html=graph_html)

if __name__ == '__main__':
    app.run(debug=True)
