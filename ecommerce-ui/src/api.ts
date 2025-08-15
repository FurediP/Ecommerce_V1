const AUTH_URL = import.meta.env.VITE_AUTH_URL as string;
const CATALOG_URL = import.meta.env.VITE_CATALOG_URL as string;
const CART_URL = import.meta.env.VITE_CART_URL as string;
const ORDER_URL = import.meta.env.VITE_ORDER_URL as string;

let token: string | null = localStorage.getItem("token");

export const setToken = (t: string | null) => {
  token = t;
  if (t) localStorage.setItem("token", t);
  else localStorage.removeItem("token");
};

async function http(url: string, opts: RequestInit = {}) {
  const headers: Record<string, string> = {
    "Content-Type": "application/json",
    ...(opts.headers as Record<string, string>),
  };
  if (token) headers.Authorization = `Bearer ${token}`;
  const res = await fetch(url, { ...opts, headers });
  if (!res.ok) {
    const msg = await res.text().catch(() => res.statusText);
    throw new Error(`${res.status} ${res.statusText}: ${msg}`);
  }
  const ct = res.headers.get("content-type") || "";
  return ct.includes("application/json") ? res.json() : res.text();
}

export async function login(email: string, password: string) {
  const data = await http(`${AUTH_URL}/login`, {
    method: "POST",
    body: JSON.stringify({ email, password }),
  });
  setToken(data.access_token);
  return data;
}

export async function products(q?: string) {
  const url = new URL(`${CATALOG_URL}/products`);
  if (q) url.searchParams.set("q", q);
  return http(url.toString());
}

export async function addToCart(product_id: number, quantity = 1) {
  return http(`${CART_URL}/cart/items`, {
    method: "POST",
    body: JSON.stringify({ product_id, quantity }),
  });
}

export async function getCart() {
  return http(`${CART_URL}/cart`);
}

export async function checkout() {
  return http(`${ORDER_URL}/orders/checkout`, { method: "POST" });
}

export async function myOrders() {
  return http(`${ORDER_URL}/orders`);
}
