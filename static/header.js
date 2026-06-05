(() => {
    // 判斷目前執行腳本的頁面是否為首頁，以給予正確的相對路徑（首頁在根目錄，其餘頁面皆在 static 目錄）
    const isHomePage = window.location.pathname.endsWith('/index.html') || window.location.pathname === '/' || window.location.pathname.endsWith('/');
    const inStatic = !isHomePage;
    const root = inStatic ? '../' : './';
    const s = inStatic ? './' : './static/';

    // 動態插入自適應 CSS 樣式與自訂彈窗樣式
    const style = document.createElement('style');
    style.textContent = `
        @media (max-width: 540px) {
            .header-icon-desktop { display: none !important; }
            .header-icon-mobile { display: flex !important; }
        }
        @media (min-width: 541px) {
            .header-icon-mobile { display: none !important; }
            #avatar-red-dot { display: none !important; }
        }
        .notification-role-sharer { border-left-color: #FBB28B !important; background-color: #fff7f2 !important; }
        .notification-role-requester { border-left-color: #A8CBCB !important; background-color: #f3fbfb !important; }
        .notification-read {
            opacity: 0.8 !important;
            filter: saturate(0.65) !important;
        }

        /* 自訂 Alert / Confirm 彈窗樣式 */
        .custom-modal-overlay {
            position: fixed;
            top: 0;
            left: 0;
            right: 0;
            bottom: 0;
            background-color: rgba(28, 25, 23, 0.4);
            backdrop-filter: blur(4px);
            display: flex;
            align-items: center;
            justify-content: center;
            z-index: 999999;
            opacity: 0;
            transition: opacity 0.2s ease-out;
        }
        .custom-modal-overlay.show {
            opacity: 1;
        }
        .custom-modal-card {
            background-color: #ffffff;
            border-radius: 1.25rem;
            box-shadow: 0 10px 25px -5px rgba(0, 0, 0, 0.08), 0 8px 10px -6px rgba(0, 0, 0, 0.08);
            border: 1px solid rgba(245, 245, 244, 0.8);
            width: 90%;
            max-width: 380px;
            padding: 1.5rem;
            transform: scale(0.95);
            transition: transform 0.2s cubic-bezier(0.34, 1.56, 0.64, 1);
        }
        .custom-modal-overlay.show .custom-modal-card {
            transform: scale(1);
        }
    `;
    document.head.appendChild(style);

    // 覆寫 window.alert
    const originalAlert = window.alert;
    window.alert = function(message, callback) {
        if (!document.body) {
            originalAlert(message);
            if (callback) callback();
            return;
        }

        const overlay = document.createElement('div');
        overlay.className = 'custom-modal-overlay';
        overlay.innerHTML = `
            <div class="custom-modal-card flex flex-col items-center text-center">
                <div class="w-12 h-12 rounded-full bg-teal-50 text-receiver flex items-center justify-center text-2xl mb-3 shadow-inner">
                    🔔
                </div>
                <p class="text-sm font-semibold text-gray-800 leading-relaxed mb-5 whitespace-pre-line">${message}</p>
                <button class="custom-modal-confirm-btn w-full py-2 bg-receiver hover:bg-teal-600 text-white font-medium rounded-xl text-xs transition transform hover:-translate-y-0.5 shadow-sm">
                    確定
                </button>
            </div>
        `;
        document.body.appendChild(overlay);

        setTimeout(() => overlay.classList.add('show'), 10);

        const closeAlert = () => {
            overlay.classList.remove('show');
            setTimeout(() => {
                overlay.remove();
                if (callback) callback();
            }, 200);
        };

        overlay.querySelector('.custom-modal-confirm-btn').addEventListener('click', closeAlert);

        const handleKeyDown = (e) => {
            if (e.key === 'Enter' || e.key === 'Escape') {
                e.preventDefault();
                document.removeEventListener('keydown', handleKeyDown);
                closeAlert();
            }
        };
        document.addEventListener('keydown', handleKeyDown);
    };

    // 覆寫 window.confirm
    const originalConfirm = window.confirm;
    window.confirm = function(message, onConfirm, onCancel) {
        if (typeof onConfirm !== 'function') {
            return originalConfirm(message);
        }

        if (!document.body) {
            const result = originalConfirm(message);
            if (result) onConfirm();
            else if (onCancel) onCancel();
            return;
        }

        const overlay = document.createElement('div');
        overlay.className = 'custom-modal-overlay';
        overlay.innerHTML = `
            <div class="custom-modal-card flex flex-col items-center text-center">
                <div class="w-12 h-12 rounded-full bg-orange-50 text-giver flex items-center justify-center text-2xl mb-3 shadow-inner">
                    ❓
                </div>
                <p class="text-sm font-semibold text-gray-800 leading-relaxed mb-5 whitespace-pre-line">${message}</p>
                <div class="flex gap-3 w-full">
                    <button class="custom-modal-cancel-btn flex-1 py-2 bg-stone-100 hover:bg-stone-200 text-gray-600 font-medium rounded-xl text-xs transition">
                        取消
                    </button>
                    <button class="custom-modal-confirm-btn flex-1 py-2 bg-receiver hover:bg-teal-600 text-white font-medium rounded-xl text-xs transition transform hover:-translate-y-0.5 shadow-sm">
                        確定
                    </button>
                </div>
            </div>
        `;
        document.body.appendChild(overlay);

        setTimeout(() => overlay.classList.add('show'), 10);

        const closeConfirm = (confirmed) => {
            overlay.classList.remove('show');
            setTimeout(() => {
                overlay.remove();
                if (confirmed) {
                    if (onConfirm) onConfirm();
                } else {
                    if (onCancel) onCancel();
                }
            }, 200);
        };

        overlay.querySelector('.custom-modal-confirm-btn').addEventListener('click', () => closeConfirm(true));
        overlay.querySelector('.custom-modal-cancel-btn').addEventListener('click', () => closeConfirm(false));

        const handleKeyDown = (e) => {
            if (e.key === 'Enter') {
                e.preventDefault();
                document.removeEventListener('keydown', handleKeyDown);
                closeConfirm(true);
            } else if (e.key === 'Escape') {
                e.preventDefault();
                document.removeEventListener('keydown', handleKeyDown);
                closeConfirm(false);
            }
        };
        document.addEventListener('keydown', handleKeyDown);
    };

    const header = document.createElement('header');
    header.className = 'fixed top-0 left-0 right-0 bg-white border-b border-gray-200 z-[10000] px-4 py-3 lg:px-6 lg:py-4 flex items-center gap-3 lg:gap-8';
    
    // 這裡就是全站共用的導覽列 HTML
    header.innerHTML = `
        <div class="shrink-0 flex items-center gap-2">
            <!-- 漢堡排按鈕 (lg以下顯示，用來收納左側功能) -->
            <button id="menu-toggle-btn" class="lg:hidden text-gray-600 hover:text-gray-900 focus:outline-none text-2xl p-1">
                ☰
            </button>
            <a href="${root}index.html" aria-label="回到首頁" class="hidden sm:block">
                <img src="${s}logo.png" alt="FoodShare Logo" style="width:3rem;height:3rem;object-fit:contain;display:block">
            </a>
        </div>
        
        <!-- 桌機版導覽列 (lg以上顯示) -->
        <nav class="hidden lg:flex items-center gap-8 text-[15px] font-medium text-gray-700">
            <a href="${root}index.html" class="hover:text-receiver transition">首頁</a>
            <a href="${s}aboutus.html" class="hover:text-receiver transition">關於我們</a>
            <a href="${s}teach.html" class="hover:text-receiver transition">使用教學</a>
            
            <a href="${s}share.html" class="text-giver hover:opacity-80 transition font-bold">分享清單</a>
            <a href="${s}food.html" class="text-receiver hover:opacity-80 transition font-bold">預約清單</a>
        </nav>
        
        <!-- 搜尋框 (各尺寸皆顯示，大螢幕最大可寬達 600px 並向右貼近 icon 區) -->
        <div class="flex-1 lg:ml-auto max-w-[600px] relative mx-2 sm:mx-0">
            <input type="text" id="header-search-input" placeholder="搜尋關鍵字或地點…"
                   class="w-full h-10 sm:h-12 pl-9 sm:pl-11 pr-4 rounded-xl border border-gray-200 bg-gray-100 focus:outline-none focus:ring-2 focus:ring-receiver focus:border-transparent text-sm">
            <div class="absolute left-3 top-2.5 sm:top-3.5 text-gray-400">
                <svg xmlns="http://www.w3.org/2000/svg" class="h-4 w-4 sm:h-5 sm:w-5" fill="none" viewBox="0 0 24 24" stroke="currentColor"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M21 21l-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0z"/></svg>
            </div>
        </div>
        
        <!-- 右側控制區 (全尺寸顯示，但內部較寬按鈕在手機版 <=540px 會隱藏並移至頭像選單) -->
        <div class="flex items-center gap-2 sm:gap-3 shrink-0 ml-auto">
            <div id="user-controls" class="flex items-center gap-2 sm:gap-3 hidden">
                <a id="msg-icon-link" href="${s}message.html" class="header-icon-desktop inline-block relative text-gray-600 hover:text-gray-900 transition" title="私訊">
                    <svg id="msg-icon-svg" xmlns="http://www.w3.org/2000/svg" class="h-5 w-5 sm:h-6 sm:w-6" fill="none" viewBox="0 0 24 24" stroke="currentColor"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M8 12h.01M12 12h.01M16 12h.01M21 12c0 4.418-4.03 8-9 8a9.863 9.863 0 01-4.255-.949L3 20l1.395-3.72C3.512 15.042 3 13.574 3 12c0-4.418 4.03-8 9-8s9 3.582 9 8z" /></svg>
                    <!-- 訊息未讀紅點提示 -->
                    <span id="msg-red-dot" class="absolute -top-0.5 -right-0.5 w-2.5 h-2.5 bg-red-500 rounded-full border border-white hidden z-10"></span>
                </a>
                
                <button id="notification-btn-desktop" class="header-icon-desktop relative text-gray-600 hover:text-gray-900 transition" title="系統通知">
                    <svg xmlns="http://www.w3.org/2000/svg" class="h-5 w-5 sm:h-6 sm:w-6" fill="none" viewBox="0 0 24 24" stroke="currentColor"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M15 17h5l-1.405-1.405A2.032 2.032 0 0118 14.158V11a6.002 6.002 0 00-4-5.659V5a2 2 0 10-4 0v.341C7.67 6.165 6 8.388 6 11v3.159c0 .538-.214 1.055-.595 1.436L4 17h5m6 0v1a3 3 0 11-6 0v-1m6 0H9"/></svg>
                    <span id="notification-badge-desktop" class="absolute -top-1 -right-1 bg-red-500 text-white text-[10px] min-w-[16px] h-4 px-1 rounded-full hidden items-center justify-center leading-4">0</span>
                </button>
                
                <div class="relative overflow-visible">
                    <button id="avatar-btn" class="w-8 h-8 sm:w-9 sm:h-9 rounded-full bg-receiver text-white flex items-center justify-center font-bold focus:outline-none overflow-hidden border border-transparent hover:border-receiver">
                        <img id="avatar-btn-image" alt="使用者頭貼" class="hidden h-full w-full object-cover">
                        <span id="avatar-btn-fallback" class="text-xs">?</span>
                    </button>
                    <!-- 紅色點點提示 -->
                    <span id="avatar-red-dot" class="absolute -top-0.5 -right-0.5 w-3 h-3 bg-red-500 rounded-full border-2 border-white hidden z-10"></span>
                    <div id="avatar-menu" class="absolute right-0 top-full mt-2 w-48 invisible opacity-0 transition-all duration-200 z-[9999]">
                        <div class="bg-white shadow-lg rounded-xl py-1 border border-gray-100">
                            <div id="user-name-display" class="px-4 py-2 text-xs font-bold text-gray-500 border-b border-gray-100 bg-gray-50 rounded-t-xl">嗨，同學</div>
                            
                            <!-- 手機版隱藏按鈕收納區 (<=540px 才會顯示) -->
                            <a href="${s}message.html" class="header-icon-mobile px-4 py-2 text-sm text-gray-700 hover:bg-gray-100 border-b border-gray-50 flex items-center justify-between">
                                <span>💬 私訊對話</span>
                                <span id="avatar-unread-badge" class="bg-red-500 text-white text-[10px] px-1.5 py-0.5 rounded-full hidden">0</span>
                            </a>
                            <button id="notification-btn-mobile" class="header-icon-mobile w-full text-left px-4 py-2 text-sm text-gray-700 hover:bg-gray-100 border-b border-gray-50 items-center justify-between">
                                <span>🔔 系統通知</span>
                                <span id="notification-badge-mobile" class="bg-red-500 text-white text-[10px] px-1.5 py-0.5 rounded-full hidden">0</span>
                            </button>
                            <a href="${s}upload.html" class="header-icon-mobile block px-4 py-2 text-sm text-giver hover:bg-orange-50 font-bold border-b border-gray-50">＋ 我要分享</a>
                            
                            <a href="${s}profile.html" class="block px-4 py-2 text-sm text-gray-700 hover:bg-gray-100">👤 個人檔案</a>
                            <hr class="my-1">
                            <button id="logout-btn" class="w-full text-left px-4 py-2 text-sm text-red-600 hover:bg-red-50">🚪 登出</button>
                        </div>
                    </div>
                </div>

                <a href="${s}upload.html" class="header-icon-desktop bg-giver hover:bg-orange-400 text-white font-medium px-3 py-1.5 sm:px-4 sm:py-2 text-xs sm:text-sm rounded-full transition shadow-sm inline-block shrink-0">
                    ＋ 分享
                </a>
            </div>
            
            <button id="header-login-btn" class="bg-[#A8CBCB] hover:bg-teal-600 text-white font-semibold px-4 py-1.5 sm:px-5 sm:py-2 text-xs sm:text-sm transition shadow-sm shrink-0 rounded-full">
                登入 / 註冊
            </button>
        </div>

        <!-- 行動裝置下拉選單 (只收納左側選單連結，在lg以下點擊三條線展開) -->
        <div id="mobile-menu" class="absolute left-0 top-full w-full bg-white border-b border-gray-200 shadow-md py-4 px-6 flex flex-col gap-2 hidden lg:hidden z-[99999]">
            <a href="${root}index.html" class="hover:text-receiver transition py-2 font-medium border-b border-gray-50"> 首頁</a>
            <a href="${s}aboutus.html" class="hover:text-receiver transition py-2 font-medium border-b border-gray-50"> 關於我們</a>
            <a href="${s}teach.html" class="hover:text-receiver transition py-2 font-medium border-b border-gray-50"> 使用教學</a>
            <a href="${s}share.html" class="text-giver hover:opacity-80 transition py-2 font-bold border-b border-gray-50"> 分享清單</a>
            <a href="${s}food.html" class="text-receiver hover:opacity-80 transition py-2 font-bold">預約清單</a>
        </div>

        <div id="notification-panel" class="absolute right-4 top-full mt-2 w-[min(360px,calc(100vw-2rem))] invisible opacity-0 transition-all duration-200 z-[99999]">
            <div class="bg-white rounded-xl border border-gray-100 shadow-xl overflow-hidden">
                <div class="px-4 py-3 border-b border-gray-100 flex items-center justify-between">
                    <p class="text-sm font-bold text-gray-800">系統通知</p>
                    <button id="notification-read-btn" class="text-xs text-gray-400 hover:text-gray-700">全部已讀</button>
                </div>
                <div id="notification-list" class="max-h-96 overflow-y-auto p-3 space-y-2">
                    <p class="text-center text-gray-400 text-sm py-6">載入中…</p>
                </div>
            </div>
        </div>
    `;

    const script = document.currentScript;
    script.parentNode.insertBefore(header, script);

    // ================= 登入狀態與頭像邏輯 =================
    function getSnapshot() {
        try {
            return JSON.parse(localStorage.getItem('fs_currentUser') || 'null');
        } catch {
            return null;
        }
    }
    let snapshot = null;
    let profile = null;
    try { snapshot = getSnapshot(); } catch {}
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
            notificationPanel?.classList.add('invisible');
            notificationPanel?.classList.add('opacity-0');
            snapshot = getSnapshot();
            if (snapshot?.uid) {
                fetch(`${root}api/messages/unread/${snapshot.uid}`)
                    .then(res => res.json())
                    .then(data => {
                        unreadMessagesCount = data?.unread || 0;
                        const badge = header.querySelector('#avatar-unread-badge');
                        if (badge) {
                            if (unreadMessagesCount > 0) {
                                badge.textContent = unreadMessagesCount;
                                badge.classList.remove('hidden');
                            } else {
                                badge.classList.add('hidden');
                            }
                        }
                        updateMsgRedDot();
                    })
                    .catch(() => {});
                loadNotifications();
            }
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

    // 漢堡排按鈕展開/收合
    const menuToggleBtn = header.querySelector('#menu-toggle-btn');
    const mobileMenu = header.querySelector('#mobile-menu');
    if (menuToggleBtn && mobileMenu) {
        menuToggleBtn.addEventListener('click', (e) => {
            e.stopPropagation();
            mobileMenu.classList.toggle('hidden');
        });
        
        document.addEventListener('click', (e) => {
            if (!mobileMenu.contains(e.target) && e.target !== menuToggleBtn) {
                mobileMenu.classList.add('hidden');
            }
        });
    }

    // ================= 系統通知 =================
    const notificationPanel = header.querySelector('#notification-panel');
    const notificationList = header.querySelector('#notification-list');
    const notificationReadBtn = header.querySelector('#notification-read-btn');
    const notificationButtons = [
        header.querySelector('#notification-btn-desktop'),
        header.querySelector('#notification-btn-mobile')
    ].filter(Boolean);

    function escapeHtml(value) {
        return String(value || '').replace(/[&<>"']/g, ch => ({
            '&': '&amp;',
            '<': '&lt;',
            '>': '&gt;',
            '"': '&quot;',
            "'": '&#39;'
        }[ch]));
    }

    let unreadNotificationsCount = 0;
    let unreadMessagesCount = 0;

    function updateAvatarRedDot() {
        const dot = header.querySelector('#avatar-red-dot');
        if (!dot) return;
        if (unreadNotificationsCount > 0) {
            dot.classList.remove('hidden');
        } else {
            dot.classList.add('hidden');
        }
    }

    function updateMsgRedDot() {
        const dot = header.querySelector('#msg-red-dot');
        if (!dot) return;
        if (unreadMessagesCount > 0) {
            dot.classList.remove('hidden');
        } else {
            dot.classList.add('hidden');
        }
    }

    function setNotificationBadges(count) {
        const badges = [
            header.querySelector('#notification-badge-desktop'),
            header.querySelector('#notification-badge-mobile')
        ].filter(Boolean);
        badges.forEach(badge => {
            if (count > 0) {
                badge.textContent = count > 99 ? '99+' : String(count);
                badge.classList.remove('hidden');
                if (badge.id === 'notification-badge-desktop') badge.classList.add('flex');
            } else {
                badge.classList.add('hidden');
                badge.classList.remove('flex');
            }
        });
        unreadNotificationsCount = count;
        updateAvatarRedDot();
    }

    function renderNotifications(items) {
        if (!notificationList) return;
        if (!items.length) {
            notificationList.innerHTML = '<p class="text-center text-gray-400 text-sm py-6">目前沒有系統通知</p>';
            return;
        }
        notificationList.innerHTML = items.map(item => {
            const roleClass = item.role === 'sharer' ? 'notification-role-sharer' : 'notification-role-requester';
            const roleLabel = item.role === 'sharer' ? '分享者' : '預約者';
            const roleColor = item.role === 'sharer' ? '#FBB28B' : '#A8CBCB';
            const href = item.food_post_id ? `${s}detail.html?id=${encodeURIComponent(item.food_post_id)}` : '#';
            const readClass = item.is_read ? 'notification-read' : '';
            return `
                <a href="${href}" data-id="${item.id}" class="notification-item block border-l-4 ${roleClass} rounded-lg px-3 py-2.5 hover:shadow-sm transition ${readClass}">
                    <div class="flex items-start justify-between gap-3">
                        <p class="text-sm font-bold text-gray-800 leading-snug">${escapeHtml(item.title)}</p>
                        <span class="shrink-0 text-[11px] font-semibold text-white px-2 py-0.5 rounded-full" style="background:${roleColor}">${roleLabel}</span>
                    </div>
                    <p class="text-xs text-gray-600 leading-relaxed mt-1">${escapeHtml(item.body)}</p>
                    <p class="text-[11px] text-gray-400 mt-1.5">${escapeHtml(item.time_ago)}</p>
                </a>
            `;
        }).join('');
    }

    async function loadNotifications() {
        snapshot = getSnapshot();
        if (!snapshot?.uid) return;
        try {
            const res = await fetch(`${root}api/notifications/${snapshot.uid}`);
            const data = await res.json();
            setNotificationBadges(data.unread || 0);
            renderNotifications(Array.isArray(data.notifications) ? data.notifications : []);
        } catch {
            if (notificationList) {
                notificationList.innerHTML = '<p class="text-center text-gray-400 text-sm py-6">通知載入失敗</p>';
            }
        }
    }

    function toggleNotifications(event) {
        event.stopPropagation();
        notificationPanel?.classList.toggle('invisible');
        notificationPanel?.classList.toggle('opacity-0');
        avatarMenu?.classList.add('invisible');
        avatarMenu?.classList.add('opacity-0');
        snapshot = getSnapshot();
        loadNotifications();
    }

    notificationButtons.forEach(btn => btn.addEventListener('click', toggleNotifications));
    notificationPanel?.addEventListener('click', event => event.stopPropagation());
    document.addEventListener('click', () => {
        notificationPanel?.classList.add('invisible');
        notificationPanel?.classList.add('opacity-0');
    });
    notificationReadBtn?.addEventListener('click', async () => {
        snapshot = getSnapshot();
        if (!snapshot?.uid) return;
        try {
            await fetch(`${root}api/notifications/${snapshot.uid}/read`, { method: 'POST' });
            await loadNotifications();
        } catch {}
    });

    notificationList?.addEventListener('click', async (event) => {
        const item = event.target.closest('.notification-item');
        if (!item) return;

        const href = item.getAttribute('href');
        const notifId = item.getAttribute('data-id');

        if (notifId && !item.classList.contains('notification-read')) {
            event.preventDefault();
            
            // visually mark as read immediately
            item.classList.add('notification-read');

            // decrement unread count locally
            if (unreadNotificationsCount > 0) {
                setNotificationBadges(unreadNotificationsCount - 1);
            }

            try {
                await fetch(`${root}api/notifications/read-single/${notifId}`, { method: 'POST' });
            } catch (e) {
                console.error("Failed to mark single notification read:", e);
            }

            if (href && href !== '#') {
                window.location.href = href;
            }
        }
    });

    // ================= 獲取未讀與狀態自動同步（輪詢監聽） =================
    let lastUid = null;
    function syncLoginState() {
        const currentSnapshot = getSnapshot();
        const currentUid = currentSnapshot?.uid || null;
        if (currentUid !== lastUid) {
            lastUid = currentUid;
            snapshot = currentSnapshot;
            if (currentUid) {
                loadNotifications();
                fetch(`${root}api/messages/unread/${currentUid}`)
                    .then(res => res.json())
                    .then(data => {
                        unreadMessagesCount = data?.unread || 0;
                        const badge = header.querySelector('#avatar-unread-badge');
                        if (badge) {
                            if (unreadMessagesCount > 0) {
                                badge.textContent = unreadMessagesCount;
                                badge.classList.remove('hidden');
                            } else {
                                badge.classList.add('hidden');
                            }
                        }
                        updateMsgRedDot();
                    })
                    .catch(() => {});
            } else {
                setNotificationBadges(0);
                unreadMessagesCount = 0;
                updateMsgRedDot();
            }
        }
    }
    syncLoginState();
    setInterval(syncLoginState, 1000);
})();
