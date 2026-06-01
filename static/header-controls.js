(() => {
    const readSnapshot = () => {
        try {
            return JSON.parse(localStorage.getItem('fs_currentUser') || 'null');
        } catch (error) {
            return null;
        }
    };

    const snapshot = readSnapshot();
    const userControls = document.getElementById('user-controls');
    const loginBtn = document.getElementById('header-login-btn');
    const avatarBtn = document.getElementById('avatar-btn');
    const avatarMenu = document.getElementById('avatar-menu');
    const avatarImage = document.getElementById('avatar-btn-image');
    const avatarFallback = document.getElementById('avatar-btn-fallback');
    const userNameDisplay = document.getElementById('user-name-display');

    if (snapshot?.uid) {
        if (userControls) userControls.classList.remove('hidden');
        if (loginBtn) loginBtn.classList.add('hidden');
    } else {
        if (userControls) userControls.classList.add('hidden');
        if (loginBtn) loginBtn.classList.remove('hidden');
    }

    const displayName = (snapshot?.displayName || snapshot?.email || '').trim();
    const fallbackText = displayName
        ? displayName.split(/\s+/).filter(Boolean).map((part) => part[0]).slice(0, 2).join('').toUpperCase()
        : '9';

    if (avatarFallback) avatarFallback.textContent = fallbackText;
    if (avatarImage && snapshot?.photoURL) {
        avatarImage.src = snapshot.photoURL;
        avatarImage.classList.remove('hidden');
        if (avatarFallback) avatarFallback.classList.add('hidden');
    }
    if (userNameDisplay) {
        userNameDisplay.textContent = displayName || '嗨，同學';
    }

    if (avatarBtn && avatarMenu) {
        avatarBtn.addEventListener('click', (event) => {
            event.stopPropagation();
            avatarMenu.classList.toggle('invisible');
            avatarMenu.classList.toggle('opacity-0');
        });

        document.addEventListener('click', (event) => {
            if (!avatarMenu.contains(event.target)) {
                avatarMenu.classList.add('invisible');
                avatarMenu.classList.add('opacity-0');
            }
        });
    }

    if (loginBtn) {
        loginBtn.addEventListener('click', () => {
            window.location.href = '../index.html';
        });
    }
})();
