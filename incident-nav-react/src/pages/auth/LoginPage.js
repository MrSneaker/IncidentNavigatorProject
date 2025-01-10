import React, { useState } from "react";
import { Link, useNavigate } from "react-router-dom";
import { login } from "../../scripts/auth";

export default function LoginPage() {
    const navigate = useNavigate();
    const [isSubmitting, setIsSubmitting] = useState(false);
    const [submissionStatus, setSubmissionStatus] = useState(null);
    const [submissionError, setSubmissionError] = useState('');

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
    }

    function onSubmit(e) {
        e.preventDefault();
        setIsSubmitting(true);
        setSubmissionStatus(null);

        login(formValues.email, formValues.password).then((response) => {
            setIsSubmitting(false);
            if (response.error !== 0) {
                setSubmissionError(response.message)
                setSubmissionStatus('error');

            } else {
                navigate('/');
            }
        });
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
                                    <p className="text-red-500 mt-2">
                                        Failed to login, {submissionError}.
                                    </p>
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
