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
        
        .year-display {
            font-size: 1.2em;
            color: #666;
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
        
        .accounts-list-section {
            background: #f8f9fa;
            border-radius: 15px;
            padding: 20px;
            margin-bottom: 30px;
        }
        
        .section-title {
            display: flex;
            justify-content: space-between;
            align-items: center;
            margin-bottom: 15px;
        }
        
        .section-title h2 {
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
            display: flex;
            justify-content: space-between;
            align-items: center;
            transition: all 0.2s;
            border-left: 4px solid #667eea;
        }
        
        .account-card:hover {
            transform: translateX(5px);
            box-shadow: 0 5px 15px rgba(0,0,0,0.15);
        }
        
        .account-info h3 {
            color: #333;
            margin-bottom: 5px;
        }
        
        .account-details {
            color: #666;
            font-size: 0.9em;
        }
        
        .account-details span {
            margin-right: 15px;
        }
        
        .account-actions {
            display: flex;
            gap: 10px;
        }
        
        .edit-btn, .delete-btn {
            background: none;
            border: none;
            cursor: pointer;
            font-size: 1.2em;
            padding: 5px;
            border-radius: 5px;
            transition: background 0.2s;
        }
        
        .edit-btn:hover {
            background: #e3f2fd;
        }
        
        .delete-btn:hover {
            background: #ffebee;
        }
        
        .calendar-grid {
            display: grid;
            grid-template-columns: repeat(3, 1fr);
            gap: 20px;
            margin-top: 20px;
        }
        
        .month-card {
            background: white;
            border-radius: 15px;
            padding: 15px;
            box-shadow: 0 4px 15px rgba(0,0,0,0.1);
            border: 1px solid #e0e0e0;
            transition: transform 0.2s;
            cursor: pointer;
        }
        
        .month-card:hover {
            transform: scale(1.02);
            box-shadow: 0 8px 25px rgba(102, 126, 234, 0.2);
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
            font-size: 1.3em;
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
            padding: 8px 12px;
            margin-bottom: 8px;
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
            font-size: 0.8em;
            color: #666;
        }
        
        .bill-amount {
            font-weight: bold;
            color: #2e7d32;
        }
        
        .bill-actions {
            display: flex;
            gap: 5px;
        }
        
        .bill-paid-toggle {
            width: 20px;
            height: 20px;
            border-radius: 4px;
            border: 2px solid #667eea;
            cursor: pointer;
            display: flex;
            align-items: center;
            justify-content: center;
            background: white;
            transition: all 0.2s;
        }
        
        .bill-paid-toggle.checked {
            background: #4caf50;
            border-color: #4caf50;
            color: white;
        }
        
        .bill-paid-toggle.checked::after {
            content: "✓";
            font-size: 14px;
        }
        
        .no-bills {
            color: #999;
            font-style: italic;
            text-align: center;
            padding: 15px;
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
            position: relative;
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
            padding: 10px;
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
        
        .btn-primary,
        .btn-secondary {
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
            padding: 12px 24px;
            border: none;
            border-radius: 8px;
            font-size: 1em;
            cursor: pointer;
            transition: all 0.2s;
        }
        
        .btn-danger:hover {
            background: #cc0000;
        }
        
        .month-view-modal .modal-content {
            max-width: 800px;
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
            font-size: 0.8em;
            border-left: 2px solid #667eea;
            cursor: pointer;
            transition: all 0.2s;
        }
        
        .day-bill:hover {
            background: #e3f2fd;
        }
        
        .day-bill.paid {
            border-left-color: #4caf50;
            opacity: 0.7;
        }
        
        .weekday-header {
            text-align: center;
            font-weight: bold;
            color: #333;
            padding: 5px;
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
                <h1>🍽️ <span>Edible</span> Bill Calendar</h1>
                <div class="year-display">2026 Financial Year</div>
            </div>
            <button class="add-account-btn" onclick="openAddAccountModal()">
                + Add New Account
            </button>
        </header>
        
        <!-- Accounts List Section -->
        <div class="accounts-list-section">
            <div class="section-title">
                <h2>Your Accounts</h2>
                <span class="account-count" id="accountCount">0 accounts</span>
            </div>
            <div class="accounts-grid" id="accountsList"></div>
        </div>
        
        <!-- Calendar Grid -->
        <div class="calendar-grid" id="calendarGrid"></div>
    </div>
    
    <!-- Add/Edit Account Modal -->
    <div class="modal" id="accountModal">
        <div class="modal-content">
            <div class="modal-header">
                <h2 id="modalTitle">Add New Account</h2>
                <button class="close-modal" onclick="closeAccountModal()">&times;</button>
            </div>
            <form id="accountForm" onsubmit="event.preventDefault(); saveAccount();">
                <input type="hidden" id="accountId">
                <div class="form-group">
                    <label for="accountName">Account Name</label>
                    <input type="text" id="accountName" required placeholder="e.g., Rent, Internet, Netflix">
                </div>
                <div class="form-group">
                    <label for="accountAmount">Amount ($)</label>
                    <input type="number" id="accountAmount" required min="0" step="0.01" placeholder="2500.00">
                </div>
                <div class="form-row">
                    <div class="form-group">
                        <label for="accountDueDay">Due Day (1-31)</label>
                        <input type="number" id="accountDueDay" required min="1" max="31" placeholder="15">
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
                </div>
                <div class="form-group">
                    <label for="accountNotes">Notes (Optional)</label>
                    <input type="text" id="accountNotes" placeholder="Any additional details">
                </div>
                <div class="modal-actions">
                    <button type="button" class="btn-danger" id="deleteAccountBtn" onclick="deleteCurrentAccount()" style="display: none;">Delete Account</button>
                    <div style="flex:1;"></div>
                    <button type="button" class="btn-secondary" onclick="closeAccountModal()">Cancel</button>
                    <button type="submit" class="btn-primary">Save Account</button>
                </div>
            </form>
        </div>
    </div>
    
    <!-- Month Detail View Modal -->
    <div class="modal month-view-modal" id="monthViewModal">
        <div class="modal-content">
            <div class="modal-header">
                <h2 id="monthViewTitle">Month View</h2>
                <button class="close-modal" onclick="closeMonthViewModal()">&times;</button>
            </div>
            <div id="monthViewContent"></div>
        </div>
    </div>
    
    <!-- Edit Bill Instance Modal -->
    <div class="modal" id="editBillModal">
        <div class="modal-content">
            <div class="modal-header">
                <h2>Edit Bill</h2>
                <button class="close-modal" onclick="closeEditBillModal()">&times;</button>
            </div>
            <form id="editBillForm" onsubmit="event.preventDefault(); saveBillEdit();">
                <input type="hidden" id="editBillId">
                <input type="hidden" id="editBillAccountId">
                <input type="hidden" id="editBillMonth">
                <input type="hidden" id="editBillYear">
                <div class="form-group">
                    <label for="editBillName">Bill Name</label>
                    <input type="text" id="editBillName" required readonly>
                </div>
                <div class="form-group">
                    <label for="editBillAmount">Amount ($)</label>
                    <input type="number" id="editBillAmount" required min="0" step="0.01">
                </div>
                <div class="form-row">
                    <div class="form-group">
                        <label for="editBillDay">Due Date</label>
                        <input type="number" id="editBillDay" required min="1" max="31">
                    </div>
                    <div class="form-group">
                        <label for="editBillStatus">Status</label>
                        <select id="editBillStatus">
                            <option value="unpaid">Unpaid</option>
                            <option value="paid">Paid</option>
                        </select>
                    </div>
                </div>
                <div class="form-group">
                    <label for="editBillNotes">Notes</label>
                    <input type="text" id="editBillNotes">
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
        let paidBills = {}; // Track paid status: { "accountId-month-year": true/false }
        let billOverrides = {}; // Track amount overrides: { "accountId-month-year": amount }
        
        // Load from localStorage
        function loadData() {
            const saved = localStorage.getItem('edibleBillCalendar');
            if (saved) {
                const data = JSON.parse(saved);
                accounts = data.accounts || [];
                paidBills = data.paidBills || {};
                billOverrides = data.billOverrides || {};
            } else {
                // Default sample data
                accounts = [
                    { id: '1', name: 'Rent', amount: 2500, dueDay: 1, category: 'Rent/Mortgage', notes: 'Apartment rent' },
                    { id: '2', name: 'Internet', amount: 85, dueDay: 15, category: 'Internet', notes: 'Spectrum' },
                    { id: '3', name: 'Electricity', amount: 150, dueDay: 10, category: 'Utilities', notes: 'Average' },
                    { id: '4', name: 'Netflix', amount: 15.99, dueDay: 20, category: 'Subscriptions', notes: 'Premium plan' },
                    { id: '5', name: 'Phone', amount: 89, dueDay: 25, category: 'Phone', notes: 'Verizon' },
                    { id: '6', name: 'Car Insurance', amount: 120, dueDay: 5, category: 'Insurance', notes: 'Progressive' }
                ];
                paidBills = {};
                billOverrides = {};
            }
        }
        
        // Save to localStorage
        function saveData() {
            localStorage.setItem('edibleBillCalendar', JSON.stringify({
                accounts: accounts,
                paidBills: paidBills,
                billOverrides: billOverrides
            }));
        }
        
        // Month names
        const monthNames = [
            'January', 'February', 'March', 'April', 'May', 'June',
            'July', 'August', 'September', 'October', 'November', 'December'
        ];
        
        // Render accounts list
        function renderAccountsList() {
            const list = document.getElementById('accountsList');
            const countSpan = document.getElementById('accountCount');
            
            if (accounts.length === 0) {
                list.innerHTML = '<div class="no-bills">No accounts yet. Click "Add New Account" to get started.</div>';
                countSpan.textContent = '0 accounts';
                return;
            }
            
            list.innerHTML = accounts.map(account => `
                <div class="account-card" data-account-id="${account.id}">
                    <div class="account-info">
                        <h3>${account.name}</h3>
                        <div class="account-details">
                            <span>$${account.amount.toFixed(2)}</span>
                            <span>Due: ${getOrdinal(account.dueDay)}</span>
                            <span>${account.category}</span>
                        </div>
                    </div>
                    <div class="account-actions">
                        <button class="edit-btn" onclick="editAccount('${account.id}')" title="Edit">✏️</button>
                        <button class="delete-btn" onclick="deleteAccount('${account.id}')" title="Delete">🗑️</button>
                    </div>
                </div>
            `).join('');
            
            countSpan.textContent = `${accounts.length} account${accounts.length !== 1 ? 's' : ''}`;
        }
        
        // Get ordinal suffix
        function getOrdinal(n) {
            const s = ['th', 'st', 'nd', 'rd'];
            const v = n % 100;
            return n + (s[(v - 20) % 10] || s[v] || s[0]);
        }
        
        // Render calendar grid
        function renderCalendar() {
            const grid = document.getElementById('calendarGrid');
            const currentYear = 2026;
            
            grid.innerHTML = monthNames.map((month, index) => {
                const monthBills = getBillsForMonth(index, currentYear);
                const total = monthBills.reduce((sum, bill) => sum + bill.amount, 0);
                
                return `
                    <div class="month-card" onclick="openMonthView(${index}, ${currentYear})">
                        <div class="month-header">
                            <span class="month-name">${month}</span>
                            <span class="month-total">$${total.toFixed(2)}</span>
                        </div>
                        <div class="month-bills">
                            ${monthBills.slice(0, 3).map(bill => `
                                <div class="bill-item ${bill.paid ? 'paid' : ''}" onclick="event.stopPropagation(); openEditBillModal('${bill.id}', '${bill.accountId}', ${bill.day}, ${bill.amount}, '${bill.name}', '${bill.notes || ''}', ${index}, ${currentYear}, ${bill.paid})">
                                    <div class="bill-info">
                                        <span class="bill-name">${bill.name}</span>
                                        <span class="bill-date">Due: ${getOrdinal(bill.day)}</span>
                                    </div>
                                    <span class="bill-amount">$${bill.amount.toFixed(2)}</span>
                                </div>
                            `).join('')}
                            ${monthBills.length > 3 ? `<div class="bill-item" style="justify-content: center; color: #667eea;">+${monthBills.length - 3} more...</div>` : ''}
                            ${monthBills.length === 0 ? '<div class="no-bills">No bills this month</div>' : ''}
                        </div>
                    </div>
                `;
            }).join('');
        }
        
        // Get bills for a specific month
        function getBillsForMonth(month, year) {
            const bills = [];
            
            accounts.forEach(account => {
                const key = `${account.id}-${month}-${year}`;
                const isPaid = paidBills[key] || false;
                
                // Check if there's an override for this bill this month
                let amount = account.amount;
                if (billOverrides[key]) {
                    amount = billOverrides[key];
                }
                
                bills.push({
                    id: key,
                    accountId: account.id,
                    name: account.name,
                    amount: amount,
                    day: account.dueDay,
                    paid: isPaid,
                    notes: account.notes,
                    category: account.category
                });
            });
            
            // Sort by due day
            return bills.sort((a, b) => a.day - b.day);
        }
        
        // Account Modal functions
        function openAddAccountModal() {
            document.getElementById('modalTitle').textContent = 'Add New Account';
            document.getElementById('accountForm').reset();
            document.getElementById('accountId').value = '';
            document.getElementById('deleteAccountBtn').style.display = 'none';
            document.getElementById('accountModal').classList.add('active');
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
            document.getElementById('accountNotes').value = account.notes || '';
            document.getElementById('deleteAccountBtn').style.display = 'block';
            document.getElementById('accountModal').classList.add('active');
        }
        
        function closeAccountModal() {
            document.getElementById('accountModal').classList.remove('active');
        }
        
        function saveAccount() {
            const id = document.getElementById('accountId').value;
            const name = document.getElementById('accountName').value;
            const amount = parseFloat(document.getElementById('accountAmount').value);
            const dueDay = parseInt(document.getElementById('accountDueDay').value);
            const category = document.getElementById('accountCategory').value;
            const notes = document.getElementById('accountNotes').value;
            
            if (id) {
                // Update existing
                const index = accounts.findIndex(a => a.id === id);
                if (index !== -1) {
                    accounts[index] = { ...accounts[index], name, amount, dueDay, category, notes };
                }
            } else {
                // Add new
                const newId = Date.now().toString();
                accounts.push({
                    id: newId,
                    name,
                    amount,
                    dueDay,
                    category,
                    notes
                });
            }
            
            saveData();
            renderAccountsList();
            renderCalendar();
            closeAccountModal();
        }
        
        function deleteAccount(id) {
            if (confirm('Are you sure you want to delete this account? This will remove all associated bills.')) {
                accounts = accounts.filter(a => a.id !== id);
                
                // Clean up paidBills and overrides for this account
                Object.keys(paidBills).forEach(key => {
                    if (key.startsWith(id + '-')) {
                        delete paidBills[key];
                    }
                });
                Object.keys(billOverrides).forEach(key => {
                    if (key.startsWith(id + '-')) {
                        delete billOverrides[key];
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
            
            const bills = getBillsForMonth(month, year);
            
            // Create calendar days
            const daysInMonth = new Date(year, month + 1, 0).getDate();
            const firstDay = new Date(year, month, 1).getDay(); // 0 = Sunday
            
            const weekdays = ['Sun', 'Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat'];
            
            let daysHTML = '<div class="month-days-grid">';
            
            // Weekday headers
            weekdays.forEach(day => {
                daysHTML += `<div class="weekday-header">${day}</div>`;
            });
            
            // Empty cells for days before month starts
            for (let i = 0; i < firstDay; i++) {
                daysHTML += '<div class="day-cell"></div>';
            }
            
            // Days of the month
            for (let d = 1; d <= daysInMonth; d++) {
                const dayBills = bills.filter(b => b.day === d);
                
                daysHTML += `
                    <div class="day-cell">
                        <div class="day-number">${d}</div>
                        <div class="day-bills">
                            ${dayBills.map(bill => `
                                <div class="day-bill ${bill.paid ? 'paid' : ''}" onclick="openEditBillModal('${bill.id}', '${bill.accountId}', ${bill.day}, ${bill.amount}, '${bill.name}', '${bill.notes || ''}', ${month}, ${year}, ${bill.paid})">
                                    ${bill.name}: $${bill.amount.toFixed(2)}
                                </div>
                            `).join('')}
                        </div>
                    </div>
                `;
            }
            
            daysHTML += '</div>';
            document.getElementById('monthViewContent').innerHTML = daysHTML;
            document.getElementById('monthViewModal').classList.add('active');
        }
        
        function closeMonthViewModal() {
            document.getElementById('monthViewModal').classList.remove('active');
        }
        
        // Edit Bill Modal functions
        function openEditBillModal(id, accountId, day, amount, name, notes, month, year, paid) {
            document.getElementById('editBillId').value = id;
            document.getElementById('editBillAccountId').value = accountId;
            document.getElementById('editBillMonth').value = month;
            document.getElementById('editBillYear').value = year;
            document.getElementById('editBillName').value = name;
            document.getElementById('editBillAmount').value = amount;
            document.getElementById('editBillDay').value = day;
            document.getElementById('editBillStatus').value = paid ? 'paid' : 'unpaid';
            document.getElementById('editBillNotes').value = notes || '';
            
            document.getElementById('editBillModal').classList.add('active');
        }
        
        function closeEditBillModal() {
            document.getElementById('editBillModal').classList.remove('active');
        }
        
        function saveBillEdit() {
            const id = document.getElementById('editBillId').value;
            const accountId = document.getElementById('editBillAccountId').value;
            const month = document.getElementById('editBillMonth').value;
            const year = document.getElementById('editBillYear').value;
            const amount = parseFloat(document.getElementById('editBillAmount').value);
            const day = parseInt(document.getElementById('editBillDay').value);
            const status = document.getElementById('editBillStatus').value;
            const notes = document.getElementById('editBillNotes').value;
            
            const key = `${accountId}-${month}-${year}`;
            
            // Save override amount if different from default
            const account = accounts.find(a => a.id === accountId);
            if (account && Math.abs(account.amount - amount) > 0.01) {
                billOverrides[key] = amount;
            } else {
                delete billOverrides[key];
            }
            
            // Save paid status
            if (status === 'paid') {
                paidBills[key] = true;
            } else {
                delete paidBills[key];
            }
            
            // Update account notes if changed (this is a bit hacky - in real app you'd want proper instance notes)
            if (account && notes !== account.notes) {
                // For simplicity, we're just storing notes in a separate object
                if (!billOverrides.notes) billOverrides.notes = {};
                if (!billOverrides.notes[key]) billOverrides.notes = { ...billOverrides.notes, [key]: notes };
            }
            
            saveData();
            renderCalendar();
            closeEditBillModal();
            
            // Refresh month view if open
            if (document.getElementById('monthViewModal').classList.contains('active')) {
                openMonthView(parseInt(month), parseInt(year));
            }
        }
        
        // Toggle paid status from calendar
        function togglePaid(accountId, month, year, element, event) {
            event.stopPropagation();
            const key = `${accountId}-${month}-${year}`;
            
            if (paidBills[key]) {
                delete paidBills[key];
            } else {
                paidBills[key] = true;
            }
            
            saveData();
            renderCalendar();
        }
        
        // Initialize
        loadData();
        renderAccountsList();
        renderCalendar();
    </script>
</body>
</html>
