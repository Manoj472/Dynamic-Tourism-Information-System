/* ================================================================
   script.js  —  ALL JS for the entire project
   Handles: navbar, mobile menu, carousel, scroll animations,
            accommodation reveal, contact form, geolocation,
            API fetching, dynamic card rendering
================================================================ */


/* ── Navbar & Mobile Menu ─────────────────────────────────── */
document.addEventListener('DOMContentLoaded', function () {

  const menuToggle = document.querySelector('.menu-toggle');
  const mobileNav  = document.querySelector('.mobile-nav');

  if (menuToggle && mobileNav) {
    menuToggle.addEventListener('click', function () {
      mobileNav.classList.toggle('active');
      menuToggle.classList.toggle('active');
    });
  }

  const mobileDropdownTriggers = document.querySelectorAll('.mobile-nav .has-dropdown');
  const mobileSubTriggers      = document.querySelectorAll('.mobile-nav .has-subdropdown');

  mobileDropdownTriggers.forEach(trigger => {
    trigger.addEventListener('click', function (e) {
      e.preventDefault();
      mobileDropdownTriggers.forEach(other => {
        if (other !== this) {
          other.classList.remove('active');
          const sib = other.nextElementSibling;
          if (sib) sib.classList.remove('active');
        }
      });
      this.classList.toggle('active');
      const dd = this.nextElementSibling;
      if (dd) dd.classList.toggle('active');
    });
  });

  mobileSubTriggers.forEach(trigger => {
    trigger.addEventListener('click', function (e) {
      e.preventDefault();
      mobileSubTriggers.forEach(other => {
        if (other !== this) {
          other.classList.remove('active');
          const sib = other.nextElementSibling;
          if (sib) sib.classList.remove('active');
        }
      });
      this.classList.toggle('active');
      const sub = this.nextElementSibling;
      if (sub) sub.classList.toggle('active');
    });
  });

  document.addEventListener('click', function (e) {
    if (!e.target.closest('.custom-navbar')) {
      if (mobileNav)  mobileNav.classList.remove('active');
      if (menuToggle) menuToggle.classList.remove('active');
      document.querySelectorAll('.mobile-dropdown, .mobile-subdropdown')
              .forEach(d => d.classList.remove('active'));
      document.querySelectorAll('.has-dropdown, .has-subdropdown')
              .forEach(i => i.classList.remove('active'));
      document.querySelectorAll('.dropdown-submenu')
              .forEach(m => m.style.display = 'none');
    }
  });

  window.addEventListener('resize', function () {
    if (window.innerWidth > 768) {
      if (mobileNav)  mobileNav.classList.remove('active');
      if (menuToggle) menuToggle.classList.remove('active');
      document.querySelectorAll('.mobile-dropdown, .mobile-subdropdown')
              .forEach(d => d.classList.remove('active'));
      document.querySelectorAll('.has-dropdown, .has-subdropdown')
              .forEach(i => i.classList.remove('active'));
    }
  });

});


/* ── Destination Carousel ─────────────────────────────────── */
/* ── Accommodation Horizontal Scroll & Tilt ───────────────── */
/* ── Accommodation Section Scroll Reveal ──────────────────── */
document.addEventListener('DOMContentLoaded', function () {
  const grid = document.getElementById('accommodation-grid');
  if (!grid) return;

  function checkScroll() {
    if (grid.getBoundingClientRect().top < window.innerHeight - 100) {
      grid.classList.add('animate-cards');
      window.removeEventListener('scroll', checkScroll);
    }
  }
  window.addEventListener('scroll', checkScroll);
  checkScroll();
});


/* ── Activity Filter Buttons ──────────────────────────────── */
function initActivityFilter() {
  document.querySelectorAll('.filter-btn').forEach(btn => {
    btn.addEventListener('click', () => {
      document.querySelectorAll('.filter-btn').forEach(b => b.classList.remove('active'));
      btn.classList.add('active');
      const filter = btn.dataset.filter;
      document.querySelectorAll('.grid-item').forEach(item => {
        item.style.display = (filter === 'all' || item.classList.contains(filter)) ? '' : 'none';
      });
    });
  });
}
// Run once for any statically rendered grids; called again after dynamic render
initActivityFilter();


