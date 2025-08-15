import { useEffect, useState } from "react";
import { login, products, addToCart, getCart, checkout, myOrders, setToken } from "./api";

/* ===== Tipos básicos ===== */
type Product = { id:number; name:string; price:string; vat_rate:string; size?:string|null; image_url?:string|null };
type CartItem = { id:number; product_id:number; quantity:number; unit_price:string; product: Product };
type Cart = { id:number; status:string; items:CartItem[]; totals:{ total_net:string; total_vat:string; total_gross:string } };
type OrderItem = { id:number; product_id:number; quantity:number; unit_price:string; vat_rate:string; product_name?:string };
type Order = { id:number; user_id:number; total:string; status:string; items:OrderItem[] };

/* ===== Componentes UI ===== */

function Badge({ children, color="blue"}:{children:React.ReactNode;color?: "blue"|"green"|"slate"|"amber"}) {
  const map:any = { blue:"bg-blue-600/20 text-blue-300", green:"bg-green-600/20 text-green-300", slate:"bg-slate-700/50 text-slate-300", amber:"bg-amber-600/20 text-amber-300" };
  return <span className={`px-2 py-0.5 rounded-full text-xs ${map[color]}`}>{children}</span>;
}

function Header({ view, setView, onLogout }:{ view:string; setView:(v:any)=>void; onLogout:()=>void }) {
  const Tab = ({id,label}:{id:string;label:string}) => (
    <button
      onClick={()=>setView(id)}
      className={`px-3 py-1.5 rounded-lg border transition
        ${view===id ? "bg-slate-800 border-slate-700 text-white"
                    : "bg-slate-900 border-slate-800 text-slate-300 hover:bg-slate-800"}`}
    >{label}</button>
  );
  return (
    <header className="sticky top-0 z-10 border-b border-slate-800 bg-slate-950/80 backdrop-blur">
      <div className="mx-auto max-w-6xl px-4 py-4 flex items-center gap-2">
        <h1 className="text-3xl font-black mr-auto">Ecommerce Local</h1>
        <Tab id="catalog" label="Catálogo"/>
        <Tab id="cart" label="Carrito"/>
        <Tab id="orders" label="Pedidos"/>
        <button onClick={onLogout} className="px-3 py-1.5 rounded-lg bg-slate-800 text-slate-200 border border-slate-700 hover:bg-slate-700">
          Salir
        </button>
      </div>
    </header>
  );
}

function ProductCard({ p, onAdd }:{ p:Product; onAdd:(id:number)=>void }) {
  return (
    <div className="group rounded-2xl border border-slate-800 bg-slate-900/60 hover:bg-slate-900 transition overflow-hidden">
      <div className="aspect-[4/3] bg-slate-800/50 flex items-center justify-center">
        {p.image_url
          ? <img src={p.image_url} className="h-full w-full object-cover" />
          : <span className="text-slate-500">sin imagen</span>}
      </div>
      <div className="p-4 flex flex-col gap-2">
        <div className="flex items-start justify-between gap-2">
          <h3 className="font-semibold leading-tight">{p.name}</h3>
          <Badge>{p.vat_rate}% IVA</Badge>
        </div>
        {p.size && <p className="text-xs text-slate-400">Talla: {p.size}</p>}
        <div className="flex items-center justify-between mt-2">
          <div className="text-xl font-bold">${Number(p.price).toLocaleString()}</div>
          <button
            onClick={()=>onAdd(p.id)}
            className="px-3 py-1.5 rounded-xl bg-brand-600 hover:bg-brand-700 text-white shadow-sm"
          >
            + Carrito
          </button>
        </div>
      </div>
    </div>
  );
}

function Empty({title,subtitle}:{title:string;subtitle?:string}) {
  return (
    <div className="py-16 text-center text-slate-400">
      <p className="text-lg">{title}</p>
      {subtitle && <p className="text-sm mt-1">{subtitle}</p>}
    </div>
  );
}

/* ===== Vistas ===== */

function LoginView({ onLogged }: { onLogged: () => void }) {
  const [email, setEmail] = useState("admin@shop.com");
  const [password, setPassword] = useState("Admin123!");
  const [loading, setLoading] = useState(false);
  const [err, setErr] = useState<string | null>(null);

  const submit = async (e: React.FormEvent) => {
    e.preventDefault();
    try {
      setLoading(true); setErr(null);
      await login(email, password);
      onLogged();
    } catch (e:any) {
      setErr(e.message);
    } finally { setLoading(false); }
  };

  return (
    <div className="min-h-dvh grid place-items-center">
      <form onSubmit={submit} className="w-full max-w-sm rounded-2xl border border-slate-800 bg-slate-900/60 p-6 space-y-3">
        <h2 className="text-2xl font-semibold">Iniciar sesión</h2>
        <div>
          <label className="text-sm text-slate-300">Email</label>
          <input className="mt-1 w-full rounded-lg bg-slate-950 border-slate-800" value={email} onChange={e=>setEmail(e.target.value)} />
        </div>
        <div>
          <label className="text-sm text-slate-300">Password</label>
          <input type="password" className="mt-1 w-full rounded-lg bg-slate-950 border-slate-800" value={password} onChange={e=>setPassword(e.target.value)} />
        </div>
        <button disabled={loading} className="w-full rounded-xl bg-brand-600 hover:bg-brand-700 py-2 font-medium">
          {loading ? "Entrando..." : "Entrar"}
        </button>
        {err && <p className="text-rose-400 text-sm">{err}</p>}
      </form>
    </div>
  );
}

