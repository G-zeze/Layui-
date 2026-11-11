# F2 让服务器提供页面（StaticFiles）

> 产出：`main.py` 末尾加 `app.mount(...)`，能从 `http://127.0.0.1:8000/13-day6-学生管理页.html` 打开页面。　旧代码对应：没写过（PDF 第 48 页）。

## 1. 这一步解决什么

最终目标：页面里的学生名单改成从服务器拿。这一步只是准备：**让页面也从服务器打开**。因为下一步页面要 `fetch` 找服务器要数据，而页面从哪来，`fetch` 就去哪要。

| 打开方式 | 地址栏 | 谁把页面给浏览器 | 页面里 `fetch("/api/...")` |
| --- | --- | --- | --- |
| 双击文件 | `file:///D:/...` | 浏览器自己读硬盘 | 去硬盘找 → 浏览器不允许，失败 |
| 地址栏输入 | `http://127.0.0.1:8000/文件名.html` | 服务器发过来 | 去 8000 要 → 能拿到 |

## 2. 代码

```python
from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles                 # 工具：按文件名找文件、发文件

app = FastAPI()

@app.get("/api/hello")
def hello():
    return {"msg": "你好"}

app.mount("/", StaticFiles(directory="."), name="static")   # 写在最后：上面没登记的地址，一律去当前文件夹找同名文件
```

## 3. 是什么 + 对应

| 写法 | 是什么 | 对应 |
| --- | --- | --- |
| `app.mount("/", …)` | 挂载：`/` 开头、上面接口都没接住的地址，交给它 | `/13-day6-学生管理页.html` 交给它 |
| `StaticFiles(directory=".")` | 去 `.`（当前文件夹）按文件名找文件，原样发回 | html、`layui-v2.13.9/` 都在当前文件夹 |
| `name="static"` | FastAPI 内部用的名字 | 照写 |

**为什么必须写在最后：** 服务器从上往下对地址。`mount` 管所有 `/` 开头的地址，写在前面会把 `/api/...` 也拦走，接口就用不了。

**同源：** 页面和数据都来自同一个地址 `127.0.0.1:8000`。这是做完之后得到的结果，先懂上面的表，名词记不住没关系。

## 4. 结构树

```text
main.py
├── import FastAPI、StaticFiles
├── app = FastAPI()
├── @app.get("/api/...") ……       所有接口
└── app.mount("/", StaticFiles(directory="."), name="static")   最后一行

浏览器要 /api/hello               → 登记过 → 调用 hello()
浏览器要 /13-day6-学生管理页.html  → 没登记 → mount → 找到文件 → 发回
```

## 5. 一句话规则

**`mount` 写在文件最后；以后页面一律从 `http://127.0.0.1:8000/文件名.html` 打开，不再双击。**

## 6. 实测现象

| 你做 | 看到 |
| --- | --- |
| 加了 `mount`，打开 `/13-day6-学生管理页.html` | 页面和以前一样，样式、表格正常 |
| 注释掉 `mount` 再打开 | `{"detail":"Not Found"}`：服务器没登记这个地址 |
| 把 `mount` 挪到接口前面，打开 `/api/hello` | 接口被拦走，打不开 |

## 7. 验收要点

注释掉 `mount` 后为什么 Not Found？——8000 号服务器只认登记过的地址，没人登记这个文件名，服务器就不知道去哪找。
