import { Component } from '@angular/core';
import { RouterOutlet, RouterLink, RouterLinkActive } from '@angular/router';
import {NgFor} from "@angular/common";

@Component({
  selector: 'app-root',
  standalone: true,
  imports: [RouterOutlet, RouterLink, RouterLinkActive, NgFor],
  template: `
    <div class="app-container">
      <nav class="nav-bar">
        <div class="nav-container">
          <a href="/" class="nav-logo">RealEstayer</a>
          <ul class="nav-links">
            <li><a routerLink="/listings" routerLinkActive="active">Listings</a></li>
            <li><a routerLink="/scrape" routerLinkActive="active">Scrape Listings</a></li>
          </ul>
          <div class="nav-auth">
            <a href="/login" class="nav-login">Login</a>
            <a href="/signup" class="nav-signup">Sign Up</a>
          </div>
        </div>
      </nav>
      <router-outlet></router-outlet>
<!--      <footer class="footer">-->
<!--        <div class="container">-->
<!--          <p>&copy; 2024 RealEstayer. All rights reserved.</p>-->
<!--        </div>-->
<!--      </footer>-->
    </div>
  `,
  styleUrls: ['./app.component.sass']
})
export class AppComponent {
  title = 'realestayer';
}
