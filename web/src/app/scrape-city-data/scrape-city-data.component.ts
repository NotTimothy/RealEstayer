import { Component } from '@angular/core';
import { CityDataService } from "../city-data.service";
import { FormsModule } from "@angular/forms";
import { NgIf, NgFor } from "@angular/common";
import { HttpClientModule } from '@angular/common/http';

@Component({
  selector: 'app-scrape-city-data',
  standalone: true,
  imports: [NgIf, NgFor, FormsModule, HttpClientModule],
  template: `
    <div>
      <h2>Scrape Airbnb Listings</h2>
      <input [(ngModel)]="cityName" placeholder="Enter city name">
      <button (click)="scrapeCityData()">Scrape Data</button>
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

  constructor(private cityDataService: CityDataService) {}

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
}
