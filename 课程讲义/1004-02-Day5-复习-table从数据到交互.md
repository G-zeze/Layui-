# Day 5 复习：table 数据表格，从数据到交互（2026-10-04）

> 用途：晚上复习用。内容全部来自今天你亲手写过的 `11-day5-数据表格入门.html`，对应速查笔记第十章（10.1～10.10）。
> 这份讲义可以长、讲原因；想直接查"怎么写"，看 [速查笔记](00-速查笔记.md) 第十章。
> 复习建议顺序：先看第 1 节整体地图 → 第 2～3 节两张"谁传给谁"的表 → 做第 6 节自测 → 最后对答案。

---

## 1. 今天的整体地图

```text
5-01  原生表格 thead/tbody  →  table.render(elem, cols, data)       让 Layui 替你写 <tr><td>
5-02  新增一列                                                      cols 与 data 要同步
5-03  分页 page / limit                                             每页几条，页数向上取整
5-04  排序 sort:true                                                列级配置，按数值或 Unicode 编码
5-05  自定义格子 templet                                            d = 这一行的对象
5-06  操作列按钮                                                    templet 返回 HTML，带 lay-event
5-07  行事件 table.on("tool(…)")                                    obj.event、obj.data
5-08  删除一行 confirm + obj.del()                                  只改页面，不改 data
5-09  选中行 checkbox + checkStatus                                 主动查询，只统计当前页
```

主线只有一句话：**你把数据（`data`）和列说明（`cols`）交给 Layui，它画表格；表格里的点击，由 Layui 通过函数通知你。**

---

## 2. 一张完整的页面（你的 11 号文件，节选）

```html
<button class="layui-btn layui-btn-sm" id="showChecked">查看选中</button>
<table id="studentTable" lay-filter="studentTable"></table>

<script src="./layui-v2.13.9/layui/layui.js"></script>
<script>
    layui.use(["table", "layer"], function(){
        const table = layui.table;
        const layer = layui.layer;

        table.render({
            elem: "#studentTable",
            cols: [[
                {type:"checkbox"},
                {field:"studentId", title:"学号", sort:true},
                {field:"studentName", title:"姓名"},
                {field:"studentGender", title:"性别", templet:function(d){
                    return d.studentGender + "生";
                }},
                {field:"studentClass", title:"班级", sort:true},
                {title:"操作", templet:function(d){
                    return '<a class="layui-btn layui-btn-xs" lay-event="edit">编辑</a> <a class="layui-btn layui-btn-xs layui-btn-danger" lay-event="delete">删除</a>';
                }}
            ]],
            data: [
                {studentId:1, studentName:"张三", studentGender:"男", studentClass:"一班"},
                {studentId:2, studentName:"李四", studentGender:"男", studentClass:"二班"},
                {studentId:3, studentName:"王五", studentGender:"女", studentClass:"三班"}
            ],
            page: true,
            limit: 5
        });

        table.on("tool(studentTable)", function(obj){
            if(obj.event === "edit"){
                layer.msg("编辑" + obj.data.studentName);
            }else if(obj.event === "delete"){
                layer.confirm("确定要删除" + obj.data.studentName + "吗?", function(index){
                    obj.del();
                    layer.close(index);
                    layer.msg("已删除" + obj.data.studentName);
                });
            }
        });

        document.querySelector("#showChecked").addEventListener("click", function(){
            const status = table.checkStatus("studentTable");
            layer.msg("已选中" + status.data.length + "条数据");
        });
    });
</script>
```

结构树：

```text
body
├── button#showChecked                     表格外面的按钮
├── table#studentTable[lay-filter]         空表格：id 给 elem 找，lay-filter 给 tool 事件找
└── script
    └── layui.use(["table","layer"], function(){
          ├── const table / layer                      取模块
          ├── table.render({ … })                      ① 画表格
          │     ├── elem   画在哪
          │     ├── cols   有哪几列（表头区）
          │     ├── data   有哪几行（数据区）
          │     └── page / limit   分页
          ├── table.on("tool(studentTable)", …)       ② 登记：点了行内按钮时被调用
          └── …addEventListener("click", …)           ③ 登记：点了"查看选中"时被调用
        })
```

