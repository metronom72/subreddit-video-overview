function getDurationFromUrl() {
    const urlParams = new URLSearchParams(window.location.search);
    return parseInt(urlParams.get('duration'), 10) || 10000; // Default to 10000ms if no duration specified
}

function joinArrayWithBr(array, node) {
    // Ensure the node is a valid DOM element
    if (!(node instanceof HTMLElement)) {
        throw new Error("The second argument must be a valid DOM element.");
    }

    // clear the element
    node.innerHTML = ""

    // Join the array elements with <br> tags
    // Append the resulting string to the specified node
    node.innerHTML = array.join('<br>');
}

function getChunks(paragraphs, chunkSize = 150) {
    //[paragraph, paragraph, paragraph] [[word, word, ...], [word, word, ...], [word, word, ...]]
    paragraphs = paragraphs.map(paragraph => paragraph.split(/\s+/))

    const chunks = [[]]

    function lastChunkIndex() {
        return chunks.length - 1
    }

    function lastParagraphIndex() {
        return chunks[lastChunkIndex()].length - 1
    }

    paragraphs.forEach((paragraph, pIndex) => {
        paragraph.forEach((word, sIndex) => {
            if (sIndex === 0) {
                chunks[lastChunkIndex()].push([])
            }

            if (chunks[lastChunkIndex()].flat().length < chunkSize) {
                chunks[lastChunkIndex()][lastParagraphIndex()].push(word);
            } else {
                chunks.push([[]])
            }
        })
    })

    return chunks
}

function animateText(element) {
    const chunks = getChunks(window.comment)
    const totalDuration = getDurationFromUrl();
    const wordsList = chunks.flat().flat()
    const sectionDuration = Math.ceil(totalDuration / chunks.length)
    let sectionDurations = chunks.map((chunk) => chunk.flat().length / wordsList.length)
    const totalLengthRelative = sectionDurations.reduce((acc, val) => acc + val, 0)
    sectionDurations = sectionDurations.map((t) => t / totalLengthRelative * totalDuration)

    chunks.forEach((chunk, chIndex) => {
        const pastDuration = sectionDurations.slice(0, chIndex + 1).reduce((acc, val) => acc + val, 0)

        setTimeout(() => {
            element.innerHTML = ''
            chunk = chunk.flat()
            const totalChunks = Math.ceil(chunk.length / 5);
            const chunkDuration = sectionDurations[chIndex] / totalChunks;

            chunk.forEach((word, index) => {
                const span = document.createElement('span');
                span.innerHTML = word + ' ';
                span.classList.add('hidden');
                element.appendChild(span);

                const chunkIndex = Math.floor(index / 5);
                setTimeout(() => {
                    for (let i = chunkIndex * 5; i < (chunkIndex + 1) * 5 && i < chunk.length; i++) {
                        element.children[i].classList.add('visible');
                    }

                    if (index === chunk.length - 1 && chIndex === chunks.length - 1) {
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
            console.log(chIndex, pastDuration, pastDuration + sectionDurations[chIndex])
        }, pastDuration - sectionDurations[chIndex])
    })
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