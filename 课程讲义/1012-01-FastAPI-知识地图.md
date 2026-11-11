# FastAPI 知识地图（第二阶段总路线）

> 每个知识点：是什么 → 你以前在哪写过 → 学生管理系统里用在哪。学到哪一节先看这里定位，细节看对应讲义，写法查 [速查笔记](00-速查笔记.md) 第十一章。
> "旧代码"指 `D:\Dev\Projects\python_study\FAST_API\my_code\`；"PDF"指同目录 `文档\FastAPI文档.pdf` 的页码。

## 1. 一次请求经过哪几步

```text
浏览器（Layui 页面）                               服务器（main.py）
fetch("/api/students?keyword=张")  ── 请求 ──▶    uvicorn 收到，交给 app
    方法 GET　路径 /api/students                    app 按"方法 + 路径"找到登记的函数并调用
    查询参数 keyword=张                             函数 return 列表
                                   ◀── 响应 ──    FastAPI 转成 JSON，状态码 200
.then(res.json()) → list → students = list → reloadData → 表格
```

## 2. 基础名词

| 名词 | 是什么 | 例子 |
| --- | --- | --- |
| 方法 | 这次请求干什么：GET 拿、POST 新增、PUT 改、DELETE 删 | 地址栏打开网址永远是 GET |
| 路径 | 端口后、`?` 前那段 | `/api/students` |
| 路径参数 | 路径里会变的一段 | `/api/students/2023001` 的 `2023001` |
| 查询参数 | `?` 后的 `名=值`，`&` 连接 | `?keyword=张&page=1` |
| 请求体 | 随请求送去的一包数据（GET 不用） | 新增时送整个学生对象 |
| JSON | 前后端通用的数据文字 | Python 字典 ⇄ JSON ⇄ JS 对象 |
| 状态码 | 结果编号 | 200 成功、404 找不到、405 方法不对、422 数据不合格 |

## 3. 路线

| 节 | 知识点 | 是什么 | 旧代码 | PDF | 系统里用在哪 | 状态 |
| --- | --- | --- | --- | --- | --- | --- |
| F1 | [第一个接口](1012-02-FastAPI-F1-第一个接口.md) | `@app.get` 登记，`return` 变 JSON | main01、02 | 5～8 | `/api/hello` | ✅ |
| F2 | [让服务器提供页面](1012-03-FastAPI-F2-让服务器提供页面.md) | `StaticFiles` 把 html 也发给浏览器 | — | 48 | 页面从 8000 打开 | ✅ |
| F3 | [名单接口 + fetch](1012-04-FastAPI-F3-名单接口与fetch.md) | 返回列表；页面 `fetch` 要数据 | main14 | 40 | 表格数据来自服务器 | ✅ |
| F4 | 路径参数 | 路径里写 `{名}`，函数同名参数接住 | main03、06、08 | 10、19 | 查 / 删 / 改某一个学生 | 下一步 |
| F5 | `HTTPException` | 出错时 `raise`，回错误码和 `{"detail":…}` | main11 | 35 | 学号不存在回 404 | |
| F6 | 查询参数 | 不在路径里的参数从 `?` 后取 | main04、06、07 | 12、16 | 搜索、分页 | |
| F7 | 请求体 + `BaseModel` | 模型类说明送来的数据长什么样 | main05、09 | 14 | `POST` 新增学生 | |
| F8 | `Field` 校验 + 422 | 字段规则，不合格自动 422 | main09 | 23 | 学号、姓名不能为空 | |
| F9 | `PUT` / `DELETE` | 修改、删除 | — | 62 | 编辑、删除写回服务器 | |
| F10 | 表格直连接口 | table `url` 模式 + `{code,msg,count,data}` | main14 | 40 | 后端分页 | |
| F11 | 数据库 | 数据存进数据库，重启不丢 | — | 49～76 | 持久保存 | |
| F12 | `APIRouter` | 按功能拆文件 | — | 85～89 | 项目变大后 | |

## 4. 暂时不学

表单 `Form`（main10，我们发 JSON）、文件上传（main11）、`Request`（main12）、`response_model`（main13，F10 后再看）、文件响应（main15）、`async def`（现在没有要 await 的，一律普通 `def`）、跨域 CORS（同源用不到）、中间件。

## 5. 旧代码里过时的写法

| 旧写法 | 现在写法 |
| --- | --- |
| `Query(..., regex='…')`（main07 第 43 行） | `pattern='…'` |
| `Field(..., min_items=1)`（main09 第 54 行） | `min_length=1` |
