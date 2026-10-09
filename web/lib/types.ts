export type StockStatus = "healthy" | "low" | "critical" | "stockout";
export type MovementType = "received" | "shipped" | "adjusted" | "transferred";
export type AlertSeverity = "info" | "warning" | "critical";

export type Sku = {
  id: string;
  sku: string;
  name: string;
  category: string;
  warehouse: string;
  bin: string;
  onHand: number;
  reserved: number;
  reorderPoint: number;
  unitCost: number;
  velocity: "fast" | "medium" | "slow";
};

export type Movement = {
  id: string;
  at: string;
  type: MovementType;
  sku: string;
  name: string;
  qty: number;
  from?: string;
  to?: string;
  note: string;
};

export type Shipment = {
  id: string;
  po: string;
  supplier: string;
  eta: string;
  status: "in-transit" | "docked" | "receiving" | "delayed";
  lines: number;
  value: number;
};

export type Alert = {
  id: string;
  severity: AlertSeverity;
  title: string;
  detail: string;
  sku?: string;
  at: string;
};

export type Store = {
  skus: Sku[];
  movements: Movement[];
  shipments: Shipment[];
  alerts: Alert[];
};

export type Kpis = {
  skus: number;
  onHandUnits: number;
  inventoryValue: number;
  fillRate: number;
  lowStock: number;
  stockouts: number;
  inbound: number;
  exceptions: number;
};
