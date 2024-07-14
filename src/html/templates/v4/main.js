document.addEventListener('DOMContentLoaded', () => {
    const canvas = document.getElementById('textCanvas');
    const ctx = canvas.getContext('2d');

    setupCanvas(canvas, ctx);
    document.getElementById('startButton').onclick = () => startAnimation(canvas, ctx);
});
