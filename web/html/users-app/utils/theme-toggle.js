/**
 * TigerEx Theme Toggle Script
 * Include this in all HTML pages
 */

function initThemeToggle() {
    // Create toggle button if not exists
    if (!document.getElementById('themeToggleBtn')) {
        const btn = document.createElement('button');
        btn.id = 'themeToggleBtn';
        btn.innerHTML = `
            <svg id="themeIconDark" class="w-6 h-6" fill="currentColor" viewBox="0 0 24 24">
                <path d="M12 3c-4.97 0-9 4.03-9 9s4.03 9 9 9 9-4.03 9-9c0-.46-.04-.92-.1-1.36-.98 1.37-2.58 2.26-4.4 2.26-2.98 0-5.4-2.42-5.4-5.4 0-1.81.89-3.42 2.26-4.4-.44-.06-.9-.1-1.36-.1z"/>
            </svg>
            <svg id="themeIconLight" class="w-6 h-6 hidden" fill="currentColor" viewBox="0 0 24 24">
                <path d="M12 7c-2.76 0-5 2.24-5 5s2.24 5 5 5 5-2.24 5-5-2.24-5-5-5z"/>
            </svg>
        `;
        btn.onclick = toggleTheme;
        btn.className = 'fixed top-4 right-4 z-50 p-3 rounded-full bg-gray-800 hover:bg-gray-700 shadow-lg transition-all';
        btn.setAttribute('title', 'Toggle Theme');
        document.body.appendChild(btn);
    }
    
    // Load saved theme
    const savedTheme = localStorage.getItem('theme');
    if (savedTheme === 'light') {
        applyLightTheme();
    }
}

function toggleTheme() {
    const isLight = document.body.classList.toggle('light');
    localStorage.setItem('theme', isLight ? 'light' : 'dark');
    
    const darkIcon = document.getElementById('themeIconDark');
    const lightIcon = document.getElementById('themeIconLight');
    
    if (darkIcon && lightIcon) {
        darkIcon.classList.toggle('hidden', isLight);
        lightIcon.classList.toggle('hidden', !isLight);
    }
}

function applyLightTheme() {
    document.body.classList.add('light');
    const darkIcon = document.getElementById('themeIconDark');
    const lightIcon = document.getElementById('themeIconLight');
    if (darkIcon) darkIcon.classList.add('hidden');
    if (lightIcon) lightIcon.classList.remove('hidden');
}

// Initialize on DOM ready
if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', initThemeToggle);
} else {
    initThemeToggle();
}

// Export for use in other scripts
window.initThemeToggle = initThemeToggle;
window.toggleTheme = toggleTheme;