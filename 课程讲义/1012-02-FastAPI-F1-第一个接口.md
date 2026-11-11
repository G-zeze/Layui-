# F1 第一个接口

> 产出：根目录 `main.py`，有 `GET /api/hello`、`GET /api/me`。　旧代码对应：`python_study\FAST_API\my_code\main01.py`、`main02.py`。
> 实测环境：Python 3.12.7、FastAPI 0.143、uvicorn 0.54。

## 1. 这一步解决什么

先让后端"活"起来：浏览器访问一个地址，服务器回一段数据。之后的所有接口都是这个套路。

## 2. 准备环境（每台电脑只做一次）

在 VS Code 打开 `D:\Dev\Projects\Layui-`，按 `` Ctrl + ` `` 打开终端：

```bash
python -m venv .venv                     # 在项目里建虚拟环境（文件夹 .venv）
.venv\Scripts\Activate.ps1               # 进入：最前面出现 (.venv)
python -m pip install fastapi uvicorn    # 装进 .venv
```

| 看到 | 怎么办 |
| --- | --- |
| `Activate.ps1` 报"禁止运行脚本" | 运行 `Set-ExecutionPolicy -Scope CurrentUser RemoteSigned`，输入 `Y`，再激活（只设一次） |
| `python` 无法识别 / 弹出微软商店 | 去 python.org 装 3.10 以上，勾选 `Add python.exe to PATH`，重开 VS Code |
| pip 很慢 | 末尾加 `-i https://pypi.tuna.tsinghua.edu.cn/simple` |

**虚拟环境是什么：** 项目自己的一套 Python 和包，不影响别的项目；不进 git，换电脑重建。每个新终端先看有没有 `(.venv)`。

## 3. 代码（示例用 `/api/ping`）

```python
from fastapi import FastAPI     # 导入 FastAPI 类

app = FastAPI()                 # 创建应用 app：所有接口都登记在它身上

@app.get("/api/ping")           # 登记：GET + /api/ping → 交给下面的函数
def ping():                     # 有人访问时，FastAPI 调用它
    return {"ok": True}         # 字典 → FastAPI 转成 JSON 发回浏览器
```

```bash
python -m uvicorn main:app --reload      # 启动；终端必须在项目根目录；这个终端不能关，停止按 Ctrl + C
```

## 4. 是什么 + 对应

| 写法 | 是什么 | 对应你学过的 / 看得见的效果 |
| --- | --- | --- |
| `app = FastAPI()` | 创建应用对象 | 像 `const table = layui.table`：拿到对象，后面都通过它 |
| `@app.get("/api/ping")` | 路径操作装饰器：登记"方法 + 路径" | 像 `table.on("tool(…)", 函数)`：只登记，请求来了 FastAPI 才调用 |
| `.get` / `.post` / `.put` / `.delete` | HTTP 方法：拿 / 新增 / 改 / 删 | 地址栏打开网址永远是 GET |
| `"/api/ping"` | 路径 | `http://127.0.0.1:8000/api/ping` 里端口后面那段 |
| `def ping():` | 路径操作函数 | 函数名自己起，和网址无关 |
| `return {...}` | 返回值 → JSON 响应 | 浏览器显示 `{"ok":true}`（Python `True` → JSON `true`） |
| `main:app` | `main.py` 文件里的 `app` 变量 | 不写 `.py` |
| `--reload` | 保存 `.py` 自动重启 | 改 html 不用重启，刷新浏览器即可 |
| `127.0.0.1:8000` | 本机地址 : 端口 | 端口像门牌号 |
| `/docs` | 自动生成的接口测试页 | 点接口 → Try it out → Execute |

## 5. 结构树

```text
main.py
├── from fastapi import FastAPI
├── app = FastAPI()                 只写一次
└── @app.方法("/路径")              登记
    def 函数名():                    请求来了被调用
        return 字典 / 列表            变成 JSON 发回去
```

```text
一次请求：浏览器发 GET /api/hello → uvicorn 收到交给 app → app 查登记表找到 hello → 调用 hello() → return 的字典转 JSON → 浏览器显示
```

## 6. 一句话规则

**`@app.get` 是登记不是调用；请求来了，FastAPI 按"方法 + 路径"找到函数并调用它。一个接口 = 方法 + 路径。**

## 7. 实测现象

| 你做 | 看到 | 原因 |
| --- | --- | --- |
| 地址拼错 | `{"detail":"Not Found"}`（404） | 没登记这个路径 |
| `@app.get` 改成 `@app.post`，地址栏打开 | `{"detail":"Method Not Allowed"}`（405） | 路径对，方法不对 |
| 函数忘写 `return` | `null` | 没返回东西 |
| 同一方法 + 路径登记两次 | 永远调用前面那个 | 从上往下找，找到就停 |

## 8. 常见错误

| 看到 | 原因 |
| --- | --- |
| `Could not import module "main"` / `No module named 'main'` | 终端所在文件夹里没有 `main.py`（放错文件夹、没保存、命令写成 `main.py:app`） |
| `Attribute "app" not found` | 文件里的变量不叫 `app` |
| `SyntaxError: invalid syntax` | Python 写法错，看行号（如字典写成 `("a":1)`，应为 `{"a":1}`） |
| `No module named 'fastapi'` | 没进 `(.venv)` |
| 提示 `10048` / 地址已被占用 | 另一个终端的服务器还开着，先 `Ctrl + C` |

## 9. 验收要点

1. `hello` 是谁调用的？——FastAPI。`@app.get` 只负责登记。
2. `get` 改 `post` 后为什么打不开？——地址栏只发 GET，接口登记的是 POST；接口由方法 + 路径共同确定。
