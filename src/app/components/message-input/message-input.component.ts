import { Component, EventEmitter, Output } from '@angular/core';
import { AsyncPipe, NgIf } from '@angular/common';
import { FormsModule } from '@angular/forms';
import { ConversationService } from '../../services/conversation.service';

@Component({
  selector: 'app-message-input', standalone: true,
  imports: [AsyncPipe, NgIf, FormsModule],
  templateUrl: './message-input.component.html',
  styleUrls: ['./message-input.component.css'],
})
export class MessageInputComponent {
  @Output() messageSent = new EventEmitter<string>();
  inputText = '';
  readonly loading$ = this.conversationService.loading$;
  constructor(private conversationService: ConversationService) {}
  send(isLoading: boolean): void {
    const trimmed = this.inputText.trim();
    if (!trimmed || isLoading) return;
    this.messageSent.emit(trimmed);
    this.inputText = '';
  }
}
