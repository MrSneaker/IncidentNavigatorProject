import React, { useState, useEffect } from 'react';
import { getCurrent, rename } from '../../scripts/auth';
import { FaSave } from 'react-icons/fa';

export default function ProfilePage() {
    const [usernameError, setUsernameError] = useState(''); // Initialize usernameError state variable
    const [emailError, setEmailError] = useState(''); // Initialize emailError state variable
    const [currentUsername, setCurrentUsername] = useState(''); // Initialize currentUsername state variable
    const [currentEmail, setCurrentEmail] = useState(''); // Initialize currentEmail state variable
    const [userName, setUserName] = useState(''); // Initialize userName state variable
    const [userEmail, setUserEmail] = useState(''); // Initialize userEmail state variable

    useEffect(() => {
        getCurrent().then(response => {
            if (response.error) {
                console.error(response.error);
            } else {
                setUserName(response.data.username);
                setUserEmail(response.data.email);
                setCurrentUsername(response.data.username);
                setCurrentEmail(response.data.email);
            }
        });
    }, []);

    function checkUsername() {
        if (userName.trim() === '') {
            setUsernameError('Username cannot be empty');
        } else {
            setUsernameError('');
        }
    }

    function checkEmail() {
        const emailPattern = /^[a-zA-Z0-9._-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,6}$/;
        if (userEmail.trim() === '') {
            setEmailError('Email cannot be empty');
        } else if (!emailPattern.test(userEmail)) {
            setEmailError('Invalid email format');
        } else {
            setEmailError('');
        }
    }

    function saveUserProfile() {
        checkUsername();
        if (userName.trim() === '') {
            return;
        }
        checkEmail();
        if (userEmail.trim() === '') {
            return;
        }

        if (userName.trim() !== currentUsername.trim()) {
            rename(userName).then(response => {
                if (response.error) {
                    console.error(response.error);
                    return;
                }
                setCurrentUsername(userName);
                window.location.reload();
            });

        }
    }


    return (
        <div className="flex flex-col items-center justify-center h-full w-full">
            <h1 className="text-center font-bold dark:text-dark-accent text-light-text w-full"
                style={{ fontSize: 'clamp(30px, 5vw, 60px)' }}>
                Profile
            </h1>

            <div className="flex flex-col justify-start h-full w-full xl:w-[60%] p-3 gap-2 rounded-3xl bg-light-surface dark:bg-dark-surface shadow-lg">
                <div className="flex flex-col gap-2 h-full">
                    <label htmlFor="email" className="text-lg font-semibold dark:text-dark-text/50 text-light-text">Email:</label>
                    <input type="email" id="email" name="email" value={userEmail} onChange={(e) => setUserEmail(e.target.value)}
                        className="p-2 border border-black/20 dark:border-white/20 rounded-md focus:outline-none focus:ring-2 focus:ring-light-accent dark:bg-dark-surface dark:text-dark-text" />
                    <p className="text-red-500 text-sm">{emailError}</p>

                    <label htmlFor="username" className="text-lg font-semibold dark:text-dark-text/50 text-light-text">Username:</label>
                    <input type="text" id="username" name="username" value={userName} onChange={(e) => setUserName(e.target.value)}
                        className="p-2 border border-black/20 dark:border-white/20 rounded-md focus:outline-none focus:ring-2 focus:ring-light-accent dark:bg-dark-surface dark:text-dark-text" />
                    <p className="text-red-500 text-sm">{usernameError}</p>
                </div>
                <div className="flex justify-end mt-4">
                    <button className={`bg-green-500 text-white  disabled:opacity-50 font-bold py-2 px-4 rounded-xl flex items-center ${userName === currentUsername && userEmail === currentEmail ? '' : 'hover:bg-green-700 hover:scale-110 transition-transform'}`}
                        onClick={saveUserProfile}
                        disabled={userName.trim() === currentUsername.trim() && userEmail.trim() === currentEmail.trim()}>
                        <FaSave className="inline-block mr-2" />
                        Save
                    </button>
                </div>
            </div>
        </div>
    );
}