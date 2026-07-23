<!doctype html>
<html lang="zh-CN">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  
  <a href="${level.file.replace('.py', '.html')}">Play</a>
  <meta name="google-site-verification" content="你的Google验证码" />

  <title>Green Block - 在线 Python 迷宫游戏</title>
  <meta name="description" content="Green Block 是一款基于 Python Turtle 开发的经典迷宫游戏，支持网页在线直接游玩及源码下载。">

  <style>
    :root { color-scheme: dark; font-family: system-ui, sans-serif; }
    body { margin: 0; min-height: 100vh; background: radial-gradient(circle at top, #334e8f, #101426 55%); color: #f6f7fb; }
    main { max-width: 960px; margin: auto; padding: 48px 20px; }
    h1 { font-size: clamp(2.2rem, 7vw, 4rem); margin: 0; color: #cbd5ef; font-size: 1.1rem; max-width: 680px; }
    .notice { margin: 24px 0; padding: 12px; border-left: 4px solid #76e4b3; background: #17233f; color: #d9f9e9; }
    .games { display: grid; grid-template-columns: repeat(auto-fit, minmax(210px, 1fr)); gap: 16px; }
    article { display: flex; flex-direction: column; gap: 12px; padding: 20px; border: 1px solid #41527e; background: #1a2340; border-radius: 14px; }
    article h2 { margin: 0; font-size: 1.2rem; }
    article p { margin: 0; color: #a2b4dc; font-size: 0.95rem; }
    .actions { display: flex; gap: 8px; margin-top: auto; }
    .actions a { flex: 1; text-align: center; padding: 10px; background: #5e76e6; color: #fff; text-decoration: none; border-radius: 8px; font-weight: bold; font-size: 0.9rem; }
    .actions a.secondary { background: #2d3a66; color: #a2b4dc; }
    .actions a:hover { opacity: 0.9; }
  </style>
</head>
<body>
  <main>
    <h1>Green Block 绿块冒险</h1>
    <p class="notice">提示：点击 Play 即可在网页端直接运行游戏，点击 Python source 可下载源码文件。</p>

    <div class="games" id="game-list"></div>
  </main>

  <script>
    const levels = [
      { id: 1, name: "第一关", desc: "初识迷宫", file: "HHHH1.py" },
      { id: 2, name: "第二关", desc: "机关重重", file: "HHHH2.py" },
      { id: 3, name: "第三关", desc: "暗道丛生", file: "HHHH3.py" },
      { id: 4, name: "第四关", desc: "迷雾重重", file: "HHHH4.py" },
      { id: 5, name: "第五关", desc: "绝地逢生", file: "HHHH5.py" },
      { id: 6, name: "第六关", desc: "电箱危机", file: "HHHH6.py" },
      { id: 7, name: "第七关", desc: "红块守卫", file: "HHHH7.py" },
      { id: 8, name: "第八关", desc: "修罗战场", file: "HHHH8.py" },
      { id: 9, name: "第九关", desc: "终极逃亡", file: "HHHH9.py" },
      { id: 10, name: "第十关", desc: "修复身体", file: "HHHH10.py" }
    ];

    const container = document.getElementById('game-list');
    levels.forEach(level => {
      const card = document.createElement('article');
      card.innerHTML = `
        <h2>${level.name}</h2>
        <p>${level.desc}</p>
        <div class="actions">
          <a href="game.html?file=${level.file}">Play</a>
          <a class="secondary" href="${level.file}" download="${level.file}">Python source</a>
        </div>
      `;
      container.appendChild(card);
    });
  </script>
</body>
</html>
