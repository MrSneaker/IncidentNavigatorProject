import React, { useState } from "react";
export default function RegisterPage() {
    const [emailError, setEmailError] = useState("");
    const [usernameError, setUsernameError] = useState("");
    const [passwordError, setPasswordError] = useState("");
    const [confirmPasswordError, setConfirmPasswordError] = useState("");

    const fields = [

        {
            label: "Email :",
            id: "email",
            type: "email",

        },
        {
            label: "Username :",
            id: "username",
            type: "text",
        },
        {
            label: "Password",
            id: "password",
            type: "password",
        },
        {
            label: "Confirm Password",
            id: "confirm_password",
            type: "password",
        },
    ];

    function onFieldChange(e) {
        const { id, value } = e.target;
        switch (id) {
            case "email":
                setEmailError("");
                break;
            case "username":
                setUsernameError("");
                break;
            case "password":
                setPasswordError("");
                break;
            case "confirm_password":
                setConfirmPasswordError("");
                break;
            default:
                break;
        }
    }

    function onSubmit(e) {
        e.preventDefault();
        const email = e.target.email.value;
        const username = e.target.username.value;
        const password = e.target.password.value;
        const confirmPassword = e.target.confirm_password.value;

        if (!email.includes("@")) {
            setEmailError("Invalid email");
        }
        if (username.length < 4) {
            setUsernameError("Username must be at least 4 characters long");
        }
        if (password.length < 8) {
            setPasswordError("Password must be at least 8 characters long");
        }
        if (password !== confirmPassword) {
            setConfirmPasswordError("Passwords do not match");
        }
    }

    return (
        <div className="bg-light-background text-light-text dark:bg-dark-background dark:text-dark-text p-5 rounded-3xl max-w-lg mx-auto my-auto">
            <h1 className="text-4xl mb-4 text-center">
                Register
            </h1>
            <hr className="my-4 dark:border-white/20 border-black/20" />
            <form className="space-y-4 flex flex-wrap p-0" onSubmit={onSubmit}>

                {fields.map((field) => (
                    <div key={field.label} className="flex flex-col w-full gap-1">
                        <label htmlFor={field.id}>{field.label}</label>
                        <input
                            id={field.id}
                            type={field.type}
                            className="p-2 rounded-md border border-gray-300 dark:border-gray-700 focus:outline-none focus:ring-2 focus:ring-light-accent dark:focus:ring-dark-accent bg-light-surface dark:bg-dark-surface"
                            onChange={onFieldChange}
                        />
                        {
                            (() => {
                                switch (field.id) {
                                    case "email":
                                        return <p className="text-red-500">{emailError}</p>;
                                    case "username":
                                        return <p className="text-red-500">{usernameError}</p>;
                                    case "password":
                                        return <p className="text-red-500">{passwordError}</p>;
                                    case "confirm_password":
                                        return <p className="text-red-500">{confirmPasswordError}</p>;
                                    default:
                                        return <p></p>;
                                }
                            })()
                        }
                    </div>
                ))}

                <div className="flex justify-center items-center w-full">
                    <button type="submit" className="bg-light-accent dark:bg-dark-accent text-light-text dark:text-dark-text p-2 px-4 min-w-[100px] rounded-full">
                        Register
                    </button>
                </div>

            </form>
        </div>
    );
}