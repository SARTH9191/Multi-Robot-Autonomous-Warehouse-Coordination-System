import { useState, useEffect, useRef, useCallback } from 'react';
import type { SimulationState } from '../types/warehouse';

export function useWarehouseSocket() {
  const [state, setState] = useState<SimulationState | null>(null);
  const [isConnected, setIsConnected] = useState<boolean>(false);
  const [error, setError] = useState<string | null>(null);
  const wsRef = useRef<WebSocket | null>(null);
  const reconnectTimeoutRef = useRef<number | null>(null);

  const connect = useCallback(() => {
    try {
      const protocol = window.location.protocol === 'https:' ? 'wss:' : 'ws:';
      const host = window.location.hostname || 'localhost';
      const wsUrl = `${protocol}//${host}:8000/ws`;

      const ws = new WebSocket(wsUrl);
      wsRef.current = ws;

      ws.onopen = () => {
        setIsConnected(true);
        setError(null);
      };

      ws.onmessage = (event) => {
        try {
          const payload = JSON.parse(event.data);
          if (payload.type === 'INIT_STATE' || payload.type === 'STATE_UPDATE') {
            setState(payload.data);
          }
        } catch (e) {
          console.error('Failed to parse WebSocket message', e);
        }
      };

      ws.onerror = (e) => {
        console.warn('WebSocket encountered error, attempting recovery...', e);
      };

      ws.onclose = () => {
        setIsConnected(false);
        wsRef.current = null;
        // Schedule reconnect
        reconnectTimeoutRef.current = window.setTimeout(() => {
          connect();
        }, 2000);
      };
    } catch (err: any) {
      setError(err?.message || 'WebSocket error');
      setIsConnected(false);
    }
  }, []);

  useEffect(() => {
    connect();
    return () => {
      if (reconnectTimeoutRef.current) {
        clearTimeout(reconnectTimeoutRef.current);
      }
      if (wsRef.current) {
        wsRef.current.close();
      }
    };
  }, [connect]);

  // Also do initial REST fetch as fallback or fast bootstrap
  useEffect(() => {
    fetch('http://localhost:8000/api/state')
      .then((res) => res.json())
      .then((data) => {
        if (!state) setState(data);
      })
      .catch(() => {
        // Backend might still be starting
      });
  }, []);

  const sendCommand = useCallback((action: string, payload: Record<string, any> = {}) => {
    if (wsRef.current && wsRef.current.readyState === WebSocket.OPEN) {
      wsRef.current.send(JSON.stringify({ action, ...payload }));
    } else {
      // Fallback to REST endpoint
      const endpointMap: Record<string, string> = {
        START: '/api/control/start',
        PAUSE: '/api/control/pause',
        STEP: '/api/control/step',
        RESET: '/api/control/reset',
      };
      if (action in endpointMap) {
        fetch(`http://localhost:8000${endpointMap[action]}`, { method: 'POST' })
          .then((res) => res.json())
          .then((res) => {
            if (res.state) setState(res.state);
          })
          .catch(console.error);
      } else if (action === 'SPEED') {
        fetch('http://localhost:8000/api/control/speed', {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({ speed: payload.value }),
        }).catch(console.error);
      } else if (action === 'LOAD_SCENARIO') {
        fetch(`http://localhost:8000/api/scenarios/${payload.scenario_id}`, { method: 'POST' })
          .then((res) => res.json())
          .then((res) => {
            if (res.state) setState(res.state);
          })
          .catch(console.error);
      }
    }
  }, [state]);

  const start = useCallback(() => sendCommand('START'), [sendCommand]);
  const pause = useCallback(() => sendCommand('PAUSE'), [sendCommand]);
  const step = useCallback(() => sendCommand('STEP'), [sendCommand]);
  const reset = useCallback(() => sendCommand('RESET'), [sendCommand]);
  const setSpeed = useCallback((val: number) => sendCommand('SPEED', { value: val }), [sendCommand]);
  const loadScenario = useCallback((id: string) => sendCommand('LOAD_SCENARIO', { scenario_id: id }), [sendCommand]);

  return {
    state,
    isConnected,
    error,
    start,
    pause,
    step,
    reset,
    setSpeed,
    loadScenario,
  };
}
