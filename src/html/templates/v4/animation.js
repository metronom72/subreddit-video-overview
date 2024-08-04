function animateText(ctx, commentChunks, duration, lineHeight, stopRecording = null) {
    const chunkDuration = duration / commentChunks.length;
    let startTime = null;
    let opacities = commentChunks.map(() => 0);

    function animate(timestamp) {
        if (!startTime) startTime = timestamp;
        const elapsed = timestamp - startTime;

        commentChunks.forEach((_, index) => {
            const delay = index * (chunkDuration);
            if (elapsed > delay) {
                const fadeElapsed = elapsed - delay;
                if (fadeElapsed < chunkDuration) {
                    opacities[index] = fadeElapsed / (chunkDuration);
                } else {
                    opacities[index] = 1;
                }
            }
        });

        drawComment(ctx, window.author || '{{ author }}', '12 days ago', window.votes || '{{ votes }}', commentChunks, opacities, lineHeight);

        if (elapsed < duration) {
            requestAnimationFrame(animate);
        } else if (stopRecording instanceof Function) {
            stopRecording();
        }
    }

    requestAnimationFrame(animate);
}

function startAnimation(canvas, ctx) {
    const comment = "This comment should be split into chunks, as sentences or chunks of 5 words maximum. These chunks should appear one after another within a box 712px wide with a comfortable fade effect. This comment should appear in a fixed duration, 10 seconds by default. ";
    const duration = 30 * 1000; // 10 seconds in milliseconds
    const wordsPerChunk = 5;

    startRecording(canvas);

    setTimeout(() => {
        const chunks = createTextChunks(comment.repeat(40), canvas, ctx).map(({text}) => splitText(text, wordsPerChunk));
        const cssProperties = getCSSProperties(canvas, ['font', 'line-height']);
        ctx.font = cssProperties.font; // Keep the original font size
        const lineHeight = cssProperties['line-height'];
        const totalLength = chunks.flat().length
        const durationsDistribution = chunks.map((chunk) => chunk.length / totalLength * duration)
        chunks.forEach((chunk, index) => {
            const pastDuration = durationsDistribution.slice(0, index).reduce((total, chunkDuration) => {
                total += chunkDuration
                return total;
            }, 0)
            setTimeout(() => {
                animateText(ctx, chunk, durationsDistribution[index], lineHeight, index === chunks.length - 1 ? stopRecording : null);
            }, pastDuration)
        })
    }, 500); // Adjust this delay if necessary to ensure recording starts before animation
}
