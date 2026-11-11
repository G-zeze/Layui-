# F3：页面用 fetch 向服务器要名单（Day 7 的 7-04，重写详细版）

> 位置：[知识地图](1012-01-FastAPI-00-知识地图.md) 的 F3 后半。前面已经做完：`main.py` 里有 `GET /api/students`，浏览器打开能看到 8 个学生（F3 前半）。
> 本讲义里的现象都用你的 13 号页面 + 你的 `main.py` 在 Chrome 里实测过（2026-10-12）。

---

## 0. 这一步要干什么（一句话）

**把页面里写死的 8 个学生删掉，改成页面打开后去服务器的 `/api/students` 要，要到了再交给表格。**

```text
以前（13 号）：
  let students = [8 个学生]  →  table.render 画表格

现在（14 号）：
  let students = []          →  table.render 先画一张空表格
  fetch("/api/students")     →  去服务器要名单
  服务器回信                  →  拆出 8 个学生  →  存进 students  →  reloadData 按新数据重画
```

最后一步 `reloadData` 你在 Day 6 已经用过很多次（搜索、删除、编辑、新增）。**今天新学的只有中间"去要、回信、拆信"这一段。**

---

## 1. 先弄清文件：改 14 号，不改 13 号

13 号是 Day 6 的独立产出，要原样留着存档。今天的改动写在一个新文件里：

```text
13-day6-学生管理页.html        原样不动（名单写死在页面里）
14-day7-接口版学生管理页.html   今天改这个（名单从服务器要）
```

---

## 2. 代码写在哪里

fetch 是 JS，和你以前写的 `table.on`、按钮点击一样，**写在 `layui.use` 的大括号里面**，位置是 **`table.render({...});` 结束之后、`// 监测点击编辑按钮` 之前**。

```text
<script>
  layui.use(["element", "table", "layer"], function () {
      const table = layui.table;               ← 第 44 行：拿到 table
      let students = [];                       ← 第 47 行：改成空数组
      table.render({ ... data: students ... }); ← 画一张空表格
      ★ fetch 写在这里 ★                        ← 去要名单，要到后重画
      table.on("tool(studentTable)", ...)      ← 编辑、删除（不动）
      搜索按钮、新增按钮、查看选中               ← 都不动
  });
</script>
```

**为什么必须写在这里：**

| 要求                          | 原因                                                                                                 |
| ----------------------------- | ---------------------------------------------------------------------------------------------------- |
| 在`layui.use` 里面          | 要用`table.reloadData`，而 `table` 是第 44 行在 `use` 里面取出来的，出了大括号就没有 `table` |
| 在`table.render` 后面       | `reloadData` 是"重画"，表格得先画出来，才能重画                                                    |
| 在`table.on` 前面或后面都行 | 互不影响；放在`render` 紧后面，读代码时一眼能看出"先画空表，再要数据"                              |

---

## 3. fetch 分三步写，每步都用 console.log 看一眼

不要一次写完。每写一步就保存、刷新页面（地址必须是 `http://127.0.0.1:8000/14-day7-接口版学生管理页.html`），按 F12 看 Console。

### 第 1 步：只发请求，看回信是什么

```js
fetch("/api/students").then(function (res) {   // fetch：去服务器要东西，第一个参数是地址；then：回信到了以后执行里面的函数
    console.log(res);                           // res：回信，由 fetch 传进来（名字自己起）
});
```

| 写法                            | 是什么                                                                                                                                                                      |
| ------------------------------- | --------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| `fetch("/api/students")`      | 向服务器发一个 GET 请求，地址是`/api/students`。和你在地址栏输入 `http://127.0.0.1:8000/api/students` 是同一件事，只是由 JS 来做，结果不显示在页面上，而是交给 `then` |
| `.then(function (res) {...})` | 登记：**回信到了**再执行这个函数。和 `layer.confirm(…, function(index){…})` 一样，等事情发生了才执行                                                              |
| `res`                         | 回信。fetch 收到服务器的回复后，调用你的函数，把回信作为第一个参数传进来                                                                                                    |

**看到：** Console 里出现 `Response {…, status: 200, ok: true, …}`。

这是"信封"，你在里面看不到 8 个学生，因为名单还装在信封里，没拆出来。

### 第 2 步：拆信，看拆出来的是什么

```js
fetch("/api/students").then(function (res) {
    return res.json();                          // res.json()：拆信，把里面的 JSON 文字变成 JS 数组；return：交给下一个 then
}).then(function (list) {                       // 第二个 then：拆完以后执行；list 是上一个 then return 出来的东西
    console.log(list);
});
```

| 写法                             | 是什么                                                                                                     |
| -------------------------------- | ---------------------------------------------------------------------------------------------------------- |
| `res.json()`                   | 拆信：服务器发来的是 JSON 文字，`.json()` 把它变成 JS 能用的数组。拆信也要一点时间，所以不能当场拿到结果 |
| `return res.json()`            | 把"拆信这件事"交出去：拆好了，就交给下一个`then`                                                         |
| `.then(function (list) {...})` | 登记：**拆完了**再执行。`list` 就是拆出来的数组                                                    |

**看到：** `(8) [{…}, {…}, …]`。点开看，每个对象有 `studentId`、`studentName`、`studentGender`、`studentClass`。

**这个 `list` 就是 `main.py` 里 `return students` 发过来的那 8 个学生。**

为什么要两个 `then`：

```text
第一个 then：信到了  → 开始拆信（要时间）→ return 交出去
第二个 then：拆完了  → 拿到数组 list
```

### 第 3 步：存进 students，重画表格

