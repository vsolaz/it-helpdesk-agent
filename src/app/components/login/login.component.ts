import { Component } from '@angular/core';
import { FormsModule } from '@angular/forms';
import { NgIf } from '@angular/common';
import { AuthService } from '../../services/auth.service';

@Component({
  selector: 'app-login',
  standalone: true,
  imports: [FormsModule, NgIf],
  template: `
    <div class="login-container">
      <div class="login-card">
        <img src="assets/img/logo_mapfre-insurance.webp" alt="Mapfre Insurance" class="login-logo" />
        <h1 class="login-title">Mapfre Insurance<br>Technical Support Center</h1>
        <div *ngIf="!newPasswordRequired" class="form">
          <input type="email" [(ngModel)]="email" placeholder="Email" class="input" />
          <input type="password" [(ngModel)]="password" placeholder="Password" class="input" (keydown.enter)="login()" />
          <button class="btn" (click)="login()" [disabled]="loading">{{ loading ? 'Signing in...' : 'Sign In' }}</button>
        </div>
        <div *ngIf="newPasswordRequired" class="form">
          <p class="subtitle">Please set a new password</p>
          <input type="password" [(ngModel)]="newPassword" placeholder="New password" class="input" (keydown.enter)="setPassword()" />
          <button class="btn" (click)="setPassword()" [disabled]="loading">{{ loading ? 'Setting...' : 'Set Password' }}</button>
        </div>
        <p *ngIf="error" class="error">{{ error }}</p>
      </div>
    </div>
  `,
  styles: [`
    .login-container { display: flex; justify-content: center; align-items: center; min-height: 100vh; background: linear-gradient(135deg, #f0f4f8 0%, #d9e2ec 100%); }
    .login-card { display: flex; flex-direction: column; align-items: center; gap: 16px; padding: 48px 40px; background: white; border-radius: 16px; box-shadow: 0 8px 32px rgba(0,0,0,0.12); max-width: 380px; width: 100%; }
    .login-logo { height: 56px; width: auto; }
    .login-title { font-size: 18px; font-weight: 600; text-align: center; color: #1a237e; margin: 0; line-height: 1.4; }
    .subtitle { font-size: 14px; color: #666; margin: 0; text-align: center; }
    .form { display: flex; flex-direction: column; gap: 12px; width: 100%; }
    .input { padding: 12px 16px; border: 1px solid #ddd; border-radius: 8px; font-size: 14px; outline: none; }
    .input:focus { border-color: #1a237e; }
    .btn { padding: 12px; background: linear-gradient(135deg, #1a237e 0%, #283593 100%); color: white; border: none; border-radius: 8px; font-size: 15px; cursor: pointer; }
    .btn:disabled { opacity: 0.6; cursor: not-allowed; }
    .error { color: #d32f2f; font-size: 13px; margin: 0; text-align: center; }
  `],
})
export class LoginComponent {
  email = ''; password = ''; newPassword = ''; error = ''; loading = false; newPasswordRequired = false;
  private session = '';
  constructor(private auth: AuthService) {}
  async login() { this.error = ''; this.loading = true; const r = await this.auth.login(this.email, this.password); this.loading = false; if (r.success) return; if (r.newPasswordRequired) { this.newPasswordRequired = true; this.session = r.session || ''; return; } this.error = r.error || 'Login failed'; }
  async setPassword() { this.error = ''; this.loading = true; const r = await this.auth.setNewPassword(this.email, this.newPassword, this.session); this.loading = false; if (!r.success) this.error = r.error || 'Failed'; }
}
