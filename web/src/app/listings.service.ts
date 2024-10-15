// listing.service.ts
import { Injectable } from '@angular/core';
import { HttpClient } from '@angular/common/http';
import { Observable } from 'rxjs';

@Injectable({
  providedIn: 'root'
})
export class ListingService {
  private apiUrl = 'http://localhost:5000/get-listings';  // Adjust this URL as needed

  constructor(private http: HttpClient) {}

  getListings(city?: string): Observable<any> {
    let url = this.apiUrl;
    if (city) {
      url += `?city=${encodeURIComponent(city)}`;
    }
    return this.http.get(url);
  }
}
