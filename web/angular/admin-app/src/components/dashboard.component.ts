import { Component, OnInit } from '@angular/core';
import { CommonModule } from '@angular/common';
import { Router } from '@angular/router';
import { ApiService } from '../services/api.service';
import { AuthService } from '../services/auth.service';

@Component({
  selector: 'app-dashboard',
  standalone: true,
  imports: [CommonModule],
  template: `
    <div class="min-h-screen bg-gray-900 text-white">
      <!-- Sidebar -->
      <aside class="fixed left-0 top-0 h-full w-64 bg-gray-800 border-r border-gray-700">
        <div class="p-6">
          <h1 class="text-2xl font-bold text-orange-500">TigerEx Admin</h1>
        </div>
        <nav class="mt-6">
          <a *ngFor="let item of menuItems" 
             [routerLink]="item.route"
             routerLinkActive="bg-orange-500 text-white"
             class="flex items-center px-6 py-3 text-gray-300 hover:bg-gray-700 hover:text-white transition">
            <span [innerHTML]="item.icon" class="mr-3"></span>
            {{ item.label }}
          </a>
        </nav>
      </aside>

      <!-- Main Content -->
      <main class="ml-64 p-8">
        <!-- Stats Cards -->
        <div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6 mb-8">
          <div *ngFor="let stat of stats" class="bg-gray-800 rounded-lg p-6">
            <div class="flex items-center justify-between">
              <div>
                <p class="text-gray-400 text-sm">{{ stat.label }}</p>
                <p class="text-2xl font-bold mt-1">{{ stat.value }}</p>
              </div>
              <div [class]="stat.trend >= 0 ? 'text-green-400' : 'text-red-400'">
                {{ stat.trend >= 0 ? '+' : '' }}{{ stat.trend }}%
              </div>
            </div>
          </div>
        </div>

        <!-- Recent Users Table -->
        <div class="bg-gray-800 rounded-lg p-6">
          <div class="flex justify-between items-center mb-4">
            <h2 class="text-xl font-semibold">Recent Users</h2>
            <button class="px-4 py-2 bg-orange-500 rounded-lg hover:bg-orange-600">
              + Add User
            </button>
          </div>
          <table class="w-full">
            <thead>
              <tr class="text-gray-400 text-left border-b border-gray-700">
                <th class="pb-3">User</th>
                <th class="pb-3">Role</th>
                <th class="pb-3">Status</th>
                <th class="pb-3">Joined</th>
                <th class="pb-3">Actions</th>
              </tr>
            </thead>
            <tbody>
              <tr *ngFor="let user of recentUsers" class="border-b border-gray-700">
                <td class="py-4">
                  <div class="flex items-center">
                    <div class="w-10 h-10 bg-orange-500 rounded-full flex items-center justify-center mr-3">
                      {{ user.email.charAt(0).toUpperCase() }}
                    </div>
                    <div>
                      <p>{{ user.email }}</p>
                      <p class="text-sm text-gray-400">{{ user.name }}</p>
                    </div>
                  </div>
                </td>
                <td><span class="px-2 py-1 bg-gray-700 rounded">{{ user.role }}</span></td>
                <td>
                  <span [class]="getStatusClass(user.status)">
                    {{ user.status }}
                  </span>
                </td>
                <td>{{ user.joinedAt | date:'short' }}</td>
                <td>
                  <button class="text-orange-500 hover:text-orange-400 mr-2">Edit</button>
                  <button class="text-red-400 hover:text-red-300">Delete</button>
                </td>
              </tr>
            </tbody>
          </table>
        </div>

        <!-- Trading Activity -->
        <div class="grid grid-cols-1 lg:grid-cols-2 gap-6 mt-8">
          <div class="bg-gray-800 rounded-lg p-6">
            <h2 class="text-xl font-semibold mb-4">Trading Volume</h2>
            <canvas baseChart [data]="chartData" type="line"></canvas>
          </div>
          <div class="bg-gray-800 rounded-lg p-6">
            <h2 class="text-xl font-semibold mb-4">Pending Actions</h2>
            <div class="space-y-3">
              <div *ngFor="let action of pendingActions" class="flex justify-between items-center p-3 bg-gray-700 rounded">
                <div>
                  <p class="font-medium">{{ action.type }}</p>
                  <p class="text-sm text-gray-400">{{ action.user }}</p>
                </div>
                <div class="flex space-x-2">
                  <button (click)="approveAction(action)" class="px-3 py-1 bg-green-500 rounded hover:bg-green-600">Approve</button>
                  <button (click)="rejectAction(action)" class="px-3 py-1 bg-red-500 rounded hover:bg-red-600">Reject</button>
                </div>
              </div>
            </div>
          </div>
        </div>
      </main>
    </div>
  `
})
export class DashboardComponent implements OnInit {
  menuItems = [
    { label: 'Dashboard', route: '/admin', icon: '📊' },
    { label: 'Users', route: '/admin/users', icon: '👥' },
    { label: 'Trading', route: '/admin/trading', icon: '📈' },
    { label: 'Wallet', route: '/admin/wallet', icon: '💼' },
    { label: 'P2P', route: '/admin/p2p', icon: '🔄' },
    { label: 'Settings', route: '/admin/settings', icon: '⚙️' },
    { label: 'Audit Logs', route: '/admin/audit', icon: '📋' }
  ];

  stats = [
    { label: 'Total Users', value: '24,521', trend: 12 },
    { label: 'Active Trading', value: '8,234', trend: 8 },
    { label: 'Volume 24h', value: '$142.5M', trend: -2 },
    { label: 'Pending KYCs', value: '156', trend: 0 }
  ];

  recentUsers = [
    { email: 'user1@example.com', name: 'John Doe', role: 'TRADER', status: 'active', joinedAt: new Date() },
    { email: 'user2@example.com', name: 'Jane Smith', role: 'VIP', status: 'active', joinedAt: new Date() },
    { email: 'user3@example.com', name: 'Bob Wilson', role: 'AFFILIATE', status: 'pending', joinedAt: new Date() }
  ];

  pendingActions = [
    { id: 1, type: 'KYC Approval', user: 'user@example.com' },
    { id: 2, type: 'Withdrawal', user: 'user2@example.com' },
    { id: 3, type: 'Feature Request', user: 'user3@example.com' }
  ];

  chartData = { labels: [], datasets: [] };

  constructor(
    private api: ApiService,
    private auth: AuthService,
    private router: Router
  ) {}

  ngOnInit() {
    this.loadStats();
  }

  async loadStats() {
    try {
      const stats = await this.api.getDashboardStats();
      this.stats = stats;
    } catch (error) {
      console.error('Failed to load stats:', error);
    }
  }

  getStatusClass(status: string): string {
    return status === 'active' ? 'text-green-400' : 'text-yellow-400';
  }

  async approveAction(action: any) {
    await this.api.approveAction(action.id);
    this.loadStats();
  }

  async rejectAction(action: any) {
    await this.api.rejectAction(action.id);
    this.loadStats();
  }
}