function getDurationFromUrl() {
    const urlParams = new URLSearchParams(window.location.search);
    return parseInt(urlParams.get('duration'), 10) || 10000; // Default to 10000ms if no duration specified
}

function joinArrayWithBr(array, node) {
  // Ensure the node is a valid DOM element
  if (!(node instanceof HTMLElement)) {
    throw new Error("The second argument must be a valid DOM element.");
  }

  // Join the array elements with <br> tags
  // Append the resulting string to the specified node
  node.innerHTML = array.join('<br>');
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
    joinArrayWithBr(window.comment, document.getElementById('comment1'));
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
