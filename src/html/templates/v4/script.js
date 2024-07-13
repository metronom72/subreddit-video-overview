const comment = "This comment should be split into chunks, as sentences or chunks of 5 words maximum. These chunks should appear one after another within a box 768px wide with a comfortable fade effect. This comment should appear in a fixed duration, 10 seconds by default.";
const duration = 10 * 1000; // 10 seconds in milliseconds
const wordsPerChunk = 5;

document.addEventListener('DOMContentLoaded', () => {
    const canvas = document.getElementById('textCanvas');
    const ctx = canvas.getContext('2d');

    // Set canvas dimensions to higher resolution
    const scaleFactor = 2;
    canvas.width = 768 * scaleFactor;
    canvas.height = 200 * scaleFactor; // Adjust height as needed
    canvas.style.width = '768px';
    canvas.style.height = '200px';

    // Scale the context
    ctx.scale(scaleFactor, scaleFactor);

    // Initialize log array
    let log = [];

    // Function to get CSS properties from an element
    function getCSSProperties(element, properties) {
        const styles = window.getComputedStyle(element);
        const result = {};
        properties.forEach(prop => {
            result[prop] = styles[prop];
        });
        return result;
    }

    function splitText(text, maxWords) {
        const words = text.split(' ');
        const chunks = [];
        for (let i = 0; i < words.length; i += maxWords) {
            chunks.push(words.slice(i, i + maxWords).join(' '));
        }
        return chunks;
    }

    function drawText(ctx, chunks, opacities, lineHeight) {
        ctx.clearRect(0, 0, canvas.width / scaleFactor, canvas.height / scaleFactor);
        ctx.textAlign = 'left';
        ctx.textBaseline = 'top';
        ctx.fillStyle = '#000';

        let x = 0;
        let y = 0;
        const maxWidth = canvas.width / scaleFactor;

        chunks.forEach((text, index) => {
            const metrics = ctx.measureText(text);
            const textWidth = metrics.width;

            if (x + textWidth > maxWidth) {
                x = 0;
                y += parseFloat(lineHeight);
            }

            ctx.globalAlpha = opacities[index];
            ctx.fillText(text, x, y);
            x += textWidth + 10; // Adding 10 pixels space between chunks
        });
    }

    function animateText(chunks, duration, lineHeight) {
        const chunkDuration = duration / chunks.length;
        let startTime = null;
        let opacities = chunks.map(() => 0);

        function animate(timestamp) {
            log.push({event: 'requestAnimationFrame', timestamp});

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

            if (elapsed < duration + chunkDuration / 2 * chunks.length) {
                requestAnimationFrame(animate);
            } else {
                // Stop recording when animation is done
                console.log("Stopping recording...");
                stopRecording();
            }
        }

        requestAnimationFrame(animate);
    }

    // MediaRecorder setup to capture the canvas animation
    let mediaRecorder;
    let recordedChunks = [];

    function startRecording() {
        console.log("Starting recording...");
        log.push({event: 'startRecording', timestamp: Date.now()});
        try {
            const stream = canvas.captureStream(30); // 30 fps
            console.log("Stream obtained:", stream);
            log.push({event: 'streamObtained', timestamp: Date.now()});
            mediaRecorder = new MediaRecorder(stream, {mimeType: 'video/webm; codecs=vp9'});
        } catch (e) {
            console.error("MediaRecorder initialization failed:", e);
            log.push({event: 'mediaRecorderError', error: e, timestamp: Date.now()});
            return;
        }

        mediaRecorder.ondataavailable = function (event) {
            console.log("Data available:", event.data);
            log.push({event: 'dataAvailable', timestamp: Date.now()});
            if (event.data.size > 0) {
                recordedChunks.push(event.data);
            }
        };

        mediaRecorder.onerror = function (event) {
            console.error("MediaRecorder error:", event);
            log.push({event: 'mediaRecorderError', error: event, timestamp: Date.now()});
        };

        mediaRecorder.onstart = function () {
            console.log("MediaRecorder started.");
            log.push({event: 'mediaRecorderStarted', timestamp: Date.now()});
        };

        mediaRecorder.onstop = function () {
            console.log("Recording stopped.");
            log.push({event: 'mediaRecorderStopped', timestamp: Date.now()});
            const blob = new Blob(recordedChunks, {type: 'video/webm'});
            const url = URL.createObjectURL(blob);
            const a = document.createElement('a');
            a.style.display = 'none';
            a.href = url;
            a.download = 'animation.webm';
            document.body.appendChild(a);
            a.click();
            window.URL.revokeObjectURL(url);
            console.log("Download link created and clicked.");
        };

        mediaRecorder.start(100); // Request data every 100ms
        console.log("MediaRecorder started.");
    }

    function stopRecording() {
        if (mediaRecorder && mediaRecorder.state !== 'inactive') {
            mediaRecorder.stop();
            console.log("MediaRecorder stopped.");
            log.push({event: 'stopRecording', timestamp: Date.now()});
        } else {
            console.log("MediaRecorder is not active or already stopped.");
            log.push({event: 'mediaRecorderNotActive', timestamp: Date.now()});
        }
    }

    setTimeout(() => {
        // Start recording
        startRecording();

        // Start animation
        const chunks = splitText(comment, wordsPerChunk);
        const cssProperties = getCSSProperties(canvas, ['font', 'line-height']);
        ctx.font = cssProperties.font; // Keep the original font size
        const lineHeight = cssProperties['line-height'];
        console.log("Starting animation...");
        log.push({event: 'startAnimation', timestamp: Date.now()});
        animateText(chunks, duration, lineHeight);
    }, 1000);
});
