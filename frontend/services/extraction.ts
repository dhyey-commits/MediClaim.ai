import { api } from "@/services/api";

export const extractionService = {
  extract: api.claims.extract,
  icdMap: api.claims.icdMap,
};