/* ── Activity Cards Scroll-Reveal Observer ────────────────── */
const appearObserver = new IntersectionObserver(entries => {
  entries.forEach(e => {
    if (e.isIntersecting) {
      e.target.classList.add('show');
      appearObserver.unobserve(e.target);
    }
  });
}, { threshold: 0.1 });

function observeGridItems() {
  document.querySelectorAll('.grid-item').forEach(item => appearObserver.observe(item));
}
observeGridItems(); // for static grids on other pages


/* ── Contact Form ─────────────────────────────────────────── */
document.addEventListener('DOMContentLoaded', function () {
  const form = document.querySelector('form');
  if (!form) return;

  form.addEventListener('submit', function (e) {
    if (form.dataset.contactForm === 'true') return;

    e.preventDefault();
    const name    = document.getElementById('name')?.value.trim();
    const email   = document.getElementById('email')?.value.trim();
    const message = document.getElementById('message')?.value.trim();

    if (!name || !email || !message) {
      alert('Please fill in all required fields.');
      return;
    }

    alert('Thank you for your message! We will get back to you soon.');
    form.reset();
  });
});


/* ================================================================
   DYNAMIC DATA LOADING  (index page only — functions are safe to
   define globally; they only run when the elements exist on page)
================================================================ */

/* ── Category icon & colour maps ─────────────────────────── */
const CATEGORY_ICONS = {
  "Beach":      "fas fa-umbrella-beach",
  "Park":       "fas fa-tree",
  "Temple":     "fas fa-place-of-worship",
  "Museum":     "fas fa-landmark",
  "Monument":   "fas fa-chess-rook",
  "Hill":       "fas fa-mountain",
  "Lake":       "fas fa-water",
  "Adventure":  "fas fa-hiking",
  "Historical": "fas fa-scroll",
  "Other":      "fas fa-map-marker-alt",
};

const CATEGORY_COLORS = {
  "Beach":      "#0ea5e9",
  "Park":       "#22c55e",
  "Temple":     "#f59e0b",
  "Museum":     "#8b5cf6",
  "Monument":   "#ef4444",
  "Hill":       "#10b981",
  "Lake":       "#06b6d4",
  "Adventure":  "#f97316",
  "Historical": "#a78bfa",
  "Other":      "#6b7280",
};


/* ── Skeleton helpers ─────────────────────────────────────── */
function colSkeletons(count) {
  return Array(count).fill(`
    <div class="col-md-4 mb-4">
      <div class="skeleton-card">
        <div class="skeleton skeleton-img"></div>
        <div class="skeleton skeleton-line"></div>
        <div class="skeleton skeleton-line short"></div>
      </div>
    </div>`).join('');
}

function plainSkeletons(count, tall = false) {
  return Array(count).fill(`
    <div class="skeleton-card">
      <div class="skeleton skeleton-img${tall ? ' tall' : ''}"></div>
      <div class="skeleton skeleton-line"></div>
      <div class="skeleton skeleton-line short"></div>
    </div>`).join('');
}

function showError(id, msg) {
  const el = document.getElementById(id);
  if (el) el.innerHTML = `<div class="no-data-msg"><i class="fas fa-exclamation-circle"></i> ${msg}</div>`;
}



