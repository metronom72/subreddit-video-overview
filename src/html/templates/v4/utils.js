const scaleFactor = 2;

function setupCanvas(canvas, ctx) {
    canvas.width = 756 * scaleFactor;
    canvas.height = 400 * scaleFactor; // Adjust height as needed
    canvas.style.width = '756px';
    canvas.style.height = '400px';

    // Scale the context
    ctx.scale(scaleFactor, scaleFactor);
}

function splitText(text, maxWords) {
    const words = text.split(' ');
    const chunks = [];
    for (let i = 0; i < words.length; i += maxWords) {
        chunks.push(words.slice(i, i + maxWords).join(' '));
    }
    return chunks;
}

function createTextChunks(text, canvas, context) {
    const canvasChunks = [];
    const words = text.split(' ');

    const originalFont = context.font;
    // why???
    const originalWidth = (756 - 120) / 2;
    const originalHeight = (400 - 120) / 2;

    console.log(originalWidth, originalHeight)

    context.clearRect(0, 0, originalWidth, originalHeight);

    let x = 0;
    let y = parseInt(originalFont, 10); // Get the font size from the font property

    let currentChunkText = '';

    function addChunk() {
        const chunkCanvas = document.createElement('canvas');
        chunkCanvas.width = originalWidth;
        chunkCanvas.height = originalHeight;
        const chunkContext = chunkCanvas.getContext('2d');

        // Copy canvas properties
        chunkContext.font = originalFont;
        chunkContext.drawImage(canvas, 0, 0);

        canvasChunks.push({
            text: currentChunkText.trim(),
            canvas: chunkCanvas
        });

        context.clearRect(0, 0, originalWidth, originalHeight);
        x = 0;
        y = parseInt(originalFont, 10);
        currentChunkText = '';
    }

    words.forEach(word => {
        const wordWidth = context.measureText(word + ' ').width;
        if (x + wordWidth > originalWidth) {
            x = 0;
            y += parseInt(originalFont, 10);
        }
        if (y > originalHeight) {
            addChunk();
        }
        context.fillText(word + ' ', x, y);
        x += wordWidth;
        currentChunkText += word + ' ';
    });

    // Add the final chunk
    if (currentChunkText.trim().length > 0) {
        addChunk();
    }

    return canvasChunks;
}

function getCSSProperties(element, properties) {
    const styles = window.getComputedStyle(element);
    const result = {};
    properties.forEach(prop => {
        result[prop] = styles[prop];
    });
    return result;
}
