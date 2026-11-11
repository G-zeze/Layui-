from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles

app=FastAPI()

@app.get("/api/hello")
def hello():
    return {"msg":"你好"}

@app.get("/api/me")
def me():
    return{"name":"zeze","class":"软件2501"}

students = [
    {"studentId": "2023001", "studentName": "张三", "studentGender": "男", "studentClass": "一班"},
    {"studentId": "2023002", "studentName": "李四", "studentGender": "女", "studentClass": "二班"},
    {"studentId": "2023003", "studentName": "王五", "studentGender": "男", "studentClass": "三班"},
    {"studentId": "2023004", "studentName": "赵六", "studentGender": "女", "studentClass": "四班"},
    {"studentId": "2023005", "studentName": "孙七", "studentGender": "男", "studentClass": "五班"},
    {"studentId": "2023006", "studentName": "周八", "studentGender": "女", "studentClass": "六班"},
    {"studentId": "2023007", "studentName": "吴九", "studentGender": "男", "studentClass": "七班"},
    {"studentId": "2023008", "studentName": "郑十", "studentGender": "女", "studentClass": "八班"},
]
@app.get("/api/students")
def stu():
    return students

app.mount("/",StaticFiles(directory="."),name="static")