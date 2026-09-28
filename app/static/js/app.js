const TOKEN_KEY = 'pocketsmart_token';

function getToken() {
    return localStorage.getItem(TOKEN_KEY);
}

function getAuthHeaders(isJson = true) {
    const headers = {};
    if (isJson) headers['Content-Type'] = 'application/json';
    const token = getToken();
    if (token) headers['Authorization'] = 'Bearer ' + token;
    return headers;
}

function requireLogin() {
    if (!getToken()) {
        window.location.href = '/login';
        return false;
    }
    return true;
}

function formatCurrency(amount) {
    return '₹' + Number(amount || 0).toLocaleString('en-IN');
}

function renderResultsContainer(data) {
    const el = document.getElementById('results');
    if (!el) return;

    const sourceBadge = data.source === 'gemini'
        ? '<span class="tag tag-ai">✨ Powered by Gemini AI</span>'
        : '<span class="tag tag-fallback">⚡ Budget Rule Engine</span>';

    const tipsHtml = (data.tips || []).map(tip => `<li>${tip}</li>`).join('');

    const recsHtml = (data.recommendations || []).map(r => `
        <div class="card rec-card">
            <div class="rec-info">
                <div class="rec-header">
                    <span class="tag tag-platform">${r.platform}</span>
                    <span class="tag tag-cat">${r.category}</span>
                </div>
                <h3>${r.title}</h3>
                <p class="rec-desc">${r.description}</p>
                <p class="rec-why"><strong>Why this fits:</strong> ${r.why}</p>
                <a href="${r.url}" target="_blank" rel="noopener" class="search-link">
                    Search on ${r.platform} ↗
                </a>
            </div>
            <div class="rec-pricing">
                <div class="price">${formatCurrency(r.estimated_price)}</div>
                <div class="qty">Qty: ${r.quantity || 1}</div>
            </div>
        </div>
    `).join('');

    el.innerHTML = `
        <div class="results-wrapper">
            <div class="card summary-card">
                <div class="summary-header">
                    ${sourceBadge}
                    <h2>${data.summary}</h2>
                </div>
                <div class="budget-pills">
                    <div class="pill"><span>Target Budget</span><strong>${formatCurrency(data.budget)}</strong></div>
                    <div class="pill"><span>Allocated Spend</span><strong>${formatCurrency(data.allocated_budget)}</strong></div>
                </div>
                ${tipsHtml ? `<div class="tips-box"><h4>💡 Smart Tips</h4><ul>${tipsHtml}</ul></div>` : ''}
            </div>
            <div class="recommendations-list">
                <h3>Recommended Items & Services</h3>
                ${recsHtml}
            </div>
        </div>
    `;

    el.scrollIntoView({ behavior: 'smooth', block: 'start' });
}

async function apiRequest(url, opts = {}) {
    const headers = getAuthHeaders(opts.body && typeof opts.body === 'string');
    const mergedOpts = {
        ...opts,
        headers: {
            ...headers,
            ...(opts.headers || {})
        }
    };
    const response = await fetch(url, mergedOpts);
    const data = await response.json().catch(() => ({ detail: 'Unexpected server response' }));
    if (!response.ok) {
        throw new Error(data.detail || 'Request failed with status ' + response.status);
    }
    return data;
}

function formToObject(form) {
    const formData = new FormData(form);
    return Object.fromEntries(formData.entries());
}

