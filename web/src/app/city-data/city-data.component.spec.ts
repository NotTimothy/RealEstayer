import { ComponentFixture, TestBed } from '@angular/core/testing';

import { CityDataComponent } from './city-data.component';

describe('CityDataComponent', () => {
  let component: CityDataComponent;
  let fixture: ComponentFixture<CityDataComponent>;

  beforeEach(async () => {
    await TestBed.configureTestingModule({
      imports: [CityDataComponent]
    })
    .compileComponents();

    fixture = TestBed.createComponent(CityDataComponent);
    component = fixture.componentInstance;
    fixture.detectChanges();
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });
});
