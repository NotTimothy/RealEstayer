import { Component } from '@angular/core';
import { CityDataService } from "../city-data.service";
import { FormsModule } from "@angular/forms";
import {NgIf, NgFor, KeyValuePipe, TitleCasePipe, NgClass} from "@angular/common";
import { HttpClientModule } from '@angular/common/http';
import { ListingService } from '../listings.service';


@Component({
  selector: 'app-scrape-city-data',
  standalone: true,
  imports: [NgIf, NgFor, KeyValuePipe, TitleCasePipe, FormsModule, HttpClientModule, NgClass],
  providers: [ListingService, CityDataService],
  template: `
    <div class="scrape-container">
      <h2 class="scrape-title">Scrape Airbnb Listings</h2>

      <div class="scrape-controls">
        <div class="input-group">
          <input [(ngModel)]="cityName" placeholder="Enter city name" class="scrape-input">
          <button (click)="scrapeCityData()" class="scrape-button">Scrape City</button>
        </div>
        <button (click)="scrapeNorthAmerica()" class="scrape-button scrape-button-large">Scrape North America</button>
      </div>

      <div *ngIf="scrapeMessage" class="scrape-message" [ngClass]="{'success': !scrapeMessage, 'error': scrapeMessage}">
        {{ scrapeMessage }}
      </div>

      <div *ngIf="cityData" class="scrape-results">
        <h3 class="results-title">Scraped Listings in {{ cityData.city }}</h3>
        <div class="listings-grid">
          <div *ngFor="let place of cityData.places" class="listing-card">
            <img [src]="place.picture_url" alt="{{ place.title }}" class="listing-image">
            <div class="listing-details">
              <h4 class="listing-title">{{ place.title }}</h4>
              <p class="listing-price">Price: {{ place.price }}</p>
              <p class="listing-rating">Rating: {{ place.rating }}</p>
              <a [href]="place.url" target="_blank" class="listing-link">View on Airbnb</a>
            </div>
          </div>
        </div>
      </div>
    </div>
  `,
  styleUrls: ['scrape-city-data.component.sass'],
})
export class ScrapeCityDataComponent {
  cityName: string = '';
  cityData: any;
  scrapeMessage: string = '';

  constructor(private cityDataService: CityDataService, private listingService: ListingService) {}

  scrapeCityData() {
    if (this.cityName) {
      this.cityDataService.scrapeCityData(this.cityName).subscribe(
        data => {
          this.cityData = data;
        },
        error => {
          console.error('Error scraping city data:', error);
          // Handle error (e.g., show error message to user)
        }
      );
    }
  }

  scrapeNorthAmerica() {
    this.scrapeMessage = 'Scraping started... This may take a while.';
    this.listingService.scrapeNorthAmerica().subscribe(
      (response: any) => {
        console.log('Scrape response:', response);
        this.scrapeMessage = `Scraping completed. ${response.total_listings} listings added (${response.canada_listings} from Canada, ${response.us_listings} from USA).`;
      },
      error => {
        console.error('Error during scraping:', error);
        this.scrapeMessage = 'An error occurred during scraping. Please try again later.';
      }
    );
  }
}
