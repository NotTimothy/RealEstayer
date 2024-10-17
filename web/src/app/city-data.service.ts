import { Injectable } from '@angular/core';
import { HttpClient, HttpErrorResponse } from '@angular/common/http';
import { Observable, throwError } from 'rxjs';
import { catchError } from 'rxjs/operators';

@Injectable({
  providedIn: 'root'
})
export class CityDataService {
  private apiUrl = 'http://127.0.0.1:5000';  // Make sure this matches your Flask server address

  constructor(private http: HttpClient) {}

  scrapeCityData(cityName: string): Observable<any> {
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

    return this.http.get(`${this.apiUrl}/scrape-city-data?city=${cityName}`, options)
      .pipe(catchError(this.handleError));
  }

  getListings(cityName?: string, limit: number = 10): Observable<any> {
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

    let url = `${this.apiUrl}/get-listings?limit=${limit}`;
    if (cityName) {
      url += `&city=${cityName}`;
    }
    return this.http.get(url, options)
      .pipe(catchError(this.handleError));
  }

  getListingById(id: string): Observable<any> {
    return this.http.get(`${this.apiUrl}/get-listing/${id}`)
      .pipe(catchError(this.handleError));
  }

  private handleError(error: HttpErrorResponse) {
    if (error.error instanceof ErrorEvent) {
      // A client-side or network error occurred. Handle it accordingly.
      console.error('An error occurred:', error.error.message);
    } else {
      // The backend returned an unsuccessful response code.
      // The response body may contain clues as to what went wrong.
      console.error(
        `Backend returned code ${error.status}, ` +
        `body was: ${error.error}`);
    }
    // Return an observable with a user-facing error message.
    return throwError('Something bad happened; please try again later.');
  }
}
