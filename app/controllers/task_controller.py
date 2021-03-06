from app import db, limiter
from app.models.db_models import Task, Contest, ContestTask
from app.controllers.user_controller import solve_task, get_team_solved_tasks


def add_task(dictionary):
    _name = dictionary['name']
    task = Task.query.filter_by(name=_name).first()
    if task is not None:
        return task.id
    db.session.add(Task(**dictionary))
    db.session.commit()
    task = Task.query.filter_by(name=_name).first()
    return task.id


@limiter.limit("1 per second")
def check_flag(_id, u_id, flag):
    task = Task.query.filter_by(id=_id).first()
    solved = get_team_solved_tasks(u_id)
    if int(_id) in solved:
        return 'Вы уже решили этот таск'
    if task is None:
        return 'Нет такого таска'
    if task.flag == flag:
        solve_task(u_id, task)
        return "Правильно!"
    else:
        return "Неа :("


def get_task(_id):
    task = Task.query.filter_by(id=_id).first()
    if task is None:
        return None
    task = task.__dict__
    del task['_sa_instance_state']
    del task['flag']
    return task


def get_all_tasks():
    tasks = Task.query.filter_by(active=True).all()
    return get_task_map(tasks)


def get_tasks_by_contest_id(contest):
    # tasks = Task.query.filter_by(active=True).join(ContestTask.query.filter_by(id=c_id)).all()
    try:
        tasks = Task.query.filter_by(active=True).join(contest.contest_tasks).all()
        # tasks = Task.query.filter_by(active=True).join(Contest.query.get(int(c_id)).contest_tasks)
    except AttributeError:
        return None
    else:
        return get_task_map(tasks)

def get_task_map(task):
    task_map = {}
    for i in task:
        if i.category not in task_map.keys():
            task_map[i.category] = []
        task_map[i.category].append((i.id, i.cost))
    return task_map
