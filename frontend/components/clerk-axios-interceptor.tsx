"use client";

import { useAuth } from "@clerk/nextjs";
import { useEffect } from "react";
import { apiClient } from "@/services/api";

export function ClerkAxiosInterceptor({ children }: { children: React.ReactNode }) {
  const { getToken } = useAuth();

  useEffect(() => {
    // Intercept requests and attach the JWT
    const requestInterceptor = apiClient.interceptors.request.use(
      async (config) => {
        try {
          const token = await getToken();
          if (token) {
            config.headers.Authorization = `Bearer ${token}`;
            console.log("JWT attached", token.slice(0, 20));
          }
        } catch (error) {
          console.error("Error attaching Clerk token:", error);
        }
        return config;
      },
      (error) => Promise.reject(error)
    );

    // Cleanup interceptor on unmount
    return () => {
      apiClient.interceptors.request.eject(requestInterceptor);
    };
  }, [getToken]);

  return <>{children}</>;
}
