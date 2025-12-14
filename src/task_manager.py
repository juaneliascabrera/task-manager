
class Task:
    def __init__(self, id, description):
        self.id = id
        self.description = description
        self.completed = False
    
class TaskManager:
    def __init__(self):
        self.pending_tasks = {}
        self.next_id = 0

    def add_task(self, description):
        #Creamos el nuevo objeto tarea
        new_task = Task(
            id=self.next_id,
            description=description
        )
        self.pending_tasks[self.next_id] = new_task
        self.next_id += 1
        return self.next_id - 1
        
    def contains_task(self, task_id):
        return task_id in self.pending_tasks
    
    def tasks_count(self):
        return len(self.pending_tasks)