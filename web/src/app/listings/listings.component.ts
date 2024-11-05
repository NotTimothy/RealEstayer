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
  state: string  // Added state field
  province: string  // Added province field
  country: string
  price: string
  features: string[]
}

interface Filter {
  name: string
  options: string[]
  selected: string[]
  isCollapsed: boolean
}

@Component({
  selector: 'app-listings',
  standalone: true,
  imports: [NgIf, NgFor, KeyValuePipe, TitleCasePipe, FormsModule, HttpClientModule],
  providers: [ListingService],
  templateUrl: 'listings.component.html',
  styleUrls: ['listings.component.sass'],
})
export class ListingsComponent implements OnInit {
  allListings: Listing[] = []
  filteredListings: Listing[] = []
  searchTerm: string = ''
  filters: Filter[] = []
  hasSearched: boolean = false
  scrapeMessage: string = ''
  currentPage: number = 1
  itemsPerPage: number = 25
  totalPages: number = 1

  constructor(private listingService: ListingService) {}

  ngOnInit() {
    // Initialize filters
    this.filters = [
      { name: 'Features', options: [], selected: [], isCollapsed: true },
      { name: 'Price Range', options: ['$0-$50', '$51-$100', '$101-$200', '$201+'], selected: [], isCollapsed: true },
      { name: 'Location', options: [], selected: [], isCollapsed: true }
    ]
  }

  getListings() {
    console.log('Searching for:', this.searchTerm) // Debug log
    this.listingService.getListings(this.searchTerm).subscribe(
      (data: Listing[]) => {
        console.log('Received data:', data) // Debug log
        this.allListings = data
        this.updateFilterOptions()
        this.filterListings()
        this.hasSearched = true
      },
      error => {
        console.error('Error fetching listings:', error)
        this.hasSearched = true
        this.allListings = []
        this.filteredListings = []
      }
    )
  }

  onSearch() {
    // Always fetch listings, regardless of whether searchTerm is empty
    this.getListings()
  }

  updateFilterOptions() {
    // Update Features filter options
    this.filters[0].options = Array.from(new Set(this.allListings.flatMap(listing => listing.features)))

    // Update Location filter options
    this.filters[2].options = Array.from(new Set(this.allListings.map(listing => listing.location)))
  }

  filterListings() {
    this.filteredListings = this.allListings.filter(listing => {
      // If searchTerm is not empty, filter by it
      if (this.searchTerm.trim() !== '') {
        const searchLower = this.searchTerm.toLowerCase()
        if (!listing.location.toLowerCase().includes(searchLower) &&
          !listing.region.toLowerCase().includes(searchLower) &&
          !listing.country.toLowerCase().includes(searchLower) &&
          !listing.state.toLowerCase().includes(searchLower) &&
          !listing.province.toLowerCase().includes(searchLower)) {
          return false
        }
      }

      return this.filters.every(filter => {
        if (filter.selected.length === 0) return true

        switch(filter.name) {
          case 'Features':
            return filter.selected.every(feature => listing.features.includes(feature))
          case 'Price Range':
            const price = parseInt(listing.price.replace(/\D/g,''))
            return filter.selected.some(range => {
              const [min, max] = range.split('-').map(v => parseInt(v.replace('$', '')))
              return price >= min && (max ? price <= max : true)
            })
          case 'Location':
            return filter.selected.includes(listing.location)
          default:
            return true
        }
      })
    })
    this.updatePagination()
  }

  toggleFilter(filterName: string, option: string) {
    const filter = this.filters.find(f => f.name === filterName)
    if (filter) {
      const index = filter.selected.indexOf(option)
      if (index > -1) {
        filter.selected.splice(index, 1)
      } else {
        filter.selected.push(option)
      }
      this.filterListings()
    }
  }

  isFilterSelected(filterName: string, option: string): boolean {
    const filter = this.filters.find(f => f.name === filterName)
    return filter ? filter.selected.includes(option) : false
  }

  toggleCollapse(filter: Filter) {
    filter.isCollapsed = !filter.isCollapsed
  }

  updatePagination() {
    this.totalPages = Math.ceil(this.filteredListings.length / this.itemsPerPage)
    this.currentPage = 1
  }

  get paginatedListings() {
    const startIndex = (this.currentPage - 1) * this.itemsPerPage
    return this.filteredListings.slice(startIndex, startIndex + this.itemsPerPage)
  }

  nextPage() {
    if (this.hasNextPage()) {
      this.currentPage++
    }
  }

  prevPage() {
    if (this.hasPreviousPage()) {
      this.currentPage--
    }
  }

  goToPage(page: number) {
    if (page >= 1 && page <= this.totalPages) {
      this.currentPage = page
    }
  }

  hasNextPage(): boolean {
    return this.currentPage < this.totalPages
  }

  hasPreviousPage(): boolean {
    return this.currentPage > 1
  }

  getVisiblePages(): number[] {
    const delta = 2;
    const range: number[] = [];
    const rangeWithDots: number[] = [];

    let left = this.currentPage - delta;
    let right = this.currentPage + delta + 1;

    // Handle edge cases
    if (left < 1) {
      left = 1;
      right = Math.min(5, this.totalPages);
    }

    if (right > this.totalPages) {
      right = this.totalPages;
      left = Math.max(1, this.totalPages - 4);
    }

    // Generate the range
    for (let i = left; i < right; i++) {
      range.push(i);
    }

    return range;
  }
}
