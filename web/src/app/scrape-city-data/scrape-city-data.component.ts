import { Component } from '@angular/core';
import { CityDataService } from "../city-data.service";
import { FormsModule } from "@angular/forms";
import { NgIf, NgFor } from "@angular/common";
import { HttpClientModule } from '@angular/common/http';
import { ListingService } from '../listings.service';


@Component({
  selector: 'app-scrape-city-data',
  standalone: true,
  imports: [NgIf, NgFor, FormsModule, HttpClientModule],
  providers: [ListingService, CityDataService],
  template: `
    <div>
      <h2>Scrape Airbnb Listings</h2>
      <input [(ngModel)]="cityName" placeholder="Enter city name">
      <button (click)="scrapeCityData()">Scrape Data</button>
      <button (click)="scrapeNorthAmerica()" class="scrape-button">Scrape North America</button>
      <div *ngIf="scrapeMessage" class="scrape-message">{{ scrapeMessage }}</div>
      <div *ngIf="cityData">
        <h3>Scraped Listings in {{ cityData.city }}</h3>
        <div *ngFor="let place of cityData.places">
          <h4>{{ place.title }}</h4>
          <p>Price: {{ place.price }}</p>
          <p>Rating: {{ place.rating }}</p>
          <a [href]="place.url" target="_blank">View on Airbnb</a>
        </div>
      </div>
    </div>
  `
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
