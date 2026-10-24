// OpenStreetMap map with Leaflet (no API key). Circle markers avoid image files.
import { useEffect, useRef } from "react";
import L from "leaflet";
import "leaflet/dist/leaflet.css";
import type { PharmacyBrief } from "../api";

export function MapView({ pharmacies, label, onSelect }: { pharmacies: PharmacyBrief[]; label: string; onSelect: (id: string) => void }) {
  const el = useRef<HTMLDivElement>(null);
  const map = useRef<L.Map | null>(null);
  const layer = useRef<L.LayerGroup | null>(null);

  useEffect(() => {
    if (!el.current || map.current) return;
    map.current = L.map(el.current, { scrollWheelZoom: false }).setView([42.33, -71.07], 12);
    L.tileLayer("https://tile.openstreetmap.org/{z}/{x}/{y}.png", {
      maxZoom: 18, attribution: '&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> contributors',
    }).addTo(map.current);
    layer.current = L.layerGroup().addTo(map.current);
    return () => { map.current?.remove(); map.current = null; };
  }, []);

  useEffect(() => {
    if (!map.current || !layer.current) return;
    layer.current.clearLayers();
    const pts: L.LatLngExpression[] = [];
    pharmacies.forEach((p) => {
      const ll: L.LatLngExpression = [p.latitude, p.longitude];
      pts.push(ll);
      L.circleMarker(ll, {
        radius: 9, weight: 2, color: "#0b2a33", fillOpacity: 0.95,
        fillColor: p.open_now ? "#f4b740" : p.open_now === false ? "#9fb7bb" : "#e8e1cf",
      })
        .bindTooltip(`${p.name} — ${p.address}`)
        .on("click", () => onSelect(p.id))
        .addTo(layer.current!);
    });
    if (pts.length) map.current.fitBounds(L.latLngBounds(pts), { padding: [30, 30], maxZoom: 14 });
  }, [pharmacies, onSelect]);

  return <div ref={el} className="map" role="region" aria-label={label} />;
}
