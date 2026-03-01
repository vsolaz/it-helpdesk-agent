import { Injectable } from '@angular/core';
import { BehaviorSubject, Observable } from 'rxjs';
import { AgentResponse, Message } from '../models/models';
import { AgentClientService } from './agent-client.service';
import { SessionManagerService } from './session-manager.service';

@Injectable({ providedIn: 'root' })
export class ConversationService {
  private readonly messagesSubject = new BehaviorSubject<Message[]>([]);
  private readonly loadingSubject = new BehaviorSubject<boolean>(false);
  readonly messages$: Observable<Message[]> = this.messagesSubject.asObservable();
  readonly loading$: Observable<boolean> = this.loadingSubject.asObservable();
  constructor(private agentClient: AgentClientService, private sessionManager: SessionManagerService) {}
  sendMessage(text: string): void {
    const trimmed = text.trim();
    if (!trimmed) return;
    this.appendMessage({ role: 'user', content: trimmed, timestamp: new Date() });
    this.loadingSubject.next(true);
    this.agentClient.sendMessage(this.sessionManager.getSessionId(), trimmed).subscribe({
      next: (r: AgentResponse) => { this.appendMessage({ role: 'agent', content: r.reply, timestamp: new Date() }); this.loadingSubject.next(false); },
      error: (msg: string) => { this.appendMessage({ role: 'agent', content: msg, timestamp: new Date() }); this.loadingSubject.next(false); },
    });
  }
  private appendMessage(message: Message): void {
    this.messagesSubject.next([...this.messagesSubject.getValue(), message]);
  }
}
