"use client";

import { useEffect } from "react";
import { apiClient } from "@/services/api";

export function MockAxiosInterceptor({ children }: { children: React.ReactNode }) {
  useEffect(() => {
    // Intercept requests and attach the mock JWT
    const requestInterceptor = apiClient.interceptors.request.use(
      (config) => {
        config.headers.Authorization = `Bearer mock-token`;
        return config;
      },
      (error) => Promise.reject(error)
    );

    // Cleanup interceptor on unmount
    return () => {
      apiClient.interceptors.request.eject(requestInterceptor);
    };
  }, []);

  return <>{children}</>;
}
