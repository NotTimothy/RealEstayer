import { Component, OnInit } from '@angular/core';
import { ListingService } from '../listings.service';
import { FormsModule } from "@angular/forms";
import { NgIf, NgFor, KeyValuePipe, TitleCasePipe } from "@angular/common";
import { HttpClientModule } from '@angular/common/http';

interface Listing {
  url: string;
  title: string;
  picture_url: string;
  location: string;
  region: string;
  country: string;
  price: string;
  features: string[];
}

interface FilterResponse {
  features: string[];
  listings: Listing[];
}

@Component({
  selector: 'app-listings',
  standalone: true,
  imports: [NgIf, NgFor, KeyValuePipe, TitleCasePipe, FormsModule, HttpClientModule],
  providers: [ListingService],
  templateUrl: 'listings.component.html'
})
export class ListingsComponent implements OnInit {
  listings: Listing[] = [];
  allFeatures: string[] = [];
  selectedFeatures: string[] = [];
  searchTerm: string = '';
  hasSearched: boolean = false;
  scrapeMessage: string = '';

  constructor(private listingService: ListingService) {}

  ngOnInit() {
    this.getFilters();
  }

  getFilters() {
    this.listingService.getFilters().subscribe(
      (data: FilterResponse) => {
        this.allFeatures = data.features;
        this.listings = data.listings;
        this.hasSearched = true;
      },
      error => {
        console.error('Error fetching filters:', error);
        this.hasSearched = true;
      }
    );
  }

  onSearch() {
    if (this.searchTerm.trim() !== '' || this.selectedFeatures.length > 0) {
      this.listingService.getFilters(this.searchTerm, this.selectedFeatures).subscribe(
        (data: FilterResponse) => {
          this.listings = data.listings;
          this.hasSearched = true;
        },
        error => {
          console.error('Error fetching listings:', error);
          this.hasSearched = true;
          this.listings = [];
        }
      );
    } else {
      console.log('Please enter a search term or select features');
    }
  }

  toggleFeature(feature: string) {
    const index = this.selectedFeatures.indexOf(feature);
    if (index > -1) {
      this.selectedFeatures.splice(index, 1);
    } else {
      this.selectedFeatures.push(feature);
    }
    this.onSearch();
  }
}
