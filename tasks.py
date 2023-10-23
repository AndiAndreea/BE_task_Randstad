import argparse
import json
import os
from datetime import datetime

RANDSTAD_ASCII = """
\033[34m____ ____ _  _ ___  ____ ___ ____ ___     ___ ____ ____ ___ \033[0m
\033[34m|__/ |__| |\ | |  \ [__   |  |__| |  \     |  |___ [__   |  \033[0m
\033[34m|  \ |  | | \| |__/ ___]  |  |  | |__/     |  |___ ___]  |   \033[0m                                                          
"""

FILE_NAME = "tasks.json"


class Task:
    def __init__(self, title, desc, tags=None):
        self.id = None
        self.title = title
        self.desc = desc
        self.status = "todo"
        self.tags = tags if tags else []
        self.created_at = datetime.now().strftime('%Y-%m-%d %H:%M')
        self.started_at = None
        self.finished_at = None


def load_tasks():
    """
    Creates file to store tasks. The try and except was added to look for file format error and permission error.
    :return: List with task objects.
    """
    if not os.path.exists(FILE_NAME):
        return []

    try:
        with open(FILE_NAME, "r") as file:
            tasks_data = json.load(file)

        tasks = []
        for task_data in tasks_data:
            task_obj = Task(task_data['title'], task_data['desc'], task_data.get('tags'))
            task_obj.id = task_data.get('id')
            task_obj.status = task_data.get('status', 'todo')
            task_obj.created_at = task_data.get('created_at')
            task_obj.started_at = task_data.get('started_at')
            task_obj.finished_at = task_data.get('finished_at')
            tasks.append(task_obj)

        return tasks

    except json.JSONDecodeError:
        print("\033[31mError: Invalid JSON format in the file.\033[31m")
        return []
    except Exception as e:
        print(f"\033[31mAn error occurred: {e}\033[31m")
        return []


def save_tasks(tasks):
    """
    Transforms and saves dictionaries to JSON formatted string.
    :param tasks: List of task objects.
    :return: Writes to JSON file.
    """
    task_dicts = []

    for task in tasks:
        task_dict = task.__dict__
        task_dicts.append(task_dict)

    try:
        with open(FILE_NAME, "w") as file:
            json.dump(task_dicts, file, indent=4)
    except json.JSONEncodeError:
        print("\033[31mError: Failed to convert tasks to JSON format.\033[31m")
    except IOError:
        print(f"\033[31mError: Unable to write to file {FILE_NAME}.\033[31m")
    except Exception as e:
        print(f"\033[31mAn unexpected error occurred: {e}\033[31m")


def new_task(title, desc, tags):
    """
    Creates a new object task and saves it to the JSON file.
    :param title: Title of the task.
    :param desc: Description of the task.
    :param tags: List of strings.
    """
    tasks = load_tasks()
    if tasks:
        highest_id = max(task.id for task in tasks)
    else:
        highest_id = 0

    task = Task(title, desc, tags)
    task.id = highest_id + 1
    tasks.append(task)
    save_tasks(tasks)


def view_task(task_id):
    """
    Shows details of a task.
    :param task_id: ID of a task (positive int).
    :return: Returns the dictionary for task ID (__dict__ attribute of instance).
    """
    if not isinstance(task_id, int) or task_id <= 0:
        print("\033[31mError: Invalid task ID provided. Please provide a positive integer.\033[31m")
        return None

    tasks = load_tasks()
    for task in tasks:
        if task.id == task_id:
            return vars(task)
    return None


def delete_task(task_id):
    """
    Deletes a task by its ID.
    :param task_id: ID of the task to delete.
    """
    tasks = load_tasks()

    task_to_delete = None
    for task in tasks:
        if task.id == task_id:
            task_to_delete = task
            break

    if task_to_delete:
        tasks.remove(task_to_delete)
        save_tasks(tasks)
        print(f"\033[32mTask with ID {task_id} deleted successfully.\033[32m")
    else:
        print(f"\033[33mTask with ID {task_id} not found.\033[33m")


def update_status(task_id, status):
    """
    Update the status of a specific task.
    :param task_id: ID (int) of the task we want to change the status.
    :param status: Options of the status: start, in_progress, finish
    :return:
    """
    if not isinstance(task_id, int) or task_id <= 0:
        print("\033[31mError: Invalid task ID provided. Please provide a positive integer.\033[31m")
        return None

    try:
        tasks = load_tasks()
        for task in tasks:
            if task.id == task_id:
                if status == 'start':
                    task.status = 'in_progress'
                    task.started_at = datetime.now().strftime('%Y-%m-%d %H:%M')
                elif status == 'finish':
                    task.status = 'done'
                    task.finished_at = datetime.now().strftime('%Y-%m-%d %H:%M')
                save_tasks(tasks)
                return True
        return False
    except AttributeError:
        print(f"\033[31mError: Malformed task data for task ID {task_id}.\033[31m")
        return False
    except Exception as e:
        print(f"\033[31mAn unexpected error occurred: {e} \033[31m")
        return False


