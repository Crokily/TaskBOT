# utils/formatter.py
def format_task_list(tasks: list) -> str:
    """
    Receives a list of tasks (each task is a dictionary or object) and returns a formatted string.
    Each task displays the task ID, title, status, priority, and deadline.
    """
    if not tasks:
        return "No tasks found."
    
    lines = []
    for task in tasks:
        # Assuming task has task_id, title, status, priority, deadline attributes
        line = f"Task ID: {task.task_id} | Title: {task.title} | Status: {task.status} | Priority: {task.priority} | Deadline: {task.deadline}"
        lines.append(line)
    return "\n".join(lines)
