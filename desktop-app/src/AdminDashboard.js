const { ipcRenderer } = require('electron');
const path = require('path');

// Admin Dashboard Class
class AdminDashboard {
  constructor() {
    this.apiBaseURL = 'http://localhost:8005';
    this.token = localStorage.getItem('admin_token');
    this.currentTab = 'overview';
    this.contracts = [];
    this.users = [];
    this.systemStats = null;
    this.auditLogs = [];
    
    this.init();
  }

  async init() {
    this.setupEventListeners();
    this.renderDashboard();
    await this.loadInitialData();
  }

  setupEventListeners() {
    // Tab navigation
    document.addEventListener('click', (e) => {
      if (e.target.classList.contains('tab-button')) {
        this.switchTab(e.target.dataset.tab);
      }
    });

    // Refresh button
    document.addEventListener('click', (e) => {
      if (e.target.id === 'refresh-btn') {
        this.loadInitialData();
      }
    });

    // Emergency controls
    document.addEventListener('click', (e) => {
      if (e.target.id === 'emergency-halt-btn') {
        this.showEmergencyHaltModal();
      }
      if (e.target.id === 'emergency-resume-btn') {
        this.emergencyResumeTrading();
      }
    });

    // Modal controls
    document.addEventListener('click', (e) => {
      if (e.target.classList.contains('modal-close')) {
        this.closeModal(e.target.closest('.modal'));
      }
      if (e.target.classList.contains('modal-backdrop')) {
        this.closeModal(e.target.querySelector('.modal'));
      }
    });

    // Form submissions
    document.addEventListener('submit', (e) => {
      e.preventDefault();
      if (e.target.id === 'create-contract-form') {
        this.createContract(new FormData(e.target));
      }
      if (e.target.id === 'create-user-form') {
        this.createUser(new FormData(e.target));
      }
      if (e.target.id === 'emergency-halt-form') {
        this.emergencyHaltTrading(new FormData(e.target));
      }
    });

    // Window controls
    ipcRenderer.on('window-controls', (event, action) => {
      switch (action) {
        case 'minimize':
          ipcRenderer.send('minimize-window');
          break;
        case 'maximize':
          ipcRenderer.send('maximize-window');
          break;
        case 'close':
          ipcRenderer.send('close-window');
          break;
      }
    });
  }

  renderDashboard() {
    document.body.innerHTML = `
      <div class="admin-dashboard">
        <!-- Header -->
        <header class="dashboard-header">
          <div class="header-left">
            <img src="assets/logo.png" alt="TigerEx" class="logo">
            <h1>TigerEx Admin Dashboard</h1>
          </div>
          <div class="header-right">
            <button id="refresh-btn" class="btn btn-outline">
              <i class="icon-refresh"></i>
              Refresh
            </button>
            <div class="window-controls">
              <button class="window-btn minimize" onclick="ipcRenderer.send('minimize-window')">−</button>
              <button class="window-btn maximize" onclick="ipcRenderer.send('maximize-window')">□</button>
              <button class="window-btn close" onclick="ipcRenderer.send('close-window')">×</button>
            </div>
          </div>
        </header>

        <!-- System Stats -->
        <div class="stats-container" id="stats-container">
          <div class="stat-card">
            <div class="stat-icon">👥</div>
            <div class="stat-content">
              <div class="stat-number" id="total-users">-</div>
              <div class="stat-label">Total Users</div>
              <div class="stat-subtext" id="users-breakdown">-</div>
            </div>
          </div>
          <div class="stat-card">
            <div class="stat-icon">📊</div>
            <div class="stat-content">
              <div class="stat-number" id="total-contracts">-</div>
              <div class="stat-label">Trading Contracts</div>
              <div class="stat-subtext" id="contracts-breakdown">-</div>
            </div>
          </div>
          <div class="stat-card">
            <div class="stat-icon">🛡️</div>
            <div class="stat-content">
              <div class="stat-number" id="total-logs">-</div>
              <div class="stat-label">Audit Logs</div>
              <div class="stat-subtext" id="logs-breakdown">-</div>
            </div>
          </div>
          <div class="stat-card">
            <div class="stat-icon">⚡</div>
            <div class="stat-content">
              <div class="stat-number status-healthy">Healthy</div>
              <div class="stat-label">System Status</div>
              <div class="stat-subtext">All systems operational</div>
            </div>
          </div>
        </div>

        <!-- Emergency Controls -->
        <div class="emergency-controls">
          <div class="emergency-card">
            <div class="emergency-icon">⚠️</div>
            <div class="emergency-content">
              <h3>Emergency Controls</h3>
              <p>System-wide emergency controls for critical situations</p>
            </div>
            <div class="emergency-actions">
              <button id="emergency-halt-btn" class="btn btn-danger">
                <i class="icon-stop"></i>
                Halt All Trading
              </button>
              <button id="emergency-resume-btn" class="btn btn-success">
                <i class="icon-play"></i>
                Resume Trading
              </button>
            </div>
          </div>
        </div>

        <!-- Tab Navigation -->
        <nav class="tab-navigation">
          <button class="tab-button active" data-tab="overview">
            <i class="icon-dashboard"></i>
            Overview
          </button>
          <button class="tab-button" data-tab="contracts">
            <i class="icon-contract"></i>
            Trading Contracts
          </button>
          <button class="tab-button" data-tab="users">
            <i class="icon-users"></i>
            User Management
          </button>
          <button class="tab-button" data-tab="audit">
            <i class="icon-audit"></i>
            Audit Logs
          </button>
        </nav>

        <!-- Tab Content -->
        <main class="tab-content">
          <div id="overview-tab" class="tab-pane active">
            ${this.renderOverviewTab()}
          </div>
          <div id="contracts-tab" class="tab-pane">
            ${this.renderContractsTab()}
          </div>
          <div id="users-tab" class="tab-pane">
            ${this.renderUsersTab()}
          </div>
          <div id="audit-tab" class="tab-pane">
            ${this.renderAuditTab()}
          </div>
        </main>

        <!-- Modals -->
        ${this.renderModals()}
      </div>
    `;

    this.loadStyles();
  }

