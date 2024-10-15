import { Routes } from '@angular/router';
import { ListingsComponent } from './listings/listings.component';
import { ScrapeCityDataComponent } from './scrape-city-data/scrape-city-data.component';

export const routes: Routes = [
  {
    path: 'listings',
    component: ListingsComponent,
    title: 'Airbnb Listings'
  },
  {
    path: 'scrape',
    component: ScrapeCityDataComponent,
    title: 'Scrape Airbnb Listings'
  },
  {
    path: '',
    redirectTo: '/listings',
    pathMatch: 'full'
  },
  {
    path: '**',
    redirectTo: '/listings'
  }
];
