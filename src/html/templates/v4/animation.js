function animateText(ctx, commentChunks, duration, lineHeight, stopRecording) {
    const chunkDuration = duration / commentChunks.length;
    let startTime = null;
    let opacities = commentChunks.map(() => 0);

    function animate(timestamp) {
        if (!startTime) startTime = timestamp;
        const elapsed = timestamp - startTime;

        commentChunks.forEach((_, index) => {
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

        drawComment(ctx, '{{ author }}', '12 days ago', '{{ votes }}', commentChunks, opacities, lineHeight);

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
