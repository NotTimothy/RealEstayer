import { Injectable } from '@angular/core';
import { HttpClient } from '@angular/common/http';
import { Observable } from 'rxjs';

@Injectable({
  providedIn: 'root'
})
export class ListingService {
  private apiUrl = 'http://localhost:5000';  // Adjust this URL as needed

  constructor(private http: HttpClient) {}

  getListings(searchTerm?: string): Observable<any> {
    let url = `${this.apiUrl}/get-listings`;
    if (searchTerm) {
      url += `?city=${encodeURIComponent(searchTerm)}`;
    }
    return this.http.get(url);
  }

  getFilters(searchTerm: string = '', features: string[] = []): Observable<any> {
    let params: any = {};
    if (searchTerm) {
      params.search = searchTerm;
    }
    if (features.length > 0) {
      params.features = features.join(',');
    }
    return this.http.get(`${this.apiUrl}/filters`, { params });
  }

  scrapeNorthAmerica(): Observable<any> {
    return this.http.get(`${this.apiUrl}/scrape-north-america`);
  }
}
