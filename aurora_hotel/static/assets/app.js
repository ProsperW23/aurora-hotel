/* Updated app.js - connects to Flask backend at http://127.0.0.1:5000 */
const API_BASE = "http://127.0.0.1:5000/api";

async function fetchRooms(){
  try{
    const res = await fetch(`${API_BASE}/rooms`);
    const rooms = await res.json();
    renderRooms(rooms);
  }catch(e){
    console.error("Failed to fetch rooms:", e);
    document.querySelector('.room-list').innerHTML = '<p class="muted">Unable to load rooms (backend not running).</p>';
  }
}

function money(v){ return "₦" + Number(v).toLocaleString(); }

function renderRooms(rooms){
  const container = document.querySelector('.room-list');
  if(!container) return;
  container.innerHTML = rooms.map(r=>`
    <article class="room-card card">
      <img src="assets/images/room-standard.webp" alt="${r.room_type}">
      <div class="room-info">
        <h4>${r.room_type}</h4>
        <p class="muted">${r.capacity} persons · Inventory: ${r.inventory}</p>
        <p><strong>${money(r.price)}</strong> / night</p>
        <div class="room-actions">
          <button class="btn btn-outline" data-quick="${r.id}">Quick View</button>
          <a class="btn btn-primary" href="bookings.html?type=${r.id}">Book</a>
        </div>
      </div>
    </article>
  `).join('');
  // quick view handlers (simple demo)
  document.querySelectorAll('[data-quick]').forEach(btn=>{
    btn.addEventListener('click', ()=> alert('Quick view: open bookings page to book.'));
  });
}

// Booking page handling
function getQueryParam(name){
  const q = new URLSearchParams(location.search);
  return q.get(name);
}

async function submitBookingForm(e){
  e.preventDefault();
  const form = e.target;
  const formData = new FormData(form);
  const payload = {
    name: formData.get('name'),
    email: formData.get('email'),
    room_type: formData.get('type') || formData.get('room_type'),
    check_in: formData.get('check_in'),
    check_out: formData.get('check_out'),
    guests: formData.get('guests') || 1
  };
  try{
    const res = await fetch(`${API_BASE}/bookings`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(payload)
    });
    const data = await res.json();
    if(res.ok){
      document.getElementById('confirm').classList.remove('hidden');
      document.getElementById('confirmMsg').innerHTML = `Thanks ${payload.name}. Reference: <strong>${data.booking_id}</strong>.`;
      form.reset();
    }else{
      alert(data.message || "Failed to create booking");
    }
  }catch(err){
    console.error(err);
    alert("Error contacting server");
  }
}

async function loadBookingPage(){
  const type = getQueryParam('type');
  const typeInput = document.querySelector('input[name="type"]') || document.querySelector('input[name="room_type"]');
  if(type && typeInput) typeInput.value = type;
  const form = document.getElementById('bookingForm');
  if(form) form.addEventListener('submit', submitBookingForm);
}

async function loginHandler(e){
  e.preventDefault();
  const f = e.target;
  const fd = new FormData(f);
  const payload = { email: fd.get('email'), password: fd.get('password') };
  try{
    const res = await fetch(`${API_BASE}/login`, {
      method: "POST",
      headers: {"Content-Type":"application/json"},
      body: JSON.stringify(payload)
    });
    const data = await res.json();
    if(res.ok){
      localStorage.setItem('hotel_user', JSON.stringify(data));
      alert('Login successful');
      location.href = 'admin.html';
    } else {
      alert(data.message || 'Invalid credentials');
    }
  }catch(err){ console.error(err); alert('Login error'); }
}

async function loadLogin(){
  const login = document.getElementById('loginForm');
  if(login) login.addEventListener('submit', loginHandler);
}

// Admin page: load bookings
async function loadAdmin(){
  try{
    const res = await fetch(`${API_BASE}/bookings`);
    const bookings = await res.json();
    const tbody = document.querySelector('#bookingsTable tbody');
    if(tbody){
      tbody.innerHTML = bookings.map(b=>`<tr><td>${b.id}</td><td>${b.name||''}</td><td>${b.email||''}</td><td>${b.room_type}</td><td>${b.check_in}</td><td>${b.check_out}</td><td>${b.status}</td></tr>`).join('');
    }
    const kpi = document.getElementById('kpiBookings');
    if(kpi) kpi.textContent = bookings.length;
  }catch(e){ console.error(e); }
}

// Wire up on DOM ready
document.addEventListener('DOMContentLoaded', ()=>{
  if(location.pathname.endsWith('index.html') || location.pathname.endsWith('/')) fetchRooms();
  loadBookingPage();
  loadLogin();
  if(location.pathname.endsWith('admin.html')) loadAdmin();
});