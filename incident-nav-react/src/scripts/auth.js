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
        const response = await fetch('/auth/token', {
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

async function getUsers() {
    try {
        const response = await fetch('/auth/users', {
            method: 'GET',
            headers: {
                'Content-Type': 'application/json',
            },
            credentials: 'include',
        });
        const data = await response.json();
        if (data.error) {
            return { error: data.error, data: null };
        } else {
            return { error: null, data: data.data };
        }
    } catch (error) {
        return { error: -1, message: error, data: null };
    }
}

async function updateUserIndustries(userId, industries, doAdd) {
    try {
        const response = await fetch(`/auth/users/${userId}/industries`, {
            method: 'PUT',
            headers: {
                'Content-Type': 'application/json',
            },
            credentials: 'include',
            body: JSON.stringify({ industries, doAdd }),
        });
        const data = await response.json();
        if (data.error) {
            return { error: data.error };
        } else {
            return { error: null };
        }
    } catch (error) {
        return { error: -1, message: error };
    }
}

async function checkAdmin() {
    try {
        const response = await fetch('/auth/check-admin', {
            method: 'GET',
            headers: {
                'Content-Type': 'application/json',
            },
            credentials: 'include',
        });
        const data = await response.json();
        if (data.error) {
            return { error: data.error, isAdmin: false };
        } else {
            return { error: null, isAdmin: data.isAdmin };
        }
    } catch (error) {
        return { error: -1, message: error, isAdmin: false };
    }
}

async function deleteUser(userIdToDelete) {
    const { error, isAdmin } = await checkAdmin();

    if (error) {
        console.error("Failed to check admin status:", error);
        alert("Failed to check admin status. Please try again.");
        return;
    }

    if (!isAdmin) {
        alert("You must be an admin to delete users.");
        return;
    }

    const confirmation = window.confirm("Are you sure you want to delete this user?");
    if (!confirmation) {
        return;
    }

    try {
        const response = await fetch('/auth/delete', {
            method: 'DELETE',
            headers: {
                'Content-Type': 'application/json',
            },
            credentials: 'include',
            body: JSON.stringify({ user_id: userIdToDelete }),
        });

        const data = await response.json();

        if (data.error) {
            console.error("Error deleting user:", data.message);
            alert("Failed to delete the user. Please try again.");
        } else {
            alert("User deleted successfully.");
            window.location.reload();
        }
    } catch (error) {
        console.error("An error occurred while deleting the user:", error);
        alert("An error occurred while deleting the user. Please try again.");
    }
}


export { login, register, logout, rename, getCurrent, refreshToken, getUsers, updateUserIndustries, checkAdmin, deleteUser }