  renderOverviewTab() {
    return `
      <div class="overview-content">
        <div class="overview-grid">
          <div class="overview-card">
            <h3>System Health</h3>
            <div class="health-items">
              <div class="health-item">
                <span>Database Connection</span>
                <span class="status-badge status-connected">Connected</span>
              </div>
              <div class="health-item">
                <span>Redis Cache</span>
                <span class="status-badge status-connected">Connected</span>
              </div>
              <div class="health-item">
                <span>API Gateway</span>
                <span class="status-badge status-healthy">Healthy</span>
              </div>
              <div class="health-item">
                <span>Trading Engine</span>
                <span class="status-badge status-running">Running</span>
              </div>
            </div>
          </div>
          
          <div class="overview-card">
            <h3>Recent Activity</h3>
            <div class="activity-items" id="recent-activity">
              <div class="activity-item">
                <div class="activity-icon success">✓</div>
                <div class="activity-content">
                  <span>Contract BTC/USDT launched</span>
                  <small>2 minutes ago</small>
                </div>
              </div>
              <div class="activity-item">
                <div class="activity-icon info">+</div>
                <div class="activity-content">
                  <span>New user registered</span>
                  <small>5 minutes ago</small>
                </div>
              </div>
              <div class="activity-item">
                <div class="activity-icon warning">⏸</div>
                <div class="activity-content">
                  <span>Contract ETH/USDT paused</span>
                  <small>10 minutes ago</small>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>
    `;
  }

  renderContractsTab() {
    return `
      <div class="contracts-content">
        <div class="content-header">
          <h2>Trading Contracts</h2>
          <div class="header-actions">
            <button class="btn btn-primary" onclick="adminDashboard.showCreateContractModal()">
              <i class="icon-plus"></i>
              Create Contract
            </button>
          </div>
        </div>
        
        <div class="contracts-table-container">
          <table class="data-table" id="contracts-table">
            <thead>
              <tr>
                <th>Symbol</th>
                <th>Exchange</th>
                <th>Type</th>
                <th>Status</th>
                <th>Fees</th>
                <th>Created</th>
                <th>Actions</th>
              </tr>
            </thead>
            <tbody id="contracts-tbody">
              <tr>
                <td colspan="7" class="loading-cell">Loading contracts...</td>
              </tr>
            </tbody>
          </table>
        </div>
      </div>
    `;
  }

  renderUsersTab() {
    return `
      <div class="users-content">
        <div class="content-header">
          <h2>User Management</h2>
          <div class="header-actions">
            <button class="btn btn-primary" onclick="adminDashboard.showCreateUserModal()">
              <i class="icon-user-plus"></i>
              Create User
            </button>
          </div>
        </div>
        
        <div class="users-table-container">
          <table class="data-table" id="users-table">
            <thead>
              <tr>
                <th>Username</th>
                <th>Email</th>
                <th>Role</th>
                <th>Status</th>
                <th>KYC</th>
                <th>Trading</th>
                <th>Actions</th>
              </tr>
            </thead>
            <tbody id="users-tbody">
              <tr>
                <td colspan="7" class="loading-cell">Loading users...</td>
              </tr>
            </tbody>
          </table>
        </div>
      </div>
    `;
  }

  renderAuditTab() {
    return `
      <div class="audit-content">
        <div class="content-header">
          <h2>Audit Logs</h2>
          <div class="header-actions">
            <select class="form-select" id="audit-filter">
              <option value="">All Actions</option>
              <option value="CREATE">Create</option>
              <option value="LAUNCH">Launch</option>
              <option value="PAUSE">Pause</option>
              <option value="RESUME">Resume</option>
              <option value="DELETE">Delete</option>
              <option value="UPDATE">Update</option>
            </select>
          </div>
        </div>
        
        <div class="audit-table-container">
          <table class="data-table" id="audit-table">
            <thead>
              <tr>
                <th>Timestamp</th>
                <th>Admin</th>
                <th>Action</th>
                <th>Target</th>
                <th>Details</th>
              </tr>
            </thead>
            <tbody id="audit-tbody">
              <tr>
                <td colspan="5" class="loading-cell">Loading audit logs...</td>
              </tr>
            </tbody>
          </table>
        </div>
      </div>
    `;
  }