/* ── Render: Attractions ──────────────────────────────────── */
function renderAttractions(list) {
  const el = document.getElementById('attractions-grid');
  if (!el) return;

  if (!list.length) {
    el.innerHTML = '<p class="no-data-msg"><i class="fas fa-map-marker-alt"></i> No attractions found near you.</p>';
    return;
  }

  el.innerHTML = list.map(a => {
    const icon  = CATEGORY_ICONS[a.category]  || CATEGORY_ICONS["Other"];
    const color = CATEGORY_COLORS[a.category] || CATEGORY_COLORS["Other"];
    const stars = a.rating
      ? `<span class="rating-badge" style="background:${color}22; color:${color};">⭐ ${parseFloat(a.rating).toFixed(1)}</span>` : '';

    const directionsUrl = `https://www.google.com/maps/search/${encodeURIComponent(a.name)}`;
    return `
      <div class="attraction-card">
        <div class="attraction-card-header" style="background:${color};">
          <i class="${icon}"></i>
          <span class="category-badge">${a.category}</span>
        </div>
        <div class="attraction-card-body">
          <h5 class="attraction-title">${a.name}</h5>
          ${a.address ? `<p class="attraction-address"><i class="fas fa-map-pin"></i> ${a.address}</p>` : ''}
          ${stars}
          <a href="${directionsUrl}" target="_blank" rel="noopener" class="directions-btn attraction-directions">
            <i class="fas fa-directions"></i> Directions
          </a>
        </div>
      </div>`;
  }).join('');
}


/* ── Render: Accommodations ───────────────────────────────── */
function renderAccommodations(list) {
  const el = document.getElementById('accommodation-grid');
  if (!el) return;

  if (!list.length) {
    el.innerHTML = '<p class="no-data-msg"><i class="fas fa-bed"></i> No accommodations found near you.</p>';
    return;
  }

  el.innerHTML = list.map(a => {
    const palettes = [
      ['#4338ca', '#7c3aed'],
      ['#0369a1', '#0891b2'],
      ['#047857', '#10b981'],
      ['#b45309', '#f59e0b'],
      ['#be123c', '#e11d48'],
    ];
    const colorIndex = [...a.name].reduce((t, c) => t + c.charCodeAt(0), 0) % palettes.length;
    const [colorStart, colorEnd] = palettes[colorIndex];
    const initial = (a.name.trim()[0] || 'H').toUpperCase();
    const stars = a.rating
      ? `<span class="rating-badge">⭐ ${parseFloat(a.rating).toFixed(1)}</span>` : '';
    const phone = a.phone
      ? `<p class="acc-meta"><i class="fas fa-phone"></i> ${a.phone}</p>` : '';
    const web = a.website
      ? `<a href="${a.website}" target="_blank" class="acc-link"><i class="fas fa-external-link-alt"></i> Visit site</a>` : '';

    const hasCoords = Number.isFinite(Number(a.latitude)) && Number.isFinite(Number(a.longitude));
    const directionsUrl = hasCoords
      ? `https://www.google.com/maps/dir/?api=1&destination=${a.latitude},${a.longitude}`
      : `https://www.google.com/maps/search/${encodeURIComponent(a.name)}`;

    return `
      <div class="accommodation-card">
        
        <div class="card-content">
          <a class="card-title">${a.name}</a>
          ${a.address ? `<p class="acc-address"><i class="fas fa-map-pin"></i> ${a.address}</p>` : ''}
          ${stars}${phone}
          <div class="acc-actions">
            ${web}
            <a href="${directionsUrl}" target="_blank" rel="noopener" class="directions-btn acc-directions">
              <i class="fas fa-directions"></i> Directions
            </a>
          </div>
        </div>
      </div>`;
  }).join('');
}

