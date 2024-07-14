function drawComment(ctx, author, date, votes, commentChunks, opacities, lineHeight) {
    const canvas = ctx.canvas;
    ctx.clearRect(0, 0, canvas.width / 2, canvas.height / 2);
    ctx.fillStyle = '#ffffff'; // White background

    // Drawing the border with rounded corners
    const borderRadius = 10;
    const borderMargin = 25; // Increased margin 2.5 times from 10 to 25
    const borderWidth = canvas.width / 2 - 2 * borderMargin;
    const borderHeight = canvas.height / 2 - 2 * borderMargin;

    ctx.fillStyle = '#ffffff'; // Background color
    ctx.strokeStyle = 'gray'; // Gray border color
    ctx.lineWidth = 1; // 1px border size

    drawRoundedRect(ctx, borderMargin, borderMargin, borderWidth, borderHeight, borderRadius);
    ctx.fill();
    ctx.stroke();

    ctx.save();
    ctx.beginPath();
    drawRoundedRect(ctx, borderMargin, borderMargin, borderWidth, borderHeight, borderRadius);
    ctx.clip();

    ctx.textAlign = 'left';
    ctx.textBaseline = 'top';
    ctx.fillStyle = '#000000'; // Pure black text for author and comment

    // Adjusting for border margins
    const contentMargin = borderMargin + 20; // Increased padding 2x from 10 to 20

    // Author Image
    const authorImageX = contentMargin;
    const authorImageY = contentMargin;
    const authorImageSize = 40;
    drawAuthorImage(ctx, authorImageX, authorImageY, authorImageSize);

    ctx.fillStyle = '#000000'; // Pure black text for author
    const authorX = authorImageX + authorImageSize + 10;
    const authorY = authorImageY;
    ctx.fillText(author, authorX, authorY);

    ctx.fillStyle = '#888888'; // Gray text for date
    const dateX = authorX + ctx.measureText(author).width + 10;
    ctx.fillText(date, dateX, authorY);

    // Gray Line
    const lineX = authorImageX + authorImageSize / 2;
    const lineYStart = authorImageY + authorImageSize;
    const lineYEnd = lineYStart + 100;
    ctx.strokeStyle = 'gray';
    ctx.beginPath();
    ctx.moveTo(lineX, lineYStart);
    ctx.lineTo(lineX, lineYEnd);
    ctx.stroke();

    // Comment Text
    drawCommentText(ctx, commentChunks, opacities, lineHeight, authorX, authorY + 30, canvas.width / 2 - contentMargin - borderMargin);

    // Comment Actions
    const actionsY = authorY + 30 + commentChunks.length * parseFloat(lineHeight) + 20;

    // Upvote Icon
    const upvotePath = "M12.877 19H7.123A1.125 1.125 0 0 1 6 17.877V11H2.126a1.114 1.114 0 0 1-1.007-.7 1.249 1.249 0 0 1 .171-1.343L9.166.368a1.128 1.128 0 0 1 1.668.004l7.872 8.581a1.25 1.25 0 0 1 .176 1.348 1.113 1.113 0 0 1-1.005.7H14v6.877A1.125 1.125 0 0 1 12.877 19ZM7.25 17.75h5.5v-8h4.934L10 1.31 2.258 9.75H7.25v8ZM2.227 9.784l-.012.016c.01-.006.014-.01.012-.016Z";
    const upvoteX = lineX + 10;
    drawSvgPath(ctx, upvotePath, upvoteX, actionsY, 0.8);

    // Votes Text
    ctx.fillStyle = '#000000'; // Pure black text for votes
    ctx.fillText(votes, upvoteX + 20, actionsY);

    // Downvote Icon
    const downvoteX = upvoteX + ctx.measureText(votes).width + 25;
    const downvotePath = "M10 20a1.122 1.122 0 0 1-.834-.372l-7.872-8.581A1.251 1.251 0 0 1 1.118 9.7 1.114 1.114 0 0 1 2.123 9H6V2.123A1.125 1.125 0 0 1 7.123 1h5.754A1.125 1.125 0 0 1 14 2.123V9h3.874a1.114 1.114 0 0 1 1.007.7 1.25 1.25 0 0 1-.171 1.345l-7.876 8.589A1.128 1.128 0 0 1 10 20Zm-7.684-9.75L10 18.69l7.741-8.44H12.75v-8h-5.5v8H2.316Zm15.469-.05c-.01 0-.014.007-.012.013l.012-.013Z";
    drawSvgPath(ctx, downvotePath, downvoteX, actionsY, 0.8);

    // Reply and Share
    const replyX = downvoteX + 20;
    ctx.fillText('Reply', replyX, actionsY);

    const shareX = replyX + ctx.measureText('Reply').width + 20;
    ctx.fillText('Share', shareX, actionsY);

    ctx.restore();
}
