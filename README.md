<!doctype html>
<html lang="en">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>Three Chambers</title>
  <style>
    :root { color-scheme: dark; font-family: system-ui, sans-serif; }
    body { margin: 0; min-height: 100vh; background: radial-gradient(circle at top, #334e8f, #101426 55%); color: #f6f7fb; }
    main { max-width: 960px; margin: auto; padding: 48px 20px; }
    h1 { font-size: clamp(2.2rem, 7vw, 4rem); margin: 0; }
    .lead { color: #cbd5ef; font-size: 1.1rem; max-width: 680px; }
    .notice { margin: 24px 0; padding: 16px; border-left: 4px solid #76e4b3; background: #17233f; color: #d9f9e9; }
    .games { display: grid; grid-template-columns: repeat(auto-fit, minmax(210px, 1fr)); gap: 16px; }
    article { display: flex; flex-direction: column; gap: 12px; padding: 20px; border: 1px solid #41527e; border-radius: 14px; background: #1a2340; }
    article h2, article p { margin: 0; }
    article p { min-height: 3em; color: #bfc9e3; }
    .actions { display: flex; gap: 8px; flex-wrap: wrap; margin-top: auto; }
    a { border-radius: 8px; padding: 9px 12px; color: #fff; text-decoration: none; background: #5e76e6; font-weight: 650; }
    a.secondary { background: #2a385d; }
    footer { margin-top: 40px; color: #aeb9d6; }
  </style>
</head>
<body>
  <main>
    <h1>Three Chambers</h1>
    <p class="lead">A browser-ready edition of the Green Block maze series. Choose any level below—this page works through VS Code Live Server and through <code>npm run dev</code>.</p>
    <p class="notice"><strong>Controls:</strong> W/A/S/D or arrow keys to move. Q pushes an adjacent enemy; E clears an adjacent wall; R restarts. The original Python Turtle source remains available on every card.</p>
    <section class="games" id="games" aria-label="Game levels"></section>
    <footer>Original Turtle files require Python 3 and a desktop display; web games run directly in this browser.</footer>
  </main>
  <script>
    const levels = [
      ['HHHH1.py', 'Power Grid', 'Learn the maze and activate the switches.'],
      ['HHHH2.py', 'Pure Chase', 'Outrun the enemy in a tighter chamber.'],
      ['HHHH3.py', 'Frozen Orb', 'Use the frozen orb to escape pursuit.'],
      ['HHHH4.py', 'Power Grid Plus', 'A tougher power-grid route.'],
      ['HHHH5.py', 'Shield & Barrier', 'Place barriers and break through.'],
      ['HHHH6.py', 'Code Gate', 'Find the key and open the final gate.'],
      ['HHHH7.py', 'Final Gate', 'Survive the first Hell Mode chamber.'],
      ['HHHH8.py', 'Final Gate Plus', 'More hazards, less room to recover.'],
      ['HHHH9.py', 'Hell Mode', 'A fast, hostile final maze.'],
      ['HHHH10.py', 'Hell Mode: Finale', 'The ultimate Three Chambers challenge.']
    ];
    document.querySelector('#games').innerHTML = levels.map(([file, name, description], i) => `
      <article>
        <h2>${i + 1}. ${name}</h2><p>${description}</p>
        <div class="actions"><a href="game.html?level=${encodeURIComponent(file)}">Play</a><a class="secondary" href="${file}.py" download="${file}.py">Python source</a></div>
      </article>`).join('');
  </script>
</body>
</html>
