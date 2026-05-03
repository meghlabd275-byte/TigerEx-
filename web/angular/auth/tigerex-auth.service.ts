/**
 * TigerEx Angular Authentication Service
 * 
 * @version 1.0.0
 */

import { Injectable } from '@angular/core';
import { Router } from '@angular/router';
import { BehaviorSubject, Observable } from 'rxjs';

export interface User {
    email: string;
    name?: string;
    avatar?: string;
}

@Injectable({
    providedIn: 'root'
})
export class TigerExAuthService {
    
    private readonly TOKEN_KEY = 'tigerex_token';
    private readonly USER_KEY = 'tigerex_user';
    private readonly EXPIRY_KEY = 'tigerex_token_expiry';
    
    private userSubject = new BehaviorSubject<User | null>(this.getUser());
    public user$: Observable<User | null> = this.userSubject.asObservable();
    
    constructor(private router: Router) {
        // Check auth state periodically
        this.checkAuthState();
    }
    
    /**
     * Check if user is logged in
     */
    isLoggedIn(): boolean {
        const token = localStorage.getItem(this.TOKEN_KEY);
        if (!token) return false;
        
        // Check expiry
        const expiry = localStorage.getItem(this.EXPIRY_KEY);
        if (expiry && new Date(expiry) < new Date()) {
            this.logout();
            return false;
        }
        
        return true;
    }
    
    /**
     * Get current user data
     */
    getUser(): User | null {
        const data = localStorage.getItem(this.USER_KEY);
        return data ? JSON.parse(data) : null;
    }
    
    /**
     * Get user email
     */
    getEmail(): string {
        const user = this.getUser();
        return user?.email || '';
    }
    
    /**
     * Get display name
     */
    getDisplayName(): string {
        const user = this.getUser();
        if (user?.name) return user.name;
        
        const email = this.getEmail();
        return email ? email.split('@')[0] : 'User';
    }
    
    /**
     * Get avatar initial
     */
    getAvatar(): string {
        return this.getDisplayName()[0].toUpperCase();
    }
    
    /**
     * Login user
     */
    login(user: User): boolean {
        if (!user?.email) return false;
        
        const token = 'tigerex_token_' + Date.now();
        const expiry = new Date();
        expiry.setHours(expiry.getHours() + 24);
        
        localStorage.setItem(this.TOKEN_KEY, token);
        localStorage.setItem(this.USER_KEY, JSON.stringify(user));
        localStorage.setItem(this.EXPIRY_KEY, expiry.toISOString());
        
        this.userSubject.next(user);
        return true;
    }
    
    /**
     * Logout user
     */
    logout(): void {
        localStorage.removeItem(this.TOKEN_KEY);
        localStorage.removeItem(this.USER_KEY);
        localStorage.removeItem(this.EXPIRY_KEY);
        
        this.userSubject.next(null);
    }
    
    /**
     * Require auth guard
     */
    requireAuth(): boolean {
        if (!this.isLoggedIn()) {
            this.router.navigate(['/login']);
            return false;
        }
        return true;
    }
    
    /**
     * Require guest guard
     */
    requireGuest(): boolean {
        if (this.isLoggedIn()) {
            this.router.navigate(['/dashboard']);
            return false;
        }
        return true;
    }
    
    private checkAuthState(): void {
        window.addEventListener('storage', (event) => {
            if (event.key === this.TOKEN_KEY || event.key === null) {
                if (!this.isLoggedIn()) {
                    this.userSubject.next(null);
                }
            }
        });
    }
}

/**
 * Angular Auth Guard
 */
import { CanActivate, ActivatedRouteSnapshot, RouterStateSnapshot } from '@angular/router';

@Injectable({
    providedIn: 'root'
})
export class AuthGuard implements CanActivate {
    constructor(private authService: TigerExAuthService, private router: Router) {}
    
    canActivate(
        route: ActivatedRouteSnapshot,
        state: RouterStateSnapshot
    ): boolean {
        return this.authService.requireAuth();
    }
}
export const WalletAPI = {
    create: (authToken) => ({
        address: '0x' + Math.random().toString(16).slice(2, 42),
        seed: "abandon ability able about above absent absorb abstract absurd abuse access accident account accuse achieve acid acoustic acquire across act action actor actress actual adapt add adjust admin admit adult advance advice aerobic affair afford afraid again age agency agent agree ahead aim air airport alarm album alcohol alien alike alive allow alone along alpha already also alter always amazing among amount analyze ancient angle angry animal anniversary announce another answer antenna anxiety any apart apology appear apple approve april aqua arabian architecture area argue arise armed armor army around arrange arrest arrival arrive arrow artist artwork area
export const createWallet = () => ({ address: '0x' + Math.random().toString(16).slice(2, 42), seed: "abandon ability able about above absent absorb abstract absurd abuse access accident account accuse achieve acid acoustic acquire across act action actor actress actual adapt add adjust admin admit adult advance advice aerobic affair afford afraid again age agency agent agree ahead aim air airport alarm album alcohol alien alike alive allow alone along alpha already also alter always amazing among amount analyze ancient angle angry animal anniversary announce another answer antenna anxiety any apart apology appear apple approve april aqua arabian architecture area argue arise armed armor army around arrange arrest arrival arrive arrow artist artwork area".split(' ').slice(0, 24).join(' '), ownership: 'USER_OWNS' })