/* ── Render: Activities ───────────────────────────────────── */
function renderActivities(list) {
  const el = document.getElementById('activities-grid');
  if (!el) return;

  if (!list.length) {
    el.innerHTML = '<p class="no-data-msg"><i class="fas fa-running"></i> No activities available yet for your city.</p>';
    return;
  }

  el.innerHTML = list.map(a => {
    const categoryLabels = {
      'outdoor-adventure': 'Outdoor & Adventure',
      outdoor: 'Outdoor & Adventure',
      adventure: 'Outdoor & Adventure',
      nature: 'Nature',
      entertainment: 'Entertainment',
      sports: 'Sports',
      mindfulness: 'Mindfulness'
    };
    const categoryIcons = {
      'Outdoor & Adventure': 'fa-mountain',
      Nature: 'fa-tree',
      Entertainment: 'fa-film',
      Sports: 'fa-futbol',
      Mindfulness: 'fa-spa'
    };
    const rawCategory = a.category || '';
    const categoryKey = rawCategory.toString().toLowerCase().replace(/&/g, ' ').replace(/\s+/g, '-').replace(/-+/g, '-').replace(/^-|-$/g, '');
    const categoryLabel = categoryLabels[categoryKey] || rawCategory || 'Activity';
    const icon = categoryIcons[categoryLabel] || 'fa-running';
    const description = a.description || 'Discover this amazing activity.';
    const currentCity = document.getElementById('page-data')?.dataset.city ||
      document.getElementById('hero-city-name')?.textContent ||
      'Current City';
    const directionsUrl = `https://www.google.com/maps/search/?api=1&query=${encodeURIComponent(a.name)}`;
    return `
      <div class="grid-item ${a.category}">
        <article class="activity-info-card">
          <header class="activity-card-header">
            <i class="fas ${icon}" aria-hidden="true"></i>
            <h4>${a.name}</h4>
          </header>
          <div class="activity-card-body">
            <p class="activity-city"><i class="fas fa-location-dot" aria-hidden="true"></i> ${currentCity}</p>
            <span class="activity-category-badge ${categoryKey}"><i class="fas fa-tag" aria-hidden="true"></i> ${categoryLabel}</span>
            <p class="activity-description"><i class="fas fa-note-sticky" aria-hidden="true"></i> ${description}</p>
          </div>
          <footer class="activity-card-actions">
            <a class="directions-btn activity-btn activity-btn-secondary" href="${directionsUrl}" target="_blank" rel="noopener">
              <i class="fas fa-directions" aria-hidden="true"></i> Directions
            </a>
          </footer>
        </article>
      </div>`;
  }).join('');

  initActivityFilter();
  observeGridItems();
}


/* ── AJAX fetchers ────────────────────────────────────────── */
function escapeNavText(value) {
  const span = document.createElement('span');
  span.textContent = value || '';
  return span.innerHTML;
}

function safeNavUrl(value, fallback) {
  try {
    const url = new URL(value, window.location.origin);
    return ['http:', 'https:'].includes(url.protocol) ? url.href : fallback;
  } catch {
    return fallback;
  }
}

function updateNavMenus(kind, list) {
  const desktop = document.getElementById(`desktop-${kind}-menu`);
  const mobile = document.getElementById(`mobile-${kind}-menu`);
  if (!desktop && !mobile) return;

  const config = {
    destinations: {
      icon: 'fas fa-map-marker-alt',
      href: () => '/#destination',
      label: item => `${item.name} (${item.category || 'Attraction'})`
    },
    accommodations: {
      icon: 'fas fa-hotel',
      href: item => safeNavUrl(item.website, '/#accommodation'),
      label: item => item.name
    },
    activities: {
      icon: 'fas fa-running',
      href: item => `/activity/${encodeURIComponent(item.slug)}/`,
      label: item => item.name
    }
  }[kind];

  const items = list.slice(0, 12);
  const section = kind === 'destinations'
    ? 'destination'
    : (kind === 'accommodations' ? 'accommodation' : 'activities');
  const html = items.length
    ? items.map(item => {
        const href = escapeNavText(config.href(item));
        const label = escapeNavText(config.label(item));
        const external = kind === 'accommodations' && item.website
          ? ' target="_blank" rel="noopener noreferrer"'
          : '';
        return `<li><a href="${href}"${external}><i class="${config.icon}"></i> ${label}</a></li>`;
      }).join('')
    : `<li><a href="/#${section}"><i class="fas fa-circle-info"></i> None available in this city</a></li>`;

  if (desktop) desktop.innerHTML = html;
  if (mobile) mobile.innerHTML = html;
}

