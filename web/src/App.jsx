import React, { useEffect, useState } from "react";

const STATE_ONLINE = new Set(["idle", "busy", "calibrating"]);

export default function App() {
  const [devices, setDevices] = useState([]);
  const [health, setHealth] = useState(null);
  const [error, setError] = useState(null);

  useEffect(() => {
    async function load() {
      try {
        const h = await fetch("/healthz").then((r) => r.json());
        setHealth(h);
        const d = await fetch("/devices").then((r) => r.json());
        setDevices(d.devices || []);
      } catch (e) {
        setError(String(e));
      }
    }
    load();
    const timer = setInterval(load, 5000);
    return () => clearInterval(timer);
  }, []);

  return (
    <div className="app">
      <div className="header">
        <h1>hardmesh 控制台</h1>
        <span className="badge">
          {health ? `在线设备 ${health.devices}` : "连接中..."}
        </span>
      </div>
      {error && <div className="error">无法连接控制面：{error}</div>}
      <div className="grid">
        {devices.map((d) => (
          <div className="card" key={d.device_id}>
            <h3>{d.name}</h3>
            <div className="kind">{d.kind} · {d.driver}</div>
            <div className={`state ${STATE_ONLINE.has(d.state) ? "online" : "offline"}`}>
              {d.state}
            </div>
            <div className="caps">
              {(d.capabilities || []).map((c) => (
                <span className="cap" key={c}>{c}</span>
              ))}
            </div>
          </div>
        ))}
      </div>
    </div>
  );
}
