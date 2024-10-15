import { Component } from '@angular/core';
import { CityDataComponent} from "./city-data/city-data.component";
import { RouterOutlet } from '@angular/router';

@Component({
  selector: 'app-root',
  standalone: true,
  imports: [RouterOutlet, CityDataComponent],
  template: '<app-city-data></app-city-data>',
  styleUrl: './app.component.sass'
})
export class AppComponent {
  title = 'realestayer';
}
