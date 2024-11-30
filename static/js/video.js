import io from socketio

const socketio = io.connect(${ window.location.protocol })

socketio.emit('start_video_stream');

socketio.on('video_frame', (data) => {
    const img = document.getElementById('videoFeed');
    img.src = 'data:image/jpeg;base64,' + data.frame;
});