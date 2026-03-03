import { Injectable } from '@angular/core';
import { BehaviorSubject, Observable } from 'rxjs';
import { environment } from '../../environments/environment';

export interface AuthUser {
  email: string;
  token: string;
}

@Injectable({ providedIn: 'root' })
export class AuthService {
  private userSubject = new BehaviorSubject<AuthUser | null>(null);
  readonly user$: Observable<AuthUser | null> = this.userSubject.asObservable();
  private readonly clientId = environment.cognitoClientId;
  private readonly region = 'us-east-1';

  constructor() {
    const token = localStorage.getItem('id_token');
    const email = localStorage.getItem('user_email');
    if (token && email) {
      this.userSubject.next({ email, token });
    }
  }

  get isAuthenticated(): boolean { return this.userSubject.value !== null; }
  get token(): string | null { return this.userSubject.value?.token ?? null; }

  async login(email: string, password: string): Promise<{ success: boolean; newPasswordRequired?: boolean; session?: string; error?: string }> {
    const url = `https://cognito-idp.${this.region}.amazonaws.com/`;
    const body = { AuthFlow: 'USER_PASSWORD_AUTH', ClientId: this.clientId, AuthParameters: { USERNAME: email, PASSWORD: password } };
    try {
      const resp = await fetch(url, { method: 'POST', headers: { 'Content-Type': 'application/x-amz-json-1.1', 'X-Amz-Target': 'AWSCognitoIdentityProviderService.InitiateAuth' }, body: JSON.stringify(body) });
      const data = await resp.json();
      if (data.ChallengeName === 'NEW_PASSWORD_REQUIRED') return { success: false, newPasswordRequired: true, session: data.Session };
      if (data.AuthenticationResult) {
        const idToken = data.AuthenticationResult.IdToken;
        const payload = JSON.parse(atob(idToken.split('.')[1]));
        const userEmail = payload.email || email;
        localStorage.setItem('id_token', idToken);
        localStorage.setItem('user_email', userEmail);
        this.userSubject.next({ email: userEmail, token: idToken });
        return { success: true };
      }
      return { success: false, error: data.message || data.__type || 'Authentication failed' };
    } catch (e: any) { return { success: false, error: e.message || 'Network error' }; }
  }

  async setNewPassword(email: string, newPassword: string, session: string): Promise<{ success: boolean; error?: string }> {
    const url = `https://cognito-idp.${this.region}.amazonaws.com/`;
    const body = { ChallengeName: 'NEW_PASSWORD_REQUIRED', ClientId: this.clientId, ChallengeResponses: { USERNAME: email, NEW_PASSWORD: newPassword }, Session: session };
    try {
      const resp = await fetch(url, { method: 'POST', headers: { 'Content-Type': 'application/x-amz-json-1.1', 'X-Amz-Target': 'AWSCognitoIdentityProviderService.RespondToAuthChallenge' }, body: JSON.stringify(body) });
      const data = await resp.json();
      if (data.AuthenticationResult) {
        const idToken = data.AuthenticationResult.IdToken;
        const payload = JSON.parse(atob(idToken.split('.')[1]));
        const userEmail = payload.email || email;
        localStorage.setItem('id_token', idToken);
        localStorage.setItem('user_email', userEmail);
        this.userSubject.next({ email: userEmail, token: idToken });
        return { success: true };
      }
      return { success: false, error: data.message || 'Failed to set password' };
    } catch (e: any) { return { success: false, error: e.message || 'Network error' }; }
  }

  logout(): void {
    localStorage.removeItem('id_token');
    localStorage.removeItem('user_email');
    this.userSubject.next(null);
  }
}