async function handlePlannerSubmit(type, form) {
    if (!requireLogin()) return;

    const resultsEl = document.getElementById('results');
    if (resultsEl) {
        resultsEl.innerHTML = `
            <div class="loading-box">
                <div class="spinner"></div>
                <p>Generating personalized recommendations with PocketSmart AI...</p>
            </div>
        `;
    }

    try {
        const rawData = formToObject(form);
        let resultData;

        if (type === 'home') {
            rawData.budget = Number(rawData.budget);
            rawData.items = (rawData.items || '')
                .split(',')
                .filter(Boolean)
                .map(itemStr => {
                    const [category, qtyStr] = itemStr.split(':');
                    return {
                        category: (category || '').trim(),
                        quantity: Number(qtyStr || 1)
                    };
                });
            resultData = await apiRequest('/generate-home', {
                method: 'POST',
                body: JSON.stringify(rawData)
            });
        } else if (type === 'party') {
            rawData.budget = Number(rawData.budget);
            rawData.guests = Number(rawData.guests);
            resultData = await apiRequest('/generate-party', {
                method: 'POST',
                body: JSON.stringify(rawData)
            });
        } else if (type === 'jewelry') {
            const payload = {
                budget: Number(rawData.budget),
                occasion: rawData.occasion,
                style: rawData.style,
                outfit_color: rawData.outfit_color || 'Not specified',
                jewelry_type: rawData.jewelry_type,
                notes: rawData.notes || ''
            };

            const fd = new FormData();
            fd.append('payload', JSON.stringify(payload));
            if (form.image && form.image.files[0]) {
                fd.append('image', form.image.files[0]);
            }

            const token = getToken();
            const headers = token ? { 'Authorization': 'Bearer ' + token } : {};

            const r = await fetch('/generate-jewelry', {
                method: 'POST',
                headers: headers,
                body: fd
            });

            const d = await r.json().catch(() => ({ detail: 'Failed to process request' }));
            if (!r.ok) throw new Error(d.detail || 'Jewelry planner request failed');
            resultData = d;
        }

        renderResultsContainer(resultData);
    } catch (err) {
        if (resultsEl) {
            resultsEl.innerHTML = `<div class="error-banner">⚠️ ${err.message}</div>`;
        }
    }
}

async function loadDashboard() {
    const welcome = document.getElementById('welcome');
    const cardsEl = document.getElementById('dashboardCards');
    if (!cardsEl) return;

    try {
        const data = await apiRequest('/session-data');
        if (data.logged_in && data.user) {
            if (welcome) {
                welcome.textContent = `Welcome back, ${data.user.name}! Choose a planner below or view your history.`;
            }
            cardsEl.innerHTML = `
                <a class="card link-card feature-card" href="/planner/home">
                    <div class="card-icon">🏠</div>
                    <b>Home Interior</b>
                    <p>Plan room furniture, lighting, decor & budget allocation.</p>
                </a>
                <a class="card link-card feature-card" href="/planner/party">
                    <div class="card-icon">🎉</div>
                    <b>Party Planner</b>
                    <p>Catering, venue, decoration & entertainment budget breakdown.</p>
                </a>
                <a class="card link-card feature-card" href="/planner/jewelry">
                    <div class="card-icon">💎</div>
                    <b>Jewelry Planner</b>
                    <p>Occasion & outfit color matching with visual upload support.</p>
                </a>
                <a class="card link-card feature-card highlight-card" href="/history">
                    <div class="card-icon">📜</div>
                    <b>Saved History (${data.personalization.saved_recommendations})</b>
                    <p>Review past budget plans and recommendation details anytime.</p>
                </a>
            `;
        } else {
            if (welcome) welcome.textContent = 'Please log in to view your dashboard.';
            cardsEl.innerHTML = `<p><a href="/login" class="btn">Login to proceed</a></p>`;
        }
    } catch (e) {
        if (welcome) welcome.textContent = 'Please log in to view your dashboard.';
    }
}

async function loadHistory() {
    const hl = document.getElementById('historyList');
    if (!hl) return;

    if (!getToken()) {
        hl.innerHTML = '<div class="card"><p>Please <a href="/login">login</a> to view your saved recommendation history.</p></div>';
        return;
    }

    try {
        const rows = await apiRequest('/history');
        if (!rows.length) {
            hl.innerHTML = '<div class="card"><p>No saved recommendations yet. Try creating one using the planners above!</p></div>';
            return;
        }

        hl.innerHTML = rows.map(r => `
            <div class="card history-card" id="history-item-${r.id}">
                <div class="history-main">
                    <div>
                        <span class="tag tag-planner">${r.planner.toUpperCase()}</span>
                        <span class="history-date">${new Date(r.created_at).toLocaleString()}</span>
                        <h3 class="history-summary">${r.summary}</h3>
                    </div>
                    <button class="btn ghost btn-sm" onclick="toggleHistoryDetails(${r.id})">View Details</button>
                </div>
                <div class="history-details" id="details-${r.id}" style="display:none;"></div>
            </div>
        `).join('');
    } catch (err) {
        hl.innerHTML = `<div class="error-banner">⚠️ ${err.message}</div>`;
    }
}