**规则：** 三件事（画表格、登记 tool、登记 click）是并列的，都写在 `use` 回调里，不要把后一个写进前一个的函数里面。

---

## 3. 最容易混的两张表

### 3.1 谁传进来的参数：`data`、`d`、`obj`、`status`

| 名字             | 出现在哪                                    | 谁传的 / 怎么来的                                | 装的是什么                                        |
| ---------------- | ------------------------------------------- | ------------------------------------------------ | ------------------------------------------------- |
| `data`（表单） | `form.on("submit(…)", function(data){})` | 点提交后，Layui 调用函数时传入                   | `data.field`：整张表单填了什么                  |
| `d`            | `templet:function(d){}`                   | 画到这一行时，Layui 调用函数传入                 | 这一行的数据对象                                  |
| `obj`          | `table.on("tool(…)", function(obj){})`   | 点了带`lay-event` 的按钮后，Layui 调用函数传入 | `obj.event`：点了哪个按钮；`obj.data`：这一行 |
| `status`       | `const status = table.checkStatus("…")`  | **你主动问**，Layui 返回                   | `status.data`：被勾选的行；`.length` 是条数   |

注意：`render({ data:[…] })` 里的 `data` 是你交给 Layui 的**整个数组**（配置项），和 `form.on` 回调的参数 `data` 只是同名，不是一回事。
参数名可以自己起（`d` 改成 `row` 也行），但函数里面用到的地方要和括号里保持一致。

### 3.2 "等触发"和"主动查"

|        | 你做什么                                | 谁来调用函数                   | 例子                                                                     |
| ------ | --------------------------------------- | ------------------------------ | ------------------------------------------------------------------------ |
| 登记   | 把函数交给 Layui 或浏览器，现在先不执行 | 事件发生时，Layui / 浏览器调用 | `table.on("tool(…)")`、`addEventListener("click")`、`form.on(…)` |
| 主动查 | 自己在需要的时候调用方法                | 你的代码执行到这一行就调用     | `table.checkStatus("studentTable")`                                    |

时间线（点"查看选中"）：

```text
勾选两行            → Layui 内部悄悄记下，没有函数被调用
点"查看选中"        → 你登记的 click 函数被调用
函数里执行 checkStatus → 此刻去问一次，结果存进 status（是快照，之后再勾选不会自动更新）
```

---

## 4. 逐节复习（代码 → 结构树 → 一句话规则）

### 4.1 原生表格 ↔ table.render（5-01）

```html
<table>
    <thead>
        <tr><th>学号</th><th>姓名</th></tr>
    </thead>
    <tbody>
        <tr><td>001</td><td>张三</td></tr>
    </tbody>
</table>
```

```text
thead → tr → th, th     表头区     ←→  cols
tbody → tr → td, td     数据区     ←→  data（一个对象 = 一行）
```

**规则：** `tr` 是一行，`th` 是表头格，`td` 是数据格；`table.render` 就是让 Layui 按 `cols` 和 `data` 替你写出这些标签。

### 4.2 cols、title、field、data（5-01、5-02）

```js
cols: [[
    {field:"studentId", title:"学号"},
    {field:"studentName", title:"姓名"}
]],
data: [
    {studentId:1, studentName:"张三"},
    {studentId:2, studentName:"李四"}
]
```

```text
对每一行对象，对每一列：
    用这一列的 field 作为键名 → 去这一行对象里找同名键 → 找到的值放进格子
    title 只管表头显示的文字
```

**规则：** `field` 必须和 `data` 里的键名**一模一样**（大小写也算）；找不到，这一格就是空白。外层 `[ ]` 是表头的行，内层 `[ ]` 是这一行的各列，现在先照写。

### 4.3 elem（5-01，Day 4 `laydate` 也出现过）

```html
<table id="studentTable"></table>
```

```js
elem: "#studentTable"
```

**规则：** `id` 在 HTML 标签里，是元素的名字；`elem:"#id"` 在 JS 配置里，是通过这个名字找元素；`#` 不能漏。`elem`、`cols`、`data`、`title`、`field` 是 Layui 的配置项，不是 HTML 属性，也不是 CSS。

### 4.4 分页 page、limit（5-03）

```js
page: true,
limit: 5
```

