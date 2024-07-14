function drawSvgPath(ctx, pathData, x, y, scale = 1) {
    const path = new Path2D(pathData);
    ctx.save();
    ctx.translate(x, y);
    ctx.scale(scale, scale);
    ctx.fill(path);
    ctx.restore();
}

function drawRoundedRect(ctx, x, y, width, height, radius) {
    ctx.beginPath();
    ctx.moveTo(x + radius, y);
    ctx.lineTo(x + width - radius, y);
    ctx.quadraticCurveTo(x + width, y, x + width, y + radius);
    ctx.lineTo(x + width, y + height - radius);
    ctx.quadraticCurveTo(x + width, y + height, x + width - radius, y + height);
    ctx.lineTo(x + radius, y + height);
    ctx.quadraticCurveTo(x, y + height, x, y + height - radius);
    ctx.lineTo(x, y + radius);
    ctx.quadraticCurveTo(x, y, x + radius, y);
    ctx.closePath();
}

function drawAuthorImage(ctx, x, y, size) {
    ctx.fillStyle = 'gray';
    ctx.beginPath();
    ctx.arc(x + size / 2, y + size / 2, size / 2, 0, Math.PI * 2);
    ctx.fill();
}

function drawCommentText(ctx, commentChunks, opacities, lineHeight, startX, startY, maxWidth) {
    let x = startX;
    let y = startY;

    ctx.fillStyle = '#000000'; // Pure black text for comment
    commentChunks.forEach((text, index) => {
        ctx.globalAlpha = opacities[index];
        const metrics = ctx.measureText(text);
        const textWidth = metrics.width;

        if (x + textWidth > maxWidth) {
            x = startX;
            y += parseFloat(lineHeight);
        }

        ctx.fillText(text, x, y);
        x += textWidth + 6; // Adding 10 pixels space between chunks
    });

    ctx.globalAlpha = 1; // Reset globalAlpha to default
}
