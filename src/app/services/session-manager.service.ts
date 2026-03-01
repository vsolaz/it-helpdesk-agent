import { Injectable } from '@angular/core';

@Injectable({ providedIn: 'root' })
export class SessionManagerService {
  private readonly sessionId: string;
  constructor() {
    this.sessionId = crypto.randomUUID?.() || 'xxxxxxxx-xxxx-4xxx-yxxx-xxxxxxxxxxxx'.replace(/[xy]/g, c => {
      const r = (Math.random() * 16) | 0;
      return (c === 'x' ? r : (r & 0x3) | 0x8).toString(16);
    });
  }
  getSessionId(): string { return this.sessionId; }
}
