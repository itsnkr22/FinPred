export interface CommodityPrice {
  commodity: string;
  name: string;
  unit: string;
  price: number;
  change: number;
  change_percent: number;
  high: number;
  low: number;
  open: number;
  volume: number;
  timestamp: string;
}

export interface CommodityHistory {
  date: string;
  open: number;
  high: number;
  low: number;
  close: number;
  volume: number;
}
