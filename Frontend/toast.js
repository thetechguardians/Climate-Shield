// toast.js
window.showToast = function(message, type = 'info') {
    // Check if toast container exists, create if not
    let toastContainer = document.getElementById('toast-container');
    if (!toastContainer) {
        toastContainer = document.createElement('div');
        toastContainer.id = 'toast-container';
        document.body.appendChild(toastContainer);
    }

    // Create toast element
    const toast = document.createElement('div');
    toast.className = `toast toast-${type}`;
    toast.setAttribute('role', 'alert');
    toast.setAttribute('aria-live', type === 'error' || type === 'warning' ? 'assertive' : 'polite');
    
    // Icon mapping
    const icons = {
        success: '✅',
        error: '❌',
        warning: '⚠️',
        info: 'ℹ️'
    };

    toast.innerHTML = `
        <span class="toast-icon">${icons[type] || icons.info}</span>
        <span class="toast-message">${message}</span>
        <button class="toast-close" aria-label="Close notification" onclick="this.parentElement.style.animation = 'toastSlideOut 0.3s ease forwards'; setTimeout(() => this.parentElement.remove(), 300);">&times;</button>
    `;

    // Add to container
    toastContainer.appendChild(toast);

    // Auto dismiss after 4 seconds
    setTimeout(() => {
        if(toast.parentElement) {
            toast.style.animation = 'toastSlideOut 0.3s ease forwards';
            setTimeout(() => {
                if(toast.parentElement) {
                    toast.remove();
                }
            }, 300);
        }
    }, 4000);
};
