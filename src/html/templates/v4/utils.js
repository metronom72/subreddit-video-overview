function setupCanvas(canvas, ctx) {
    const scaleFactor = 2;
    canvas.width = 712 * scaleFactor;
    canvas.height = 400 * scaleFactor; // Adjust height as needed
    canvas.style.width = '712px';
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

function getCSSProperties(element, properties) {
    const styles = window.getComputedStyle(element);
    const result = {};
    properties.forEach(prop => {
        result[prop] = styles[prop];
    });
    return result;
}
