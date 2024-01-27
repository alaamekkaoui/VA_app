from datetime import datetime
import os
from flask import Flask, render_template, request, redirect, session, url_for,jsonify
from gmail_handler import *
from task_manager import TaskManager

app = Flask(__name__)
app.secret_key = "it's a secret"
task_manager = TaskManager('mongodb+srv://test:test123@cluster0.htaswor.mongodb.net/?retryWrites=true&w=majority','DB_PFA')

GOOGLE_API_KEY = 'AIzaSyCbPhOCx7wcrm_Y_z6FtR5lMKYhKkPSOsk'
initialize_genai(GOOGLE_API_KEY)


@app.route('/login')
def login():
    GMAIL = authenticate_gmail()
    auth_url = GMAIL.authorization_url()
    return redirect(auth_url)


@app.route('/')
def index():
    if authenticate_gmail():
        if 'user_email' in session:
            user_email = session['user_email']
            tasks = task_manager.view_tasks()
            return render_template('index.html', user_email=user_email, tasks=tasks)
        else:
            return redirect(url_for('login'))


@app.route('/add_task', methods=['GET', 'POST'])
def add_task():
    if request.method == 'POST':
        if 'user_email' in session:
            user_email = session['user_email']
            name = request.form.get('name')
            description = request.form.get('description')
            category = request.form.get('category')
            task_date_str = request.form.get('finish_date')
            task_date = datetime.strptime(task_date_str, '%Y-%m-%d')

            # Call the Bard API function to generate short description
            prompt = "Generate a short description for the task depending on the following category" + category + " and name" + name
            short_description = generate_short_description(prompt)

            # Add the task with the generated short description
            task_manager.add_task(user_email, name, short_description, category, task_date)
            return redirect('/list_tasks')

    return render_template('add_task.html')

@app.route('/update/<numeric_id>', methods=['GET', 'POST'])
def update_task(numeric_id):
    if request.method == 'GET':
        task = task_manager.get_task_by_numeric_id(int(numeric_id))
        return render_template('update.html', task=task)
    elif request.method == 'POST':
        name = request.form.get('name')
        description = request.form.get('description')
        category = request.form.get('category')
        completed = request.form.get('completed') == 'on'
        task_manager.update_task(int(numeric_id), name, description, category, completed)
        return redirect('/list_tasks')


@app.route('/delete/<numeric_id>')
def delete_task(numeric_id):
    task_manager.delete_task(int(numeric_id))
    return redirect('/list_tasks')


@app.route('/list_tasks')
def list_tasks():
    tasks = task_manager.view_tasks()
    return render_template('list_tasks.html', tasks=tasks)


@app.route('/logout')
def logout():
    session.clear()
    try:
        os.remove('storage.json')
        print('storage.json deleted successfully.')
    except FileNotFoundError:
        print('storage.json not found.')

    return redirect(url_for('index'))


@app.route('/fetch_emails')
def fetch_emails():
    # Call your Gmail API script
    emails = fetch_unread_emails()
    return render_template('email.html', emails=emails)


@app.route('/compose', methods=['GET', 'POST'])
def compose_email():
    if request.method == 'POST':
        to = request.form.get('to')
        subject = request.form.get('subject')
        body = request.form.get('body')

        send_email(to, subject, body)

        return redirect(url_for('compose_email'))  # Redirect to inbox after sending email

    return render_template('compose.html')


@app.route('/complete/<numeric_id>')
def complete_task(numeric_id):
    if 'user_email' in session:
        user_email = session['user_email']
        result = task_manager.update_completion_status(int(numeric_id), True)
        return redirect(url_for('list_tasks'))
    else:
        return redirect(url_for('login'))


@app.route('/add_meeting')
def add_meeting():
    # Fetch unread emails
    unread_emails = fetch_unread_emails()
    if not unread_emails:
        return "No unread emails found."

    email_data = unread_emails[0]

    # Process and generate confirmation
    meeting_data = get_meeting_data(email_data)
    if meeting_data:
        result = add_meeting_to_db()
        send_email(email_data.get('Sender', 'No Sender Email'), 'Meeting Confirmation', meeting_data['summary'])
        print(result)
        return result
    else:
        return "Unable to parse meeting data."

@app.route('/send_confirmation/<email_index>', methods=['POST'])
def send_confirmation(email_index):

    unread_emails = fetch_unread_emails()

    if not unread_emails:
        return "No unread emails found."

    try:
        selected_email = unread_emails[int(email_index)]
        generate_and_send_response(selected_email)

        print("|-----------------------------------------------------------------------------------------------|")
        print("Confirmation email sent successfully to " + selected_email.get('Sender'))
        print("|-----------------------------------------------------------------------------------------------|")
        return "Confirmation email sent successfully."
    except IndexError:
        return "Invalid email index."

if __name__ == '__main__':
    print("|----------Starting app script----------|")
    app.run(debug=False)
