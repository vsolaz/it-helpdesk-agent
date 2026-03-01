import { Component } from '@angular/core';
import { ChatWindowComponent } from './components/chat-window/chat-window.component';
import { MessageInputComponent } from './components/message-input/message-input.component';
import { ConversationService } from './services/conversation.service';

@Component({
  selector: 'app-root', standalone: true,
  imports: [ChatWindowComponent, MessageInputComponent],
  templateUrl: './app.component.html',
  styleUrls: ['./app.component.css'],
})
export class AppComponent {
  constructor(readonly conversationService: ConversationService) {}
}
