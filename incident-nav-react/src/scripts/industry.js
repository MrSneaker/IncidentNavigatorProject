async function getAllIndustries() {
    try {
        const response = await fetch('/industry/industries', {
            method: 'GET',
            headers: {
                'Content-Type': 'application/json',
                'Authorization': `Bearer ${sessionStorage.getItem('token')}`
            }
        })

        if (response.ok) {
            const data = await response.json();
            return { error: false, data: data };
        } else {
            return { error: true, message: 'Failed to fetch industries' };
        }
    } catch (error) {
        console.error('Error fetching industries:', error);
        return { error: true, message: error.message };
    }
}

async function addIndustry(name, description) {
    const response = await fetch('/industry/industries', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
            'Authorization': `Bearer ${sessionStorage.getItem('token')}`
        },
        body: JSON.stringify({ name, description }),
    });

    const data = await response.json();

    if (data.error !== 0) {
        console.error('Error adding industry:', data.message);
    }

    return data;
};


async function deleteIndustry(industryId) {
    const response = await fetch(`/industry/industries/${industryId}`, {
        method: 'DELETE',
        headers: {
            'Content-Type': 'application/json',
            'Authorization': `Bearer ${sessionStorage.getItem('token')}`
        },
    });

    const data = await response.json();

    if (data.error !== 0) {
        console.error('Error deleting industry:', data.message);
    }

    return data;
};


async function updateIndustry(industryId, name, description) {
    const response = await fetch(`/industry/industries/${industryId}`, {
        method: 'PUT',
        headers: {
            'Content-Type': 'application/json',
            'Authorization': `Bearer ${sessionStorage.getItem('token')}`
        },
        body: JSON.stringify({ name, description }),
    });

    const data = await response.json();

    if (data.error !== 0) {
        console.error('Error updating industry:', data.message);
    }

    return data;
};

async function getIndustry(industryId) {
    const response = await fetch(`/industry/industries/${industryId}`, {
        method: 'GET',
        headers: {
            'Content-Type': 'application/json',
            'Authorization': `Bearer ${sessionStorage.getItem('token')}`
        }
    });

    const data = await response.json();

    if (data.error !== 0) {
        console.error('Error updating industry:', data.message);
    }

    return data;
};



export { getAllIndustries, addIndustry, deleteIndustry, updateIndustry, getIndustry }