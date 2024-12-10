document.addEventListener('DOMContentLoaded', function () {
    const permissionButton = document.getElementById('permissionButton');
    const dataContainer = document.querySelector('.data-container');
    const startStopButton = document.getElementById('start_stop');
    const sendStatus = document.getElementById('sendStatus');
    const testButton = document.getElementById('testButton')

    let socket = null

    let accX = 0;
    let accY = 0;
    let accZ = 0;

    let envoi = false;
    startStopButton.disabled = true;

    const delay = 1000;

    let intervalId;

    function recup_acc(event) {
        accX = event.accelerationIncludingGravity.x.toFixed(1) || 0;
        accY = event.accelerationIncludingGravity.y.toFixed(1) || 0;
        accZ = event.accelerationIncludingGravity.z.toFixed(1) || 0;

        document.getElementById('accX').innerText = accX;
        document.getElementById('accY').innerText = accY;
        document.getElementById('accZ').innerText = accZ;
    }

    function initializeSocket() {
        if (!socket) {
            socket = io.connect(`${window.location.protocol}//${window.location.hostname}/websocket:${window.location.port}`);
            socket.on('data_response', function (data) {
                console.log("Réponse serveur :", data);
            });
        }
    }

    function sendDataToServer() {
        if (socket) {
            socket.emit('send_data', { "x": accX, "y": accY, "z": accZ });
        }
    }

    function main() {
        permissionButton.style.display = 'none';
        dataContainer.style.display = 'block';
        window.addEventListener('devicemotion', recup_acc);
        startStopButton.addEventListener('click', function () {
            if (!envoi) {
                initializeSocket();
                intervalId = setInterval(sendDataToServer, delay);
                envoi = true;
                sendStatus.textContent = "actif";
            } else {
                clearInterval(intervalId);
                socket = null
                envoi = false;
                sendStatus.textContent = "inactif";
            }
        });
        testButton.addEventListener('click', function () {
            fetch('/test')
                .then(response => response.text())
                .then(data => alert(data))
                .catch(error => console.error('Erreur : ', error))
        });
    }

    if (typeof DeviceMotionEvent !== 'undefined') {
        if (typeof DeviceMotionEvent.requestPermission === 'function') {
            permissionButton.addEventListener('click', function () {
                DeviceMotionEvent.requestPermission().then(function (permissionState) {
                    if (permissionState === 'granted') {
                        main();
                    } else {
                        alert('L\'autorisation d\'accès aux capteurs a été refusée.');
                    }
                }).catch(function (error) {
                    console.error('Erreur lors de la demande d\'autorisation :', error);
                    alert('Une erreur est survenue lors de la demande d\'autorisation.');
                });
            });
        } else {
            main();
        }
    } else {
        alert('API DeviceMotionEvent non supportée sur cet appareil.');
        startStopButton.disabled = true;
        permissionButton.style.display = 'none';
    }

    function check_compatibilite() {
        startStopButton.disabled = false;
        sendStatus.textContent = "inactif";
        window.removeEventListener('devicemotion', check_compatibilite);
    }
    sendStatus.textContent = "inactif (pas d'accéléromètre détécté, essayez de bouger votre appareil)";
    window.addEventListener('devicemotion', check_compatibilite);
});
