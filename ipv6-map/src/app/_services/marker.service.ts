import { Injectable } from '@angular/core';
import { HttpClient } from '@angular/common/http';
import * as L from 'leaflet';
import 'leaflet.heat/dist/leaflet-heat.js'

@Injectable({
  providedIn: 'root'
})
export class MarkerService {

  constructor(private http: HttpClient) { }

  drawIPMarkers(map: L.Map) {
    this.http.get("http://localhost:5000/ipCounts", {observe: 'response', responseType: 'json'}).subscribe((res: any) => {
      const markers = res.body.result.map((ipCount: any) => { return [ipCount.latitude, ipCount.longitude]})  
      // TODO: Figure out why 'as any' is needed
      const heat = (L as any).heatLayer(markers, {}).addTo(map);
    });
  }
}
