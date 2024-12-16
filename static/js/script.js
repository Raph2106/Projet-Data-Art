document.addEventListener('DOMContentLoaded', function () {
    const permissionButton = document.getElementById('permissionButton');
    const dataContainer = document.querySelector('.data-container');
    const startStopButton = document.getElementById('start_stop');
    const sendStatus = document.getElementById('sendStatus');

    const url = 'http://127.0.0.1:1120/data';
    const delay = 1000;

    let accX = 0;
    let accY = 0;
    let accZ = 0;
    let list_accX = []
    let list_accY = []
    let list_accZ = []
    let avgX = 0
    let avgY = 0
    let avgZ = 0

    let envoi = false;

    startStopButton.disabled = true;

    function recup_acc(event) {
        accX = event.accelerationIncludingGravity.x.toFixed(1) || 0;
        accY = event.accelerationIncludingGravity.y.toFixed(1) || 0;
        accZ = event.accelerationIncludingGravity.z.toFixed(1) || 0;
        list_accX.push(accX)
        list_accY.push(accY)
        list_accZ.push(accZ)
        document.getElementById('accX').innerText = accX;
        document.getElementById('accY').innerText = accY;
        document.getElementById('accZ').innerText = accZ;
    }

    function sendDataToServer() {
        for (wx in list_accX) {

        }
        fetch(url, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({ "x": accX, "y": accY, "z": accZ })
        })
            .then(response => response.json())
            .then(data => console.log("Données envoyées avec succès:", data))
            .catch(error => console.error("Erreur d'envoi des données:", error));
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

    function check_compatibilite() {
        startStopButton.disabled = false;
        sendStatus.textContent = "inactif";
        window.removeEventListener('devicemotion', check_compatibilite);
    }
    sendStatus.textContent = "inactif (pas d'accéléromètre détécté, essayez de bouger votre appareil)";
    window.addEventListener('devicemotion', check_compatibilite);
});