  renderModals() {
    return `
      <!-- Create Contract Modal -->
      <div class="modal" id="create-contract-modal">
        <div class="modal-backdrop" onclick="adminDashboard.closeModal(this.parentElement)">
          <div class="modal-dialog" onclick="event.stopPropagation()">
            <div class="modal-header">
              <h3>Create Trading Contract</h3>
              <button class="modal-close" onclick="adminDashboard.closeModal(this.closest('.modal'))">&times;</button>
            </div>
            <div class="modal-body">
              <form id="create-contract-form">
                <div class="form-row">
                  <div class="form-group">
                    <label>Exchange</label>
                    <select name="exchange" class="form-select" required>
                      <option value="">Select Exchange</option>
                      <option value="binance">Binance</option>
                      <option value="kucoin">KuCoin</option>
                      <option value="bybit">Bybit</option>
                      <option value="okx">OKX</option>
                      <option value="mexc">MEXC</option>
                      <option value="bitget">Bitget</option>
                      <option value="bitfinex">Bitfinex</option>
                    </select>
                  </div>
                  <div class="form-group">
                    <label>Trading Type</label>
                    <select name="trading_type" class="form-select" required>
                      <option value="">Select Type</option>
                      <option value="spot">Spot</option>
                      <option value="futures_perpetual">Futures Perpetual</option>
                      <option value="futures_cross">Futures Cross</option>
                      <option value="margin">Margin</option>
                      <option value="options">Options</option>
                      <option value="derivatives">Derivatives</option>
                      <option value="copy_trading">Copy Trading</option>
                      <option value="etf">ETF</option>
                    </select>
                  </div>
                </div>
                <div class="form-row">
                  <div class="form-group">
                    <label>Symbol</label>
                    <input type="text" name="symbol" class="form-input" placeholder="BTC/USDT" required>
                  </div>
                  <div class="form-group">
                    <label>Base Asset</label>
                    <input type="text" name="base_asset" class="form-input" placeholder="BTC" required>
                  </div>
                  <div class="form-group">
                    <label>Quote Asset</label>
                    <input type="text" name="quote_asset" class="form-input" placeholder="USDT" required>
                  </div>
                </div>
                <div class="form-row">
                  <div class="form-group">
                    <label>Maker Fee (%)</label>
                    <input type="number" name="maker_fee" class="form-input" step="0.0001" value="0.001" required>
                  </div>
                  <div class="form-group">
                    <label>Taker Fee (%)</label>
                    <input type="number" name="taker_fee" class="form-input" step="0.0001" value="0.001" required>
                  </div>
                </div>
                <div class="modal-actions">
                  <button type="button" class="btn btn-secondary" onclick="adminDashboard.closeModal(this.closest('.modal'))">Cancel</button>
                  <button type="submit" class="btn btn-primary">Create Contract</button>
                </div>
              </form>
            </div>
          </div>
        </div>
      </div>

      <!-- Create User Modal -->
      <div class="modal" id="create-user-modal">
        <div class="modal-backdrop" onclick="adminDashboard.closeModal(this.parentElement)">
          <div class="modal-dialog" onclick="event.stopPropagation()">
            <div class="modal-header">
              <h3>Create User Account</h3>
              <button class="modal-close" onclick="adminDashboard.closeModal(this.closest('.modal'))">&times;</button>
            </div>
            <div class="modal-body">
              <form id="create-user-form">
                <div class="form-group">
                  <label>Email</label>
                  <input type="email" name="email" class="form-input" required>
                </div>
                <div class="form-group">
                  <label>Username</label>
                  <input type="text" name="username" class="form-input" required>
                </div>
                <div class="form-group">
                  <label>Password</label>
                  <input type="password" name="password" class="form-input" required>
                </div>
                <div class="form-group">
                  <label>Full Name</label>
                  <input type="text" name="full_name" class="form-input">
                </div>
                <div class="form-group">
                  <label>Role</label>
                  <select name="role" class="form-select" required>
                    <option value="trader">Trader</option>
                    <option value="moderator">Moderator</option>
                    <option value="admin">Admin</option>
                    <option value="viewer">Viewer</option>
                  </select>
                </div>
                <div class="modal-actions">
                  <button type="button" class="btn btn-secondary" onclick="adminDashboard.closeModal(this.closest('.modal'))">Cancel</button>
                  <button type="submit" class="btn btn-primary">Create User</button>
                </div>
              </form>
            </div>
          </div>
        </div>
      </div>

      <!-- Emergency Halt Modal -->
      <div class="modal" id="emergency-halt-modal">
        <div class="modal-backdrop" onclick="adminDashboard.closeModal(this.parentElement)">
          <div class="modal-dialog emergency-modal" onclick="event.stopPropagation()">
            <div class="modal-header emergency-header">
              <h3>⚠️ Emergency Trading Halt</h3>
              <button class="modal-close" onclick="adminDashboard.closeModal(this.closest('.modal'))">&times;</button>
            </div>
            <div class="modal-body">
              <div class="emergency-warning">
                <p>This will immediately halt all trading activities system-wide. Please provide a reason:</p>
              </div>
              <form id="emergency-halt-form">
                <div class="form-group">
                  <label>Reason for Emergency Halt</label>
                  <textarea name="reason" class="form-textarea" rows="3" placeholder="Enter reason for emergency halt" required></textarea>
                </div>
                <div class="modal-actions">
                  <button type="button" class="btn btn-secondary" onclick="adminDashboard.closeModal(this.closest('.modal'))">Cancel</button>
                  <button type="submit" class="btn btn-danger">CONFIRM HALT</button>
                </div>
              </form>
            </div>
          </div>
        </div>
      </div>
    `;
  }

