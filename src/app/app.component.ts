import { Component } from '@angular/core';
import { AsyncPipe, NgIf } from '@angular/common';
import { ChatWindowComponent } from './components/chat-window/chat-window.component';
import { MessageInputComponent } from './components/message-input/message-input.component';
import { LoginComponent } from './components/login/login.component';
import { ConversationService } from './services/conversation.service';
import { AuthService } from './services/auth.service';

@Component({
  selector: 'app-root', standalone: true,
  imports: [AsyncPipe, NgIf, ChatWindowComponent, MessageInputComponent, LoginComponent],
  templateUrl: './app.component.html', styleUrls: ['./app.component.css'],
})
export class AppComponent {
  constructor(readonly conversationService: ConversationService, readonly auth: AuthService) {}
  logout(): void { this.auth.logout(); }
}