async function toggleHistoryDetails(historyId) {
    const detailsEl = document.getElementById(`details-${historyId}`);
    if (!detailsEl) return;

    if (detailsEl.style.display === 'block') {
        detailsEl.style.display = 'none';
        return;
    }

    if (detailsEl.innerHTML.trim() === '') {
        detailsEl.innerHTML = '<p class="loading-text">Loading recommendation details...</p>';
        detailsEl.style.display = 'block';

        try {
            const data = await apiRequest(`/recommendations-details/${historyId}`);
            const res = data.result;

            const recsHtml = (res.recommendations || []).map(r => `
                <div class="history-rec-item">
                    <div>
                        <strong>${r.title}</strong> (${r.platform})
                        <p class="small-desc">${r.description}</p>
                    </div>
                    <div class="price">${formatCurrency(r.estimated_price)}</div>
                </div>
            `).join('');

            detailsEl.innerHTML = `
                <div class="history-details-content">
                    <p><strong>Allocated Budget:</strong> ${formatCurrency(res.allocated_budget)} / ${formatCurrency(res.budget)}</p>
                    <div class="history-recs-list">${recsHtml}</div>
                </div>
            `;
        } catch (e) {
            detailsEl.innerHTML = `<p class="error-text">Failed to load details: ${e.message}</p>`;
        }
    } else {
        detailsEl.style.display = 'block';
    }
}

document.addEventListener('DOMContentLoaded', () => {
    // Navigation / Auth link state
    const authLink = document.getElementById('authLink');
    if (getToken() && authLink) {
        authLink.textContent = 'Logout';
        authLink.onclick = (e) => {
            e.preventDefault();
            localStorage.removeItem(TOKEN_KEY);
            window.location.href = '/';
        };
    }

    // Auth forms
    const lf = document.getElementById('loginForm');
    if (lf) {
        lf.onsubmit = async (e) => {
            e.preventDefault();
            const msgEl = lf.querySelector('.message');
            if (msgEl) msgEl.textContent = '';
            try {
                const res = await apiRequest('/login', {
                    method: 'POST',
                    body: JSON.stringify(formToObject(lf))
                });
                localStorage.setItem(TOKEN_KEY, res.access_token);
                window.location.href = '/dashboard';
            } catch (err) {
                if (msgEl) msgEl.textContent = err.message;
            }
        };
    }

    const rf = document.getElementById('registerForm');
    if (rf) {
        rf.onsubmit = async (e) => {
            e.preventDefault();
            const msgEl = rf.querySelector('.message');
            if (msgEl) msgEl.textContent = '';
            try {
                const res = await apiRequest('/register', {
                    method: 'POST',
                    body: JSON.stringify(formToObject(rf))
                });
                localStorage.setItem(TOKEN_KEY, res.access_token);
                window.location.href = '/dashboard';
            } catch (err) {
                if (msgEl) msgEl.textContent = err.message;
            }
        };
    }

    // Planner forms
    const hf = document.getElementById('homeForm');
    if (hf) hf.onsubmit = (e) => { e.preventDefault(); handlePlannerSubmit('home', hf); };

    const pf = document.getElementById('partyForm');
    if (pf) pf.onsubmit = (e) => { e.preventDefault(); handlePlannerSubmit('party', pf); };

    const jf = document.getElementById('jewelryForm');
    if (jf) jf.onsubmit = (e) => { e.preventDefault(); handlePlannerSubmit('jewelry', jf); };

    // Dashboard & History page initializers
    if (document.getElementById('dashboardCards')) loadDashboard();
    if (document.getElementById('historyList')) loadHistory();
});
