import { Injectable } from '@angular/core';
import { HttpClient } from '@angular/common/http';
import { Observable } from 'rxjs';

@Injectable({
  providedIn: 'root'
})
export class ListingService {
  private apiUrl = 'http://localhost:8782';  // Adjust this URL as needed

  constructor(private http: HttpClient) {}

  getListings(searchTerm?: string): Observable<any> {
    var queryApiHeaders = {
      'Content-Type': 'application/json',
      'Access-Control-Allow-Origin': '*',
      'Access-Control-Allow-Credentials': 'true',
      'Access-Control-Allow-Headers': 'Content-Type',
      'Access-Control-Allow-Methods': 'GET,POST,DELETE',
    };

    const options = {
      headers: queryApiHeaders,
      rejectUnauthorized: false,
    };

    let url = `${this.apiUrl}/get-listings`;
    if (searchTerm) {
      url += `?city=${encodeURIComponent(searchTerm)}`;
    }
    return this.http.get(url, options);
  }

  scrapeNorthAmerica(): Observable<any> {
    var queryApiHeaders = {
      'Content-Type': 'application/json',
      'Access-Control-Allow-Origin': '*',
      'Access-Control-Allow-Credentials': 'true',
      'Access-Control-Allow-Headers': 'Content-Type',
      'Access-Control-Allow-Methods': 'GET,POST,DELETE',
    };

    const options = {
      headers: queryApiHeaders,
      rejectUnauthorized: false,
    };

    return this.http.get(`${this.apiUrl}/scrape-north-america`, options);
  }
}
