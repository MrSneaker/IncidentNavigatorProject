import React, { useState, useEffect, useContext } from 'react';
import { getUsers, updateUserIndustries, deleteUser } from '../scripts/auth';
import { getAllIndustries } from '../scripts/industry';
import { getAllLLMs, addLLM, deleteLLM, updateLLM, selectLlm } from '../scripts/llm';
import { FaEdit, FaPlus, FaMinus, FaTrash } from 'react-icons/fa';
import { AuthContext } from '../components/auth/AuthContext';

export default function SettingsPage() {
    const [users, setUsers] = useState([]);
    const [selectedUser, setSelectedUser] = useState(null);
    const [llmUri, setLlmUri] = useState('');
    const [apiKey, setApiKey] = useState('');
    const [model, setModel] = useState('');
    const [industriesList, setIndustriesList] = useState([]);
    const [llmList, setLlmList] = useState([]);
    const [newLlm, setNewLlm] = useState({ uri: '', apiKey: '', model: '', selected: false });
    const [selectedLlm, setSelectedLlm] = useState(null);
    const [expandedPanels, setExpandedPanels] = useState({});
    const { user } = useContext(AuthContext);
    const currentUser = user;

    useEffect(() => {
        getUsers().then((usersResponse) => {
            if (!usersResponse.error) {
                setUsers(usersResponse.data);
            }
        });

        getAllIndustries().then((industriesResponse) => {
            if (!industriesResponse.error) {
                setIndustriesList(industriesResponse.data.industries);
            }
        });

        getAllLLMs().then((llmsResponse) => {
            if (!llmsResponse.error) {
                console.log('llms response : ', llmsResponse.data.llms)
                setLlmList(llmsResponse.data.llms);
            }
        });
    }, []);

    function handleLlmChange(event) {
        const selected = llmList.find(llm => llm.id === event.target.value);
        console.log('selected llm : ', selected)
        setSelectedLlm(selected);
        setLlmUri(selected?.uri || '');
        setApiKey(selected?.api_key || '');
        setModel(selected?.model || '');
    }

    function handleSaveSettings() {
        if (selectedLlm) {
            updateLLM(selectedLlm.id, llmUri, apiKey, model).then((response) => {
                if (!response.error) {
                    const updatedLLMList = llmList.map(llm =>
                        llm.id === selectedLlm.id ? { ...llm, uri: llmUri, api_key: apiKey, model: model } : llm
                    );
                    setLlmList(updatedLLMList);
                }
            });
            window.location.reload();
        }
    }

    function handleIndustryChange(userId, industries) {
        updateUserIndustries(userId, industries).then((response) => {
            if (!response.error) {
                setUsers(users.map((user) =>
                    user.id === userId ? { ...user, industries } : user
                ));
            }
        });
    }

    function renderIndustryEditor() {
        if (!selectedUser) return null;

        const updatedIndustries = [...selectedUser.industries];

        return (
            <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
                <div className={`bg-white dark:bg-neutral-800 p-6 rounded-lg shadow-lg w-1/2 max-h-[80vh] overflow-y-auto`}>
                    <h1 className="text-center font-extrabold text-2xl text-gray-900 dark:text-white mb-6">
                        Edit Industries for <span className="text-indigo-600">{selectedUser.username}</span>
                    </h1>

                    {/* Panel for each industry */}
                    {industriesList.map((industry) => (
                        <div key={industry.id} className="mb-4 border-b border-gray-300 dark:border-gray-700">
                            <div className="flex items-center justify-between py-2">
                                <span className="text-gray-900 dark:text-white">{industry.name}</span>
                                <button
                                    onClick={() => {
                                        if (updatedIndustries.some(ind => ind.id === industry.id)) {
                                            // Remove industry if it already exists in updatedIndustries
                                            const updatedList = updatedIndustries.filter(ind => ind.id !== industry.id);
                                            setSelectedUser({ ...selectedUser, industries: updatedList });
                                        } else {
                                            // Add industry if it is not in the list
                                            updatedIndustries.push(industry);
                                            setSelectedUser({ ...selectedUser, industries: updatedIndustries });
                                        }
                                    }}
                                    className={`py-1 px-2 rounded-md ${updatedIndustries.some(ind => ind.id === industry.id) ? 'bg-red-500' : 'bg-green-500'} text-white transition duration-300 ease-in-out`}
                                >
                                    {updatedIndustries.some(ind => ind.id === industry.id) ? <FaMinus /> : <FaPlus />}
                                </button>
                            </div>
                        </div>
                    ))}

                    <div className="flex justify-end mt-4">
                        <button
                            onClick={() => setSelectedUser(null)}
                            className="bg-gray-500 text-white py-2 px-4 rounded-md mr-2"
                        >
                            Cancel
                        </button>
                        <button
                            onClick={() => {
                                handleIndustryChange(selectedUser.id, updatedIndustries);
                                setSelectedUser(null);
                            }}
                            className="bg-green-500 text-white py-2 px-4 rounded-md"
                        >
                            Save
                        </button>
                    </div>
                </div>
            </div>
        );
    }

    function handlePanelToggle(userId) {
        setExpandedPanels((prev) => ({
            ...prev,
            [userId]: !prev[userId],
        }));
    }

    function handleDeleteUser(userId) {
        if (userId === currentUser.id) {
            alert("You cannot delete your own account.");
            return;
        }

        deleteUser(userId).then((response) => {
            if (!response.error) {
                setUsers(users.filter(user => user.id !== userId));
            }
        });
    }

    const handleAddLlm = () => {
        if (newLlm.uri && newLlm.apiKey && newLlm.model) {
            addLLM(newLlm.uri, newLlm.apiKey, newLlm.model).then((response) => {
                if (!response.error) {
                    setLlmList([...llmList, { id: llmList.length + 1, uri: newLlm.uri, api_key: newLlm.apiKey }]);
                    setNewLlm({ uri: '', apiKey: '', model: '' });
                }
            });
            window.location.reload();
        } else {
            alert("Please provide both LLM URI and API Key.");
        }
    };

    const handleDeleteLlm = (llmId) => {
        deleteLLM(llmId).then((response) => {
            if (!response.error) {
                setLlmList(llmList.filter(llm => llm.id !== llmId));
            }
        });
    };

    const handleSelectLlm = (id) => {
        selectLlm(id).then(data => {
            console.log('data : ', data)
            if (!data.error) {
                setLlmList(llmList.map(llm => ({
                    ...llm,
                    selected: llm.id === id,
                })));
            }
        });
    };


    return (
        <div className="p-2 w-full mx-auto">
            <h1 className="text-2xl font-bold mb-6">Admin Settings</h1>

            {/* LLM Configurations Section */}
            <div className="bg-light-surface dark:bg-dark-surface p-6 mb-6 shadow-md rounded-lg">
                <h2 className="text-2xl font-bold mb-4">LLM Configurations</h2>
                <div className="space-y-4">
                    {/* LLM Model Selection */}
                    <div>
                        <label className="block font-medium text-gray-700 dark:text-white">Select LLM Model</label>
                        <select
                            className="mt-1 p-2 w-full bg-gray-100 dark:bg-neutral-800 rounded-md"
                            onChange={handleLlmChange}
                            value={selectedLlm ? selectedLlm.id : ''}
                        >
                            <option value="">Select LLM</option>
                            {llmList.map(llm => (
                                <option key={llm.id} value={llm.id}>
                                    {llm.model}
                                </option>
                            ))}
                        </select>
                    </div>

                    {/* LLM URI */}
                    <div>
                        <label className="block font-medium text-gray-700 dark:text-white">LLM Model URI</label>
                        <input
                            type="text"
                            className="mt-1 p-2 w-full bg-gray-100 dark:bg-neutral-800 rounded-md"
                            value={llmUri}
                            onChange={(e) => setLlmUri(e.target.value)}
                            placeholder="Enter the URI of the LLM model"
                            disabled={!selectedLlm}
                        />
                    </div>

                    {/* API Key */}
                    <div>
                        <label className="block font-medium text-gray-700 dark:text-white">API Key</label>
                        <input
                            type="text"
                            className="mt-1 p-2 w-full bg-gray-100 dark:dark:bg-neutral-800 rounded-md"
                            value={apiKey}
                            onChange={(e) => setApiKey(e.target.value)}
                            placeholder="Enter your API key"
                            disabled={!selectedLlm}
                        />
                    </div>

                    {/* Save Button */}
                    <div>
                        <button
                            onClick={handleSaveSettings}
                            className="bg-green-500 text-white py-2 px-4 rounded-md hover:bg-green-700"
                        >
                            Save Configuration
                        </button>
                    </div>
                </div>
            </div>

            {/* Add New LLM Configuration */}
            <div className="bg-light-surface dark:bg-dark-surface p-6 mb-6 shadow-md rounded-lg">
                <h2 className="text-2xl font-bold mb-4">Add New LLM Configuration</h2>
                <div className="space-y-4">
                    <div>
                        <label className="block font-medium text-gray-700 dark:text-white">LLM Model</label>
                        <input
                            type="text"
                            className="mt-1 p-2 w-full bg-gray-100 dark:bg-neutral-800 rounded-md"
                            value={newLlm.model}
                            onChange={(e) => setNewLlm({ ...newLlm, model: e.target.value })}
                            placeholder="Enter the name of the new LLM model"
                        />
                    </div>

                    <div>
                        <label className="block font-medium text-gray-700 dark:text-white">LLM URI</label>
                        <input
                            type="text"
                            className="mt-1 p-2 w-full bg-gray-100 dark:bg-neutral-800 rounded-md"
                            value={newLlm.uri}
                            onChange={(e) => setNewLlm({ ...newLlm, uri: e.target.value })}
                            placeholder="Enter the URI of the new LLM model"
                        />
                    </div>

                    <div>
                        <label className="block font-medium text-gray-700 dark:text-white">API Key</label>
                        <input
                            type="text"
                            className="mt-1 p-2 w-full bg-gray-100 dark:bg-neutral-800 rounded-md"
                            value={newLlm.apiKey}
                            onChange={(e) => setNewLlm({ ...newLlm, apiKey: e.target.value })}
                            placeholder="Enter the API key for the new LLM"
                        />
                    </div>

                    <div>
                        <button
                            onClick={handleAddLlm}
                            className="bg-green-500 text-white py-2 px-4 rounded-md hover:bg-green-700"
                        >
                            Add LLM Configuration
                        </button>
                    </div>
                </div>
            </div>

            {/* LLM Configurations List */}
            <div className="bg-light-surface dark:bg-dark-surface p-6 mb-6 shadow-md rounded-lg">
                <h2 className="text-2xl font-bold mb-4">Existing LLM Configurations</h2>
                <table className="w-full text-left border-collapse">
                    <thead>
                        <tr className="border-b dark:border-neutral-700">
                            <th className="p-4 font-semibold text-gray-700 dark:text-gray-300">Model</th>
                            <th className="p-4 font-semibold text-gray-700 dark:text-gray-300">URI</th>
                            <th className="p-4 font-semibold text-gray-700 dark:text-gray-300">Secret Key</th>
                            <th className="p-4"></th>
                            <th className="p-4"></th>
                        </tr>
                    </thead>
                    <tbody className="divide-y divide-gray-200 dark:divide-neutral-700">
                        {llmList.map((llm) => (
                            <tr key={llm.id} className="hover:bg-gray-100 dark:hover:bg-neutral-800">
                                <td className="p-4 text-gray-800 dark:text-gray-200">{llm.model}</td>
                                <td className="p-4 text-gray-800 dark:text-gray-200">{llm.uri}</td>
                                <td className="p-4 text-gray-800 dark:text-gray-200">{llm.api_key}</td>
                                <td className="p-4 text-right">
                                    <button
                                        onClick={() => handleSelectLlm(llm.id)}
                                        className={`py-2 px-4 rounded-md ${llm.selected ? 'bg-blue-500 text-white' : 'bg-gray-200 text-gray-700'}`}
                                    >
                                        {llm.selected ? 'Selected' : 'Select'}
                                    </button>
                                </td>
                                <td className="p-4 text-right">
                                    <button
                                        onClick={() => handleDeleteLlm(llm.id)}
                                        className="bg-red-500 text-white py-2 px-4 rounded-md hover:bg-red-700"
                                    >
                                        Delete
                                    </button>
                                </td>
                            </tr>
                        ))}
                    </tbody>
                </table>
            </div>

            {/* User List */}
            <div className="grid grid-cols-1 sm:grid-cols-2 md:grid-cols-2 lg:grid-cols-2 gap-4 bg-light-surface dark:bg-dark-surface p-6 mb-6 shadow-md rounded-lg">
                <h2 className="text-2xl font-bold mb-3 col-span-2">Users Management</h2>
                <div className="overflow-y-auto max-h-[400px] space-y-4 p-2 col-span-2">
                    {users.map((user) => (
                        !user.admin && (
                            <div
                                key={user.id}
                                className="w-full p-6 bg-light-surface dark:bg-neutral-800 shadow-md rounded-lg flex flex-col justify-between dark:border-dark-accent hover:border-light-primary dark:hover:border-dark-primary transition duration-300"
                            >
                                <div className="w-full">
                                    <h3 className="font-bold text-lg">{user.username}</h3>
                                    <p>Email: {user.email}</p>
                                    <div className="mt-2">
                                        <button
                                            onClick={() => handlePanelToggle(user.id)}
                                            className="text-blue-500 font-bold"
                                        >
                                            {expandedPanels[user.id] ? 'Hide Industries' : 'Show Industries'}
                                        </button>
                                        {expandedPanels[user.id] && (
                                            <div className="mt-2 max-h-40 overflow-y-auto transition duration-300 ease-in-out">
                                                <div className="flex flex-wrap gap-2">
                                                    {user.industries.length ? (
                                                        user.industries.map((industry) => (
                                                            <span
                                                                key={industry.id}
                                                                className="inline-block bg-blue-500 text-white text-sm font-medium py-1 px-3 rounded-lg"
                                                            >
                                                                {industry.name}
                                                            </span>
                                                        ))
                                                    ) : (
                                                        <span className="text-gray-500">No industries assigned</span>
                                                    )}
                                                </div>
                                            </div>
                                        )}
                                    </div>
                                </div>
                                <div className="flex justify-end gap-2 mt-4">
                                    <button
                                        onClick={() => setSelectedUser(user)}
                                        className="bg-green-500 text-white font-bold py-2 px-4 rounded-md hover:bg-green-700 flex items-center gap-2"
                                    >
                                        <FaEdit /> Edit Industries
                                    </button>
                                    <button
                                        onClick={() => handleDeleteUser(user.id)}
                                        className={`font-bold py-2 px-4 rounded-md flex items-center gap-2 
                                                ${user.id === currentUser.id ? 'bg-gray-500 text-gray-300 cursor-not-allowed' : 'bg-red-500 text-white hover:bg-red-700'}`}
                                        disabled={user.id === currentUser.id}
                                    >
                                        <FaTrash /> Delete
                                    </button>
                                </div>
                            </div>
                        )
                    ))}
                </div>
            </div>

            {/* Industry Editor */}
            {renderIndustryEditor()}
        </div>
    );
}
