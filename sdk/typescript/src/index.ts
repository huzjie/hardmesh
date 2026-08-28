export interface DeviceSnapshot {
  device_id: string;
  name: string;
  kind: string;
  state: string;
  capabilities: string[];
  driver: string;
  last_seen: number;
}

export class HardmeshClient {
  constructor(private baseUrl: string = "http://localhost:8080") {}

  private async request<T>(method: string, path: string, body?: unknown): Promise<T> {
    const res = await fetch(this.baseUrl + path, {
      method,
      headers: { "Content-Type": "application/json" },
      body: body ? JSON.stringify(body) : undefined,
    });
    if (!res.ok) throw new Error(`HTTP ${res.status}`);
    return (await res.json()) as T;
  }

  async health(): Promise<{ status: string; devices: number }> {
    return this.request("GET", "/healthz");
  }

  async listDevices(): Promise<DeviceSnapshot[]> {
    const res = await this.request<{ devices: DeviceSnapshot[] }>("GET", "/devices");
    return res.devices;
  }

  async read(deviceId: string, channel?: string): Promise<unknown> {
    const path = `/devices/${deviceId}/read${channel ? `?channel=${channel}` : ""}`;
    const res = await this.request<{ value: unknown }>("GET", path);
    return res.value;
  }

  async act(deviceId: string, action: string, params: Record<string, unknown> = {}): Promise<unknown> {
    return this.request("POST", `/devices/${deviceId}/act`, { action, params });
  }
}
