import React, { useState, useEffect } from "react";
import { Link, useNavigate } from "react-router-dom";

export default function LoginPage() {
    const navigate = useNavigate();
    const [emailError, setEmailError] = useState("");
    const [passwordError, setPasswordError] = useState("");
    const [isSubmitting, setIsSubmitting] = useState(false);
    const [submissionStatus, setSubmissionStatus] = useState(null);

    const fields = [
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
    ];

    const [formValues, setFormValues] = useState({
        email: "",
        password: ""
    });

    const isFormValid = () => {
        return (
            formValues.email &&
            formValues.password
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
            case "password":
                setPasswordError("");
                if (value.length < 8) {
                    setPasswordError("Password must be at least 8 characters long");
                }
                break;
            default:
                break;
        }
    }

    function onAuthResponse(response) {

    }

    function onSubmit(e) {
        e.preventDefault();
        setIsSubmitting(true);
        setSubmissionStatus(null);

        setTimeout(() => {
            fetch('http://localhost:4000/login', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify(formValues),
            })
                .then(onAuthResponse)
                .then(() => {
                    localStorage.setItem('authToken', 'fake-auth-token');
                    localStorage.setItem('username', formValues.email);

                    setIsSubmitting(false);
                    navigate('/');
                })
                .catch(() => {
                    setIsSubmitting(false);
                    setSubmissionStatus('error');
                });

        }, 2000);
    }

    return (
        <div className="bg-light-background text-light-text dark:bg-dark-background dark:text-dark-text p-5 rounded-3xl max-w-lg mx-auto my-auto">
            <h1 className="text-[4vh] mb-4 text-center">
                Login
            </h1>
            <hr className="my-4 dark:border-white/20 border-black/20" />

            <form className="space-y-4 flex flex-wrap p-0" onSubmit={onSubmit} autoComplete="off">
                {fields.map((field) => (
                    <div key={field.label} className="flex flex-col w-full gap-1">
                        <label htmlFor={field.id}>{field.label}</label>
                        <input
                            id={field.id}
                            type={field.type}
                            className="p-2 rounded-md border border-gray-300 dark:border-gray-700 focus:outline-none focus:ring-2 focus:ring-light-accent dark:focus:ring-dark-accent bg-light-surface dark:bg-dark-surface"
                            onChange={onFieldChange}
                            autoComplete="off"
                        />
                    </div>
                ))}
                <div className="flex flex-col justify-center items-center w-full">
                    {
                        isSubmitting ? (
                            <div 
                                className="flex justify-center items-center flex-col gap-2 text-light-accent dark:text-dark-accent">
                                <div 
                                    className="loader border-t-transparent border-solid border-4 rounded-full p-2 w-10 h-10 animate-spin border-light-accent bg-transparent"></div>
                                <p>Connecting...</p>
                            </div>
                        ) : (
                            <>
                                <button type="submit"
                                    className="bg-light-accent dark:bg-dark-accent text-light-text dark:text-dark-text disabled:opacity-50 p-2 px-4 min-w-[200px] rounded-full text-center"
                                    disabled={!isFormValid()}>
                                    Connect
                                </button>
                                {submissionStatus === 'error' && (
                                    <p className="text-red-500 mt-2">Invalid email or password. Please try again.</p>
                                )}
                                <Link to="/register" className="hover:text-light-accent hover:dark:text-dark-accent mt-2 hover:underline">
                                    Create an account
                                </Link>
                            </>
                        )
                    }


                </div>
            </form>
        </div>
    );
}
