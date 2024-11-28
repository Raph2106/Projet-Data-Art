document.addEventListener('DOMContentLoaded', function () {
    const permissionButton = document.getElementById('permissionButton');
    const dataContainer = document.querySelector('.data-container');
    const startStopButton = document.getElementById('start_stop');
    const sendStatus = document.getElementById('sendStatus');

    const socket = io.connect(`${window.location.protocol}//${window.location.hostname}:${window.location.port}`);

    let accX = 0;
    let accY = 0;
    let accZ = 0;

    let envoi = false;
    startStopButton.disabled = true;

    const delay = 500;

    let intervalId;

    function recup_acc(event) {
        accX = event.accelerationIncludingGravity.x.toFixed(1) || 0;
        accY = event.accelerationIncludingGravity.y.toFixed(1) || 0;
        accZ = event.accelerationIncludingGravity.z.toFixed(1) || 0;

        document.getElementById('accX').innerText = accX;
        document.getElementById('accY').innerText = accY;
        document.getElementById('accZ').innerText = accZ;
    }

    function sendDataToServer() {
        socket.emit('send_data', { x: accX, y: accY, z: accZ });
    }

    function main() {
        permissionButton.style.display = 'none';
        dataContainer.style.display = 'block';
        window.addEventListener('devicemotion', recup_acc);
        startStopButton.addEventListener('click', function () {
            if (!envoi) {
                intervalId = setInterval(sendDataToServer, delay);
                envoi = true;
                sendStatus.textContent = "actif";
            } else {
                clearInterval(intervalId);
                envoi = false;
                sendStatus.textContent = "inactif";
            }
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

    // Réception d'une réponse du serveur
    socket.on('data_response', function (data) {
        console.log("Réponse du serveur :", data);
    });

    function check_compatibilite(event) {
        startStopButton.disabled = false;
        endStatus.textContent = "inactif (pas d'accéléromètre détécté, essayez de bouger votre appareil)";
        window.removeEventListener('devicemotion', check_compatibilite);
    }
    window.addEventListener('devicemotion', check_compatibilite);
});
