let mediaRecorder;
let recordedChunks = [];

const mimeType = 'video/mp4; codecs=avc1.42E01E, mp4a.40.2'

function startRecording(canvas) {
    const options = {mimeType};

    if (!MediaRecorder.isTypeSupported(options.mimeType)) {
        console.warn(`${options.mimeType} is not supported, trying another option.`);
        options.mimeType = 'video/mp4'; // Fallback option
        if (!MediaRecorder.isTypeSupported(options.mimeType)) {
            console.error('Neither video/mp4 nor video/mp4; codecs=avc1.42E01E, mp4a.40.2 is supported on this browser.');
            return;
        }
    }

    try {
        const stream = canvas.captureStream(60); // 60 fps
        mediaRecorder = new MediaRecorder(stream, options);
    } catch (e) {
        console.error("MediaRecorder initialization failed:", e);
        return;
    }

    mediaRecorder.ondataavailable = function (event) {
        if (event.data.size > 0) {
            recordedChunks.push(event.data);
        }
    };

    mediaRecorder.onstop = function () {
        const blob = new Blob(recordedChunks, {type: mimeType});
        const url = URL.createObjectURL(blob);

        const videoContainer = document.getElementById('videoContainer');
        const video = document.createElement('video');
        video.controls = true;
        video.src = url;
        video.style.display = 'block';
        video.style.marginTop = '20px';

        const downloadLink = document.createElement('a');
        downloadLink.href = url;
        downloadLink.download = 'animation.webm';
        downloadLink.textContent = 'Download Video';
        downloadLink.style.display = 'block';
        downloadLink.style.marginTop = '10px';

        videoContainer.appendChild(video);
        videoContainer.appendChild(downloadLink);
    };

    mediaRecorder.start();
}

function stopRecording() {
    if (mediaRecorder && mediaRecorder.state !== 'inactive') {
        mediaRecorder.stop();
    }
}