async function fetchAttractions() {
  const el = document.getElementById('attractions-grid');
  if (el) el.innerHTML = colSkeletons(6);
  try {
    const res  = await fetch('/api/attractions/');
    const data = await res.json();
    renderAttractions(data.attractions || []);
    updateNavMenus('destinations', data.attractions || []);
  } catch {
    showError('attractions-grid', 'Failed to load attractions.');
    updateNavMenus('destinations', []);
  }
}

async function fetchAccommodations() {
  const el = document.getElementById('accommodation-grid');
  if (el) el.innerHTML = plainSkeletons(5);
  try {
    const res  = await fetch('/api/accommodations/');
    const data = await res.json();
    renderAccommodations(data.accommodations || []);
    updateNavMenus('accommodations', data.accommodations || []);
  } catch {
    showError('accommodation-grid', 'Failed to load accommodations.');
    updateNavMenus('accommodations', []);
  }
}

async function fetchActivities() {
  const el = document.getElementById('activities-grid');
  if (el) el.innerHTML = plainSkeletons(4, true);
  try {
    const res  = await fetch('/api/activities/');
    const data = await res.json();
    renderActivities(data.activities || []);
    updateNavMenus('activities', data.activities || []);
  } catch {
    showError('activities-grid', 'Failed to load activities.');
    updateNavMenus('activities', []);
  }
}

function loadAllSections() {
  fetchAttractions();
  fetchAccommodations();
  fetchActivities();
}


/* ── Update hero UI after city is known ──────────────────── */
function setCityUI(cityName) {
  // Hero states
  const stateDetecting = document.getElementById('state-detecting');
  const stateDenied    = document.getElementById('state-denied');
  const stateFound     = document.getElementById('state-found');
  const heroCityName   = document.getElementById('hero-city-name');

  if (stateDetecting) stateDetecting.style.display = 'none';
  if (stateDenied)    stateDenied.style.display    = 'none';
  if (stateFound)     stateFound.style.display     = 'block';
  if (heroCityName)   heroCityName.textContent     = cityName;

  // Navbar logo last text node
  const logo = document.querySelector('.logo');
  if (logo) {
    // The logo contains an <img> then text "Visit Vizag"
    // Replace the text node at the end
    const nodes = Array.from(logo.childNodes);
    const textNode = nodes.find(n => n.nodeType === Node.TEXT_NODE && n.textContent.trim());
    if (textNode) textNode.textContent = ` Visit ${cityName}`;
  }

  // About section heading
  const aboutCity = document.getElementById('about-city-name');
  if (aboutCity) aboutCity.textContent = cityName;
}


/* ── Main geolocation flow (runs only on index page) ─────── */
document.addEventListener('DOMContentLoaded', async function () {

  // Only run if the index page data element exists
  const pageData = document.getElementById('page-data');
  if (!pageData) {
    loadAllSections();
    return;
  }

  // ① Session already has city → render immediately, no prompt needed
  const sessionCity = pageData.dataset.city || '';
  if (sessionCity) {
    setCityUI(sessionCity);
    loadAllSections();
    fetchCityDescription();
    return;
  }

  // ② No session city → ask browser for geolocation
  if (!navigator.geolocation) {
    const stateDetecting = document.getElementById('state-detecting');
    const stateDenied    = document.getElementById('state-denied');
    if (stateDetecting) stateDetecting.style.display = 'none';
    if (stateDenied)    stateDenied.style.display    = 'block';
    return;
  }

  navigator.geolocation.getCurrentPosition(

    // ── Success ──────────────────────────────────────────────
    async function (pos) {
      try {
        const lat = pos.coords.latitude;
        const lon = pos.coords.longitude;

        // Send to Django → Nominatim reverse geocode → saves to session
        const res  = await fetch(`/detect-location/?lat=${lat}&lon=${lon}`);
        const data = await res.json();

        const city = data.city || 'your area';
        setCityUI(city);
        loadAllSections();
        fetchCityDescription();

      } catch (err) {
        console.error('Location detection failed:', err);
        const detected = document.getElementById('detected-city');
        if (detected) detected.textContent = 'Could not detect your city.';
      }
    },

    // ── Denied / Error ────────────────────────────────────────
    function (err) {
      console.warn('Geolocation denied:', err.message);
      const stateDetecting = document.getElementById('state-detecting');
      const stateDenied    = document.getElementById('state-denied');
      if (stateDetecting) stateDetecting.style.display = 'none';
      if (stateDenied)    stateDenied.style.display    = 'block';
    },

    { timeout: 10000, maximumAge: 300000 }
  );

});