**规则：** `page`、`limit` 和 `elem`、`cols`、`data` 同级，管整张表；页数 = 总条数 ÷ 每页条数，**向上取整**（8 条、`limit:5` → 2 页；`limit:3` → 3 页；`limit:10` → 1 页）。

### 4.5 排序 sort（5-04）

```js
{field:"studentId", title:"学号", sort:true}
```

**规则：** `sort` 写在**某一列的对象里**，只管这一列。数字按**数值大小**排；文字按 **Unicode 字符编码**逐字比（不是拼音、不是笔画，所以"一班、二班、三班"不会按一二三排）；数字和文字混在一列时数字在前。

### 4.6 自定义格子 templet（5-05）

```js
{field:"studentGender", title:"性别", templet:function(d){
    return d.studentGender + "生";
}}
```

```text
templet: function(d){ return 要显示的内容; }
├── d       这一行的对象（Layui 画到这一行时传入）
└── return  返回什么，这一格就显示什么；忘了 return 就是空白
```

**规则：** 这个函数不是你调用的，是 Layui 画**每一行**时调用一次（第一次画、翻页、排序重画都会调用）；`d` 是当前这一行的对象。

### 4.7 操作列按钮（5-06）

```js
{title:"操作", templet:function(d){
    return '<a class="layui-btn layui-btn-xs" lay-event="edit">编辑</a> <a class="layui-btn layui-btn-xs layui-btn-danger" lay-event="delete">删除</a>';
}}
```

```text
没有 field            内容是自己写的，不从 data 取值
layui-btn-xs          基础按钮类 + 超小尺寸（sm 小、lg 大）；layui-btn-danger 是红色
lay-event="edit"      名字牌：告诉 Layui 这个按钮叫 edit
外层用单引号，里面的属性用双引号
```

**规则：** `field` 的作用是"去 data 取哪个键的值"；操作列不读 `data`，所以不写 `field`。

### 4.8 行事件 tool（5-07）

```html
<table id="studentTable" lay-filter="studentTable"></table>
```

```js
table.on("tool(studentTable)", function(obj){
    if(obj.event === "edit"){
        layer.msg("编辑" + obj.data.studentName);
    }else if(obj.event === "delete"){
        layer.msg("删除" + obj.data.studentName);
    }
});
```

```text
① table 元素写 lay-filter="名字"
② table.on("tool(名字)", function(obj){…})   名字要和 ① 一致
③ 按钮写 lay-event="edit"                    对应 obj.event
obj.event   点的是哪个按钮
obj.data    点的是哪一行的数据对象
```

**规则：** Layui 在 `table.render` 时给整个表格挂了点击监听，点到带 `lay-event` 的元素就触发 `tool(lay-filter 的值)`，并把"点了哪个按钮、哪一行"装进 `obj` 交给你的函数。`if (obj.event === "edit")` 里的 `===` 是"是否相等"，是才执行大括号里的内容。

### 4.9 删除一行（5-08）

```js
layer.confirm("确定要删除" + obj.data.studentName + "吗?", function(index){
    obj.del();
    layer.close(index);
    layer.msg("已删除" + obj.data.studentName);
});
```

**规则：** 确定函数写在 `confirm` 的括号里，点了确定才执行；`layer.msg` 写在括号外会一闪而过。`obj.del()` 只把页面上这一行拿掉，**不改 `data`**：分页条不变，翻页或刷新后这一行会回来。要真的删除，得改 `data` 再让表格重新读，这是 Day 6 的 `table.reload`。

### 4.10 选中行（5-09）

```js
{type:"checkbox"},
```

```js
document.querySelector("#showChecked").addEventListener("click", function(){
    const status = table.checkStatus("studentTable");
    layer.msg("已选中" + status.data.length + "条数据");
});
```

**规则：** `checkStatus("表格id")` 是主动查"现在谁被勾选了"，返回的 `status.data` 是被选中行组成的数组，`.length` 是条数。带分页的静态数据，只统计**当前这一页**（源码里每次翻页只取这一页的行放进缓存）。`click` 的登记要写在 `table.on` 函数的**外面**。

---

## 5. 今天出过的错（先自查这几类）

