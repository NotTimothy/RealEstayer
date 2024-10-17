import { Component, OnInit } from '@angular/core'
import { ListingService } from '../listings.service'
import { FormsModule } from "@angular/forms"
import { NgIf, NgFor, KeyValuePipe, TitleCasePipe } from "@angular/common"
import { HttpClientModule } from '@angular/common/http'

interface Listing {
  url: string
  title: string
  picture_url: string
  location: string
  region: string
  country: string
  price: string
  features: string[]
}

@Component({
  selector: 'app-listings',
  standalone: true,
  imports: [NgIf, NgFor, KeyValuePipe, TitleCasePipe, FormsModule, HttpClientModule],
  providers: [ListingService],
  templateUrl: 'listings.component.html'
})
export class ListingsComponent implements OnInit {
  listings: Listing[] = []
  searchTerm: string = ''
  hasSearched: boolean = false
  scrapeMessage: string = ''
  currentPage: number = 1
  itemsPerPage: number = 25
  totalPages: number = 1

  constructor(private listingService: ListingService) {}

  ngOnInit() {
    // You might want to load regions or countries here if you decide to add dropdowns
  }

  getListings() {
    console.log('Searching for:', this.searchTerm); // Debug log
    this.listingService.getListings(this.searchTerm).subscribe(
      (data: Listing[]) => {
        console.log('Received data:', data); // Debug log
        this.listings = data;
        this.hasSearched = true;
      },
      error => {
        console.error('Error fetching listings:', error);
        this.hasSearched = true;
        this.listings = [];
      }
    );
  }

  onSearch() {
    if (this.searchTerm.trim() !== '') {
      this.getListings()
    } else {
      console.log('Please enter a place, region, or country to search')
    }
  }

  get paginatedListings() {
    const startIndex = (this.currentPage - 1) * this.itemsPerPage
    return this.listings.slice(startIndex, startIndex + this.itemsPerPage)
  }

  nextPage() {
    if (this.currentPage < this.totalPages) {
      this.currentPage++
    }
  }

  prevPage() {
    if (this.currentPage > 1) {
      this.currentPage--
    }
  }

  goToPage(page: number) {
    if (page >= 1 && page <= this.totalPages) {
      this.currentPage = page
    }
  }
}
