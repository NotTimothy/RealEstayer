import { Injectable } from '@angular/core';
import { HttpClient } from '@angular/common/http';
import { Observable } from 'rxjs';

@Injectable({
  providedIn: 'root'
})
export class CityDataService {
  private apiUrl = 'http://localhost:5000/city-data';  // Adjust this URL to match your backend

  constructor(private http: HttpClient) {}

  getCityData(cityName: string): Observable<any> {
    return this.http.get(`${this.apiUrl}?city=${cityName}`);
  }
}
