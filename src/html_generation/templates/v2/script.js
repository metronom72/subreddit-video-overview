function getDurationFromUrl() {
    const urlParams = new URLSearchParams(window.location.search);
    return parseInt(urlParams.get('duration'), 10) || 10000; // Default to 10000ms if no duration specified
}

function animateText(element) {
    const text = element.innerHTML;
    const words = text.split(' ');
    element.innerHTML = '';

    const totalDuration = getDurationFromUrl();
    const totalChunks = Math.ceil(words.length / 5);
    const chunkDuration = totalDuration / totalChunks;

    words.forEach((word, index) => {
        const span = document.createElement('span');
        span.innerHTML = word + ' ';
        span.classList.add('hidden');
        element.appendChild(span);

        const chunkIndex = Math.floor(index / 5);
        setTimeout(() => {
            for (let i = chunkIndex * 5; i < (chunkIndex + 1) * 5 && i < words.length; i++) {
                element.children[i].classList.add('visible');
            }
            if (index === words.length - 1) {
                setTimeout(() => {
                    const body = document.querySelector('body');
                    body.setAttribute('data-rendering-over', true);
                }, 2000);

                setTimeout(() => {
                    const body = document.body;
                    body.style.cssText = 'opacity: 0;';
                }, 750);
            }
        }, chunkIndex * chunkDuration);
    });
}

document.addEventListener('DOMContentLoaded', () => {
    setTimeout(() => {
        const commentText = document.getElementById('comment1');
        commentText.style.cssText = 'opacity: 1;';
        animateText(commentText);
    }, 1000);

    setTimeout(() => {
        const body = document.body;
        body.style.cssText = 'opacity: 1;';
    }, 1000);
});
