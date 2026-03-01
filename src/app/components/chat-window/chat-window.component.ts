import { Component } from '@angular/core';
import { AsyncPipe, NgFor, NgIf, DatePipe } from '@angular/common';
import { ConversationService } from '../../services/conversation.service';

@Component({
  selector: 'app-chat-window', standalone: true,
  imports: [AsyncPipe, NgFor, NgIf, DatePipe],
  templateUrl: './chat-window.component.html',
  styleUrls: ['./chat-window.component.css'],
})
export class ChatWindowComponent {
  readonly messages$ = this.conversationService.messages$;
  readonly loading$ = this.conversationService.loading$;
  constructor(private conversationService: ConversationService) {}
}