  loadStyles() {
    const styles = `
      <style>
        * {
          margin: 0;
          padding: 0;
          box-sizing: border-box;
        }

        body {
          font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
          background: #f8fafc;
          color: #1e293b;
          overflow-x: hidden;
        }

        .admin-dashboard {
          min-height: 100vh;
          display: flex;
          flex-direction: column;
        }

        /* Header */
        .dashboard-header {
          background: #ffffff;
          border-bottom: 1px solid #e2e8f0;
          padding: 1rem 2rem;
          display: flex;
          justify-content: space-between;
          align-items: center;
          -webkit-app-region: drag;
        }

        .header-left {
          display: flex;
          align-items: center;
          gap: 1rem;
        }

        .logo {
          width: 32px;
          height: 32px;
        }

        .header-left h1 {
          font-size: 1.5rem;
          font-weight: 700;
          color: #1e293b;
        }

        .header-right {
          display: flex;
          align-items: center;
          gap: 1rem;
          -webkit-app-region: no-drag;
        }

        .window-controls {
          display: flex;
          gap: 0.5rem;
        }

        .window-btn {
          width: 32px;
          height: 32px;
          border: none;
          border-radius: 6px;
          font-size: 14px;
          font-weight: bold;
          cursor: pointer;
          transition: all 0.2s;
        }

        .window-btn.minimize {
          background: #fbbf24;
          color: #92400e;
        }

        .window-btn.maximize {
          background: #34d399;
          color: #065f46;
        }

        .window-btn.close {
          background: #f87171;
          color: #991b1b;
        }

        .window-btn:hover {
          opacity: 0.8;
        }

        /* Stats Container */
        .stats-container {
          display: grid;
          grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
          gap: 1.5rem;
          padding: 2rem;
        }

        .stat-card {
          background: #ffffff;
          border-radius: 12px;
          padding: 1.5rem;
          box-shadow: 0 1px 3px rgba(0, 0, 0, 0.1);
          display: flex;
          align-items: center;
          gap: 1rem;
        }

        .stat-icon {
          font-size: 2rem;
          width: 60px;
          height: 60px;
          display: flex;
          align-items: center;
          justify-content: center;
          background: #f1f5f9;
          border-radius: 12px;
        }

        .stat-content {
          flex: 1;
        }

        .stat-number {
          font-size: 2rem;
          font-weight: 700;
          color: #1e293b;
          margin-bottom: 0.25rem;
        }

        .stat-label {
          font-size: 0.875rem;
          color: #64748b;
          margin-bottom: 0.25rem;
        }

        .stat-subtext {
          font-size: 0.75rem;
          color: #94a3b8;
        }

        .status-healthy {
          color: #059669 !important;
        }

        /* Emergency Controls */
        .emergency-controls {
          padding: 0 2rem 2rem;
        }

        .emergency-card {
          background: #ffffff;
          border: 2px solid #fecaca;
          border-radius: 12px;
          padding: 1.5rem;
          display: flex;
          align-items: center;
          gap: 1.5rem;
        }

        .emergency-icon {
          font-size: 2.5rem;
        }

        .emergency-content {
          flex: 1;
        }

        .emergency-content h3 {
          color: #dc2626;
          margin-bottom: 0.5rem;
        }

        .emergency-content p {
          color: #64748b;
          font-size: 0.875rem;
        }

        .emergency-actions {
          display: flex;
          gap: 1rem;
        }

        /* Tab Navigation */
        .tab-navigation {
          background: #ffffff;
          border-bottom: 1px solid #e2e8f0;
          padding: 0 2rem;
          display: flex;
          gap: 0.5rem;
        }

        .tab-button {
          background: none;
          border: none;
          padding: 1rem 1.5rem;
          cursor: pointer;
          display: flex;
          align-items: center;
          gap: 0.5rem;
          color: #64748b;
          font-weight: 500;
          border-bottom: 2px solid transparent;
          transition: all 0.2s;
        }

        .tab-button:hover {
          color: #3b82f6;
        }

        .tab-button.active {
          color: #3b82f6;
          border-bottom-color: #3b82f6;
        }

        /* Tab Content */
        .tab-content {
          flex: 1;
          padding: 2rem;
        }

        .tab-pane {
          display: none;
        }

        .tab-pane.active {
          display: block;
        }

        /* Overview Tab */
        .overview-grid {
          display: grid;
          grid-template-columns: repeat(auto-fit, minmax(400px, 1fr));
          gap: 2rem;
        }

        .overview-card {
          background: #ffffff;
          border-radius: 12px;
          padding: 1.5rem;
          box-shadow: 0 1px 3px rgba(0, 0, 0, 0.1);
        }

        .overview-card h3 {
          margin-bottom: 1rem;
          color: #1e293b;
        }

        .health-items, .activity-items {
          display: flex;
          flex-direction: column;
          gap: 0.75rem;
        }

        .health-item, .activity-item {
          display: flex;
          justify-content: space-between;
          align-items: center;
          padding: 0.5rem 0;
        }

        .activity-item {
          justify-content: flex-start;
          gap: 1rem;
        }

        .activity-icon {
          width: 32px;
          height: 32px;
          border-radius: 50%;
          display: flex;
          align-items: center;
          justify-content: center;
          font-weight: bold;
          color: white;
        }

        .activity-icon.success {
          background: #059669;
        }

        .activity-icon.info {
          background: #3b82f6;
        }

        .activity-icon.warning {
          background: #f59e0b;
        }

        .activity-content {
          flex: 1;
        }

        .activity-content small {
          display: block;
          color: #64748b;
          font-size: 0.75rem;
        }

        .status-badge {
          padding: 0.25rem 0.75rem;
          border-radius: 9999px;
          font-size: 0.75rem;
          font-weight: 600;
          color: white;
        }

        .status-connected, .status-healthy, .status-running {
          background: #059669;
        }

        /* Content Header */
        .content-header {
          display: flex;
          justify-content: space-between;
          align-items: center;
          margin-bottom: 2rem;
        }

        .content-header h2 {
          font-size: 1.5rem;
          font-weight: 700;
          color: #1e293b;
        }

        .header-actions {
          display: flex;
          gap: 1rem;
          align-items: center;
        }

        /* Data Tables */
        .data-table {
          width: 100%;
          background: #ffffff;
          border-radius: 12px;
          overflow: hidden;
          box-shadow: 0 1px 3px rgba(0, 0, 0, 0.1);
        }

        .data-table th,
        .data-table td {
          padding: 1rem;
          text-align: left;
          border-bottom: 1px solid #e2e8f0;
        }

        .data-table th {
          background: #f8fafc;
          font-weight: 600;
          color: #374151;
        }

        .data-table tbody tr:hover {
          background: #f8fafc;
        }

        .loading-cell {
          text-align: center;
          color: #64748b;
          font-style: italic;
        }

        /* Buttons */
        .btn {
          padding: 0.5rem 1rem;
          border: none;
          border-radius: 6px;
          font-weight: 500;
          cursor: pointer;
          display: inline-flex;
          align-items: center;
          gap: 0.5rem;
          transition: all 0.2s;
          text-decoration: none;
        }

        .btn-primary {
          background: #3b82f6;
          color: white;
        }

        .btn-primary:hover {
          background: #2563eb;
        }

        .btn-secondary {
          background: #6b7280;
          color: white;
        }

        .btn-secondary:hover {
          background: #4b5563;
        }

        .btn-success {
          background: #059669;
          color: white;
        }

        .btn-success:hover {
          background: #047857;
        }

        .btn-danger {
          background: #dc2626;
          color: white;
        }

        .btn-danger:hover {
          background: #b91c1c;
        }

        .btn-outline {
          background: transparent;
          border: 1px solid #d1d5db;
          color: #374151;
        }

        .btn-outline:hover {
          background: #f3f4f6;
        }

        .btn-sm {
          padding: 0.25rem 0.5rem;
          font-size: 0.875rem;
        }

        /* Modals */
        .modal {
          position: fixed;
          top: 0;
          left: 0;
          width: 100%;
          height: 100%;
          background: rgba(0, 0, 0, 0.5);
          display: none;
          align-items: center;
          justify-content: center;
          z-index: 1000;
        }

        .modal.show {
          display: flex;
        }

        .modal-dialog {
          background: #ffffff;
          border-radius: 12px;
          width: 90%;
          max-width: 600px;
          max-height: 90vh;
          overflow-y: auto;
        }

        .modal-header {
          padding: 1.5rem;
          border-bottom: 1px solid #e2e8f0;
          display: flex;
          justify-content: space-between;
          align-items: center;
        }

        .modal-header h3 {
          margin: 0;
          color: #1e293b;
        }

        .modal-close {
          background: none;
          border: none;
          font-size: 1.5rem;
          cursor: pointer;
          color: #64748b;
          padding: 0;
          width: 32px;
          height: 32px;
          display: flex;
          align-items: center;
          justify-content: center;
        }

        .modal-body {
          padding: 1.5rem;
        }

        .modal-actions {
          display: flex;
          gap: 1rem;
          justify-content: flex-end;
          margin-top: 1.5rem;
        }

        .emergency-modal {
          border: 2px solid #fecaca;
        }

        .emergency-header {
          background: #fef2f2;
          border-bottom-color: #fecaca;
        }

        .emergency-warning {
          background: #fef2f2;
          border: 1px solid #fecaca;
          border-radius: 6px;
          padding: 1rem;
          margin-bottom: 1rem;
        }

        .emergency-warning p {
          color: #dc2626;
          margin: 0;
        }

        /* Forms */
        .form-group {
          margin-bottom: 1rem;
        }

        .form-row {
          display: grid;
          grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
          gap: 1rem;
          margin-bottom: 1rem;
        }

        .form-group label {
          display: block;
          margin-bottom: 0.5rem;
          font-weight: 500;
          color: #374151;
        }

        .form-input,
        .form-select,
        .form-textarea {
          width: 100%;
          padding: 0.75rem;
          border: 1px solid #d1d5db;
          border-radius: 6px;
          font-size: 1rem;
          transition: border-color 0.2s;
        }

        .form-input:focus,
        .form-select:focus,
        .form-textarea:focus {
          outline: none;
          border-color: #3b82f6;
          box-shadow: 0 0 0 3px rgba(59, 130, 246, 0.1);
        }

        .form-textarea {
          resize: vertical;
          min-height: 80px;
        }

        /* Action Buttons */
        .action-buttons {
          display: flex;
          gap: 0.5rem;
        }

        /* Status Badges */
        .status-active {
          background: #059669;
        }

        .status-pending {
          background: #f59e0b;
        }

        .status-paused {
          background: #f97316;
        }

        .status-suspended,
        .status-delisted {
          background: #dc2626;
        }

        /* Responsive */
        @media (max-width: 768px) {
          .dashboard-header {
            padding: 1rem;
          }

          .stats-container {
            grid-template-columns: 1fr;
            padding: 1rem;
          }

          .tab-content {
            padding: 1rem;
          }

          .overview-grid {
            grid-template-columns: 1fr;
          }

          .form-row {
            grid-template-columns: 1fr;
          }
        }
      </style>
    `;

    document.head.insertAdjacentHTML('beforeend', styles);
  }

