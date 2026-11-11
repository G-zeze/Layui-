# Day 7：接上 FastAPI —— 表格的数据改成从接口拿

> 本讲义按"代码 → 结构树 → 一句话规则"写。示例用的是**课程表**（`courses`），不是你的练习；看懂后换成学生，自己敲。
> 已在 FastAPI 0.143 + uvicorn 0.54 + Layui 2.13.9 上实测通过（2026-10-11）。

## 0. 今天解决什么

你在 13 号页面里问过："刷新后为什么恢复？"——因为名单 `students` 写死在页面里，只活在浏览器内存。

今天把名单搬到 **FastAPI 服务器**上，页面打开时去**问服务器要**，拿到后还是交给你已经会的 `reloadData`。

```text
以前：页面里写死 students ───────────────→ reloadData → 表格
今天：服务器上的 students → /api/students → fetch 拿到 → reloadData → 表格
                                                            ↑ 这一步你已经会，不变
```

**今天只做"读"。** 新增、编辑、删除改服务器上的数据，是 Day 8 的事（`POST` / `PUT` / `DELETE`）。

## 一条主线，5 小步

| 节   | 做什么                                    | 新东西                                   |
| ---- | ----------------------------------------- | ---------------------------------------- |
| 7-00 | 装 FastAPI，确认能运行                    | 命令行`pip`、`uvicorn`               |
| 7-01 | 写一个最小接口，浏览器里看到它返回的数据  | `@app.get`、`return` 字典、`/docs` |
| 7-02 | 让 FastAPI 同时提供你的 html 页面（同源） | `app.mount` + `StaticFiles`          |
| 7-03 | 写`/api/students`，返回学生名单         | Python 列表 → JSON                      |
| 7-04 | 页面用`fetch` 拿名单 → `reloadData`  | `fetch`、`.then`、`res.json()`     |

每一节做完都要测一次，再进下一节。

---

## 7-00 准备环境

在你的项目文件夹 `D:\Dev\Projects\Layui-` 里打开终端（VS Code：菜单"终端 → 新建终端"），逐行输入：

```bash
python --version                          # 看 Python 版本：显示 3.x 就行
python -m pip install fastapi uvicorn     # 装两个包：fastapi 写接口，uvicorn 负责把它跑起来
```

| 看到                                                                | 说明 / 怎么办                                                                                   |
| ------------------------------------------------------------------- | ----------------------------------------------------------------------------------------------- |
| `Successfully installed ...` 或 `Requirement already satisfied` | 装好了                                                                                          |
| `'python' 不是内部或外部命令`                                     | Python 没装或没加进 PATH，把报错发给我                                                          |
| 下载很慢或超时                                                      | 换国内源：`python -m pip install fastapi uvicorn -i https://pypi.tuna.tsinghua.edu.cn/simple` |

---

## 7-01 最小接口（FastAPI 复习）

在项目根目录（和 13 号 html 同一层）新建 `main.py`：

```python
from fastapi import FastAPI          # 从 fastapi 包里拿出 FastAPI 这个类

app = FastAPI()                      # 创建应用，名字叫 app（启动命令里会用到这个名字）

@app.get("/api/hello")               # 登记：有人用 GET 访问 /api/hello 时，调用下面的函数
def hello():
    return {"msg": "你好"}            # 返回字典，FastAPI 自动转成 JSON 发给浏览器
```

启动（终端里，当前目录必须是项目根目录）：

```bash
python -m uvicorn main:app --reload
```

```text
python -m uvicorn   用 uvicorn 运行
main:app            main.py 文件里的 app 变量
--reload            改了 .py 保存后自动重启（改 html 不用重启，刷新浏览器就行）
```

看到 `Uvicorn running on http://127.0.0.1:8000` 就成功了。**这个终端不要关**，关了服务器就停了；要停按 `Ctrl + C`。

**测试：**

1. 浏览器打开 `http://127.0.0.1:8000/api/hello`，看到 `{"msg":"你好"}`。
2. 打开 `http://127.0.0.1:8000/docs`，能看到 `/api/hello`，点开 → "Try it out" → "Execute"，看到同样的结果。

**一句话规则：** `@app.get("路径")` 是登记，不是调用；有人访问那个路径时，FastAPI 调用下面的函数，把 `return` 的东西转成 JSON 发回去。
（和 `table.on("tool(…)", 函数)` 是同一个思路：先登记，事件来了别人调用你。）

---

## 7-02 同源：让 FastAPI 顺便提供页面

**为什么要这一步：** 双击打开 html，地址栏是 `file:///D:/...`，这时页面里的 `fetch` 会直接失败（我实测报错：`URL scheme "file" is not supported`）。页面必须从服务器打开，地址变成 `http://127.0.0.1:8000/...`，页面和接口在同一个地址下，叫**同源**，`fetch` 才能用。

在 `main.py` **最后面**加：

```python
from fastapi.staticfiles import StaticFiles      # 放在文件顶部，和第一行 import 放一起

app.mount("/", StaticFiles(directory="."), name="static")   # 把当前文件夹的文件当网页提供出去
```

```text
app.mount("/", …)            访问 / 开头、又没被上面接口接住的地址，交给它处理
StaticFiles(directory=".")   "." 是当前文件夹：你的 html、layui-v2.13.9 都在这里
name="static"                起个名字，照写
```

**必须写在所有 `@app.get` 后面。** 它管的是"/"开头的全部地址，写在前面会把 `/api/...` 也抢走，接口就访问不到了。

