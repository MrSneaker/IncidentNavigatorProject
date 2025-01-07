async function login(email, password) {
    try {
        const response = await fetch('/auth/login', {
            method: 'POST',
            headers: { 
            'Content-Type': 'application/json'
            },
            credentials: 'include',
            body: JSON.stringify({ email: email, password: password })
        });
        const data = await response.json();
        sessionStorage.setItem('user_id', data.data.id);
        sessionStorage.setItem('username', data.data.username);
        sessionStorage.setItem('email', data.data.email);
        sessionStorage.setItem('token', data.data.token);
        return data;
    } catch (error) {
        return { error: -1, data: null };
    }
}

async function register(email, username, password) {
    try {
        const response = await fetch('/auth/register', {
            method: 'POST',
            headers: { 
            'Content-Type': 'application/json',
            },
            credentials: 'include',
            body: JSON.stringify({ email: email, username: username, password: password })
        });
        const data = await response.json();
        if (data.error) {
            return { error: data.error };
        } else {
            return { error: null };
        }
    } catch (error) {
        return { error: error };
    }
}


async function logout() {
    try {
        const response = await fetch('/auth/logout', {
            method: 'POST',
            headers: { 
            'Content-Type': 'application/json',
            },
            credentials: 'include',
        });
        response.json().then(data => {
            if (data.error) {
                return { error: data.error };
            }
            sessionStorage.removeItem('token');
            sessionStorage.removeItem('user_id');
            sessionStorage.removeItem('username');
            sessionStorage.removeItem('email');
            return { error: null };
        });
    } catch (error) {
        return { error: error };
    }
}

async function rename(newUsername) {
    try {
        const response = await fetch('/auth/rename', {
            method: 'POST',
            headers: { 
            'Content-Type': 'application/json',
            },
            credentials: 'include',
            body: JSON.stringify({ username: newUsername })
        });
        const data = await response.json();
        if (data.error) {
            return { error: data.error };
        } else {
            sessionStorage.setItem('username', newUsername);
            return { error: null };
        }
    } catch (error) {
        return { error: error };
    }
}

// get infos about the current user
async function getCurrent() {
    try {
        const response = await fetch('/auth/@me', {
            method: 'GET',
            headers: { 
            'Content-Type': 'application/json',
            },
            credentials: 'include',
        });
        const data = await response.json();
        return data;
        
    } catch (error) {
        return { error: -1, message: error, data: null };
    }
}

async function refreshToken() {
    try {
        const response = await fetch('/auth/refresh', {
            method: 'POST',
            headers: { 
            'Content-Type': 'application/json',
            },
            credentials: 'include',
        });
        response.json().then(data => {
            if (data.error) {
                return { error: data.error };
            } else {
                sessionStorage.setItem('token', data.data.token);
                return { error: null };
            }
        });
    } catch (error) {
        return { error: error };
    }
}

export { login, register, logout, rename, getCurrent, refreshToken }