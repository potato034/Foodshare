(() => {
    // 判斷目前執行腳本的頁面是否為首頁，以給予正確的相對路徑（首頁在根目錄，其餘頁面皆在 static 目錄）
    const isHomePage = window.location.pathname.endsWith('/index.html') || window.location.pathname === '/' || window.location.pathname.endsWith('/');
    const inStatic = !isHomePage;
    const root = inStatic ? '../' : './';
    const s = inStatic ? './' : './static/';

    const header = document.createElement('header');
    header.className = 'fixed top-0 left-0 right-0 bg-white border-b border-gray-200 z-[10000] px-6 py-4 flex items-center gap-8';
    
    // 這裡就是全站共用的導覽列 HTML
    header.innerHTML = `
        <div class="shrink-0 flex items-center">
            <a href="${root}index.html" aria-label="回到首頁">
                <img src="${s}logo.png" alt="FoodShare Logo" style="width:3rem;height:3rem;object-fit:contain;display:block">
            </a>
        </div>
        <nav class="flex items-center gap-8 text-[15px] font-medium text-gray-700">
            <a href="${root}index.html" class="hover:text-receiver transition">首頁</a>
            <a href="${s}aboutus.html" class="hover:text-receiver transition">關於我們</a>
            <a href="${s}teach.html" class="hover:text-receiver transition">使用教學</a>
            
            <a href="${s}share.html" class="text-giver hover:opacity-80 transition font-bold">分享清單</a>
            <a href="${s}food.html" class="text-receiver hover:opacity-80 transition font-bold">預約清單</a>
        </nav>
        <div class="ml-auto w-[360px] relative hidden xl:block">
            <input type="text" id="header-search-input" placeholder="搜尋關鍵字或地點…"
                   class="w-full h-12 pl-11 pr-4 rounded-xl border border-gray-200 bg-gray-100 focus:outline-none focus:ring-2 focus:ring-receiver focus:border-transparent text-sm">
            <div class="absolute left-3.5 top-3.5 text-gray-400">
                <svg xmlns="http://www.w3.org/2000/svg" class="h-5 w-5" fill="none" viewBox="0 0 24 24" stroke="currentColor"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M21 21l-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0z"/></svg>
            </div>
        </div>
        <div class="ml-auto flex items-center gap-3">
            <div id="user-controls" class="flex items-center gap-3 hidden">
                <a href="${s}message.html" class="text-gray-600 hover:text-gray-900 transition" title="私訊">
                    <svg xmlns="http://www.w3.org/2000/svg" class="h-6 w-6" fill="none" viewBox="0 0 24 24" stroke="currentColor"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M8 12h.01M12 12h.01M16 12h.01M21 12c0 4.418-4.03 8-9 8a9.863 9.863 0 01-4.255-.949L3 20l1.395-3.72C3.512 15.042 3 13.574 3 12c0-4.418 4.03-8 9-8s9 3.582 9 8z"/></svg>
                </a>
                
                <button class="text-gray-600 hover:text-gray-900 transition" title="系統通知">
                    <svg xmlns="http://www.w3.org/2000/svg" class="h-6 w-6" fill="none" viewBox="0 0 24 24" stroke="currentColor"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M15 17h5l-1.405-1.405A2.032 2.032 0 0118 14.158V11a6.002 6.002 0 00-4-5.659V5a2 2 0 10-4 0v.341C7.67 6.165 6 8.388 6 11v3.159c0 .538-.214 1.055-.595 1.436L4 17h5m6 0v1a3 3 0 11-6 0v-1m6 0H9"/></svg>
                </button>
                
                <div class="relative overflow-visible">
                    <button id="avatar-btn" class="w-9 h-9 rounded-full bg-receiver text-white flex items-center justify-center font-bold focus:outline-none overflow-hidden border border-transparent hover:border-receiver">
                        <img id="avatar-btn-image" alt="使用者頭貼" class="hidden h-full w-full object-cover">
                        <span id="avatar-btn-fallback" class="text-xs">?</span>
                    </button>
                    <div id="avatar-menu" class="absolute right-0 top-full mt-2 w-48 invisible opacity-0 transition-all duration-200 z-[9999]">
                        <div class="bg-white shadow-lg rounded-xl py-1 border border-gray-100">
                            <div id="user-name-display" class="px-4 py-2 text-xs font-bold text-gray-500 border-b border-gray-100 bg-gray-50 rounded-t-xl">嗨，同學</div>
                            <a href="${s}profile.html" class="block px-4 py-2 text-sm text-gray-700 hover:bg-gray-100">👤 個人檔案</a>
                            
                            <hr class="my-1">
                            <button id="logout-btn" class="w-full text-left px-4 py-2 text-sm text-red-600 hover:bg-red-50">🚪 登出</button>
                        </div>
                    </div>
                </div>

                <a href="${s}upload.html" class="bg-giver hover:bg-orange-400 text-white font-medium px-4 py-2 text-sm rounded-full transition shadow-sm inline-block shrink-0">
                    ＋ 馬上分享
                </a>
            </div>
            
            <button id="header-login-btn" class="bg-[#A8CBCB] hover:bg-teal-600 text-white font-semibold px-5 py-2 text-sm transition shadow-sm shrink-0 rounded-full">
                登入 / 註冊
            </button>
        </div>
    `;

    const script = document.currentScript;
    script.parentNode.insertBefore(header, script);

    // ================= 登入狀態與頭像邏輯 =================
    let snapshot = null;
    let profile = null;
    try { snapshot = JSON.parse(localStorage.getItem('fs_currentUser') || 'null'); } catch {}
    if (snapshot?.uid) {
        try { profile = JSON.parse(localStorage.getItem(`fs_user_${snapshot.uid}`) || 'null'); } catch {}
    }

    const userControls = header.querySelector('#user-controls');
    const loginBtn = header.querySelector('#header-login-btn');
    const avatarBtn = header.querySelector('#avatar-btn');
    const avatarMenu = header.querySelector('#avatar-menu');
    const avatarImage = header.querySelector('#avatar-btn-image');
    const avatarFallback = header.querySelector('#avatar-btn-fallback');
    const userNameDisplay = header.querySelector('#user-name-display');
    const logoutBtn = header.querySelector('#logout-btn');

    if (snapshot?.uid) {
        userControls?.classList.remove('hidden');
        loginBtn?.classList.add('hidden');
    } else {
        userControls?.classList.add('hidden');
        loginBtn?.classList.remove('hidden');
    }

    const displayName = (profile?.displayName || snapshot?.displayName || snapshot?.email || '').trim();

    function getInitials(text) {
        const t = (text || '').trim();
        if (!t) return '?';
        const parts = t.split(/\s+/).filter(Boolean);
        return parts.length === 1 ? parts[0][0].toUpperCase() : (parts[0][0] + parts[parts.length - 1][0]).toUpperCase();
    }

    function buildAvatarDataUrl(label) {
        try {
            const canvas = document.createElement('canvas');
            canvas.width = 120; canvas.height = 120;
            const ctx = canvas.getContext('2d');
            const g = ctx.createLinearGradient(0, 0, 120, 120);
            g.addColorStop(0, '#FBB28B'); g.addColorStop(1, '#A8CBCB');
            ctx.fillStyle = g; ctx.fillRect(0, 0, 120, 120);
            ctx.fillStyle = 'rgba(255,255,255,0.92)';
            ctx.beginPath(); ctx.arc(60, 60, 52, 0, Math.PI * 2); ctx.fill();
            ctx.fillStyle = '#0f172a'; ctx.font = 'bold 42px sans-serif';
            ctx.textAlign = 'center'; ctx.textBaseline = 'middle';
            ctx.fillText(getInitials(label), 60, 63);
            return canvas.toDataURL('image/png');
        } catch { return ''; }
    }

    if (avatarImage && snapshot?.uid) {
        let avatarSrc = '';
        const mode = profile?.avatarMode;
        if (mode === 'upload' && profile?.photoURL) {
            avatarSrc = profile.photoURL;
        } else if (mode === 'email' && profile?.photoURL) {
            avatarSrc = profile.photoURL;
        } else {
            avatarSrc = buildAvatarDataUrl(displayName || snapshot?.email || '');
        }
        if (avatarSrc) {
            avatarImage.src = avatarSrc;
            avatarImage.classList.remove('hidden');
            avatarFallback?.classList.add('hidden');
        } else {
            if (avatarFallback) avatarFallback.textContent = getInitials(displayName);
        }
    }

    if (userNameDisplay) {
        userNameDisplay.textContent = `嗨，${displayName || '同學'}`;
    }

    if (avatarBtn && avatarMenu) {
        avatarBtn.addEventListener('click', e => {
            e.stopPropagation();
            avatarMenu.classList.toggle('invisible');
            avatarMenu.classList.toggle('opacity-0');
        });
        document.addEventListener('click', e => {
            if (!avatarMenu.contains(e.target)) {
                avatarMenu.classList.add('invisible');
                avatarMenu.classList.add('opacity-0');
            }
        });
    }

    if (loginBtn) {
        loginBtn.addEventListener('click', () => {
            const modal = document.getElementById('login-view');
            if (modal) {
                modal.classList.remove('hidden');
            } else {
                window.location.href = root + 'index.html';
            }
        });
    }

    if (logoutBtn) {
        logoutBtn.addEventListener('click', () => {
            localStorage.removeItem('fs_currentUser');
            window.location.href = root + 'index.html?action=logout';
        });
    }

    // 搜尋 bar：按 Enter 導向 browse.html
    const searchInput = header.querySelector('#header-search-input');
    if (searchInput) {
        const urlQ = new URLSearchParams(window.location.search).get('q');
        if (urlQ && window.location.pathname.includes('browse.html')) {
            searchInput.value = urlQ;
        }

        searchInput.addEventListener('keydown', e => {
            if (e.key !== 'Enter') return;
            const q = searchInput.value.trim();
            if (!q) {
                window.location.href = `${s}browse.html`;
            } else {
                window.location.href = `${s}browse.html?q=${encodeURIComponent(q)}`;
            }
        });
    }
})();