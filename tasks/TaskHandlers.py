from config import jwt
from tasks.models import TaskModel, TaskID, AddRequest, EditRequest
from fastapi import Depends, APIRouter

from storage.repository import TaskRepo

router = APIRouter(prefix="/tasks", tags=["tag1"])

@router.post("/add")
async def add_task(task: AddRequest, curr_user = Depends(jwt.get_current_user)) -> TaskID:
    new_task_id = await TaskRepo.add_task_DB(task, curr_user["id"])
    return new_task_id

@router.get("/get")
async def get_task(curr_user = Depends(jwt.get_current_user)) -> list[TaskModel]:
    tasks = await TaskRepo.get_tasks_DB(curr_user["id"])
    return tasks

@router.delete("/{task_id}")
async def delete_task(task_id: int, curr_user = Depends(jwt.get_current_user)) -> TaskID:
    del_task_id = await TaskRepo.delete_task_DB(task_id, curr_user["id"])
    return del_task_id

@router.patch("/{task_id}")
async def edit_task(req: EditRequest, curr_user = Depends(jwt.get_current_user)) -> TaskID:
    edit_task_id = await TaskRepo.edit_task_DB(req, curr_user["id"])
    return edit_task_id