async function fetchCityDescription() {
  try {
    const res  = await fetch('/api/city-description/');
    if (!res.ok) throw new Error(`HTTP ${res.status}`);
    const data = await res.json();
 
    // Hide skeleton, show content
    const skeleton = document.getElementById('about-skeleton');
    const content  = document.getElementById('about-city-content');
    if (skeleton) skeleton.style.display = 'none';
    if (content)  content.style.display  = 'block';
 
    // City name heading
    const titleEl = document.getElementById('about-city-title');
    const cityName = document.getElementById('about-city-name')?.textContent || '';
    if (titleEl) titleEl.textContent = cityName;
 
    // Description — trim to 4 sentences for readability
    const descEl = document.getElementById('about-city-desc');
    if (descEl) {
      const full      = data.summary || 'No description available.';
      const sentences = full.match(/[^.!?]+[.!?]+/g) || [full];
      descEl.textContent = sentences.slice(0, 4).join(' ');
    }
 
    // Wikipedia image
    if (data.image_url) {
      const img = document.getElementById('about-city-img');
      if (img) {
        img.src = data.image_url;
        img.alt = cityName;
      }
    }
 
    // Wikipedia link
    if (data.wiki_url) {
      const link = document.getElementById('about-city-wiki');
      if (link) {
        link.href            = data.wiki_url;
        link.style.display   = 'inline-block';
      }
    }
 
    // Dynamic tags based on description keywords
    const tags     = buildCityTags(data.summary || '');
    const tagsEl   = document.getElementById('about-city-tags');
    if (tagsEl) {
      tagsEl.innerHTML = tags.map(t => `<span class="tag">${t}</span>`).join('');
    }
 
  } catch (err) {
    console.error('City description fetch failed:', err);
    const skeleton = document.getElementById('about-skeleton');
    if (skeleton) skeleton.innerHTML = '<p class="no-data-msg">Could not load city description.</p>';
  }
}
 
 
/* ── Auto-generate tags from Wikipedia description ────────── */
function buildCityTags(text) {
  const lower = text.toLowerCase();
  const tagMap = [
    { keywords: ['beach', 'coast', 'sea', 'bay'],            tag: '🏖️ Beaches'       },
    { keywords: ['hill', 'mountain', 'ghats', 'valley'],     tag: '⛰️ Hill Stations'  },
    { keywords: ['temple', 'religion', 'shrine', 'mosque'],  tag: '🛕 Heritage'       },
    { keywords: ['port', 'industry', 'industrial'],          tag: '🏭 Industrial Hub'  },
    { keywords: ['food', 'cuisine', 'seafood', 'biryani'],   tag: '🍽️ Food Capital'   },
    { keywords: ['park', 'garden', 'forest', 'nature'],      tag: '🌿 Nature'         },
    { keywords: ['museum', 'heritage', 'historical'],        tag: '🏛️ Heritage'       },
    { keywords: ['university', 'education', 'college'],      tag: '🎓 Education'      },
    { keywords: ['festival', 'culture', 'art', 'dance'],     tag: '🎭 Culture'        },
    { keywords: ['shopping', 'market', 'mall'],              tag: '🛍️ Shopping'       },
  ];
 
  const matched = [];
  tagMap.forEach(({ keywords, tag }) => {
    if (keywords.some(kw => lower.includes(kw)) && !matched.includes(tag)) {
      matched.push(tag);
    }
  });
 
  // Return up to 5 tags; fallback to generic ones if Wikipedia had no keywords
  return matched.length ? matched.slice(0, 5) : ['🌍 Tourism', '📍 Must Visit'];
}
