import type { CommodityPrice, CommodityHistory } from "~/types/commodity";

export function useCommodities() {
  const config = useRuntimeConfig();
  const apiBase = config.public.apiBase;

  async function getAllPrices(): Promise<CommodityPrice[]> {
    return await $fetch<CommodityPrice[]>(`${apiBase}/api/v1/commodities`);
  }

  async function getPrice(commodity: string): Promise<CommodityPrice> {
    return await $fetch<CommodityPrice>(
      `${apiBase}/api/v1/commodities/${commodity}`
    );
  }

  async function getHistory(
    commodity: string,
    period: string = "1mo"
  ): Promise<CommodityHistory[]> {
    return await $fetch<CommodityHistory[]>(
      `${apiBase}/api/v1/commodities/${commodity}/history`,
      { params: { period } }
    );
  }

  return { getAllPrices, getPrice, getHistory };
}
