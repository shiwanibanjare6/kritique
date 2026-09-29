import axios from "axios";
import { getSession } from "next-auth/react";

export const apiUrl = (
  process.env.NEXT_PUBLIC_API_URL ||
  (process.env.NODE_ENV === "production"
    ? "https://kritique-6zrw.onrender.com"
    : "http://127.0.0.1:8000")
).replace(/\/$/, "");

const api = axios.create({
  baseURL: `${apiUrl}/api/v1`,
  headers: {
    "Content-Type": "application/json",
  },
});

api.interceptors.request.use(async (config) => {
  if (typeof window !== "undefined") {
    const session = await getSession();
    if (session?.accessToken) {
      config.headers.Authorization = `Bearer ${session.accessToken}`;
    }
  }
  return config;
});

export default api;
