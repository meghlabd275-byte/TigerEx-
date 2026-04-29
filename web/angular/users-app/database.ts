import { Injectable } from '@angular/core';
import { HttpClient } from '@angular/common/http';
@Injectable({ providedIn: 'root' })
export class DatabaseService {
    // Same backend for all platforms
    private api = 'https://api.tigerex.com';
    constructor(private http: HttpClient) {}
}