  // API Methods
  async apiRequest(endpoint, options = {}) {
    try {
      const response = await fetch(`${this.apiBaseURL}${endpoint}`, {
        ...options,
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${this.token}`,
          ...options.headers,
        },
      });

      if (!response.ok) {
        throw new Error(`API Error: ${response.statusText}`);
      }

      return await response.json();
    } catch (error) {
      console.error('API Request failed:', error);
      this.showNotification('API request failed: ' + error.message, 'error');
      throw error;
    }
  }

  // Data Loading Methods
  async loadInitialData() {
    try {
      await Promise.all([
        this.loadSystemStats(),
        this.loadContracts(),
        this.loadUsers(),
        this.loadAuditLogs(),
      ]);
    } catch (error) {
      console.error('Failed to load initial data:', error);
    }
  }

  async loadSystemStats() {
    try {
      const stats = await this.apiRequest('/api/admin/statistics');
      this.systemStats = stats;
      this.updateStatsDisplay();
    } catch (error) {
      console.error('Failed to load system stats:', error);
    }
  }

  async loadContracts() {
    try {
      const response = await this.apiRequest('/api/admin/contracts');
      this.contracts = response.contracts;
      this.updateContractsTable();
    } catch (error) {
      console.error('Failed to load contracts:', error);
    }
  }

  async loadUsers() {
    try {
      const response = await this.apiRequest('/api/admin/users');
      this.users = response.users;
      this.updateUsersTable();
    } catch (error) {
      console.error('Failed to load users:', error);
    }
  }

  async loadAuditLogs() {
    try {
      const response = await this.apiRequest('/api/admin/audit-logs');
      this.auditLogs = response.audit_logs;
      this.updateAuditTable();
    } catch (error) {
      console.error('Failed to load audit logs:', error);
    }
  }

  // UI Update Methods
  updateStatsDisplay() {
    if (!this.systemStats) return;

    document.getElementById('total-users').textContent = this.systemStats.users.total;
    document.getElementById('users-breakdown').textContent = 
      `${this.systemStats.users.active} active, ${this.systemStats.users.suspended} suspended`;

    document.getElementById('total-contracts').textContent = this.systemStats.contracts.total;
    document.getElementById('contracts-breakdown').textContent = 
      `${this.systemStats.contracts.active} active, ${this.systemStats.contracts.paused} paused`;

    document.getElementById('total-logs').textContent = this.systemStats.audit.total_logs;
    document.getElementById('logs-breakdown').textContent = 
      `${this.systemStats.audit.recent_actions_24h} in 24h`;
  }

  updateContractsTable() {
    const tbody = document.getElementById('contracts-tbody');
    if (!tbody) return;

    if (this.contracts.length === 0) {
      tbody.innerHTML = '<tr><td colspan="7" class="loading-cell">No contracts found</td></tr>';
      return;
    }

    tbody.innerHTML = this.contracts.map(contract => `
      <tr>
        <td><strong>${contract.symbol}</strong></td>
        <td>${contract.exchange.toUpperCase()}</td>
        <td>${contract.trading_type.replace('_', ' ').toUpperCase()}</td>
        <td><span class="status-badge status-${contract.status}">${contract.status.toUpperCase()}</span></td>
        <td>${contract.maker_fee}% / ${contract.taker_fee}%</td>
        <td>${new Date(contract.created_at).toLocaleDateString()}</td>
        <td>
          <div class="action-buttons">
            ${this.getContractActionButtons(contract)}
          </div>
        </td>
      </tr>
    `).join('');
  }

  updateUsersTable() {
    const tbody = document.getElementById('users-tbody');
    if (!tbody) return;

    if (this.users.length === 0) {
      tbody.innerHTML = '<tr><td colspan="7" class="loading-cell">No users found</td></tr>';
      return;
    }

    tbody.innerHTML = this.users.map(user => `
      <tr>
        <td><strong>${user.username}</strong></td>
        <td>${user.email}</td>
        <td>${user.role.replace('_', ' ').toUpperCase()}</td>
        <td><span class="status-badge status-${user.status}">${user.status.toUpperCase()}</span></td>
        <td>Level ${user.kyc_level}</td>
        <td>${user.trading_enabled ? '✅' : '❌'}</td>
        <td>
          <div class="action-buttons">
            ${this.getUserActionButtons(user)}
          </div>
        </td>
      </tr>
    `).join('');
  }

  updateAuditTable() {
    const tbody = document.getElementById('audit-tbody');
    if (!tbody) return;

    if (this.auditLogs.length === 0) {
      tbody.innerHTML = '<tr><td colspan="5" class="loading-cell">No audit logs found</td></tr>';
      return;
    }

    tbody.innerHTML = this.auditLogs.map(log => `
      <tr>
        <td>${new Date(log.timestamp).toLocaleString()}</td>
        <td>${log.admin_username}</td>
        <td><span class="status-badge status-${log.action.toLowerCase()}">${log.action}</span></td>
        <td>${log.target_type}: ${log.target_id}</td>
        <td><pre style="font-size: 0.75rem; margin: 0;">${JSON.stringify(log.details, null, 2)}</pre></td>
      </tr>
    `).join('');
  }

  getContractActionButtons(contract) {
    let buttons = [];

    if (contract.status === 'pending') {
      buttons.push(`<button class="btn btn-success btn-sm" onclick="adminDashboard.launchContract('${contract.contract_id}')">Launch</button>`);
    }

    if (contract.status === 'active') {
      buttons.push(`<button class="btn btn-secondary btn-sm" onclick="adminDashboard.pauseContract('${contract.contract_id}')">Pause</button>`);
    }

    if (contract.status === 'paused') {
      buttons.push(`<button class="btn btn-success btn-sm" onclick="adminDashboard.resumeContract('${contract.contract_id}')">Resume</button>`);
    }

    buttons.push(`<button class="btn btn-danger btn-sm" onclick="adminDashboard.deleteContract('${contract.contract_id}')">Delete</button>`);

    return buttons.join('');
  }

  getUserActionButtons(user) {
    let buttons = [];

    if (user.status === 'active') {
      buttons.push(`<button class="btn btn-secondary btn-sm" onclick="adminDashboard.suspendUser('${user.user_id}')">Suspend</button>`);
    }

    if (user.status === 'suspended') {
      buttons.push(`<button class="btn btn-success btn-sm" onclick="adminDashboard.activateUser('${user.user_id}')">Activate</button>`);
    }

    return buttons.join('');
  }

  // Navigation Methods
  switchTab(tabName) {
    // Update tab buttons
    document.querySelectorAll('.tab-button').forEach(btn => {
      btn.classList.remove('active');
    });
    document.querySelector(`[data-tab="${tabName}"]`).classList.add('active');

    // Update tab content
    document.querySelectorAll('.tab-pane').forEach(pane => {
      pane.classList.remove('active');
    });
    document.getElementById(`${tabName}-tab`).classList.add('active');

    this.currentTab = tabName;
  }

  // Modal Methods
  showCreateContractModal() {
    document.getElementById('create-contract-modal').classList.add('show');
  }

  showCreateUserModal() {
    document.getElementById('create-user-modal').classList.add('show');
  }

  showEmergencyHaltModal() {
    document.getElementById('emergency-halt-modal').classList.add('show');
  }

  closeModal(modal) {
    modal.classList.remove('show');
  }

  // Contract Management Methods
  async createContract(formData) {
    try {
      const data = {
        exchange: formData.get('exchange'),
        trading_type: formData.get('trading_type'),
        symbol: formData.get('symbol'),
        base_asset: formData.get('base_asset'),
        quote_asset: formData.get('quote_asset'),
        maker_fee: parseFloat(formData.get('maker_fee')),
        taker_fee: parseFloat(formData.get('taker_fee')),
      };

      await this.apiRequest('/api/admin/contracts/create', {
        method: 'POST',
        body: JSON.stringify(data),
      });

      this.showNotification('Contract created successfully', 'success');
      this.closeModal(document.getElementById('create-contract-modal'));
      await this.loadContracts();
    } catch (error) {
      this.showNotification('Failed to create contract', 'error');
    }
  }

  async launchContract(contractId) {
    try {
      await this.apiRequest(`/api/admin/contracts/${contractId}/launch`, {
        method: 'POST',
      });

      this.showNotification('Contract launched successfully', 'success');
      await this.loadContracts();
    } catch (error) {
      this.showNotification('Failed to launch contract', 'error');
    }
  }

  async pauseContract(contractId) {
    try {
      await this.apiRequest(`/api/admin/contracts/${contractId}/pause`, {
        method: 'POST',
        body: JSON.stringify({ reason: 'Admin pause' }),
      });

      this.showNotification('Contract paused successfully', 'success');
      await this.loadContracts();
    } catch (error) {
      this.showNotification('Failed to pause contract', 'error');
    }
  }

  async resumeContract(contractId) {
    try {
      await this.apiRequest(`/api/admin/contracts/${contractId}/resume`, {
        method: 'POST',
      });

      this.showNotification('Contract resumed successfully', 'success');
      await this.loadContracts();
    } catch (error) {
      this.showNotification('Failed to resume contract', 'error');
    }
  }

  async deleteContract(contractId) {
    if (!confirm('Are you sure you want to delete this contract?')) {
      return;
    }

    try {
      await this.apiRequest(`/api/admin/contracts/${contractId}`, {
        method: 'DELETE',
        body: JSON.stringify({ reason: 'Admin deletion' }),
      });

      this.showNotification('Contract deleted successfully', 'success');
      await this.loadContracts();
    } catch (error) {
      this.showNotification('Failed to delete contract', 'error');
    }
  }

  // User Management Methods
  async createUser(formData) {
    try {
      const data = {
        email: formData.get('email'),
        username: formData.get('username'),
        password: formData.get('password'),
        full_name: formData.get('full_name'),
        role: formData.get('role'),
      };

      await this.apiRequest('/api/admin/users/create', {
        method: 'POST',
        body: JSON.stringify(data),
      });

      this.showNotification('User created successfully', 'success');
      this.closeModal(document.getElementById('create-user-modal'));
      await this.loadUsers();
    } catch (error) {
      this.showNotification('Failed to create user', 'error');
    }
  }

  async suspendUser(userId) {
    try {
      await this.apiRequest(`/api/admin/users/${userId}/suspend`, {
        method: 'POST',
        body: JSON.stringify({ reason: 'Admin suspension' }),
      });

      this.showNotification('User suspended successfully', 'success');
      await this.loadUsers();
    } catch (error) {
      this.showNotification('Failed to suspend user', 'error');
    }
  }

  async activateUser(userId) {
    try {
      await this.apiRequest(`/api/admin/users/${userId}/activate`, {
        method: 'POST',
      });

      this.showNotification('User activated successfully', 'success');
      await this.loadUsers();
    } catch (error) {
      this.showNotification('Failed to activate user', 'error');
    }
  }

  // Emergency Methods
  async emergencyHaltTrading(formData) {
    try {
      const reason = formData.get('reason');

      await this.apiRequest('/api/admin/emergency/halt-trading', {
        method: 'POST',
        body: JSON.stringify({ reason }),
      });

      this.showNotification('Trading halted system-wide', 'warning');
      this.closeModal(document.getElementById('emergency-halt-modal'));
      await this.loadSystemStats();
    } catch (error) {
      this.showNotification('Failed to halt trading', 'error');
    }
  }

  async emergencyResumeTrading() {
    if (!confirm('Are you sure you want to resume trading?')) {
      return;
    }

    try {
      await this.apiRequest('/api/admin/emergency/resume-trading', {
        method: 'POST',
      });

      this.showNotification('Trading resumed', 'success');
      await this.loadSystemStats();
    } catch (error) {
      this.showNotification('Failed to resume trading', 'error');
    }
  }

  // Utility Methods
  showNotification(message, type = 'info') {
    // Create notification element
    const notification = document.createElement('div');
    notification.className = `notification notification-${type}`;
    notification.innerHTML = `
      <div class="notification-content">
        <span>${message}</span>
        <button class="notification-close" onclick="this.parentElement.parentElement.remove()">&times;</button>
      </div>
    `;

    // Add notification styles if not already added
    if (!document.querySelector('#notification-styles')) {
      const styles = document.createElement('style');
      styles.id = 'notification-styles';
      styles.textContent = `
        .notification {
          position: fixed;
          top: 20px;
          right: 20px;
          padding: 1rem;
          border-radius: 6px;
          color: white;
          z-index: 10000;
          min-width: 300px;
          animation: slideIn 0.3s ease;
        }

        .notification-info {
          background: #3b82f6;
        }

        .notification-success {
          background: #059669;
        }

        .notification-warning {
          background: #f59e0b;
        }

        .notification-error {
          background: #dc2626;
        }

        .notification-content {
          display: flex;
          justify-content: space-between;
          align-items: center;
        }

        .notification-close {
          background: none;
          border: none;
          color: white;
          font-size: 1.2rem;
          cursor: pointer;
          padding: 0;
          margin-left: 1rem;
        }

        @keyframes slideIn {
          from {
            transform: translateX(100%);
            opacity: 0;
          }
          to {
            transform: translateX(0);
            opacity: 1;
          }
        }
      `;
      document.head.appendChild(styles);
    }

    // Add to DOM
    document.body.appendChild(notification);

    // Auto remove after 5 seconds
    setTimeout(() => {
      if (notification.parentElement) {
        notification.remove();
      }
    }, 5000);
  }
}

// Initialize dashboard when DOM is loaded
document.addEventListener('DOMContentLoaded', () => {
  window.adminDashboard = new AdminDashboard();
});

// Export for use in main process
module.exports = AdminDashboard;