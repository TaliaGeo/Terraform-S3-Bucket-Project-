from flask import Flask, render_template, request
from DeploymentTracker import DeploymentTracker
import io
import contextlib

app = Flask(__name__)
tracker = DeploymentTracker()

@app.route('/')
def home():
    return render_template('index.html')

@app.route('/load', methods=['GET', 'POST'])
def load():
    message = None
    if request.method == 'POST':
        file_path = request.form.get('file_path')
        output = io.StringIO()
        with contextlib.redirect_stdout(output):
            tracker.read_records(file_path)
        message = output.getvalue().strip()
    records = tracker.get_records()
    return render_template('load.html', records=records, message=message)

@app.route('/add', methods=['GET', 'POST'])
def add():
    message = None
    if request.method == 'POST':
        app_name = request.form.get('application')
        env = request.form.get('environment')
        version = request.form.get('version')
        deploy_date = request.form.get('deployment_date')
        deployed_by = request.form.get('deployed_by')
        output = io.StringIO()
        with contextlib.redirect_stdout(output):
            tracker.add_record(app_name, env, version, deploy_date, deployed_by)
        message = output.getvalue().strip()
    records = tracker.get_records()
    return render_template('add.html', records=records, message=message)

@app.route('/update', methods=['GET', 'POST'])
def update():
    message = None
    if request.method == 'POST':
        orig_app = request.form.get('original_application')
        orig_env = request.form.get('original_environment')
        orig_ver = request.form.get('original_version')
        new_app = request.form.get('new_application')
        new_env = request.form.get('new_environment')
        new_ver = request.form.get('new_version')
        new_date = request.form.get('new_deployment_date')
        new_by = request.form.get('new_deployed_by')
        output = io.StringIO()
        with contextlib.redirect_stdout(output):
            tracker.update_record(
                orig_app, orig_env, orig_ver,
                Application=new_app,
                Environment=new_env,
                Version=new_ver,
                DeploymentDate=new_date,
                DeployedBy=new_by
            )
        message = output.getvalue().strip()
    records = tracker.get_records()
    return render_template('update.html', records=records, message=message)

@app.route('/delete', methods=['GET', 'POST'])
def delete():
    message = None
    if request.method == 'POST':
        app_name = request.form.get('application')
        output = io.StringIO()
        with contextlib.redirect_stdout(output):
            tracker.delete_record(app_name)
        message = output.getvalue().strip()
    records = tracker.get_records()
    return render_template('delete.html', records=records, message=message)

@app.route('/save')
def save():
    output = io.StringIO()
    with contextlib.redirect_stdout(output):
        tracker.save_records()
    message = output.getvalue().strip()
    records = tracker.get_records()
    return render_template('save.html', records=records, message=message)

@app.route('/display')
def display():
    records = tracker.get_records()
    return render_template('display.html', records=records)

if __name__ == '__main__':
    app.run(debug=True, port=5001)
