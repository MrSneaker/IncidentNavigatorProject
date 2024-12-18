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
        if (data.error) {
            return { error: data.error, token: null };
        }
        localStorage.setItem('user_id', data.data.user_id);
        localStorage.setItem('username', data.data.username);
        localStorage.setItem('email', data.data.email);
        return { error: null, data: data.data };
    } catch (error) {
        return { error: error, token: null };
    }
}

async function register(email, password) {
    try {
        const response = await fetch('/auth/register', {
            method: 'POST',
            headers: { 
            'Content-Type': 'application/json',
            },
            credentials: 'include',
            body: JSON.stringify({ username: email, password: password })
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
        return await response.json();
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
            }
        });
        const data = await response.json();
        return data;
        
    } catch (error) {
        return { error: error };
    }
}

export { login, register, logout, getCurrent };