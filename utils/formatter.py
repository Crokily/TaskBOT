# utils/formatter.py
def format_task_list(tasks: list) -> str:
    """
    接收任务列表（每个任务为字典或对象），返回格式化后的字符串。
    每个任务显示任务ID、标题、状态、优先级和截止日期。
    """
    if not tasks:
        return "No tasks found."
    
    lines = []
    for task in tasks:
        # 假设 task 有 task_id, title, status, priority, deadline 这些属性
        line = f"Task ID: {task.task_id} | Title: {task.title} | Status: {task.status} | Priority: {task.priority} | Deadline: {task.deadline}"
        lines.append(line)
    return "\n".join(lines)
