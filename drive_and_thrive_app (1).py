<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Edible Bill Payment Calendar</title>
    <style>
        * {
            margin: 0;
            padding: 0;
            box-sizing: border-box;
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
        }
        
        body {
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            min-height: 100vh;
            padding: 20px;
        }
        
        .container {
            max-width: 1400px;
            margin: 0 auto;
            background: white;
            border-radius: 20px;
            padding: 30px;
            box-shadow: 0 20px 60px rgba(0,0,0,0.3);
        }
        
        header {
            display: flex;
            justify-content: space-between;
            align-items: center;
            margin-bottom: 30px;
            flex-wrap: wrap;
            gap: 20px;
        }
        
        h1 {
            color: #333;
            font-size: 2.5em;
        }
        
        h1 span {
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
        }
        
        .year-selector {
            display: flex;
            gap: 10px;
            align-items: center;
        }
        
        .year-btn {
            background: #f0f0f0;
            border: none;
            width: 40px;
            height: 40px;
            border-radius: 10px;
            font-size: 1.2em;
            cursor: pointer;
            transition: all 0.2s;
        }
        
        .year-btn:hover {
            background: #667eea;
            color: white;
        }
        
        .current-year {
            font-size: 1.5em;
            font-weight: bold;
            color: #333;
            min-width: 100px;
            text-align: center;
        }
        
        .add-account-btn {
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            border: none;
            padding: 12px 24px;
            border-radius: 10px;
            font-size: 1em;
            cursor: pointer;
            display: flex;
            align-items: center;
            gap: 8px;
            transition: transform 0.2s;
        }
        
        .add-account-btn:hover {
            transform: translateY(-2px);
        }
        
        .stats-bar {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
            gap: 20px;
            margin-bottom: 30px;
        }
        
        .stat-card {
            background: linear-gradient(135deg, #f5f7fa 0%, #e9ecf2 100%);
            border-radius: 15px;
            padding: 20px;
            text-align: center;
        }
        
        .stat-card h3 {
            color: #666;
            font-size: 0.9em;
            margin-bottom: 10px;
            text-transform: uppercase;
        }
        
        .stat-card .number {
            font-size: 2em;
            font-weight: bold;
            color: #333;
        }
        
        .calendar-grid {
            display: grid;
            grid-template-columns: repeat(3, 1fr);
            gap: 20px;
            margin-bottom: 30px;
        }
        
        .month-card {
            background: white;
            border-radius: 15px;
            padding: 15px;
            box-shadow: 0 4px 15px rgba(0,0,0,0.1);
            border: 1px solid #e0e0e0;
            cursor: pointer;
            transition: all 0.3s;
        }
        
        .month-card:hover {
            transform: translateY(-5px);
            box-shadow: 0 8px 25px rgba(102, 126, 234, 0.3);
            border-color: #667eea;
        }
        
        .month-header {
            display: flex;
            justify-content: space-between;
            align-items: center;
            margin-bottom: 15px;
            padding-bottom: 10px;
            border-bottom: 2px solid #f0f0f0;
        }
        
        .month-name {
            font-size: 1.2em;
            font-weight: bold;
            color: #333;
        }
        
        .month-total {
            background: #e8f5e9;
            color: #2e7d32;
            padding: 5px 10px;
            border-radius: 20px;
            font-size: 0.9em;
            font-weight: bold;
        }
        
        .month-bills {
            min-height: 100px;
        }
        
        .bill-item {
            background: #f8f9fa;
            border-radius: 8px;
            padding: 8px 10px;
            margin-bottom: 6px;
            display: flex;
            justify-content: space-between;
            align-items: center;
            font-size: 0.9em;
            border-left: 3px solid #667eea;
            transition: all 0.2s;
        }
        
        .bill-item:hover {
            background: #f0f0f0;
        }
        
        .bill-item.paid {
            opacity: 0.6;
            border-left-color: #4caf50;
            background: #f1f8e9;
        }
        
        .bill-item.paid .bill-amount {
            text-decoration: line-through;
            color: #666;
        }
        
        .bill-info {
            display: flex;
            flex-direction: column;
            gap: 2px;
        }
        
        .bill-name {
            font-weight: 600;
            color: #333;
        }
        
        .bill-date {
            font-size: 0.75em;
            color: #666;
        }
        
        .bill-amount {
            font-weight: bold;
            color: #2e7d32;
        }
        
        .no-bills {
            color: #999;
            font-style: italic;
            text-align: center;
            padding: 15px;
            font-size: 0.9em;
        }
        
        .accounts-section {
            background: #f8f9fa;
            border-radius: 15px;
            padding: 20px;
            margin-top: 20px;
        }
        
        .section-header {
            display: flex;
            justify-content: space-between;
            align-items: center;
            margin-bottom: 20px;
        }
        
        .section-header h2 {
            color: #333;
            font-size: 1.5em;
        }
        
        .accounts-grid {
            display: grid;
            grid-template-columns: repeat(auto-fill, minmax(300px, 1fr));
            gap: 15px;
        }
        
        .account-card {
            background: white;
            border-radius: 10px;
            padding: 15px;
            box-shadow: 0 2px 10px rgba(0,0,0,0.1);
            border-left: 4px solid #667eea;
        }
        
        .account-header {
            display: flex;
            justify-content: space-between;
            align-items: start;
            margin-bottom: 10px;
        }
        
        .account-name {
            font-size: 1.1em;
            font-weight: bold;
            color: #333;
        }
        
        .account-category {
            background: #e3f2fd;
            color: #1976d2;
            padding: 2px 8px;
            border-radius: 15px;
            font-size: 0.75em;
        }
        
        .account-details {
            display: flex;
            justify-content: space-between;
            margin-bottom: 10px;
            font-size: 0.9em;
        }
        
        .account-amount {
            color: #2e7d32;
            font-weight: bold;
        }
        
        .account-due {
            color: #666;
        }
        
        .account-actions {
            display: flex;
            gap: 10px;
            justify-content: flex-end;
            border-top: 1px solid #eee;
            padding-top: 10px;
        }
        
        .edit-btn, .delete-btn {
            background: none;
            border: none;
            cursor: pointer;
            font-size: 0.9em;
            padding: 5px 10px;
            border-radius: 5px;
            transition: all 0.2s;
        }
        
        .edit-btn {
            color: #1976d2;
            background: #e3f2fd;
        }
        
        .edit-btn:hover {
            background: #bbdefb;
        }
        
        .delete-btn {
            color: #d32f2f;
            background: #ffebee;
        }
        
        .delete-btn:hover {
            background: #ffcdd2;
        }
        
        /* Modal Styles */
        .modal {
            display: none;
            position: fixed;
            top: 0;
            left: 0;
            width: 100%;
            height: 100%;
            background: rgba(0,0,0,0.5);
            justify-content: center;
            align-items: center;
            z-index: 1000;
        }
        
        .modal.active {
            display: flex;
        }
        
        .modal-content {
            background: white;
            border-radius: 20px;
            padding: 30px;
            width: 90%;
            max-width: 500px;
            max-height: 90vh;
            overflow-y: auto;
        }
        
        .modal-header {
            display: flex;
            justify-content: space-between;
            align-items: center;
            margin-bottom: 20px;
        }
        
        .modal-header h2 {
            color: #333;
        }
        
        .close-modal {
            background: none;
            border: none;
            font-size: 24px;
            cursor: pointer;
            color: #666;
        }
        
        .form-group {
            margin-bottom: 20px;
        }
        
        .form-group label {
            display: block;
            margin-bottom: 5px;
            color: #333;
            font-weight: 500;
        }
        
        .form-group input,
        .form-group select {
            width: 100%;
            padding: 12px;
            border: 2px solid #e0e0e0;
            border-radius: 8px;
            font-size: 1em;
            transition: border-color 0.2s;
        }
        
        .form-group input:focus,
        .form-group select:focus {
            outline: none;
            border-color: #667eea;
        }
        
        .form-row {
            display: grid;
            grid-template-columns: 1fr 1fr;
            gap: 15px;
        }
        
        .modal-actions {
            display: flex;
            justify-content: flex-end;
            gap: 15px;
            margin-top: 30px;
        }
        
        .btn-primary, .btn-secondary, .btn-danger {
            padding: 12px 24px;
            border: none;
            border-radius: 8px;
            font-size: 1em;
            cursor: pointer;
            transition: all 0.2s;
        }
        
        .btn-primary {
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
        }
        
        .btn-primary:hover {
            transform: translateY(-2px);
            box-shadow: 0 5px 15px rgba(102, 126, 234, 0.4);
        }
        
        .btn-secondary {
            background: #f0f0f0;
            color: #333;
        }
        
        .btn-secondary:hover {
            background: #e0e0e0;
        }
        
        .btn-danger {
            background: #ff4444;
            color: white;
        }
        
        .btn-danger:hover {
            background: #cc0000;
        }
        
        /* Month View Modal */
        .month-view-modal .modal-content {
            max-width: 900px;
        }
        
        .month-days-grid {
            display: grid;
            grid-template-columns: repeat(7, 1fr);
            gap: 10px;
            margin-top: 20px;
        }
        
        .day-cell {
            background: #f8f9fa;
            border-radius: 10px;
            padding: 10px;
            min-height: 100px;
            border: 1px solid #e0e0e0;
        }
        
        .day-header {
            font-weight: bold;
            color: #667eea;
            margin-bottom: 5px;
            text-align: center;
        }
        
        .day-number {
            font-size: 0.9em;
            color: #666;
            margin-bottom: 5px;
            font-weight: bold;
        }
        
        .day-bills {
            display: flex;
            flex-direction: column;
            gap: 3px;
        }
        
        .day-bill {
            background: white;
            border-radius: 4px;
            padding: 3px 6px;
            font-size: 0.75em;
            border-left: 2px solid #667eea;
            cursor: pointer;
            transition: all 0.2s;
            margin-bottom: 2px;
        }
        
        .day-bill:hover {
            background: #e3f2fd;
        }
        
        .day-bill.paid {
            border-left-color: #4caf50;
            opacity: 0.7;
            background: #f1f8e9;
        }
        
        .weekday-header {
            text-align: center;
            font-weight: bold;
            color: #333;
            padding: 5px;
            background: #f0f0f0;
            border-radius: 5px;
        }
        
        @media (max-width: 1024px) {
            .calendar-grid {
                grid-template-columns: repeat(2, 1fr);
            }
        }
        
        @media (max-width: 768px) {
            .calendar-grid {
                grid-template-columns: 1fr;
            }
            
            .container {
                padding: 15px;
            }
            
            h1 {
                font-size: 2em;
            }
        }
    </style>
</head>
<body>
    <div class="container">
        <header>
            <div>
                <h1>🍽️ <span>Edible</span> Bill Payment Calendar</h1>
            </div>
            <div class="year-selector">
                <button class="year-btn" onclick="changeYear(-1)">←</button>
                <span class="current-year" id="currentYear">2026</span>
                <button class="year-btn" onclick="changeYear(1)">→</button>
            </div>
            <button class="add-account-btn" onclick="openAddAccountModal()">
                + Add Account
            </button>
        </header>

        <!-- Stats Bar -->
        <div class="stats-bar">
            <div class="stat-card">
                <h3>Total Accounts</h3>
                <div class="number" id="totalAccounts">0</div>
            </div>
            <div class="stat-card">
                <h3>Monthly Average</h3>
                <div class="number" id="monthlyAverage">$0</div>
            </div>
            <div class="stat-card">
                <h3>Paid This Month</h3>
                <div class="number" id="paidThisMonth">0</div>
            </div>
            <div class="stat-card">
                <h3>Upcoming</h3>
                <div class="number" id="upcomingCount">0</div>
            </div>
        </div>

        <!-- Calendar Grid -->
        <div class="calendar-grid" id="calendarGrid"></div>

        <!-- Accounts Section -->
        <div class="accounts-section">
            <div class="section-header">
                <h2>Your Accounts</h2>
            </div>
            <div class="accounts-grid" id="accountsList"></div>
        </div>
    </div>

    <!-- Account Modal -->
    <div class="modal" id="accountModal">
        <div class="modal-content">
            <div class="modal-header">
                <h2 id="modalTitle">Add Account</h2>
                <button class="close-modal" onclick="closeAccountModal()">&times;</button>
            </div>
            <form id="accountForm" onsubmit="event.preventDefault(); saveAccount();">
                <input type="hidden" id="accountId">
                <div class="form-group">
                    <label for="accountName">Account Name</label>
                    <input type="text" id="accountName" required placeholder="e.g., Rent, Internet">
                </div>
                <div class="form-row">
                    <div class="form-group">
                        <label for="accountAmount">Amount ($)</label>
                        <input type="number" id="accountAmount" required min="0" step="0.01" placeholder="0.00">
                    </div>
                    <div class="form-group">
                        <label for="accountDueDay">Due Day (1-31)</label>
                        <input type="number" id="accountDueDay" required min="1" max="31" placeholder="1">
                    </div>
                </div>
                <div class="form-group">
                    <label for="accountCategory">Category</label>
                    <select id="accountCategory" required>
                        <option value="Rent/Mortgage">Rent/Mortgage</option>
                        <option value="Utilities">Utilities</option>
                        <option value="Internet">Internet</option>
                        <option value="Phone">Phone</option>
                        <option value="Insurance">Insurance</option>
                        <option value="Subscriptions">Subscriptions</option>
                        <option value="Other">Other</option>
                    </select>
                </div>
                <div class="modal-actions">
                    <button type="button" class="btn-danger" id="deleteAccountBtn" onclick="deleteCurrentAccount()" style="display:none">Delete</button>
                    <button type="button" class="btn-secondary" onclick="closeAccountModal()">Cancel</button>
                    <button type="submit" class="btn-primary">Save</button>
                </div>
            </form>
        </div>
    </div>

    <!-- Month View Modal -->
    <div class="modal month-view-modal" id="monthViewModal">
        <div class="modal-content">
            <div class="modal-header">
                <h2 id="monthViewTitle">Month View</h2>
                <button class="close-modal" onclick="closeMonthViewModal()">&times;</button>
            </div>
            <div id="monthViewContent"></div>
        </div>
    </div>

    <!-- Edit Bill Modal -->
    <div class="modal" id="editBillModal">
        <div class="modal-content">
            <div class="modal-header">
                <h2>Edit Bill</h2>
                <button class="close-modal" onclick="closeEditBillModal()">&times;</button>
            </div>
            <form id="editBillForm" onsubmit="event.preventDefault(); saveBillEdit();">
                <input type="hidden" id="editBillKey">
                <input type="hidden" id="editBillAccountId">
                <input type="hidden" id="editBillMonth">
                <input type="hidden" id="editBillYear">
                
                <div class="form-group">
                    <label for="editBillName">Account Name</label>
                    <input type="text" id="editBillName" readonly>
                </div>
                
                <div class="form-row">
                    <div class="form-group">
                        <label for="editBillAmount">Amount ($)</label>
                        <input type="number" id="editBillAmount" required min="0" step="0.01">
                    </div>
                    <div class="form-group">
                        <label for="editBillDay">Due Day</label>
                        <input type="number" id="editBillDay" required min="1" max="31">
                    </div>
                </div>
                
                <div class="form-group">
                    <label for="editBillPaid">Status</label>
                    <select id="editBillPaid">
                        <option value="false">Unpaid</option>
                        <option value="true">Paid</option>
                    </select>
                </div>
                
                <div class="modal-actions">
                    <button type="button" class="btn-secondary" onclick="closeEditBillModal()">Cancel</button>
                    <button type="submit" class="btn-primary">Save Changes</button>
                </div>
            </form>
        </div>
    </div>

    <script>
        // Data Storage
        let accounts = [];
        let payments = {}; // Track paid status and amount overrides: { "accountId-month-year": { paid: boolean, amount: number } }
        let currentYear = 2026;
        
        // Load from localStorage
        function loadData() {
            const saved = localStorage.getItem('edibleBillCalendar');
            if (saved) {
                const data = JSON.parse(saved);
                accounts = data.accounts || [];
                payments = data.payments || {};
            } else {
                // Sample data
                accounts = [
                    { id: '1', name: 'Rent', amount: 2500, dueDay: 1, category: 'Rent/Mortgage' },
                    { id: '2', name: 'Internet', amount: 85, dueDay: 15, category: 'Internet' },
                    { id: '3', name: 'Electricity', amount: 150, dueDay: 10, category: 'Utilities' },
                    { id: '4', name: 'Netflix', amount: 15.99, dueDay: 20, category: 'Subscriptions' },
                    { id: '5', name: 'Phone', amount: 89, dueDay: 25, category: 'Phone' },
                    { id: '6', name: 'Car Insurance', amount: 120, dueDay: 5, category: 'Insurance' }
                ];
                payments = {};
            }
        }
        
        // Save to localStorage
        function saveData() {
            localStorage.setItem('edibleBillCalendar', JSON.stringify({
                accounts: accounts,
                payments: payments
            }));
        }
        
        // Month names
        const monthNames = [
            'January', 'February', 'March', 'April', 'May', 'June',
            'July', 'August', 'September', 'October', 'November', 'December'
        ];
        
        // Get payment key
        function getPaymentKey(accountId, month, year) {
            return `${accountId}-${month}-${year}`;
        }
        
        // Get bill amount (respecting overrides)
        function getBillAmount(account, month, year) {
            const key = getPaymentKey(account.id, month, year);
            if (payments[key] && payments[key].amount) {
                return payments[key].amount;
            }
            return account.amount;
        }
        
        // Get paid status
        function isBillPaid(accountId, month, year) {
            const key = getPaymentKey(accountId, month, year);
            return payments[key] ? payments[key].paid || false : false;
        }
        
        // Set paid status
        function setBillPaid(accountId, month, year, paid) {
            const key = getPaymentKey(accountId, month, year);
            if (!payments[key]) {
                payments[key] = {};
            }
            payments[key].paid = paid;
            saveData();
        }
        
        // Set bill amount override
        function setBillAmount(accountId, month, year, amount) {
            const key = getPaymentKey(accountId, month, year);
            if (!payments[key]) {
                payments[key] = {};
            }
            payments[key].amount = amount;
            saveData();
        }
        
        // Update stats
        function updateStats() {
            document.getElementById('totalAccounts').textContent = accounts.length;
            
            // Calculate monthly average
            if (accounts.length > 0) {
                const total = accounts.reduce((sum, acc) => sum + acc.amount, 0);
                document.getElementById('monthlyAverage').textContent = `$${(total / accounts.length).toFixed(2)}`;
            }
            
            // Calculate paid this month
            const currentMonth = new Date().getMonth();
            let paidCount = 0;
            accounts.forEach(account => {
                if (isBillPaid(account.id, currentMonth, currentYear)) {
                    paidCount++;
                }
            });
            document.getElementById('paidThisMonth').textContent = paidCount;
            
            // Calculate upcoming (next 7 days)
            const today = new Date();
            const todayDay = today.getDate();
            const todayMonth = today.getMonth();
            let upcoming = 0;
            
            accounts.forEach(account => {
                if (!isBillPaid(account.id, todayMonth, currentYear)) {
                    if (account.dueDay >= todayDay && account.dueDay <= todayDay + 7) {
                        upcoming++;
                    }
                }
            });
            document.getElementById('upcomingCount').textContent = upcoming;
        }
        
        // Render calendar
        function renderCalendar() {
            const grid = document.getElementById('calendarGrid');
            
            grid.innerHTML = monthNames.map((month, index) => {
                const monthBills = accounts.map(account => ({
                    ...account,
                    amount: getBillAmount(account, index, currentYear),
                    paid: isBillPaid(account.id, index, currentYear)
                })).sort((a, b) => a.dueDay - b.dueDay);
                
                const total = monthBills.reduce((sum, bill) => sum + bill.amount, 0);
                const unpaidTotal = monthBills.filter(b => !b.paid).reduce((sum, bill) => sum + bill.amount, 0);
                
                return `
                    <div class="month-card" onclick="openMonthView(${index}, ${currentYear})">
                        <div class="month-header">
                            <span class="month-name">${month}</span>
                            <span class="month-total">$${unpaidTotal.toFixed(2)}</span>
                        </div>
                        <div class="month-bills">
                            ${monthBills.slice(0, 3).map(bill => `
                                <div class="bill-item ${bill.paid ? 'paid' : ''}" onclick="event.stopPropagation(); openEditBillModal('${bill.id}', '${bill.name}', ${bill.amount}, ${bill.dueDay}, ${index}, ${currentYear}, ${bill.paid})">
                                    <div class="bill-info">
                                        <span class="bill-name">${bill.name}</span>
                                        <span class="bill-date">Due: ${bill.dueDay}</span>
                                    </div>
                                    <span class="bill-amount">$${bill.amount.toFixed(2)}</span>
                                </div>
                            `).join('')}
                            ${monthBills.length > 3 ? `<div class="bill-item" style="justify-content: center; color: #667eea;">+${monthBills.length - 3} more</div>` : ''}
                            ${monthBills.length === 0 ? '<div class="no-bills">No bills</div>' : ''}
                        </div>
                    </div>
                `;
            }).join('');
            
            updateStats();
        }
        
        // Render accounts list
        function renderAccountsList() {
            const list = document.getElementById('accountsList');
            
            if (accounts.length === 0) {
                list.innerHTML = '<div class="no-bills">No accounts yet. Click "Add Account" to get started.</div>';
                return;
            }
            
            list.innerHTML = accounts.map(account => `
                <div class="account-card">
                    <div class="account-header">
                        <span class="account-name">${account.name}</span>
                        <span class="account-category">${account.category}</span>
                    </div>
                    <div class="account-details">
                        <span class="account-amount">$${account.amount.toFixed(2)}</span>
                        <span class="account-due">Due: ${getOrdinal(account.dueDay)}</span>
                    </div>
                    <div class="account-actions">
                        <button class="edit-btn" onclick="editAccount('${account.id}')">✏️ Edit</button>
                        <button class="delete-btn" onclick="deleteAccount('${account.id}')">🗑️ Delete</button>
                    </div>
                </div>
            `).join('');
        }
        
        // Helper: Get ordinal
        function getOrdinal(n) {
            const s = ['th', 'st', 'nd', 'rd'];
            const v = n % 100;
            return n + (s[(v - 20) % 10] || s[v] || s[0]);
        }
        
        // Change year
        function changeYear(delta) {
            currentYear += delta;
            document.getElementById('currentYear').textContent = currentYear;
            renderCalendar();
        }
        
        // Account Modal functions
        function openAddAccountModal() {
            document.getElementById('modalTitle').textContent = 'Add Account';
            document.getElementById('accountForm').reset();
            document.getElementById('accountId').value = '';
            document.getElementById('deleteAccountBtn').style.display = 'none';
            document.getElementById('accountModal').classList.add('active');
        }
        
        function closeAccountModal() {
            document.getElementById('accountModal').classList.remove('active');
        }
        
        function editAccount(id) {
            const account = accounts.find(a => a.id === id);
            if (!account) return;
            
            document.getElementById('modalTitle').textContent = 'Edit Account';
            document.getElementById('accountId').value = account.id;
            document.getElementById('accountName').value = account.name;
            document.getElementById('accountAmount').value = account.amount;
            document.getElementById('accountDueDay').value = account.dueDay;
            document.getElementById('accountCategory').value = account.category;
            document.getElementById('deleteAccountBtn').style.display = 'block';
            document.getElementById('accountModal').classList.add('active');
        }
        
        function saveAccount() {
            const id = document.getElementById('accountId').value;
            const name = document.getElementById('accountName').value;
            const amount = parseFloat(document.getElementById('accountAmount').value);
            const dueDay = parseInt(document.getElementById('accountDueDay').value);
            const category = document.getElementById('accountCategory').value;
            
            if (id) {
                // Update existing
                const index = accounts.findIndex(a => a.id === id);
                if (index !== -1) {
                    accounts[index] = { ...accounts[index], name, amount, dueDay, category };
                }
            } else {
                // Add new
                accounts.push({
                    id: Date.now().toString(),
                    name,
                    amount,
                    dueDay,
                    category
                });
            }
            
            saveData();
            renderAccountsList();
            renderCalendar();
            closeAccountModal();
        }
        
        function deleteAccount(id) {
            if (confirm('Delete this account? This will remove all payment history.')) {
                accounts = accounts.filter(a => a.id !== id);
                
                // Clean up payments
                Object.keys(payments).forEach(key => {
                    if (key.startsWith(id + '-')) {
                        delete payments[key];
                    }
                });
                
                saveData();
                renderAccountsList();
                renderCalendar();
            }
        }
        
        function deleteCurrentAccount() {
            const id = document.getElementById('accountId').value;
            if (id) {
                deleteAccount(id);
                closeAccountModal();
            }
        }
        
        // Month View functions
        function openMonthView(month, year) {
            const monthName = monthNames[month];
            document.getElementById('monthViewTitle').textContent = `${monthName} ${year}`;
            
            const daysInMonth = new Date(year, month + 1, 0).getDate();
            const firstDay = new Date(year, month, 1).getDay();
            
            let html = '<div class="month-days-grid">';
            
            // Weekday headers
            const weekdays = ['Sun', 'Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat'];
            weekdays.forEach(day => {
                html += `<div class="weekday-header">${day}</div>`;
            });
            
            // Empty cells
            for (let i = 0; i < firstDay; i++) {
                html += '<div class="day-cell"></div>';
            }
            
            // Days
            for (let d = 1; d <= daysInMonth; d++) {
                const dayBills = accounts
                    .filter(a => a.dueDay === d)
                    .map(account => ({
                        ...account,
                        amount: getBillAmount(account, month, year),
                        paid: isBillPaid(account.id, month, year)
                    }));
                
                html += `
                    <div class="day-cell">
                        <div class="day-number">${d}</div>
                        <div class="day-bills">
                            ${dayBills.map(bill => `
                                <div class="day-bill ${bill.paid ? 'paid' : ''}" 
                                     onclick="openEditBillModal('${bill.id}', '${bill.name}', ${bill.amount}, ${bill.dueDay}, ${month}, ${year}, ${bill.paid})">
                                    ${bill.name}: $${bill.amount.toFixed(2)}
                                </div>
                            `).join('')}
                        </div>
                    </div>
                `;
            }
            
            html += '</div>';
            document.getElementById('monthViewContent').innerHTML = html;
            document.getElementById('monthViewModal').classList.add('active');
        }
        
        function closeMonthViewModal() {
            document.getElementById('monthViewModal').classList.remove('active');
        }
        
        // Edit Bill Modal functions
        function openEditBillModal(accountId, name, amount, dueDay, month, year, paid) {
            document.getElementById('editBillKey').value = getPaymentKey(accountId, month, year);
            document.getElementById('editBillAccountId').value = accountId;
            document.getElementById('editBillMonth').value = month;
            document.getElementById('editBillYear').value = year;
            document.getElementById('editBillName').value = name;
            document.getElementById('editBillAmount').value = amount;
            document.getElementById('editBillDay').value = dueDay;
            document.getElementById('editBillPaid').value = paid;
            
            document.getElementById('editBillModal').classList.add('active');
        }
        
        function closeEditBillModal() {
            document.getElementById('editBillModal').classList.remove('active');
        }
        
        function saveBillEdit() {
            const key = document.getElementById('editBillKey').value;
            const accountId = document.getElementById('editBillAccountId').value;
            const month = parseInt(document.getElementById('editBillMonth').value);
            const year = parseInt(document.getElementById('editBillYear').value);
            const amount = parseFloat(document.getElementById('editBillAmount').value);
            const paid = document.getElementById('editBillPaid').value === 'true';
            
            // Save payment data
            if (!payments[key]) {
                payments[key] = {};
            }
            
            // Check if amount is different from default
            const account = accounts.find(a => a.id === accountId);
            if (account && Math.abs(account.amount - amount) > 0.01) {
                payments[key].amount = amount;
            } else {
                delete payments[key].amount;
            }
            
            payments[key].paid = paid;
            
            // Clean up if empty
            if (Object.keys(payments[key]).length === 0) {
                delete payments[key];
            }
            
            saveData();
            renderCalendar();
            
            // Refresh month view if open
            if (document.getElementById('monthViewModal').classList.contains('active')) {
                openMonthView(month, year);
            }
            
            closeEditBillModal();
        }
        
        // Initialize
        loadData();
        renderAccountsList();
        renderCalendar();
    </script>
</body>
</html>
