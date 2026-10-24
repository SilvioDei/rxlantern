// OpenStreetMap map with Leaflet (no API key). Circle markers avoid image files.
// The patient's own point (if any) is drawn in the browser only; it is never sent to the server.
import { useEffect, useRef } from "react";
import L from "leaflet";
import "leaflet/dist/leaflet.css";

export interface MapPoint { id: string; name: string; address: string; latitude: number; longitude: number; open_now: boolean | null }

export function MapView({ points, label, onSelect, origin, originLabel, className }: {
  points: MapPoint[]; label: string; onSelect: (id: string) => void;
  origin?: { lat: number; lon: number } | null; originLabel?: string; className?: string;
}) {
  const el = useRef<HTMLDivElement>(null);
  const map = useRef<L.Map | null>(null);
  const layer = useRef<L.LayerGroup | null>(null);
  const select = useRef(onSelect);
  select.current = onSelect;

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
    points.forEach((p) => {
      const ll: L.LatLngExpression = [p.latitude, p.longitude];
      pts.push(ll);
      L.circleMarker(ll, {
        radius: 9, weight: 2, color: "#0f2440", fillOpacity: 0.95,
        fillColor: p.open_now ? "#f2a91f" : p.open_now === false ? "#9aa9b0" : "#e9e2cf",
      })
        .bindTooltip(`${p.name} — ${p.address}`)
        .on("click", () => select.current(p.id))
        .addTo(layer.current!);
    });
    if (origin) {
      const ll: L.LatLngExpression = [origin.lat, origin.lon];
      pts.push(ll);
      L.circleMarker(ll, { radius: 8, weight: 3, color: "#ffffff", fillColor: "#0e6e72", fillOpacity: 1 })
        .bindTooltip(originLabel ?? "")
        .addTo(layer.current);
    }
    if (pts.length) map.current.fitBounds(L.latLngBounds(pts), { padding: [30, 30], maxZoom: 14 });
  }, [points, origin, originLabel]);

  return <div ref={el} className={`map ${className ?? ""}`} role="region" aria-label={label} />;
}