| 现象                               | 原因                                                                                                  | 位置 / 做法      |
| ---------------------------------- | ----------------------------------------------------------------------------------------------------- | ---------------- |
| 表头和行数都有，格子全空           | `data` 的键名和 `cols` 的 `field` 不一致（如 `id`/`name` 对 `studentId`/`studentName`） | 逐个字符对照两处 |
| 点"查看选中"没反应，点过编辑后才有 | `click` 登记写进了 `table.on` 函数里面（写错层）                                                  | 登记写外层       |
| 点操作按钮没反应                   | `lay-filter` 与 `tool(…)` 括号里的名字不一致；或按钮没有 `lay-event`                           | 两处名字完全一致 |
| `layer is not defined`           | `use` 数组没写 `"layer"`，或漏了 `const layer = layui.layer;`                                   | 补上             |
| 操作列空白 / 显示`undefined`     | `templet` 里漏了 `return`，或 `d.` 后面的键名拼错                                               | 检查             |
| 新增一行`<tr>` 后表格错乱        | 漏了`</tr>`（浏览器会自动补，页面看着没事，但属于标签配对问题）                                     | 写完逐层配对     |
| 确认框一闪就没了                   | `layer.msg` 写在 `confirm` 括号外面                                                               | 移到括号里面     |

共同规律：**拼写、括号配对、代码写错层**。写完先用 F12 的 Console 看红字。

---

## 6. 自测题（先自己答，再对答案）

1. 表格的"姓名"这一格的值，是怎么从 `data` 里拿到的？
2. `cols` 对应原生表格的哪一块？`data` 对应哪一块？
3. 为什么操作列不需要写 `field`？
4. 8 条数据，`limit:3` 有几页？`limit:10` 有几页？
5. `page`、`limit` 写在哪里？`sort` 写在哪里？区别是什么？
6. 文字列排序是按什么规则？为什么"一班二班三班"排不出一二三？
7. `templet:function(d){}` 里的函数是谁调用的？`d` 是什么？
8. `table.on("tool(studentTable)")` 括号里的 `studentTable` 对应哪里？`lay-event` 起什么作用？
9. `obj.event` 和 `obj.data` 分别是什么？
10. 点"删除"并确认后，一行消失了。刷新页面，这一行回来了，为什么？
11. `checkStatus` 和 `tool` 有什么区别？
12. 为什么"查看选中"的 `click` 登记要写在 `table.on` 外面？

---

## 7. 参考答案

1. 姓名那一列的 `field` 是 `studentName`，Layui 去这一行对象里找键名同为 `studentName` 的值，放进格子。
2. `cols` ↔ `thead`（表头区），`data` ↔ `tbody`（数据区，一个对象是一行）。
3. `field` 是"去 data 里取哪个键"；操作列的内容是自己写的 HTML，不从 data 取值。
4. `limit:3` 是 8÷3=2.67 → 3 页；`limit:10` 是 8÷10=0.8 → 1 页。
5. `page`、`limit` 写在 `render({ })` 最外层，管整张表；`sort` 写在某一列的对象里，只管这一列。
6. 文字按 Unicode 字符编码逐字比，不是拼音也不是笔画；"一二三"的编码顺序不是一二三，所以升序是 一班、七班、三班、二班、五班、八班、六班、四班。
7. 是 Layui 调用的，画每一行时调用一次；`d` 是这一行的数据对象。
8. 对应 `<table>` 上的 `lay-filter`；`lay-event` 是按钮上的名字牌，点到它时 Layui 触发 `tool` 事件，并把它的值放进 `obj.event`。
9. `obj.event` 是点的按钮的 `lay-event` 值；`obj.data` 是被点那一行的数据对象。
10. `obj.del()` 只拿掉页面上那一行，没有改 `data`；刷新后页面按 `data` 重新画，所以回来了。
11. `tool` 是事件通知：点了按钮，Layui 调用你登记的函数；`checkStatus` 是主动查询：你的代码执行到那一行才去问当前勾选情况。
12. 登记写在 `table.on` 函数里面，要等点过一次编辑或删除才会登记（还会重复登记）；登记应写在外层，等触发的代码才写在里层。

---

## 8. 明天入口

- 先口头复述第 6 节中你答不顺的 3 道题。
- 做 `12-day5-学生列表页.html`：从空文件做，要求清单见当前任务。
- 通过后写 Day 5 收尾总结，进 Day 6：`table.reload`，解决"删除后翻页又回来"的问题。
