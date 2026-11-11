# F3 名单接口 + 页面用 fetch 拿名单

> 产出：`main.py` 的 `GET /api/students`；`14-day7-接口版学生管理页.html`（13 号原样存档）。　旧代码对应：`main14.py` 的 `/items2`（PDF 第 40 页）。

## 1. 这一步解决什么

13 号的名单写死在页面里，页面上删人只删了浏览器内存里的那份，刷新就回来。要想以后真正改得动，名单得放在服务器上。

```text
以前：页面里写死 students ───────────────────────────→ reloadData → 表格
现在：main.py 的 students → /api/students → fetch 拿到 → students = list → reloadData → 表格
                                                                  └ Day 6 已会
```

今天新学的只有两样：**服务器返回列表**、**页面用 fetch 要数据**。

---

## 2. 后端：返回列表

```python
books = [                                     # 列表：一本书一个字典
    {"bookId": "B01", "bookName": "三体"},     # Python 字典：键名必须加引号
    {"bookId": "B02", "bookName": "活着"},
]

@app.get("/api/books")
def get_books():
    return books                              # 返回列表 → 浏览器收到 JSON 数组
```

| 在哪 | 写法 |
| --- | --- |
| 页面 JS | `[{ bookId: "B01" }]`：键名可以不加引号 |
| `main.py` | `[{"bookId": "B01"}]`：键名必须加引号 |
| 浏览器收到的 JSON | `[{"bookId":"B01"}]` |

**规则：** 字典键名 = 前端 `cols` 的 `field`，一字不差；列表和接口都写在 `mount` 上面。批量给键名加引号：`Ctrl + H` 查找 `studentName:`，替换为 `"studentName":`。

---

## 3. 前端：fetch 写在哪

写在 **`layui.use` 的大括号里、`table.render({...});` 之后**：

```text
layui.use([...], function () {
    const table = layui.table;
    let students = [];                 ← 改成空数组
    table.render({ … data: students }) ← 先画空表
    ★ fetch 写在这里 ★
    table.on(…) / 搜索 / 新增 / 查看选中   ← 都不动
});
```

| 要求 | 原因 |
| --- | --- |
| 在 `layui.use` 里面 | 要用 `table`，它是在 `use` 里取出来的 |
| 在 `table.render` 后面 | `render` 画表头并把 `studentTable` 登记成 Layui 表格；`reloadData` 只能重画已登记的表（没有 render 会警告 `table instance ... not found`） |

---

## 4. fetch 三步写（每步刷新看 F12 Console）

```js
// 第 1 步：发请求，看回信
fetch("/api/students").then(function (res) {   // fetch：去要，参数是地址；then：回信到了才执行；res：回信（fetch 传进来）
    console.log(res);                           // 看到 Response {status: 200, ok: true, …}：这是信封，名单还在里面
});

// 第 2 步：拆信
fetch("/api/students").then(function (res) {
    return res.json();                          // 拆信：JSON 文字 → JS 数组；拆要时间，所以 return 交给下一个 then
}).then(function (list) {                       // list：拆好的数组（上一个 then 传进来）
    console.log(list);                          // 看到 (8) [{…}, …]：就是 main.py 里 return 的 students
});

// 第 3 步：存起来、重画
fetch("/api/students").then(function (res) {
    return res.json();
}).then(function (list) {
    students = list;                            // 存进第 47 行的 students
    table.reloadData("studentTable", { data: students, page: { curr: 1 } });   // 按新数据重画
});
```

**fetch 官方定义（MDN）：** "`fetch()` 方法用于发起获取资源的请求，它会返回一个会在请求响应后兑现的 promise。" promise = 取件单：先拿到单子，回信到了才执行 `then`。服务器回 404 时 fetch 不算失败，照样进 `then`，要自己看 `res.ok`。

---

## 5. 示例名 ↔ 你页面里的名字

| 示例里 | 是什么 | 你页面里 | 在哪定义 |
| --- | --- | --- | --- |
| `"/api/books"` | 接口地址 | `"/api/students"` | `main.py` 的 `@app.get` |
| `books` | 存名单的变量 | `students` | 14 号 `let students = [];` |
| `"bookTable"` | 表格 id | `"studentTable"` | `<table id="studentTable">` |
| `res`、`list` | then 传进来的参数 | 名字自己起 | then 调用时传入 |

**`main.py` 里的名字（如函数名 `stu`）页面看不见**，页面只能通过地址拿到 `return` 的结果。

---

## 6. 执行顺序

```js
console.log("1");
fetch("/api/students").then(function (res) { return res.json(); })
                      .then(function (list) { console.log("3"); });
console.log("2");
```

实测打印 **1 → 2 → 3**：fetch 只登记 `then` 不等待，下面的代码先跑完，回信到了才执行 `then`。

**规则：** 用到服务器数据的代码，写在最后一个 `then` 里面（和 `confirm` 的"写错层"同一个道理）。

---

## 7. 结构树

```text
main.py                                   14 号页面 layui.use 里
├── students = [8 个字典]                  ├── let students = [];
├── @app.get("/api/students")              ├── table.render(...)          画空表 + 登记
│   def …(): return students   ──JSON──▶  ├── fetch("/api/students")
└── app.mount(...)                         │     .then(res → return res.json())
                                           │     .then(list → students = list → reloadData)
                                           └── table.on / 按钮事件     用的还是 students
```

## 8. 一句话规则

**`fetch(地址).then(拆信).then(用数据)`：拿到数据先存进变量，再 `reloadData`；页面必须从 8000 打开。**

## 9. 常见错误（F12 Console）

| 红字 | 原因 |
| --- | --- |
| `xxx is not defined`（在 then 里） | 用了页面里不存在的名字：照抄示例名，或用了 `main.py` 里的名字 |
| `fetch(...).them is not a function` | `then` 拼错；而且后面的代码都没执行，按钮全失灵 |
| `URL scheme "file" is not supported` / `Failed to fetch` | 双击打开的，改从 `http://127.0.0.1:8000/…` 打开 |
| 表格一直空，没有红字 | 漏了 `reloadData`，或 id 写错 |
| `GET …/api/student 404` | 地址和 `main.py` 不一致 |
| 有行数但格子空白 | 字典键名 ≠ `field` |

## 10. 验收要点

1. 双击打开为什么拿不到数据？——页面来自 `file://`，`/api/students` 就去硬盘找，浏览器不允许；从 8000 打开才去服务器要。
2. 页面上删掉的人，刷新又回来，为什么？——删的是浏览器内存里的 `students`，服务器那份没变；要真正删，得让服务器改 `main.py` 里的 `students`（F4 起）。
