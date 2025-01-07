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

        if (response.status === 500) {
            return { error: -1, message: 'Internal server error' };
        }

        const data = await response.json();
        if (data.error) {
            sessionStorage.removeItem('user_id');
            sessionStorage.removeItem('username');
            sessionStorage.removeItem('email');
            sessionStorage.removeItem('token');

        } else {
            sessionStorage.setItem('user_id', data.data.id);
            sessionStorage.setItem('username', data.data.username);
            sessionStorage.setItem('email', data.data.email);
            sessionStorage.setItem('token', data.data.token);
        }
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

        if (response.status === 500) {
            return { error: -1, message: 'Internal server error' };
        }
        // check if the response is a json
        const data = await response.json();
        return data;
    } catch (error) {
        return { error: -1, message: error }
    }
}

async function logout() {
    try {
        sessionStorage.removeItem('token');
        sessionStorage.removeItem('user_id');
        sessionStorage.removeItem('username');
        sessionStorage.removeItem('email');
        
        const response = await fetch('/auth/logout', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            credentials: 'include',
        });

        if (response.status === 500) {
            return { error: 500, message: "Internal server error" }
        }
        const data = await response.json();
        return data;

    } catch (error) {
        return { error: -1, message: error };
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
        })

        if (response.status === 500) {
            return { error: 500, message: "Internal server error" }
        }
        const data = await response.json()
        return data
    } catch (error) {
        return { error: -1, message: error };
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
        if (response.status === 500) {
            return { error: 500, message: "Internal server error" }
        }
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
        
        if (response.status === 500) {
            return { error: 500, message: "Internal server error" }
        }

        const data = await response.json();
        if (data.error) {
            sessionStorage.removeItem('token');
            return data;
        }

        sessionStorage.setItem('token', data.data.token);
        return data;

    } catch (error) {
        return { error: -1, message: error };
    }
}

export { login, register, logout, rename, getCurrent, refreshToken }