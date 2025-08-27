from typing import Dict

from fastapi import FastAPI, HTTPException, status
from pydantic import BaseModel, Field

# 1. FastAPI 앱 생성하기
app = FastAPI(
    title="Single-File To-Do API",
    description="A simple To-do API built with FastAPI and SQLite",
    version="0.1.0"
)

# 2. Pydantic 데이터 모델 정의
# 데이터베이스에 저장 될 기본 To-do모델
class Todo(BaseModel):
    id: int # 할일 고유의 ID
    title: str # 할일 제목
    description: str | None = None # 할일 상세설명
    completed: bool = False # 완료여부

# 새로운 To-Do 항목 설정할때 클라이언트로부터 요청(Request)받을 데이터 형태를 정의합니다.
# ID는 서버에서 자동으로 생성한다.
class TodoCreate(BaseModel):
    title: str = Field(..., min_length=1, max_length=100, description="To-do title")
    description: str | None = Field(None, max_length=100, description="To-do description")

# 3. 임시 인메모리 데이터 베이스
# 실제 DB 대신 프로그램이 실행되는 동안에 데이터를 저장하는 파이썬 딕셔네리
# 서버가 재시작되면 데이터는 사라짐
# 키(Key)는 To-do의 ID(int), 값(value)은 To-Do 객체(To-do)다.
fake_todos_db: Dict [int, Todo] = {
    1: Todo(id=1, title="Buy groceries", description="Milk, Cheese, Pizza, Fruit, Tylenol", completed=False),
    2: Todo(id=2, title="Learn Python", description="Need to find a good Python tutorial on the web", completed=False)
}
@app.post("/todos", response_model=Todo, status_code=201, tags=["todos"])
def create_todo(todo_data:TodoCreate):
    """
    할일을 생성하고 데이터베이스에 넣는다.
    :param todo_data:
    :return:
    """
    # 새로운 글을 작성하기 위해 현재 가지고있는 id+1을 더한다.
    new_id = max(fake_todos_db.keys() or [0]) + 1

    # 전달받은 데이터 (todo_data)와 새로 생성한 ID를 사용하여 완전한 To-do객체를 만든다.
    new_todo = {
        Todo(
            id=new_id,
            title=todo_data.title,
            description=todo_data.description,
            completed=False
        )
    }
    # DB 임시 딕셔네리에 넣는다.
    fake_todos_db[new_id] = new_todo
    return new_todo
@app.get("/todos", response_model=Todo, tags=["todos"])
def get_todo(todo_id:int) :
    """
    URL 경로에서 전달받은 ID와 일치하는 데이터를 찾는다.
    :param id:
    :return:
    """
    # 전달받은 id로 DB에서 찾는다.
    todo = fake_todos_db.get(todo_id)

    if not todo: # 만약 없다면
        # 못찾는다고한다.
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"할 일을 찾을 수 없습니다. : {todo_id}")

    # 찾았으니 여기까지 왔고 리턴한다.
    return todo

@app.put("/todos/{todo_id}", response_model=Todo, tags=["todos"])
def update_todo(todo_data:TodoCreate, todo_id:int): # 수정할 데이터를 TodoCreate모델에 받는다.
    """
    # 지정될 ID의 할 일을 업데이트 한다.
    :param todo_data:
    :param todo_id:
    :return:
    """
    # 체크
    if todo_id not in fake_todos_db:
        raise HTTPException(status.HTTP_404_NOT_FOUND, detail=f"할 일을 찾을 수 없습니다. : {todo_id}")

    # 기존에 저장 되어있던 할일 불러오기
    todo = fake_todos_db[todo_id]
    # 받은 todo_data를 불러온거에 수정
    todo.title = todo_data.title
    todo.description = todo_data.description

    # 해당 아이디의 DB를 수정
    fake_todos_db[todo_id] = todo

    # 리턴
    return todo

# [DELETE] 특정 ID의 To-Do 삭제
@app.delete("/todos/{todo_id}", status_code=status.HTTP_204_NO_CONTENT, tags=["todos"])
def delete_todo(todo_id: int):
    """
    지정된 ID의 할 일을 삭제합니다.
    """
    if todo_id not in fake_todos_db:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="해당 ID의 할 일을 찾을 수 없습니다.")
    del fake_todos_db[todo_id]
    # 성공적으로 삭제 시에는 내용(content) 없이 204 상태 코드를 반환하는 것이 일반적입니다.
    return

@app.get("/todos/list", status_code=200, tags=["todos"])
def list_todo():
    todo = fake_todos_db
    return todo


# 루트 경로
@app.get("/", tags=["Root"])
def read_root():
    return {"message": "To-Do List API에 오신 것을 환영합니다!"}
