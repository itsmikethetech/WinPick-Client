/*
 * WinPick Web App - Main JavaScript
 * Provides common functionality for the web interface
 */

document.addEventListener('DOMContentLoaded', function() {
    // Initialize tooltips
    initializeTooltips();
    
    // Initialize alert dismissal
    initializeAlerts();
    
    // Apply responsive behavior
    applyResponsiveBehavior();
    
    // Set up theme detection
    setupThemeDetection();
});

/**
 * Initialize Bootstrap tooltips
 */
function initializeTooltips() {
    const tooltipTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="tooltip"]'));
    tooltipTriggerList.map(function(tooltipTriggerEl) {
        return new bootstrap.Tooltip(tooltipTriggerEl, {
            delay: { show: 500, hide: 100 }
        });
    });
}

/**
 * Initialize alert dismissal with auto timeout
 */
function initializeAlerts() {
    // Auto-dismiss alerts after 5 seconds
    const alerts = document.querySelectorAll('.alert:not(.alert-permanent)');
    alerts.forEach(alert => {
        setTimeout(() => {
            const bsAlert = new bootstrap.Alert(alert);
            bsAlert.close();
        }, 5000);
    });
    
    // Add fade-out animation to alert dismissal
    document.querySelectorAll('.btn-close').forEach(button => {
        button.addEventListener('click', function() {
            const alert = this.closest('.alert');
            alert.style.opacity = '0';
            setTimeout(() => {
                alert.style.display = 'none';
            }, 150);
        });
    });
}

/**
 * Apply responsive behavior to the UI
 */
function applyResponsiveBehavior() {
    // Handle window resize events
    window.addEventListener('resize', handleWindowResize);
    
    // Initial call to set proper sizing
    handleWindowResize();
    
    // Adjust console output height based on window size
    const consoleOutput = document.getElementById('console-output');
    if (consoleOutput) {
        adjustConsoleHeight();
        window.addEventListener('resize', adjustConsoleHeight);
    }
}

/**
 * Handle window resize events
 */
function handleWindowResize() {
    const width = window.innerWidth;
    
    // Apply classes based on window width
    document.body.classList.toggle('compact-view', width < 768);
    
    // Adjust card layouts
    if (width < 576) {
        document.querySelectorAll('.card-responsive').forEach(card => {
            card.classList.add('mb-3');
        });
    }
}

/**
 * Adjust console output height based on available space
 */
function adjustConsoleHeight() {
    const consoleOutput = document.getElementById('console-output');
    if (!consoleOutput) return;
    
    const windowHeight = window.innerHeight;
    
    // Make console smaller on small screens
    if (windowHeight < 800) {
        consoleOutput.style.maxHeight = '200px';
    } else {
        consoleOutput.style.maxHeight = '300px';
    }
}

/**
 * Setup theme detection (light/dark mode)
 */
function setupThemeDetection() {
    // Check if user prefers dark mode
    const prefersDarkScheme = window.matchMedia('(prefers-color-scheme: dark)');
    
    // Function to apply theme based on preference
    function applyTheme(darkMode) {
        document.body.classList.toggle('dark-theme', darkMode);
        
        // Update theme-sensitive elements
        const scriptContents = document.querySelectorAll('.script-content');
        if (darkMode) {
            scriptContents.forEach(el => {
                el.style.backgroundColor = '#1e1e1e';
                el.style.color = '#d4d4d4';
            });
        } else {
            scriptContents.forEach(el => {
                el.style.backgroundColor = '#f8f9fa';
                el.style.color = '#212529';
            });
        }
    }
    
    // Apply theme on load
    applyTheme(prefersDarkScheme.matches);
    
    // Listen for changes in user preference
    prefersDarkScheme.addEventListener('change', e => {
        applyTheme(e.matches);
    });
}

/**
 * Format a file size in bytes to a human-readable string
 * @param {number} bytes - File size in bytes
 * @returns {string} Formatted file size
 */
function formatFileSize(bytes) {
    if (bytes === 0) return '0 Bytes';
    
    const k = 1024;
    const sizes = ['Bytes', 'KB', 'MB', 'GB'];
    const i = Math.floor(Math.log(bytes) / Math.log(k));
    
    return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + sizes[i];
}

/**
 * Copy text to clipboard
 * @param {string} text - Text to copy
 * @returns {Promise<boolean>} Success indicator
 */
async function copyToClipboard(text) {
    try {
        await navigator.clipboard.writeText(text);
        return true;
    } catch (err) {
        console.error('Failed to copy text: ', err);
        return false;
    }
}

// Attach to window for global access
window.WinPick = {
    copyToClipboard,
    formatFileSize
};