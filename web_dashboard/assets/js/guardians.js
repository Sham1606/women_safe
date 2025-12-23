/**
 * Guardians page logic
 */

// Require authentication
if (!Auth.requireAuth()) {
    throw new Error('Unauthorized');
}

// Get user data
const userData = Auth.getUserData();
if (userData && userData.name) {
    document.getElementById('userName').textContent = userData.name;
}

let guardians = [];

/**
 * Load guardians list
 */
async function loadGuardians() {
    const guardiansList = document.getElementById('guardiansList');
    
    try {
        guardians = await API.get(CONFIG.ENDPOINTS.GUARDIANS);
        
        if (guardians.length === 0) {
            guardiansList.innerHTML = `
                <div class="col-12">
                    <div class="empty-state">
                        <i class="bi bi-people"></i>
                        <h4>No Guardians Added</h4>
                        <p class="text-muted">Add family members or friends who will be notified during emergencies</p>
                        <button class="btn btn-primary mt-3" data-bs-toggle="modal" data-bs-target="#addGuardianModal">
                            <i class="bi bi-person-plus"></i> Add Guardian
                        </button>
                    </div>
                </div>
            `;
            return;
        }
        
        guardiansList.innerHTML = '';
        
        guardians.forEach(guardian => {
            const col = document.createElement('div');
            col.className = 'col-lg-4 col-md-6 mb-4';
            col.innerHTML = `
                <div class="card border-0 shadow-sm h-100">
                    <div class="card-body">
                        <div class="d-flex justify-content-between align-items-start mb-3">
                            <div>
                                <h5 class="card-title mb-1">
                                    <i class="bi bi-person-circle text-primary"></i>
                                    ${guardian.name}
                                </h5>
                                ${guardian.relationship ? `<small class="text-muted">${guardian.relationship}</small>` : ''}
                            </div>
                            <button class="btn btn-sm btn-outline-danger" onclick="deleteGuardian(${guardian.id})" title="Remove">
                                <i class="bi bi-trash"></i>
                            </button>
                        </div>
                        
                        <div class="mb-2">
                            <i class="bi bi-envelope"></i>
                            <a href="mailto:${guardian.email}" class="text-decoration-none ms-2">${guardian.email}</a>
                        </div>
                        
                        <div class="mb-2">
                            <i class="bi bi-telephone"></i>
                            <a href="tel:${guardian.phone}" class="text-decoration-none ms-2">${guardian.phone}</a>
                        </div>
                        
                        <hr>
                        
                        <small class="text-muted">
                            <i class="bi bi-calendar"></i> Added ${Utils.formatDate(guardian.created_at)}
                        </small>
                    </div>
                </div>
            `;
            guardiansList.appendChild(col);
        });
        
    } catch (error) {
        console.error('Error loading guardians:', error);
        Utils.showError('Failed to load guardians');
    }
}

/**
 * Delete guardian
 */
async function deleteGuardian(guardianId) {
    if (!confirm('Are you sure you want to remove this guardian?')) {
        return;
    }
    
    try {
        await API.delete(`${CONFIG.ENDPOINTS.GUARDIANS}/${guardianId}`);
        Utils.showSuccess('Guardian removed successfully');
        loadGuardians();
    } catch (error) {
        Utils.showError('Failed to remove guardian: ' + error.message);
    }
}

/**
 * Handle add guardian form
 */
const addGuardianForm = document.getElementById('addGuardianForm');
const guardianAlert = document.getElementById('guardianAlert');
const addGuardianBtnText = document.getElementById('addGuardianBtnText');
const addGuardianSpinner = document.getElementById('addGuardianSpinner');

addGuardianForm.addEventListener('submit', async (e) => {
    e.preventDefault();
    
    const name = document.getElementById('guardianName').value;
    const email = document.getElementById('guardianEmail').value;
    const phone = document.getElementById('guardianPhone').value;
    const relationship = document.getElementById('guardianRelationship').value;
    
    guardianAlert.classList.add('d-none');
    addGuardianBtnText.textContent = 'Adding...';
    addGuardianSpinner.classList.remove('d-none');
    addGuardianForm.querySelector('button[type="submit"]').disabled = true;
    
    try {
        await API.post(CONFIG.ENDPOINTS.GUARDIANS, {
            name,
            email,
            phone,
            relationship
        });
        
        // Close modal
        const modal = bootstrap.Modal.getInstance(document.getElementById('addGuardianModal'));
        modal.hide();
        
        // Reset form
        addGuardianForm.reset();
        
        Utils.showSuccess('Guardian added successfully!');
        loadGuardians();
        
    } catch (error) {
        guardianAlert.textContent = error.message;
        guardianAlert.classList.remove('alert-success');
        guardianAlert.classList.add('alert-danger');
        guardianAlert.classList.remove('d-none');
    } finally {
        addGuardianBtnText.textContent = 'Add Guardian';
        addGuardianSpinner.classList.add('d-none');
        addGuardianForm.querySelector('button[type="submit"]').disabled = false;
    }
});

// Reset alert when modal is hidden
document.getElementById('addGuardianModal').addEventListener('hidden.bs.modal', () => {
    guardianAlert.classList.add('d-none');
    addGuardianForm.reset();
});

// Load guardians on page load
document.addEventListener('DOMContentLoaded', loadGuardians);