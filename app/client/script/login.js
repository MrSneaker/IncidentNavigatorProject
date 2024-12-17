function submitLogin(event) {
    event.preventDefault();
    const username = document.querySelector('#username').value;
    const password = document.querySelector('#password').value;

    fetch('/login', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ username: username, password: password })
    }).then(response => response.json()).then(data => {
        if (data.error) {
            document.querySelector('#errorMessage').innerText = data.error;
            document.querySelector('#errorMessage').style.display = 'block';
        } else {
            alert('Connexion réussie !');
            jwtToken = data.token;
            sessionStorage.setItem("jwt", jwtToken);
            getNavigatorPage();
        }
    }).catch(error => {
        console.error('Erreur :', error);
        document.querySelector('#errorMessage').innerText = "Une erreur est survenue.";
        document.querySelector('#errorMessage').style.display = 'block';
    });
}

function getNavigatorPage() {
    fetch('/incidentnavigator', {
        method: 'GET',
        headers: {
            'Authorization': 'Bearer ' + sessionStorage.getItem('jwt')
        }
    }).then(response => {
        if (response.ok) {
            return response.text();  
        } else {
            console.log('error : ', response.text());
            throw new Error("Token invalide ou expiré");
        } 
    }).then(html => {
        document.documentElement.innerHTML = html;
        document.querySelectorAll('script').forEach((script) => {
            const newScript = document.createElement('script');
            newScript.src = script.src + '?v=' + new Date().getTime();
            document.body.appendChild(newScript);
        });
    }).catch(error => {
        console.error("Erreur : ", error);
    });
}

window.addEventListener('load', async function() {
    const jwtToken = sessionStorage.getItem('jwt');
    if (jwtToken) {
        try {
            await getNavigatorPage();
        } catch (error) {
            console.error("Erreur lors du chargement de la page de navigation :", error);
            sessionStorage.removeItem('jwt');
            window.location.href = '/';
        }
    } else {
        console.log('Aucun token trouvé. L\'utilisateur doit se connecter.');
    }
});

