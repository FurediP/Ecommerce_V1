import { useEffect, useState } from "react";
import { login, products, addToCart, getCart, checkout, myOrders, setToken } from "./api";

type Product = { id:number; name:string; price:string; vat_rate:string; size?:string|null; image_url?:string|null };
type CartItem = { id:number; product_id:number; quantity:number; unit_price:string; product: Product };
type Cart = { id:number; status:string; items:CartItem[]; totals:{ total_net:string; total_vat:string; total_gross:string } };
type OrderItem = { id:number; product_id:number; quantity:number; unit_price:string; vat_rate:string; product_name?:string };
type Order = { id:number; user_id:number; total:string; status:string; items:OrderItem[] };

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
    <div className="p-4 max-w-sm mx-auto">
      <h2>Login</h2>
      <form onSubmit={submit}>
        <label>Email<br/><input value={email} onChange={e=>setEmail(e.target.value)} /></label><br/>
        <label>Password<br/><input type="password" value={password} onChange={e=>setPassword(e.target.value)} /></label><br/>
        <button disabled={loading}>{loading ? "Entrando..." : "Entrar"}</button>
      </form>
      {err && <p style={{color:"crimson"}}>{err}</p>}
    </div>
  );
}

function CatalogView() {
  const [list, setList] = useState<Product[]>([]);
  const [q, setQ] = useState("");
  const [msg, setMsg] = useState("");

  const load = async () => {
    const data = await products(q);
    setList(data);
  };
  useEffect(() => { load(); }, []); // load al inicio

  const add = async (id:number) => {
    try { await addToCart(id, 1); setMsg("Añadido al carrito ✅"); }
    catch(e:any){ setMsg(e.message); }
  };

  return (
    <div className="p-4">
      <h2>Catálogo</h2>
      <input placeholder="Buscar..." value={q} onChange={(e)=>setQ(e.target.value)} />
      <button onClick={load}>Buscar</button>
      <p>{msg}</p>
      <ul>
        {list.map(p=>(
          <li key={p.id} style={{margin:"8px 0", borderBottom:"1px solid #eee", paddingBottom:8}}>
            <strong>{p.name}</strong> — ${p.price} (IVA {p.vat_rate}%)
            <button style={{marginLeft:8}} onClick={()=>add(p.id)}>+ Carrito</button>
          </li>
        ))}
      </ul>
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

  return (
    <div className="p-4">
      <h2>Carrito</h2>
      {!cart ? <p>Cargando…</p> : (
        <>
          <ul>
            {cart.items.map(i=>(
              <li key={i.id}>
                {i.product.name} × {i.quantity} — ${i.unit_price}
              </li>
            ))}
          </ul>
          <p><b>Neto:</b> ${cart.totals.total_net}  <b>IVA:</b> ${cart.totals.total_vat}  <b>Total:</b> ${cart.totals.total_gross}</p>
          <button onClick={doCheckout}>Checkout</button>
          <p>{msg}</p>
        </>
      )}
    </div>
  );
}

function OrdersView() {
  const [orders, setOrders] = useState<Order[]>([]);
  useEffect(() => { myOrders().then(setOrders); }, []);
  return (
    <div className="p-4">
      <h2>Mis pedidos</h2>
      <ul>
        {orders.map(o=>(
          <li key={o.id}>
            #{o.id} — {o.status} — ${o.total}
            <ul>
              {o.items.map(it=>(
                <li key={it.id}>{it.product_name} × {it.quantity}</li>
              ))}
            </ul>
          </li>
        ))}
      </ul>
    </div>
  );
}

export default function App() {
  const [view, setView] = useState<"login"|"catalog"|"cart"|"orders">(
    localStorage.getItem("token") ? "catalog" : "login"
  );

  const logout = () => { setToken(null); setView("login"); };

  return (
    <div style={{fontFamily:"system-ui, Arial", maxWidth:900, margin:"0 auto"}}>
      <header style={{display:"flex", gap:8, alignItems:"center", padding:"8px 4px", borderBottom:"1px solid #eee"}}>
        <h1 style={{marginRight:"auto"}}>Ecommerce Local</h1>
        {view!=="login" && <>
          <button onClick={()=>setView("catalog")}>Catálogo</button>
          <button onClick={()=>setView("cart")}>Carrito</button>
          <button onClick={()=>setView("orders")}>Pedidos</button>
          <button onClick={logout}>Salir</button>
        </>}
      </header>

      {view==="login" && <LoginView onLogged={()=>setView("catalog")} />}
      {view==="catalog" && <CatalogView />}
      {view==="cart" && <CartView />}
      {view==="orders" && <OrdersView />}
    </div>
  );
}
