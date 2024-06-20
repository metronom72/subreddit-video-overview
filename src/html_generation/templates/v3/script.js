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

function getChunks(paragraphs, chunkSize = 150) {
    //[paragraph, paragraph, paragraph] [[word, word, ...], [word, word, ...], [word, word, ...]]
    paragraphs = paragraphs.map(paragraph => paragraph.split(/\s+/))

    const chunks = []
    paragraphs.forEach((paragraph, pIndex) => {
        const lastChIndex = chunks.length - 1
        if (chunks.length === 0) {
            chunks.push([])
        }
        const lastPIndex = chunks[lastChIndex].length - 1
        if (pIndex === 0) {
            chunks[chunks.length - 1].push([])
        }
        paragraph.map((word, sIndex) => {
            if (chunks[lastChIndex][lastPIndex].length < chunkSize) {
                chunks[lastChIndex][lastPIndex].push(word);
            } else {
                chunks.push([word])
            }
        })
    })

    return chunks
}

function animateText(element) {
    const text = element.innerHTML;
    const words = text.split(/\s+/);
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
    console.log(getChunks(window.comment), window.comment)
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
