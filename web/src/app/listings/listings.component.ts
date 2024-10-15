import { Component, OnInit } from '@angular/core';
import { CityDataService } from "../city-data.service";
import { FormsModule } from "@angular/forms";
import { NgIf, NgFor } from "@angular/common";
import { HttpClientModule } from '@angular/common/http';
import { ListingService } from '../listings.service';

@Component({
  selector: 'app-listings',
  standalone: true,
  imports: [NgIf, NgFor, FormsModule, HttpClientModule],
  providers: [ListingService],
  templateUrl: 'listings.component.html'
})
export class ListingsComponent implements OnInit {
  listings: any[] = [];
  searchCity: string = '';

  constructor(private listingService: ListingService) {}

  ngOnInit() {
    this.getListings();
  }

  getListings() {
    this.listingService.getListings(this.searchCity).subscribe(
      (data: any) => {
        this.listings = data;
      },
      error => {
        console.error('Error fetching listings:', error);
      }
    );
  }

  onSearch() {
    this.getListings();
  }
}
