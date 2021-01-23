import { Injectable } from '@angular/core';
import { HttpClient, HttpParams } from '@angular/common/http';
import * as L from 'leaflet';
import 'leaflet.heat/dist/leaflet-heat.js'

@Injectable({
  providedIn: 'root'
})
export class MarkerService {
  private heat!: any;
  private inUse = false;
  private waiting = false;

  constructor(private http: HttpClient) { }

  drawIPMarkers(map: L.Map) {
    if(this.inUse){
      this.waiting = true;
      return;
    } else {
      this.inUse = true;
      const bounds = map.getBounds();
      let params: HttpParams = new HttpParams();
      const boundsParam = "[["
        + bounds.getNorthWest().lat + "," + bounds.getNorthWest().lng + "],["
        + bounds.getNorthEast().lat + "," + bounds.getNorthEast().lng + "],[" 
        + bounds.getSouthEast().lat + "," + bounds.getSouthEast().lng + "],["
        + bounds.getSouthWest().lat + "," + bounds.getSouthWest().lng + "]]";
      params = params.append('bounds', boundsParam);
      this.http.get("http://localhost:5000/ipCounts", {observe: 'response', responseType: 'json', params}).subscribe((res: any) => {
        const result = res.body.result;
        // Find the maximum density (represented by log(log(count))) in the set
        const maxDensity = Math.max.apply(Math, result.map((ipCount: any) => { return Math.log(Math.log(ipCount.count+1)+1) }));
        const markers = result.map((ipCount: any) => { 
          // Each point's intensity is defined as maxDensity - density of this point over the maxDensity
          const density = Math.log(Math.log(ipCount.count+1)+1)
          return [ipCount.latitude, ipCount.longitude, (maxDensity - density) / maxDensity] 
        })
        if(this.heat){
          map.removeLayer(this.heat);
        }
        // TODO: Figure out why 'as any' is needed
        this.heat = (L as any).heatLayer(markers, {gradient: {0.3: 'blue', 0.5: 'lime', .75: 'yellow', 1: 'red'}}).addTo(map);
        this.inUse = false;
        if(this.waiting) {
          this.waiting = false;
          this.drawIPMarkers(map);
        }
      });
    }
  }
}