**测试：** 保存后（`--reload` 会自动重启），浏览器打开：

```
http://127.0.0.1:8000/13-day6-学生管理页.html
```

页面和以前一模一样，样式、表格都正常。再确认 `http://127.0.0.1:8000/api/hello` 仍然能访问。

**一句话规则：** 以后打开页面一律走 `http://127.0.0.1:8000/文件名.html`，不再双击。

---

## 7-03 学生名单接口

示例（课程表）：

```python
courses = [                                        # Python 列表，里面是字典：一门课一个字典
    {"id": 1, "name": "HTML"},
    {"id": 2, "name": "CSS"},
]

@app.get("/api/courses")
def get_courses():
    return courses                                 # 返回列表 → 浏览器收到 JSON 数组
```

**你的任务：**

1. 在 `main.py` 里写 `students` 列表：把 13 号页面里的 8 个学生搬过来（Python 写法：键要加引号，`"studentId": "2023001"`）。
2. 写 `GET /api/students`，返回 `students`。
3. 记得写在 `app.mount(...)` 上面。

**测试：** 打开 `http://127.0.0.1:8000/api/students`，看到 8 个学生的 JSON。

**一句话规则：** Python 字典的键名 = 前端 `cols` 的 `field`。键名对不上，表格格子就是空白（和 Day 5 `data` 键名写错是同一个错误）。

---

## 7-04 页面用 fetch 拿名单

**文件：** 复制 `13-day6-学生管理页.html`，改名 `14-day7-接口版学生管理页.html`（13 号保留存档）。

### 新东西：fetch

```js
fetch("/api/courses").then(function(res){      // fetch：向服务器要 /api/courses；回来后 then 里的函数被调用，res 是服务器的回复（像一封信）
    return res.json();                         // res.json()：拆信，把 JSON 文字变成 JS 数组；return 交给下一个 then
}).then(function(list){                        // list：拆出来的数组（就是服务器 return 的 courses）
    courses = list;                            // 存进页面变量
    table.reloadData("courseTable", {data: courses, page: {curr: 1}});   // 按新数据重画——你已经会的那一步
});
```

```text
fetch("/api/courses")          发请求。"/" 开头 = 同一个服务器（7-02 的同源）
.then(function(res){ … })      回复到了，fetch 调用这个函数，把回复交给 res
    return res.json()          拆出数据也要一点时间，所以 return 出去，交给下一个 then
.then(function(list){ … })     数据拆好了，调用这个函数，把数组交给 list
```

**为什么不能直接 `const list = fetch(...)`：** 请求要走网络，不是马上回来。和 `layer.confirm` 一样——确定函数要等用户点了才执行；`then` 里的函数要等服务器回复了才执行。写在 `then` 外面的代码会先执行，那时数据还没到。

`res`、`list` 都是**调用者传进来的**：名字自己起，值由 `fetch` / `then` 给。

### 你的任务（在 14 号文件里）

1. 把 `let students = [ 8 个学生 ];` 改成空数组 `let students = [];`。
2. `table.render` 不动（`data: students`，一开始是空的）。
3. 在 `table.render(...)` 后面写 `fetch("/api/students")`，照上面的示例：拿到后 `students = list;` 再 `reloadData`。
4. 可以在第二个 `then` 里先 `console.log(list)` 看一眼，看完删掉。

**测试（地址必须是 `http://127.0.0.1:8000/14-day7-接口版学生管理页.html`）：**

1. 打开页面，表格有 8 个学生。
2. 去 `main.py` 把某个学生改个名字，保存；回到页面刷新——表格跟着变。**这证明数据来自服务器。**
3. 在页面上删除一个学生，再刷新——他又回来了。为什么？（提示：删除改的是哪里的 `students`？这是 Day 8 要解决的。）
4. 实验：双击打开 14 号文件（`file://`），按 F12 看 Console 的红字，然后关掉。

## 常见错误（先自查）

| 现象                                                              | 原因                                                 |
| ----------------------------------------------------------------- | ---------------------------------------------------- |
| 访问`/api/students` 显示 `{"detail":"Not Found"}`             | 接口写在了`app.mount` 后面；或路径拼错             |
| 页面能开，表格空白，Console 有`Failed to fetch` / `file` 字样 | 双击打开的，不是从`http://127.0.0.1:8000/...` 打开 |
| 表格有行数但格子空白                                              | Python 字典的键名和`cols` 的 `field` 不一致      |
| `NameError` / `SyntaxError`（终端里红字）                     | Python 拼写或缩进错；看终端里给出的行号              |
| 改了`main.py` 没反应                                            | 启动时没加`--reload`，或终端已关；重新启动         |
| `then` 里 `students` 有数据，但表格不变                       | 忘了`reloadData`，或第一个参数不是表格 `id`      |

## 验收（写完口头回答）

1. 为什么双击打开 html 时 `fetch` 拿不到数据，从 `http://127.0.0.1:8000/` 打开就可以？
2. 测试第 3 步：删掉的学生刷新后又回来了，原因是什么？要真正删掉，需要谁去改服务器上的 `students`？

## 和后面的衔接

- **Day 8：** `POST /api/students`（新增）、`DELETE /api/students/{id}`（删除）、`PUT`（编辑），配合 Pydantic 模型；前端用 `fetch` 带上 `method` 和数据，成功后重新拿名单再 `reloadData`。
- **之后：** 数据从 Python 列表换成 SQLite，刷新、重启服务器都不丢。
