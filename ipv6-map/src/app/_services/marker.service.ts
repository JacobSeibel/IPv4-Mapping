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
      const result = res.body.result;
      // Find the maximum density (represented by log(log(count))) in the set
      const maxDensity = Math.max.apply(Math, result.map((ipCount: any) => { return Math.log(Math.log(ipCount.count+1)+1) }));
      console.log(maxDensity);
      const markers = result.map((ipCount: any) => { 
        // Each point's intensity is defined as maxDensity - density of this point over the maxDensity
        const density = Math.log(Math.log(ipCount.count+1)+1)
        return [ipCount.latitude, ipCount.longitude, (maxDensity - density) / maxDensity] 
      })  
      // TODO: Figure out why 'as any' is needed
      const heat = (L as any).heatLayer(markers, {gradient: {0.3: 'blue', 0.5: 'lime', .75: 'yellow', 1: 'red'}}).addTo(map);
    });
  }
}
