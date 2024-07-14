function drawText(ctx, chunks, opacities, lineHeight) {
    const canvas = ctx.canvas;
    ctx.clearRect(0, 0, canvas.width / 2, canvas.height / 2);
    ctx.fillStyle = '#fff'; // White background
    ctx.fillRect(0, 0, canvas.width / 2, canvas.height / 2);

    ctx.textAlign = 'left';
    ctx.textBaseline = 'top';
    ctx.fillStyle = '#000';

    let x = 0;
    let y = 0;
    const maxWidth = canvas.width / 2;

    chunks.forEach((text, index) => {
        ctx.globalAlpha = opacities[index];
        const metrics = ctx.measureText(text);
        const textWidth = metrics.width;

        if (x + textWidth > maxWidth) {
            x = 0;
            y += parseFloat(lineHeight);
        }

        ctx.fillText(text, x, y);
        x += textWidth + 10; // Adding 10 pixels space between chunks
    });

    ctx.globalAlpha = 1; // Reset globalAlpha to default
}

function animateText(ctx, chunks, duration, lineHeight, stopRecording) {
    const chunkDuration = duration / chunks.length;
    let startTime = null;
    let opacities = chunks.map(() => 0);

    function animate(timestamp) {
        if (!startTime) startTime = timestamp;
        const elapsed = timestamp - startTime;

        chunks.forEach((_, index) => {
            const delay = index * (chunkDuration / 2);
            if (elapsed > delay) {
                const fadeElapsed = elapsed - delay;
                if (fadeElapsed < chunkDuration / 2) {
                    opacities[index] = fadeElapsed / (chunkDuration / 2);
                } else {
                    opacities[index] = 1;
                }
            }
        });

        drawText(ctx, chunks, opacities, lineHeight);

        if (elapsed < duration) {
            requestAnimationFrame(animate);
        } else {
            stopRecording();
        }
    }

    requestAnimationFrame(animate);
}

function startAnimation(canvas, ctx) {
    const comment = "This comment should be split into chunks, as sentences or chunks of 5 words maximum. These chunks should appear one after another within a box 712px wide with a comfortable fade effect. This comment should appear in a fixed duration, 10 seconds by default.";
    const duration = 10 * 1000; // 10 seconds in milliseconds
    const wordsPerChunk = 5;

    startRecording(canvas);

    setTimeout(() => {
        const chunks = splitText(comment, wordsPerChunk);
        const cssProperties = getCSSProperties(canvas, ['font', 'line-height']);
        ctx.font = cssProperties.font; // Keep the original font size
        const lineHeight = cssProperties['line-height'];
        animateText(ctx, chunks, duration, lineHeight, stopRecording);
    }, 500); // Adjust this delay if necessary to ensure recording starts before animation
}
