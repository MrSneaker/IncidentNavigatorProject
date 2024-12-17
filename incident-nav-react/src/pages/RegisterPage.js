import React, { useState } from "react";
import { Link } from "react-router-dom";

export default function RegisterPage() {
    const [emailError, setEmailError] = useState("");
    const [usernameError, setUsernameError] = useState("");
    const [confirmPasswordError, setConfirmPasswordError] = useState("");

    const fields = [
        {
            label: "Username :",
            id: "username",
            type: "text",
        },
        {
            label: "Email :",
            id: "email",
            type: "email",
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

    const [formValues, setFormValues] = useState({
        email: "",
        username: "",
        password: "",
        confirm_password: ""
    });

    const passwordCriteria = {
        minLength: { label: 'Minimum 8 characters', isValid: false },
        uppercase: { label: 'Uppercase letter', isValid: false },
        lowercase: { label: 'Lowercase letter', isValid: false },
        number: { label: 'Number', isValid: false },
        specialChar: { label: 'Special character', isValid: false },
    };

    const [criteria, setCriteria] = useState(passwordCriteria);

    const isFormValid = () => {
        return (
            formValues.email &&
            formValues.username &&
            formValues.password &&
            formValues.confirm_password &&
            !emailError &&
            !usernameError &&
            !confirmPasswordError
        );
    };

    function onFieldChange(e) {
        const { id, value } = e.target;
        setFormValues({ ...formValues, [id]: value });

        switch (id) {
            case "email":
                setEmailError("");
                if (!value.includes("@")) {
                    setEmailError("Invalid email");
                }
                break;
            case "username":
                setUsernameError("");
                if (value.length < 4) {
                    setUsernameError("Username must be at least 4 characters long");
                }
                break;
            case "password":
                const newCriteria = { ...criteria };
                newCriteria.minLength.isValid = value.length >= 8;
                newCriteria.uppercase.isValid = /[A-Z]/.test(value);
                newCriteria.lowercase.isValid = /[a-z]/.test(value);
                newCriteria.number.isValid = /[0-9]/.test(value);
                newCriteria.specialChar.isValid = /[!@#$%^&*(),.?":{}|<>+\-=_]/.test(value);
                setCriteria(newCriteria);
                break;
            case "confirm_password":
                setConfirmPasswordError("");
                if (value !== formValues.password) {
                    setConfirmPasswordError("Passwords do not match");
                }
                break;
            default:
                break;
        }
    }

    function onSubmit(e) {
        e.preventDefault();
    }

    return (
        <div className="bg-light-background text-light-text dark:bg-dark-background dark:text-dark-text p-5 rounded-3xl max-w-lg mx-auto my-auto">
            <h1 className="text-[4vh] mb-4 text-center">
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
                        {(() => {
                            switch (field.id) {
                                case "email":
                                    return <p className="text-red-500">{emailError}</p>;
                                case "username":
                                    return <p className="text-red-500">{usernameError}</p>;
                                case "password":
                                    return (
                                        <div>
                                            <ul className="list-disc list-inside text-sm grid grid-cols-2 gap-2">
                                                {Object.entries(criteria).map(([key, { label, isValid }]) => (
                                                    <li key={key} className={isValid ? 'text-green-500' : 'text-red-500'}>{label}</li>
                                                ))}
                                            </ul>
                                        </div>
                                    );
                                case "confirm_password":
                                    return <p className="text-red-500">{confirmPasswordError}</p>;
                                default:
                                    return <p></p>;
                            }
                        })()}
                    </div>
                ))}

                <div className="flex flex-col justify-center items-center w-full">
                    <button type="submit" className="bg-light-accent dark:bg-dark-accent text-light-text dark:text-dark-text disabled:opacity-50 p-2 px-4 min-w-[200px] rounded-full" disabled={!isFormValid()}>
                        Register
                    </button>
                    <Link to="/login" className="hover:text-light-accent hover:dark:text-dark-accent mt-2 hover:underline">
                        Already have an account?
                    </Link>
                </div>
            </form>
        </div>
    );
}