function CatalogView({ onGoCart }:{ onGoCart:()=>void }) {
  const [list, setList] = useState<Product[]>([]);
  const [q, setQ] = useState("");
  const [msg, setMsg] = useState("");

  const load = async () => { setList(await products(q)); };
  useEffect(() => { load(); }, []);

  const add = async (id:number) => {
    try {
      await addToCart(id, 1);
      setMsg("Añadido al carrito ✅");
      setTimeout(()=>setMsg(""), 2000);
      onGoCart();
    } catch(e:any){ setMsg(e.message); }
  };

  return (
    <div className="mx-auto max-w-6xl p-4">
      <div className="flex items-center gap-2 mb-4">
        <input
          placeholder="Buscar en el catálogo…"
          value={q}
          onChange={(e)=>setQ(e.target.value)}
          className="w-full rounded-xl bg-slate-900 border-slate-800"
        />
        <button onClick={load} className="px-4 py-2 rounded-xl bg-slate-800 hover:bg-slate-700">Buscar</button>
      </div>

      {msg && <div className="mb-4 text-emerald-300">{msg}</div>}

      {list.length === 0 ? (
        <Empty title="Sin resultados" subtitle="Prueba con 'camiseta', 'jeans' o deja vacío para ver todo." />
      ) : (
        <div className="grid gap-4 sm:grid-cols-2 lg:grid-cols-3">
          {list.map(p => <ProductCard key={p.id} p={p} onAdd={add} />)}
        </div>
      )}
    </div>
  );
}

function CartView() {
  const [cart, setCart] = useState<Cart | null>(null);
  const [msg, setMsg] = useState("");

  const load = async () => setCart(await getCart());
  useEffect(() => { load(); }, []);

  const doCheckout = async () => {
    try {
      const order = await checkout();
      setMsg(`Pedido creado #${order.id} ✅`);
      await load();
    } catch (e:any) {
      setMsg(e.message);
    }
  };

  if (!cart) return <div className="p-6">Cargando…</div>;

  return (
    <div className="mx-auto max-w-4xl p-4 space-y-4">
      {cart.items.length === 0 ? (
        <Empty title="Tu carrito está vacío" />
      ) : (
        <div className="rounded-2xl border border-slate-800 overflow-hidden">
          <table className="w-full text-sm">
            <thead className="bg-slate-900">
              <tr className="text-left">
                <th className="px-4 py-3">Producto</th>
                <th className="px-4 py-3">Cant.</th>
                <th className="px-4 py-3">Precio</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-slate-800">
              {cart.items.map(it=>(
                <tr key={it.id} className="bg-slate-950">
                  <td className="px-4 py-3">{it.product.name}</td>
                  <td className="px-4 py-3">{it.quantity}</td>
                  <td className="px-4 py-3">${Number(it.unit_price).toLocaleString()}</td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      )}

      <div className="flex items-center justify-between">
        <div className="text-slate-300">
          Neto: <b>${Number(cart.totals.total_net).toLocaleString()}</b> ·
          IVA: <b>${Number(cart.totals.total_vat).toLocaleString()}</b> ·
          Total: <b>${Number(cart.totals.total_gross).toLocaleString()}</b>
        </div>
        <button onClick={doCheckout} className="px-4 py-2 rounded-xl bg-brand-600 hover:bg-brand-700">
          Checkout
        </button>
      </div>

      {msg && <p className="text-emerald-300">{msg}</p>}
    </div>
  );
}

function OrdersView() {
  const [orders, setOrders] = useState<Order[]>([]);
  useEffect(() => { myOrders().then(setOrders); }, []);
  return (
    <div className="mx-auto max-w-4xl p-4 space-y-4">
      {orders.length===0 ? <Empty title="Aún no tienes pedidos" /> : orders.map(o=>(
        <div key={o.id} className="rounded-2xl border border-slate-800 p-4 bg-slate-900/40">
          <div className="flex items-center justify-between">
            <div className="font-semibold">Pedido #{o.id}</div>
            <div className="flex items-center gap-2">
              <Badge color={o.status==="paid" ? "green" : o.status==="created" ? "blue" : "slate"}>
                {o.status}
              </Badge>
              <div className="text-lg font-bold">${Number(o.total).toLocaleString()}</div>
            </div>
          </div>
          <ul className="mt-2 text-sm text-slate-300 list-disc ml-6">
            {o.items.map(it=>(
              <li key={it.id}>{it.product_name} × {it.quantity}</li>
            ))}
          </ul>
        </div>
      ))}
    </div>
  );
}

/* ===== App ===== */

export default function App() {
  const [view, setView] = useState<"login"|"catalog"|"cart"|"orders">(
    localStorage.getItem("token") ? "catalog" : "login"
  );

  const logout = () => { setToken(null); setView("login"); };

  if (view==="login") return <LoginView onLogged={()=>setView("catalog")} />;

  return (
    <div>
      <Header view={view} setView={setView} onLogout={logout}/>
      {view==="catalog" && <CatalogView onGoCart={()=>setView("cart")} />}
      {view==="cart" && <CartView />}
      {view==="orders" && <OrdersView />}
    </div>
  );
}
