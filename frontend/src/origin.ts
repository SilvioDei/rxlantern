// Where distances are measured from: "Use my location" (memory only) or the ZIP / neighborhood saved in this browser.
import { useEffect, useState } from "react";
import { api } from "./api";
import { useApp, type Origin } from "./state";

export function useOrigin(): { origin: Origin | null; loading: boolean } {
  const { deviceOrigin, place } = useApp();
  const [resolved, setResolved] = useState<Origin | null>(null);
  const [loading, setLoading] = useState(false);
  useEffect(() => {
    if (deviceOrigin || !place.trim()) { setResolved(null); return; }
    let live = true;
    setLoading(true);
    api.get<{ found: boolean; label: string; latitude: number; longitude: number }>(`/api/location?place=${encodeURIComponent(place.trim())}`)
      .then((r) => { if (live) setResolved(r.found ? { lat: r.latitude, lon: r.longitude, label: r.label, fromDevice: false } : null); })
      .catch(() => { if (live) setResolved(null); })
      .finally(() => { if (live) setLoading(false); });
    return () => { live = false; };
  }, [deviceOrigin, place]);
  return { origin: deviceOrigin ?? resolved, loading };
}
