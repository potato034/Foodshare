const FALLBACK_PROFILE = {
    displayName: '',
    department: '',
    avatarMode: 'email',
    photoURL: '',
    shareHistory: [],
    requestHistory: []
};

export function getCurrentUserSnapshot() {
    try {
        return JSON.parse(localStorage.getItem('fs_currentUser') || 'null');
    } catch (error) {
        return null;
    }
}

export function getProfileKey(uid) {
    return `fs_user_${uid}`;
}

export function normalizeProfile(rawProfile, fallbackUser) {
    const displayName = rawProfile?.displayName || fallbackUser?.displayName || (fallbackUser?.email ? fallbackUser.email.split('@')[0] : '');
    const photoURL = rawProfile?.photoURL || fallbackUser?.photoURL || '';
    return {
        ...FALLBACK_PROFILE,
        ...rawProfile,
        displayName,
        photoURL,
        avatarMode: rawProfile?.avatarMode || (photoURL ? 'email' : 'generated'),
        shareHistory: Array.isArray(rawProfile?.shareHistory) ? rawProfile.shareHistory : [],
        requestHistory: Array.isArray(rawProfile?.requestHistory) ? rawProfile.requestHistory : []
    };
}

export function loadUserProfile(uid, fallbackUser) {
    try {
        const raw = localStorage.getItem(getProfileKey(uid));
        if (!raw) {
            const profile = normalizeProfile({}, fallbackUser);
            localStorage.setItem(getProfileKey(uid), JSON.stringify(profile));
            return profile;
        }
        return normalizeProfile(JSON.parse(raw), fallbackUser);
    } catch (error) {
        return normalizeProfile({}, fallbackUser);
    }
}

export function saveUserProfile(uid, profile) {
    localStorage.setItem(getProfileKey(uid), JSON.stringify(profile));
}

export function syncCurrentUserSnapshot(user) {
    try {
        let finalUid = user.uid;
        if (finalUid && !finalUid.startsWith('user_') && !finalUid.startsWith('demo_')) {
            const mapped = localStorage.getItem(`fs_mapped_uid_${finalUid}`);
            if (mapped) {
                finalUid = mapped;
            }
        }
        localStorage.setItem('fs_currentUser', JSON.stringify({
            uid: finalUid,
            email: user.email || '',
            displayName: user.displayName || user.email?.split('@')[0] || ''
        }));
    } catch (error) {
        console.warn('localStorage set failed', error);
    }
}

export function clearCurrentUserSnapshot() {
    localStorage.removeItem('fs_currentUser');
}

export function addShareItem(uid, item, fallbackUser) {
    const profile = loadUserProfile(uid, fallbackUser);
    const nextProfile = {
        ...profile,
        shareHistory: [
            {
                id: item.id || `share-${Date.now()}`,
                title: item.title,
                emoji: item.emoji || '🎁',
                location: item.location,
                timeLabel: item.timeLabel || '剛剛發布',
                href: item.href || `/static/detail.html?id=${item.id || ''}`,
                status: item.status || '進行中',
                ...item
            },
            ...profile.shareHistory
        ]
    };
    saveUserProfile(uid, nextProfile);
    return nextProfile;
}

export function addRequestItem(uid, item, fallbackUser) {
    const profile = loadUserProfile(uid, fallbackUser);
    const nextProfile = {
        ...profile,
        requestHistory: [
            {
                id: item.id || `request-${Date.now()}`,
                title: item.title,
                emoji: item.emoji || '🍴',
                location: item.location,
                timeLabel: item.timeLabel || '待前往領取',
                href: item.href || `/static/detail.html?id=${item.id || ''}`,
                status: item.status || '待處理',
                ...item
            },
            ...profile.requestHistory
        ]
    };
    saveUserProfile(uid, nextProfile);
    return nextProfile;
}

export function getDefaultAvatarDataUrl(label) {
    const canvas = document.createElement('canvas');
    canvas.width = 120;
    canvas.height = 120;
    const ctx = canvas.getContext('2d');
    const gradient = ctx.createLinearGradient(0, 0, 120, 120);
    gradient.addColorStop(0, '#FBB28B');
    gradient.addColorStop(1, '#A8CBCB');
    ctx.fillStyle = gradient;
    ctx.fillRect(0, 0, 120, 120);
    ctx.fillStyle = 'rgba(255,255,255,0.92)';
    ctx.beginPath();
    ctx.arc(60, 60, 52, 0, Math.PI * 2);
    ctx.fill();
    ctx.fillStyle = '#0f172a';
    ctx.font = 'bold 42px sans-serif';
    ctx.textAlign = 'center';
    ctx.textBaseline = 'middle';
    const text = (label || '').trim();
    const parts = text.split(/\s+/).filter(Boolean);
    const initials = !text ? '9' : (parts.length === 1 ? parts[0].slice(0, 1).toUpperCase() : (parts[0][0] + parts[parts.length - 1][0]).toUpperCase());
    ctx.fillText(initials, 60, 63);
    return canvas.toDataURL('image/png');
}