```js
fetch("/api/students").then(function (res) {
    return res.json();
}).then(function (list) {
    students = list;                            // 把拆出来的数组存进页面的 students（第 47 行那个变量）
    table.reloadData("studentTable", {          // reloadData：重画表格，第一个参数是表格 id，第二个参数是新配置
        data: students,                         // 用新的 students 重画
        page: { curr: 1 }                       // 回到第 1 页
    });
});
```

**看到：** 表格出现 8 个学生，每页 3 条，下面是 3 页的分页条（你的 `limit: 3`）。

---

## 4. 示例里的名字 ↔ 你页面里的名字

讲义示例故意用了别的名字（`courses`、`books`），**照抄示例的名字是不会对的**。每个名字都要换成你页面里真实存在的东西：

| 示例里的          | 是什么             | 你页面里对应的               | 在哪定义的                                   |
| ----------------- | ------------------ | ---------------------------- | -------------------------------------------- |
| `"/api/books"`  | 接口地址           | `"/api/students"`          | `main.py` 的 `@app.get("/api/students")` |
| `books`         | 页面里存名单的变量 | `students`                 | 14 号第 47 行`let students = [];`          |
| `"bookTable"`   | 表格的 id          | `"studentTable"`           | 第 34 行`<table ... id="studentTable">`    |
| `res`、`list` | then 传进来的参数  | 名字可以自己起，前后一致就行 | then 调用你的函数时传入                      |

**注意 Python 里的名字在页面里不存在：** `main.py` 里的函数名（比如 `stu`）只活在服务器上，页面的 JS 看不见它。页面只能通过地址 `/api/students` 拿到函数 `return` 的结果。

---

## 5. 执行顺序（最重要，也最容易误会）

在第 3 步的代码里加三个 `console.log`，看谁先打印：

```js
console.log("1. render 画完了，students 里有", students.length, "个");
fetch("/api/students").then(function (res) {
    return res.json();
}).then(function (list) {
    console.log("3. 拆完了，list 有", list.length, "个");
    students = list;
    table.reloadData("studentTable", { data: students, page: { curr: 1 } });
});
console.log("2. fetch 下面的代码");
```

**实测顺序是 1 → 2 → 3，不是 1 → 3 → 2。**

```text
1. render 画了一张空表（students 还是 0 个）
   fetch 发出请求 → 只登记 then，不等
2. 紧接着往下执行 fetch 下面的代码（table.on、按钮……都在这时登记好）
   ……服务器回信、拆信……
3. then 里的函数这时才执行 → students 变成 8 个 → 重画
```

**一句话规则：** 用到服务器数据的代码，必须写在 `then` 的函数**里面**；写在外面会先执行，那时数据还没到。（和 Day 6 `confirm` 的"写错层"是同一个道理。）

看完把三个 `console.log` 删掉。

---

## 6. 结构树（14 号脚本改完后的样子）

```text
layui.use([...], function () {
├── const table = layui.table;  …
├── let students = [];                      ← 空数组
├── table.render({ elem, cols, data: students, page, limit });   ← 先画空表
├── fetch("/api/students")                  ← 去要
│     .then(function (res) {
│         return res.json();                ← 拆信，交给下一个 then
│     })
│     .then(function (list) {
│         students = list;                  ← 存起来
│         table.reloadData("studentTable", { data: students, page: { curr: 1 } });  ← 重画
│     });
├── table.on("tool(studentTable)", …)       ← 不动
└── 搜索 / 新增 / 查看选中                     ← 不动
});
```

为什么搜索、编辑、删除、新增都不用改：它们用的都是 `students` 这个变量，而 `students` 已经在第二个 `then` 里换成了服务器给的 8 个人。

---

## 7. 常见错误（F12 Console 里看到的红字）

| 红字                                                                                                       | 原因                                                                                                                      |
| ---------------------------------------------------------------------------------------------------------- | ------------------------------------------------------------------------------------------------------------------------- |
| `Uncaught (in promise) ReferenceError: xxx is not defined`                                               | `then` 里用了一个页面里不存在的名字（比如照抄示例，或用了 `main.py` 里的函数名）。按第 4 节对照表换成页面里的名字     |
| `Fetch API cannot load file:///api/students. URL scheme "file" is not supported.` 和 `Failed to fetch` | 双击打开的（地址栏是`file:///`）。改从 `http://127.0.0.1:8000/14-...html` 打开                                        |
| 表格一直是空的，Console 没有红字                                                                           | 第二个`then` 里只写了 `students = list`，没有 `reloadData`；或者 `reloadData` 的第一个参数不是 `"studentTable"` |
| `GET http://127.0.0.1:8000/api/student 404 (Not Found)`                                                  | 地址拼错，要和`main.py` 里的路径一字不差                                                                                |
| 表格有 8 行但格子空白                                                                                      | `main.py` 字典的键名和 `cols` 的 `field` 不一致                                                                     |
| Console 里有几个字体文件 404                                                                               | 和今天无关，可以忽略                                                                                                      |

---

## 8. 一句话规则

**`fetch(地址).then(拆信).then(用数据)`：要数据的代码写在最后一个 `then` 里面；拿到数据后，先存进变量，再 `reloadData`。**

---

## 9. 验收（写完口头回答）

1. 双击打开 14 号时 Console 报了什么？为什么从 `http://127.0.0.1:8000/` 打开就没事？
2. 在页面上删除一个学生，再刷新页面，他又回来了。原因是什么？要想真正删掉，需要改哪里的 `students`：页面里的，还是 `main.py` 里的？
