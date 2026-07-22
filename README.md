<!DOCTYPE html>
<html lang="zh-CN">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>Green Block - 游戏运行中</title>
  <style>
    :root { color-scheme: dark; font-family: system-ui, sans-serif; }
    body { margin: 0; background: #101426; color: #f6f7fb; text-align: center; padding: 20px; }
    #canvas-container {
      margin: 20px auto;
      width: 800px;
      height: 600px;
      background: #1a2340;
      border: 2px solid #76e4b3;
      border-radius: 12px;
      overflow: hidden;
      position: relative;
    }
    .status { margin-bottom: 15px; color: #cbd5ef; font-size: 1.1rem; }
    .back-btn {
      display: inline-block;
      padding: 10px 20px;
      background: #5e76e6;
      color: #fff;
      text-decoration: none;
      border-radius: 8px;
      font-weight: bold;
    }
    .back-btn:hover { background: #4b62d1; }
  </style>

  <!-- 加载 Skulpt (可以在浏览器中运行 Python 及 turtle 的引擎) -->
  <script src="https://cdn.jsdelivr.net/npm/skulpt@1.2.0/dist/skulpt.min.js"></script>
  <script src="https://cdn.jsdelivr.net/npm/skulpt@1.2.0/dist/skulpt-stdlib.js"></script>
</head>
<body>

  <a href="index.html" class="back-btn">← 返回关卡列表</a>
  <div class="status" id="status">正在加载 Python 引擎及关卡文件...</div>

  <!-- Turtle 画布渲染区域 -->
  <div id="canvas-container">
    <div id="mycanvas"></div>
  </div>

  <script>
    <div class="actions"><a href="game.html?file=${file}">Play</a><a class="secondary" href="${file}" download="${file}">Python source</a></div>
    const urlParams = new URLSearchParams(window.location.search);
    const pyFile = urlParams.get('file');

    if (!pyFile) {
      document.getElementById('status').innerText = '未找到关卡文件！';
    } else {
      document.getElementById('status').innerText = '正在运行: ' + pyFile;

      // 2. 动态读取对应的 .py 代码文件
      fetch(pyFile)
        .then(response => {
          if (!response.ok) throw new Error('网络响应异常，文件可能不存在');
          return response.text();
        })
        .then(code => {
          // 3. 配置并运行 Skulpt 解释器
          Sk.python3 = true;
          Sk.configure({
            output: function(text) { console.log(text); },
            read: function(x) {
              if (Sk.builtinFiles === undefined || Sk.builtinFiles["files"][x] === undefined)
                throw "File not found: '" + x + "'";
              return Sk.builtinFiles["files"][x];
            },
            // 将 turtle 的绘制目标指向 div #mycanvas
            (Sk.TurtleGraphics || (Sk.TurtleGraphics = {})).target = 'mycanvas'
          });

          // 执行 Python 代码
          Sk.misceval.asyncToPromise(function() {
            return Sk.importMainWithBody("<stdin>", false, code, true);
          }).catch(err => {
            console.error(err);
            document.getElementById('status').innerText = '运行出错: ' + err.toString();
          });
        })
        .catch(err => {
          document.getElementById('status').innerText = '加载文件失败: ' + err.message;
        });
    }
  </script>
</body>
</html>