def update_task(task_id, title=None, desc=None):
    """
    Updates the title and/or description of a task.
    :param task_id: ID (int) of the task to be updated.
    :param title: New title for the task. (optional)
    :param desc: New description for the task. (optional)
    """
    tasks = load_tasks()
    task_found = False

    for task in tasks:
        if task.id == task_id:
            task_found = True
            if title:
                task.title = title
            if desc:
                task.desc = desc
            break

    if not task_found:
        raise ValueError(f"\033[33mNo task found with ID {task_id}\033[33m")

    save_tasks(tasks)


def list_tasks(status=None, tag=None, sort=None, search=None):
    """
    Function returns the tasks that have a specific status or tag.
    Tasks can e also sorted by creation, started or finished time.
    You can also search a specific task by a given string. It will check if that sting is in the title or description.

    :param status: Options of the status: 'todo', 'in_progress', 'done'.
    :param tag: List of strings.
    :param sort: Options for sort: 'created_at', 'started_at', 'finished_at'.
    :param search: Will search the given string in the title or description of the task.
    :returns: A list with tasks.
    """
    tasks = load_tasks()

    if status:
        filtered_tasks = []
        for task in tasks:
            if task.status == status:
                filtered_tasks.append(task)
        tasks = filtered_tasks

    if tag:
        filtered_tasks = []
        for task in tasks:
            if tag in task.tags:
                filtered_tasks.append(task)
        tasks = filtered_tasks

    if search:
        filtered_tasks = []
        for task in tasks:
            if search in task.title or search in task.desc:
                filtered_tasks.append(task)
        tasks = filtered_tasks

    if sort:
        def sort_key(task):
            value = getattr(task, sort)
            if value is None and sort in ['created_at', 'started_at', 'finished_at']:
                return '0000-00-00 00:00'
            return value

        tasks.sort(key=sort_key)

    result = []
    for task in tasks:
        result.append(vars(task))

    return result


def full_help(parser):
    parser.print_help()
    subparsers_actions = [
        action for action in parser._actions
        if isinstance(action, argparse._SubParsersAction)
    ]

    for subparsers_action in subparsers_actions:
        for choice, subparser in subparsers_action.choices.items():
            print("\033[34m\nCommand '{}'\033[34m".format(choice))
            print("\033[33m-\033[33m" * len("Command '{}'".format(choice)))
            subparser.print_help()


def main():
    print(RANDSTAD_ASCII)
    parser = argparse.ArgumentParser(description=" ***** CLI Task Manager ***** ", add_help=False)

    parser.add_argument('--help', action='store_true',
                        help="Show detailed help message including subcommands.")
    subparsers = parser.add_subparsers(dest='command')

    new_task_parser = subparsers.add_parser('new_task')
    new_task_parser.add_argument('--title', required=True, help="Title of the task")
    new_task_parser.add_argument('--desc', required=True, help="Description of the task")
    new_task_parser.add_argument('--tags', nargs='+', default=[],
                                 help="List of tags for the task, separated by spaces")

    task_parser = subparsers.add_parser('task')
    task_parser.add_argument('id', type=int, help="ID of the task to interact with")
    task_parser.add_argument('action', choices=['start', 'finish', 'view'], default='view',
                             help="Action to perform on the task: start, finish, or view")

    delete_task_parser = subparsers.add_parser('delete')
    delete_task_parser.add_argument('id', type=int, help="ID of the task to delete")

    update_task_parser = subparsers.add_parser('update_task')
    update_task_parser.add_argument('id', type=int, help="ID of the task to update title and description")
    update_task_parser.add_argument('--title', help="New title for the task")
    update_task_parser.add_argument('--desc', help="New description for the task")

    list_tasks_parser = subparsers.add_parser('tasks')
    list_tasks_parser.add_argument('--status', choices=['todo', 'in_progress', 'done'],
                                   help="Filter tasks by their status: todo, in_progress, or done")
    list_tasks_parser.add_argument('--tag', help="Filter tasks by a specific tag")
    list_tasks_parser.add_argument('--sort', choices=['created_at', 'started_at', 'finished_at'],
                                   help="Sort tasks by their timestamps: created_at, started_at, or finished_at")
    list_tasks_parser.add_argument('--search', help="Search tasks by a keyword in their title or description")

    args, unknown = parser.parse_known_args()

    if args.help:
        full_help(parser)
        return

    args = parser.parse_args()

    if args.command is None:
        response = input("\033[1mNo parameters provided. Do you need help? (yes/no): \033[1m").lower().strip()
        if response == 'yes':
            full_help(parser)
            return

    if args.command == 'new_task':
        new_task(args.title, args.desc, args.tags)
    elif args.command == 'task':
        if args.action == 'view':
            print(json.dumps(view_task(args.id), indent=4))
        else:
            update_status(args.id, args.action)
    elif args.command == 'delete':
        delete_task(args.id)
    elif args.command == 'update_task':
        try:
            update_task(args.id, args.title, args.desc)
        except ValueError as e:
            print(e)
    elif args.command == 'tasks':
        tasks = list_tasks(args.status, args.tag, args.sort, args.search)
        for task in tasks:
            print(json.dumps(task, indent=4))


if __name__ == "__main__":
    main()
