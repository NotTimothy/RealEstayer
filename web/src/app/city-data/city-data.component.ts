import { Component } from '@angular/core';
import { CityDataService } from "../city-data.service";
import { FormsModule } from "@angular/forms";
import { NgIf, NgFor } from "@angular/common";
import { HttpClientModule } from '@angular/common/http';

@Component({
  selector: 'app-city-data',
  standalone: true,
  imports: [NgIf, NgFor, FormsModule, HttpClientModule],
  providers: [CityDataService, HttpClientModule],
  template: `
    <div>
      <h2>Airbnb Listings Lookup</h2>
      <input [(ngModel)]="cityName" placeholder="Enter city name">
      <button (click)="getCityData()">Get Data</button>
      <div *ngIf="cityData">
        <h3>Listings in {{ cityData.city }}</h3>
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
export class CityDataComponent {
  cityName: string = '';
  cityData: any;

  constructor(private cityDataService: CityDataService) {}

  getCityData() {
    if (this.cityName) {
      this.cityDataService.getCityData(this.cityName).subscribe(
        data => {
          this.cityData = data;
        },
        error => {
          console.error('Error fetching city data:', error);
          // Handle error (e.g., show error message to user)
        }
      );
    }
  }
}
