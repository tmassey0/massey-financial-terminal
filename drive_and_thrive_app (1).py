<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>アニメ · 篮球传说 · MJ vs LBJ</title>
    <style>
        * {
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }
        body {
            background: linear-gradient(145deg, #0b1a2e 0%, #1a2f3f 100%);
            min-height: 100vh;
            display: flex;
            justify-content: center;
            align-items: center;
            font-family: 'Segoe UI', 'Helvetica', system-ui, sans-serif;
        }
        .anime-hoops {
            background: #1e3b4f;
            border-radius: 2.5rem 2.5rem 1.5rem 1.5rem;
            padding: 2rem 2rem 1.8rem 2rem;
            box-shadow: 0 25px 40px rgba(0,0,0,0.7), 0 0 0 2px #ffb347 inset, 0 0 0 5px #2b5f7a inset;
        }
        .canvas-wrapper {
            position: relative;
            display: flex;
            justify-content: center;
            border-radius: 1.8rem;
            overflow: hidden;
            box-shadow: 0 0 0 4px #f9d27e, 0 20px 30px rgba(0,0,0,0.8);
        }
        canvas {
            display: block;
            width: 900px;
            height: 450px;
            background: #7ccf9f;  /* anime court green */
            cursor: pointer;
        }
        .scoreboard {
            display: flex;
            justify-content: space-between;
            align-items: center;
            margin: 18px 15px 0 15px;
            color: #faeac6;
            text-shadow: 3px 3px 0 #1f4d6e, 5px 5px 0 #00000060;
            font-weight: 800;
            letter-spacing: 2px;
        }
        .player-tag {
            display: flex;
            align-items: center;
            gap: 12px;
            font-size: 1.6rem;
            background: #263f4e;
            padding: 0.7rem 2rem;
            border-radius: 4rem;
            border: 3px solid #fec260;
            box-shadow: 0 8px 0 #0f2c3a;
        }
        .mj-tag {
            background: #be6e46;  /* warm anime accent */
        }
        .lbj-tag {
            background: #b1624b;
        }
        .score-display {
            background: #141c24;
            border-radius: 2rem;
            padding: 0.2rem 1.2rem;
            font-size: 2.5rem;
            font-family: 'Courier New', monospace;
            color: #ffd966;
            border: 3px solid #fff2b5;
            box-shadow: inset 0 -3px 0 #473d2b;
        }
        .anime-badge {
            background: #ffb703;
            border-radius: 30px;
            padding: 0.4rem 1.8rem;
            font-size: 1.1rem;
            font-weight: 600;
            color: #082b39;
            border: 2px solid white;
            transform: rotate(-1deg);
            box-shadow: 0 6px 0 #a0661c;
        }
        button {
            background: #fedb9f;
            border: none;
            border-radius: 50px;
            padding: 12px 28px;
            font-weight: bold;
            font-size: 1.3rem;
            color: #113946;
            border-bottom: 6px solid #af7b3a;
            border-right: 3px solid #ca984b;
            transition: 0.08s linear;
            cursor: pointer;
            box-shadow: 0 7px 0 #4f3620;
        }
        button:active {
            transform: translateY(5px);
            border-bottom-width: 2px;
            box-shadow: 0 2px 0 #4f3620;
        }
        .footer-note {
            text-align: center;
            color: #ccdde4;
            margin-top: 16px;
            font-size: 1.1rem;
            font-style: italic;
            background: #183d4b;
            padding: 8px 20px;
            border-radius: 40px;
            display: inline-block;
            margin-left: auto;
            margin-right: auto;
            width: fit-content;
            border: 2px solid #96cadf;
        }
        .sparkle {
            font-size: 1.6rem;
            filter: drop-shadow(0 0 6px gold);
        }
    </style>
</head>
<body>
<div class="anime-hoops">
    <div class="canvas-wrapper">
        <canvas id="battleCourt" width="900" height="450"></canvas>
    </div>

    <!-- anime style scoreboard + tags -->
    <div class="scoreboard">
        <div class="player-tag mj-tag">
            <span class="sparkle">✨</span>
            <span>M·J</span>
            <span class="score-display" id="mjScore">0</span>
        </div>
        <div class="anime-badge">⚡ 黄金一代 ⚡</div>
        <div class="player-tag lbj-tag">
            <span class="sparkle">🔥</span>
            <span>LBJ</span>
            <span class="score-display" id="lbjScore">0</span>
        </div>
    </div>

    <!-- controls + anime flavor -->
    <div style="display: flex; justify-content: center; margin-top: 22px; gap: 20px; align-items: center;">
        <button id="resetBtn">🔄 始まり · 重置</button>
        <span style="color:#ffe2a3; font-weight:500;">⚡ 点击画面 · 加速灵魂 ⚡</span>
    </div>
    <div class="footer-note">
        🏀  anime style · マイケル vs レブロン  🏀
    </div>
</div>

<script>
    (function() {
        // ==========  canvas & anime context ==========
        const canvas = document.getElementById('battleCourt');
        const ctx = canvas.getContext('2d');

        // score elements
        const mjScoreSpan = document.getElementById('mjScore');
        const lbjScoreSpan = document.getElementById('lbjScore');

        // dimensions
        const W = 900, H = 450;
        // player base positions
        const mjPos = { x: 200, y: 280 };   // left side (Michael)
        const lbjPos = { x: 700, y: 280 };  // right side (LeBron)

        // ball state
        let ball = {
            x: mjPos.x + 30,
            y: mjPos.y - 30,
            vx: 2.2,          // horizontal speed
            vy: 0,
            bouncePhase: 0,
            radius: 16,
            owner: 'mj'       // 'mj' or 'lbj' (who last touched)
        };

        // scores
        let mjScore = 0;
        let lbjScore = 0;

        // animation control
        let animFrame = null;
        let lastTimestamp = 0;
        // speed multiplier (tap canvas to boost)
        let speedFactor = 1.0;
        const BASE_SPEED = 2.2;

        // ==========  draw anime-styled players ==========
        function drawMJ(x, y) {
            // skin tone (warm brown, anime highlight)
            ctx.save();
            // head (large expressive anime style)
            ctx.beginPath();
            ctx.ellipse(x, y-42, 24, 26, 0, 0, Math.PI*2);  // head
            ctx.fillStyle = '#8d5524';  // base skin
            ctx.fill();
            ctx.strokeStyle = '#3e2a1f';
            ctx.lineWidth = 2;
            ctx.stroke();

            // shiny anime eyes (big, determined)
            ctx.save();
            ctx.shadowColor = '#fffde7';
            ctx.shadowBlur = 10;
            // left eye
            ctx.beginPath();
            ctx.ellipse(x-10, y-50, 5, 8, 0, 0, Math.PI*2);
            ctx.fillStyle = '#ffffff';
            ctx.fill();
            ctx.fillStyle = '#2b1e12';
            ctx.beginPath();
            ctx.arc(x-13, y-53, 3, 0, Math.PI*2);
            ctx.fill();
            ctx.fillStyle = 'white';
            ctx.beginPath();
            ctx.arc(x-14, y-55, 1.2, 0, Math.PI*2);
            ctx.fill();

            // right eye
            ctx.beginPath();
            ctx.ellipse(x+10, y-50, 5, 8, 0, 0, Math.PI*2);
            ctx.fillStyle = '#ffffff';
            ctx.fill();
            ctx.fillStyle = '#2b1e12';
            ctx.beginPath();
            ctx.arc(x+7, y-53, 3, 0, Math.PI*2);
            ctx.fill();
            ctx.fillStyle = 'white';
            ctx.beginPath();
            ctx.arc(x+6, y-55, 1.2, 0, Math.PI*2);
            ctx.fill();
            ctx.restore();

            // iconic mj smile / determined mouth
            ctx.beginPath();
            ctx.strokeStyle = '#5a3f2b';
            ctx.lineWidth = 2;
            ctx.arc(x, y-40, 9, 0.1, Math.PI - 0.1);
            ctx.stroke();

            // ears
            ctx.fillStyle = '#8d5524';
            ctx.beginPath();
            ctx.ellipse(x-24, y-42, 5, 8, 0, 0, Math.PI*2);
            ctx.fill();
            ctx.beginPath();
            ctx.ellipse(x+24, y-42, 5, 8, 0, 0, Math.PI*2);
            ctx.fill();

            // bald head with fade line (anime effect)
            ctx.beginPath();
            ctx.strokeStyle = '#c57e4a';
            ctx.lineWidth = 2.5;
            ctx.setLineDash([5, 6]);
            ctx.arc(x, y-54, 20, 0.2, Math.PI - 0.2);
            ctx.stroke();
            ctx.setLineDash([]); // reset

            // body (jersey)
            ctx.fillStyle = '#c41e3a';  // red like bulls
            ctx.beginPath();
            ctx.ellipse(x, y+8, 28, 35, 0, 0, Math.PI*2);
            ctx.fill();
            // number 23
            ctx.font = 'bold 22px "Courier New", monospace';
            ctx.fillStyle = '#f9eec1';
            ctx.shadowColor = '#440000';
            ctx.shadowBlur = 8;
            ctx.fillText('23', x-19, y+24);
            ctx.shadowBlur = 0;

            // shorts
            ctx.fillStyle = '#b22222';
            ctx.beginPath();
            ctx.ellipse(x, y+45, 30, 20, 0, 0, Math.PI*2);
            ctx.fill();
            // legs
            ctx.strokeStyle = '#6b4226';
            ctx.lineWidth = 9;
            ctx.beginPath();
            ctx.moveTo(x-12, y+58);
            ctx.lineTo(x-20, y+90);
            ctx.stroke();
            ctx.beginPath();
            ctx.moveTo(x+12, y+58);
            ctx.lineTo(x+20, y+90);
            ctx.stroke();

            // shoes
            ctx.fillStyle = '#111111';
            ctx.beginPath();
            ctx.ellipse(x-24, y+92, 8, 4, 0, 0, Math.PI*2);
            ctx.fill();
            ctx.beginPath();
            ctx.ellipse(x+20, y+92, 8, 4, 0, 0, Math.PI*2);
            ctx.fill();

            // sweat effect (anime)
            ctx.fillStyle = '#add8e6';
            ctx.globalAlpha = 0.6;
            ctx.beginPath();
            ctx.arc(x-35, y-50, 3, 0, Math.PI*2);
            ctx.fill();
            ctx.globalAlpha = 1;
            ctx.restore();
        }

        function drawLBJ(x, y) {
            ctx.save();
            // skin tone (deep brown)
            ctx.fillStyle = '#6b4226';
            ctx.beginPath();
            ctx.ellipse(x, y-42, 26, 28, 0, 0, Math.PI*2);  // head
            ctx.fill();
            ctx.strokeStyle = '#3e2a1f';
            ctx.lineWidth = 2;
            ctx.stroke();

            // anime eyes (intense)
            ctx.save();
            ctx.shadowColor = 'white';
            ctx.shadowBlur = 8;
            ctx.beginPath();
            ctx.ellipse(x-12, y-50, 6, 9, 0, 0, Math.PI*2);
            ctx.fillStyle = '#f0f0f0';
            ctx.fill();
            ctx.fillStyle = '#1f120a';
            ctx.beginPath();
            ctx.arc(x-15, y-53, 3.5, 0, Math.PI*2);
            ctx.fill();
            ctx.fillStyle = 'white';
            ctx.beginPath();
            ctx.arc(x-16, y-55, 1.5, 0, Math.PI*2);
            ctx.fill();

            ctx.beginPath();
            ctx.ellipse(x+12, y-50, 6, 9, 0, 0, Math.PI*2);
            ctx.fillStyle = '#f0f0f0';
            ctx.fill();
            ctx.fillStyle = '#1f120a';
            ctx.beginPath();
            ctx.arc(x+9, y-53, 3.5, 0, Math.PI*2);
            ctx.fill();
            ctx.fillStyle = 'white';
            ctx.beginPath();
            ctx.arc(x+8, y-55, 1.5, 0, Math.PI*2);
            ctx.fill();
            ctx.restore();

            // lebron beard (anime style stubble)
            ctx.fillStyle = '#4a3320';
            ctx.globalAlpha = 0.4;
            ctx.beginPath();
            ctx.ellipse(x, y-34, 12, 6, 0, 0, Math.PI*2);
            ctx.fill();
            ctx.globalAlpha = 1;

            // headband
            ctx.fillStyle = '#ff4d4d';
            ctx.beginPath();
            ctx.ellipse(x, y-58, 22, 7, 0, 0, Math.PI*2);
            ctx.fill();

            // ears
            ctx.fillStyle = '#6b4226';
            ctx.beginPath();
            ctx.ellipse(x-26, y-44, 5, 9, 0, 0, Math.PI*2);
            ctx.fill();
            ctx.beginPath();
            ctx.ellipse(x+26, y-44, 5, 9, 0, 0, Math.PI*2);
            ctx.fill();

            // jersey (blue and gold)
            ctx.fillStyle = '#2d4f7c';
            ctx.beginPath();
            ctx.ellipse(x, y+8, 30, 37, 0, 0, Math.PI*2);
            ctx.fill();
            ctx.fillStyle = '#f4c542';
            ctx.font = 'bold 22px "Courier New", monospace';
            ctx.fillText('23', x-19, y+24);

            // shorts
            ctx.fillStyle = '#1f3a5f';
            ctx.beginPath();
            ctx.ellipse(x, y+45, 32, 21, 0, 0, Math.PI*2);
            ctx.fill();

            // legs
            ctx.strokeStyle = '#4f311b';
            ctx.lineWidth = 10;
            ctx.beginPath();
            ctx.moveTo(x-15, y+58);
            ctx.lineTo(x-24, y+92);
            ctx.stroke();
            ctx.beginPath();
            ctx.moveTo(x+15, y+58);
            ctx.lineTo(x+24, y+92);
            ctx.stroke();

            // shoes
            ctx.fillStyle = '#222222';
            ctx.beginPath();
            ctx.ellipse(x-28, y+94, 9, 5, 0, 0, Math.PI*2);
            ctx.fill();
            ctx.beginPath();
            ctx.ellipse(x+24, y+94, 9, 5, 0, 0, Math.PI*2);
            ctx.fill();

            // anime spark (determination)
            ctx.fillStyle = '#ffdb9f';
            ctx.globalAlpha = 0.5;
            ctx.beginPath();
            ctx.arc(x+35, y-75, 12, 0, Math.PI*2);
            ctx.fill();
            ctx.globalAlpha = 1;
            ctx.restore();
        }

        // draw basketball
        function drawBall(x, y, r) {
            ctx.save();
            ctx.shadowColor = '#222222';
            ctx.shadowBlur = 12;
            ctx.beginPath();
            ctx.arc(x, y, r, 0, 2 * Math.PI);
            ctx.fillStyle = '#d87c1c';
            ctx.fill();
            ctx.strokeStyle = '#2b1e0e';
            ctx.lineWidth = 3;
            ctx.stroke();
            // black curved lines
            ctx.beginPath();
            ctx.moveTo(x - r+3, y - r+3);
            ctx.lineTo(x + r-4, y + r-4);
            ctx.strokeStyle = '#2c2c2c';
            ctx.lineWidth = 2.8;
            ctx.stroke();
            ctx.beginPath();
            ctx.moveTo(x + r-4, y - r+3);
            ctx.lineTo(x - r+3, y + r-4);
            ctx.stroke();
            ctx.restore();
        }

        // draw court with anime vibes
        function drawCourt() {
            // gradient floor
            const grd = ctx.createLinearGradient(0, 0, 0, H);
            grd.addColorStop(0, '#a7e0b0');
            grd.addColorStop(1, '#479f7a');
            ctx.fillStyle = grd;
            ctx.fillRect(0, 0, W, H);

            // key lines
            ctx.strokeStyle = '#f8f0d5';
            ctx.lineWidth = 4;
            ctx.setLineDash([15, 20]);
            ctx.beginPath();
            ctx.moveTo(0, H/2+20);
            ctx.lineTo(W, H/2+20);
            ctx.stroke();

            ctx.setLineDash([]);
            ctx.lineWidth = 5;
            ctx.strokeStyle = '#ebd6b0';
            // center circle
            ctx.beginPath();
            ctx.arc(W/2, H-110, 60, 0, Math.PI*2);
            ctx.stroke();

            // three point lines (anime curvy)
            ctx.beginPath();
            ctx.strokeStyle = '#c9af7b';
            ctx.lineWidth = 3;
            ctx.ellipse(150, H-150, 70, 40, 0, 0, Math.PI*2);
            ctx.stroke();
            ctx.beginPath();
            ctx.ellipse(750, H-150, 70, 40, 0, 0, Math.PI*2);
            ctx.stroke();

            // anime glow spots
            ctx.fillStyle = '#fef7d6';
            ctx.globalAlpha = 0.4;
            for (let i=0; i<3; i++) {
                ctx.beginPath();
                ctx.arc(150 + i*300, H-100, 12, 0, Math.PI*2);
                ctx.fill();
            }
            ctx.globalAlpha = 1;
        }

        // ==========  animation & collision ==========
        function updateBall() {
            // move ball
            ball.x += ball.vx * speedFactor;
            // simple bouncing y (dribble)
            ball.bouncePhase += 0.15 * speedFactor;
            ball.y = (ball.owner === 'mj' ? mjPos.y-45 : lbjPos.y-45) + Math.abs(Math.sin(ball.bouncePhase) * 20) - 15;

            // boundary check + scoring / change possession
            if (ball.x > lbjPos.x - 40 && ball.x < lbjPos.x + 40 && ball.owner === 'mj') {
                // reached LeBron -> lbj steals? but we count as receive (score for lbj)
                if (ball.vx > 0) {
                    lbjScore += 1;
                    lbjScoreSpan.textContent = lbjScore;
                    ball.owner = 'lbj';
                    ball.vx = -BASE_SPEED;  // now go towards mj
                    ball.x = lbjPos.x - 25;
                }
            } else if (ball.x < mjPos.x + 40 && ball.x > mjPos.x - 40 && ball.owner === 'lbj') {
                if (ball.vx < 0) {
                    mjScore += 1;
                    mjScoreSpan.textContent = mjScore;
                    ball.owner = 'mj';
                    ball.vx = BASE_SPEED;  // towards lbj
                    ball.x = mjPos.x + 30;
                }
            }

            // keep ball from leaving court horizontally (just in case)
            if (ball.x < 40) { ball.x = 40; ball.vx = BASE_SPEED; ball.owner='mj';}
            if (ball.x > W-40) { ball.x = W-40; ball.vx = -BASE_SPEED; ball.owner='lbj';}
        }

        function drawScene() {
            ctx.clearRect(0, 0, W, H);
            drawCourt();

            // draw players
            drawMJ(mjPos.x, mjPos.y);
            drawLBJ(lbjPos.x, lbjPos.y);

            // draw ball
            drawBall(ball.x, ball.y, ball.radius);

            // extra anime FX: speed lines if speedFactor > 1.2
            if (speedFactor > 1.2) {
                ctx.save();
                ctx.strokeStyle = '#fffdd0';
                ctx.lineWidth = 2;
                for (let s=0; s<5; s++) {
                    let xOff = 200 + s*100;
                    ctx.beginPath();
                    ctx.moveTo(xOff, 200);
                    ctx.lineTo(xOff-40, 350);
                    ctx.strokeStyle = '#ffe68f';
                    ctx.globalAlpha = 0.5;
                    ctx.stroke();
                }
                ctx.restore();
            }
        }

        // animation loop
        function animate() {
            updateBall();
            drawScene();
            animFrame = requestAnimationFrame(animate);
        }

        // start animation
        animFrame = requestAnimationFrame(animate);

        // ===  canvas click = speed burst (anime powerup) ===
        canvas.addEventListener('click', (e) => {
            speedFactor = 2.4;
            setTimeout(() => {
                speedFactor = 1.0;
            }, 400);
        });

        // reset button
        document.getElementById('resetBtn').addEventListener('click', () => {
            mjScore = 0;
            lbjScore = 0;
            mjScoreSpan.textContent = '0';
            lbjScoreSpan.textContent = '0';
            ball = {
                x: mjPos.x + 30,
                y: mjPos.y - 30,
                vx: BASE_SPEED,
                vy: 0,
                bouncePhase: 0,
                radius: 16,
                owner: 'mj'
            };
            speedFactor = 1.0;
        });

        // (optional) adjust speed on window blur? ignore
        // clean up animation (not critical for demo)
        window.addEventListener('beforeunload', () => {
            if (animFrame) cancelAnimationFrame(animFrame);
        });
    })();
</script>
</body>
</html>
