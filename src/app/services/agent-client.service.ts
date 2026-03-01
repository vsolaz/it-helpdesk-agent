import { Injectable } from '@angular/core';
import { HttpClient, HttpErrorResponse } from '@angular/common/http';
import { Observable, throwError, TimeoutError } from 'rxjs';
import { catchError, timeout } from 'rxjs/operators';
import { AgentRequest, AgentResponse } from '../models/models';
import { environment } from '../../environments/environment';

@Injectable({ providedIn: 'root' })
export class AgentClientService {
  private readonly endpointUrl = environment.agentEndpointUrl;
  constructor(private http: HttpClient) {}
  sendMessage(sessionId: string, message: string): Observable<AgentResponse> {
    const body: AgentRequest = { session_id: sessionId, message };
    return this.http.post<AgentResponse>(this.endpointUrl, body).pipe(
      timeout(30000),
      catchError((error) => {
        if (error instanceof TimeoutError) return throwError(() => 'The service is taking too long to respond.');
        return throwError(() => 'The service is currently unavailable.');
      })
    );
  }
}
