from flask import session
from pymongo import MongoClient
from bson import ObjectId
from datetime import date, datetime
from bs4 import BeautifulSoup


class TaskManager:
    def __init__(self, connection_uri, database_name):
        # Connect to MongoDB
        self.client = MongoClient(connection_uri)
        self.db = self.client[database_name]
        self.tasks_collection = self.db["tasks"]
        try:
            self.client.admin.command('ping')
            print("|---------Successfully connected to MongoDB!-------|")
        except Exception as e:
            print(f"|---------Failed to connect to MongoDB. -------| \n |------ Error: {e}-------|")

    
    def add_task(self, user_email, name, description, category, finish_date, completed=False):
        # Convert date to datetime if it's a date object
        if isinstance(finish_date, date):
            finish_date = datetime.combine(finish_date, datetime.min.time())

        # Find the maximum numeric_id in the collection and increment by 1
        max_numeric_id = self.tasks_collection.find_one(sort=[("numeric_id", -1)])
        next_numeric_id = (max_numeric_id["numeric_id"] + 1) if max_numeric_id else 0

        task = {
            'numeric_id': next_numeric_id,
            'user_email': user_email,
            'name': name,
            'description': description,
            'category': category,
            'finish_date': finish_date,
            'completed': completed
        }

        result = self.tasks_collection.insert_one(task)
        #print(f'Task "{name}" added successfully with numeric ID: {next_numeric_id} for user: {user_email}')
        return f'Task "{name}" added successfully with numeric ID: {next_numeric_id} for user: {user_email}'

    def view_tasks(self):
        tasks_cursor = self.tasks_collection.find()
        tasks = list(tasks_cursor)  # Convert the cursor to a list of dictionaries
        task_count = len(tasks)

        if task_count == 0:
            print("No tasks available.")
            return []
        else:
            print("|-----------------Tasks-----------------|") 
            print(f'Total tasks: {task_count}')

            # Create a dictionary to store the count for each category
            category_count = {}

            for task in tasks:
                category = task.get("category", "Uncategorized")
                category_count[category] = category_count.get(category, 0) + 1

            # Display the count for each category
            for category, count in category_count.items():
                print(f'Tasks in Category "{category}": {count}')

            print("|-----------------End of Tasks-----------------|") 

            return tasks



    def get_task_by_numeric_id(self, numeric_id):
        return self.tasks_collection.find_one({'numeric_id': numeric_id})

    def update_task(self, numeric_id, name, description, category, completed):
        task = {
            'name': name,
            'description': description,
            'category': category,
            'completed': completed
        }
        result = self.tasks_collection.update_one({'numeric_id': numeric_id}, {'$set': task})
        if result.modified_count > 0:
            print(f'Task with numeric ID {numeric_id} updated successfully.')
            return f'Task updated successfully.'
        else:
            print(f'Invalid numeric ID {numeric_id} or no modifications made.')
            return 'Invalid numeric ID or no modifications made.'

    def delete_task(self, numeric_id):
        result = self.tasks_collection.delete_one({'numeric_id': numeric_id})
        if result.deleted_count > 0:
            print(f'Task with numeric ID {numeric_id} deleted successfully.')
            return f'Task deleted successfully.'
        else:
            print(f'Invalid numeric ID {numeric_id} or task not found.')
            return 'Invalid numeric ID or task not found.'
    def update_completion_status(self, numeric_id, completed):
        task = {
            'completed': completed
        }
        result = self.tasks_collection.update_one({'numeric_id': numeric_id}, {'$set': task})
        if result.modified_count > 0:
            status = "completed" if completed else "incomplete"
            print(f'Task with numeric ID {numeric_id} marked as {status}.')
            return f'Task marked as {status}.'
        else:
            print(f'Invalid numeric ID {numeric_id} or no modifications made.')
            return 'Invalid numeric ID or no modifications made.'
    from datetime import datetime


