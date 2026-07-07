@import url('https://fonts.googleapis.com/css2?family=Cinzel:wght@400;500;600;700&family=Cormorant+Garamond:ital,wght@0,300;0,400;0,500;1,300;1,400&family=Raleway:wght@300;400;500;600&family=Shrikhand&display=swap');

:root {
  /* --bg-1: #080c18;
  --bg-2: #0d1430;
  --bg-3: #0a1525;
  --bg-4: #0b0d20; */
  --bg-1: #151226; 
  --bg-2: #100e1f; 
  --bg-3: #0a0914; 
  --bg-4: #07060d;
  --text: #f0e8d5;
  --muted: #c8b8e8;
  --accent-soft: #c7afea;
  --surface: rgba(20, 20, 46, 0.74);
  --surface-2: rgba(12, 26, 48, 0.78);
  --surface-border: rgba(180, 140, 255, 0.24);
  --success: #b7e7c5;
  --error: #ffd0d0;
}

* {
  box-sizing: border-box;
}

html,
body {
  min-height: 100%;
}

body {
  margin: 0;
  min-height: 100vh;
  display: flex;
  flex-direction: column;
  position:relative;
  color: var(--text);
  font-family: "Raleway", sans-serif;
  background:
    radial-gradient(circle at 8% 10%, rgba(180, 140, 255, 0.14), transparent 28%),
    radial-gradient(circle at 92% 20%, rgba(123, 200, 176, 0.08), transparent 22%),
    linear-gradient(160deg, var(--bg-1) 0%, var(--bg-2) 30%, var(--bg-3) 60%, var(--bg-4) 100%);
  overflow-x: clip;
}

body::before {
  content: "";
  position: fixed;
  inset: 0;
  pointer-events: none;
  z-index: -1;
  background-image:
    radial-gradient(0.6px 0.6px at 18% 22%, rgba(255, 255, 255, 0.45) 99%, transparent 100%),
    radial-gradient(0.7px 0.7px at 74% 31%, rgba(255, 255, 255, 0.38) 99%, transparent 100%),
    radial-gradient(0.5px 0.5px at 58% 77%, rgba(255, 255, 255, 0.32) 99%, transparent 100%),
    radial-gradient(0.6px 0.6px at 34% 64%, rgba(255, 255, 255, 0.28) 99%, transparent 100%),
    radial-gradient(0.6px 0.6px at 85% 82%, rgba(255, 255, 255, 0.28) 99%, transparent 100%),
    radial-gradient(0.5px 0.5px at 9% 82%, rgba(255, 255, 255, 0.28) 99%, transparent 100%);
  opacity: 0.9;
}

a {
  color: var(--accent-soft);
}

/* 2. Un-glue the scene from the viewport */
.cosmic-scene {
  position: absolute;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  pointer-events: none;
  z-index: 0;
  overflow: hidden;
  animation: sceneFadeIn 0.6s ease-out both;
}

@keyframes sceneFadeIn {
  from { opacity: 0; }
  to   { opacity: 1; }
}

.cosmic-sun-arc {
  position: absolute;
  top: -280px;
  left: -280px;
  width: 560px;
  height: 560px;
  border-radius: 999px;
  background: transparent;

  /* Keep the arc border but soften it slightly */
  border: 60px solid rgba(255, 208, 96, 0.22);
  border-right-color: transparent;
  border-bottom-color: transparent;

  filter: blur(0.8px);

  /* Layered glow: tight warm core + wide soft corona */
  box-shadow:
    0 0 60px  rgba(255, 200, 60, 0.20),
    0 0 140px rgba(255, 160, 30, 0.10),
    0 0 280px rgba(255, 120, 20, 0.06);
}

/* Sun disc — sits inside the arc as a circular glowing fill */
.cosmic-sun-arc::before {
  content: "";
  position: absolute;
  /* Inset by the border width so it fills the inner circle of the arc */
  inset: 60px;
  border-radius: 999px;
  background: radial-gradient(circle at 50% 50%,
    rgba(255, 230, 140, 0.28) 0%,
    rgba(255, 190, 60, 0.14) 40%,
    rgba(255, 140, 20, 0.05) 70%,
    transparent 100%
  );
  filter: blur(12px);
}

.cosmic-stars {
  position: absolute;
  inset: 0;
}

/* --- CONSTELLATION STYLES --- */
.cosmic-constellations {
  position: absolute;
  inset: 0;
  width: 100%;
  height: 100%;
  opacity: 0.96;
  pointer-events: none;
}

/* The new square wrapper */
.constellation-group {
  position: absolute;
  width: min(280px, 45vw);
  height: min(280px, 45vw);
  transform: translate3d(-50%, calc(-50% + var(--parallax-y, 0px)), 0);
  will-change: transform, opacity;
  opacity: 0.35;
  filter: drop-shadow(0 0 7px rgba(168, 210, 255, 0.16));
  transition: opacity 120ms ease, filter 120ms ease;
  animation: constellationBreathe 4s ease-in-out infinite;
}

.constellation-line {
  stroke-linecap: round;
  stroke-width: 0.8;
  transition: stroke-width 120ms ease, stroke 120ms ease, stroke-dasharray 120ms ease;
}

.constellation-group.is-lit {
  opacity: 1;
  filter: drop-shadow(0 0 16px rgba(180, 210, 255, 0.9));
  animation: none;
}

.constellation-group.is-lit .constellation-line {
  stroke-width: 1.2;
  stroke-dasharray: 0 !important; 
  stroke: rgba(220, 240, 255, 0.9);
}

.is-lit .constellation-star {
  fill: #e0f0ff;
  r: 2.5;
}

.constellation-star {
  fill: #fff;
  filter: drop-shadow(0 0 4px rgba(255, 255, 255, 0.8));
  transition: opacity 120ms ease;
}

.constellation-label {
  fill: rgba(204, 222, 255, 0.52);
  font-family: "Cinzel", serif;
  font-size: 8px; /* Bumped up for legibility */
  letter-spacing: 0.3em;
  opacity: 0.7;
}

@keyframes constellationBreathe {
  0%, 100% { opacity: 0.25; }
  50% { opacity: 0.85; }
}
.cosmic-planets {
  position: absolute;
  inset: 0;
}
/* --- SILKY SMOOTH PLANETS --- */
.cosmic-planet {
  position: absolute;
  border-radius: 50%;

  --parallax-y: 0px;
  --hover-scale: 1;

  will-change: transform;

  /* transform is owned exclusively by the JS scroll handler — nothing else touches it */
  transform: translate3d(-50%, calc(-50% + var(--parallax-y)), 0) scale(var(--hover-scale));

  opacity: 0.8;
  filter: saturate(0.9);
  backface-visibility: hidden;

  /* Only animate properties that don't conflict with transform */
  transition: opacity 150ms ease, box-shadow 150ms ease;
  animation: planetBreathe 8s ease-in-out infinite;
  animation-delay: var(--planet-delay, 0s);
}

/* Remove the old glossy ::before reflection, it makes them look like plastic marbles */
.cosmic-planet::before {
  display: none; 
}
/* A gentle wake-up on hover */
.cosmic-planet.is-active {
--hover-scale: 1.03;
  opacity: 1;
  filter: saturate(1.1) brightness(1.05) blur(0px); 
  box-shadow: 
    0 0 45px rgba(180, 190, 255, 0.25), 
    inset -12px -12px 24px rgba(20, 25, 45, 0.25);
}
/* --- THE BRIGHT FROSTED RINGS --- */
.planet-ring {
  position: absolute;
  left: 50%;
  top: 50%;
  width: 145%;
  height: 35%;
  transform: translate(-50%, -50%) rotate(-20deg);
  border-radius: 50%;
  
  /* Thicker, much brighter borders to survive the blur */
  border-top: 3px solid rgba(255, 255, 255, 0.95);
  border-bottom: 2px solid rgba(220, 230, 255, 0.65);
  border-left: 1px solid rgba(255, 255, 255, 0.15);
  border-right: 1px solid rgba(255, 255, 255, 0.15);
  
  /* Adds a milky, frosted band inside the ring itself */
  background: radial-gradient(ellipse, transparent 55%, rgba(255, 255, 255, 0.15) 65%, transparent 72%);
  
  /* Keeps the soft, icy texture */
  filter: blur(1.5px); 
  
  /* A bright, ambient starlight glow */
  box-shadow: 
    inset 0 0 12px rgba(255, 255, 255, 0.4),
    0 0 18px rgba(230, 240, 255, 0.5);
}
/* --- BOUTIQUE, DUSTY PASTEL PALETTES --- */
/* Notice how they fade into deep, muted hues of their own color family, rather than pitch black */

.palette-violet {
  background: radial-gradient(circle at 35% 35%, #bcaadb 0%, #7d6b9e 55%, #3d3254 100%);
}

.palette-blue {
  background: radial-gradient(circle at 35% 35%, #a6c0d4 0%, #5b7c96 55%, #2a3c4f 100%);
}

.palette-teal {
  background: radial-gradient(circle at 35% 35%, #a5c7be 0%, #58877a 55%, #24423a 100%);
}

.palette-amber {
  background: radial-gradient(circle at 35% 35%, #d9bba0 0%, #9c7b5c 55%, #4a3826 100%);
}

.palette-rose {
  background: radial-gradient(circle at 35% 35%, #d4a6b1 0%, #945d6a 55%, #472931 100%);
}
/* --- NEW ETHEREAL PALETTES --- */

/* Slate: A moody, storm-cloud grey-blue. Perfect for massive gas giants. */
.palette-slate {
  background: radial-gradient(circle at 35% 35%, #b2b8c2 0%, #6c7687 55%, #2a303b 100%);
}

/* Champagne: A soft, elegant ivory/beige. A great replacement for Amber. */
.palette-champagne {
  background: radial-gradient(circle at 35% 35%, #e8dcca 0%, #b09c84 55%, #4a3e31 100%);
}

/* Sage: A dusty, earthy green. Very calming and organic. */
.palette-sage {
  background: radial-gradient(circle at 35% 35%, #bcc7bc 0%, #7b8c7c 55%, #344035 100%);
}

/* Lilac: A cooler, softer purple/grey (distinct from the darker Violet). */
.palette-lilac {
  background: radial-gradient(circle at 35% 35%, #d0c4d9 0%, #8c7b99 55%, #3b2f45 100%);
}

/* Midnight: Deep twilight blue-purple, blends into the dark background. */
.palette-midnight {
  background: radial-gradient(circle at 35% 35%, #6b6a8a 0%, #383655 45%, #1a1828 100%);
}

/* Dusk-teal: Muted deep teal, much less saturated than teal. */
.palette-dusk-teal {
  background: radial-gradient(circle at 35% 35%, #4a6e6a 0%, #263f3d 50%, #101e1d 100%);
}
/* Breathing animation — opacity + glow only, transform is untouched */
@keyframes planetBreathe {
  0%, 100% {
    opacity: 0.65;
    filter: saturate(0.8) brightness(0.9);
  }
  50% {
    opacity: 0.92;
    filter: saturate(1.05) brightness(1.08);
  }
}
.container {
  width: min(1100px, 92vw);
  margin: 0 auto;
}

.site-header,
.page-content,
.site-footer {
  position: relative;
  z-index: 2;
}

/* 3. Bulletproof the Header stacking context */
.site-header {
  position: sticky;
  top: 0;
  z-index: 9999 !important; /* Massively boosted to prevent the cards from overlapping it */
  backdrop-filter: blur(8px);
  background: rgba(8, 12, 25, 0.66);
  border-bottom: 1px solid rgba(180, 140, 255, 0.18);
}

.nav-wrap {
  display: flex;
  flex-wrap: wrap;
  justify-content: space-between;
  align-items: center;
  gap: 1rem;
  padding: 1rem 0;
}

.brand {
  color: var(--text);
  text-decoration: none;
  display: flex;
  flex-direction: column;
  gap: 0.15rem;
}

.brand-title {
  font-family: "Cinzel", serif;
  font-size: 1.24rem;
  letter-spacing: 0.08em;
  text-shadow: 0 0 20px rgba(180, 140, 255, 0.3);
}

.brand-subtitle {
  font-family: "Cormorant Garamond", serif;
  font-size: 0.74rem;
  letter-spacing: 0.2em;
  text-transform: uppercase;
  color: var(--muted);
}

.main-nav {
  display: flex;
  flex-wrap: wrap;
  gap: 0.55rem;
}

.main-nav a {
  color: var(--muted);
  text-decoration: none;
  border: 1px solid transparent;
  border-radius: 999px;
  padding: 0.5rem 0.85rem;
  font-family: "Cinzel", serif;
  font-size: 0.8rem;
  letter-spacing: 0.1em;
}

.main-nav a:hover,
.main-nav a.active {
  color: var(--text);
  border-color: rgba(180, 140, 255, 0.45);
  background: rgba(140, 100, 240, 0.16);
}

.page-content {
  flex: 1 0 auto;
  padding: 2rem 0 2.5rem;
}

.page-intro {
  margin: 0 auto 2rem;
  text-align: left;
  max-width: min(1200px, 92vw);
}

.page-intro h1 {
  margin: 0 0 0.4rem;
  font-family: "Cinzel", serif;
  font-size: clamp(1.9rem, 3.8vw, 2.8rem);
  letter-spacing: 0.09em;
  text-shadow: 0 0 24px rgba(180, 140, 255, 0.35);
}

/* Home title stays centered — it's a brand statement */
.home-intro {
  text-align: center;
  margin-bottom: 0.5rem;
}
.home-intro h1 {
  font-family: 'Shrikhand', cursive; /* Google Fonts classifies it with a cursive fallback */
  font-weight: 400; /* Shrikhand is only available in 400 weight */
  font-size: clamp(2.2rem, 4.5vw, 3.2rem); /* Slightly scaled down because it is a very wide font */
  letter-spacing: 0.02em; /* Adds a tiny bit of space so the thick letters don't bleed together */
  text-transform: none; 
  /* A soft glow looks great behind the heavy letters */
  text-shadow: 0 0 28px rgba(180, 140, 255, 0.45); 
}
.home-intro .lede {
  text-transform: uppercase;
  letter-spacing: 0.18em;
  font-size: 1.03rem;
}

/* --- HEADER STYLE 1: shared card headers — Home, Pricing, Trainings --- */
.section-header {
  margin: 0 0 0.5rem;
  font-family: "Cinzel", serif;
  letter-spacing: 0.04em;
  color: #d4a84b;
  text-shadow: 0 0 14px rgba(212, 168, 75, 0.3);
}

.section-header::after {
  content: "";
  display: block;
  width: 4rem;
  height: 1px;
  margin-top: 0.35rem;
  background: linear-gradient(to right, rgba(180, 140, 255, 0.5), transparent);
}

/* --- SUB-HEADER: credentials, roles, secondary titles under a section-header --- */
.sub-header {
  margin: -0.2rem 0 0.9rem;
  font-family: "Cormorant Garamond", serif;
  font-size: 0.88rem;
  font-style: italic;
  letter-spacing: 0.14em;
  text-transform: none;
  color: var(--muted);
  opacity: 0.85;
}

/* --- HEADER STYLE 2: resource card titles — smaller, reserved height for alignment --- */
.resource-title {
  font-size: 0.95rem;
  color: #d4a84b;
  text-shadow: 0 0 14px rgba(212, 168, 75, 0.3);
  min-height: 2.8rem;
  display: flex;
  align-items: flex-start;
  margin: 0 0 0.5rem;
  font-family: "Cinzel", serif;
  letter-spacing: 0.04em;
}

.info-card-purple .section-header::after {
  background: linear-gradient(to right, rgba(255, 208, 96, 0.5), transparent);
}

.info-card-teal .section-header::after {
  background: linear-gradient(to right, rgba(120, 200, 176, 0.5), transparent);
}

.info-card-blue .section-header::after {
  background: linear-gradient(to right, rgba(120, 190, 255, 0.5), transparent);
}

h2,
h3 {
  margin: 0 0 0.5rem;
  font-family: "Cinzel", serif;
  letter-spacing: 0.04em;
}

h2 {
  font-size: 1.3rem;
}

.lede {
  margin: 0;
  color: var(--muted);
  font-family: "Cormorant Garamond", serif;
  font-size: 1.15rem;
  letter-spacing: 0.06em;
}

.section-card {
  background: linear-gradient(135deg, var(--surface), var(--surface-2));
  border: 1px solid var(--surface-border);
  border-radius: 18px;
  padding: 1.8rem 2rem;
  backdrop-filter: blur(8px);
  box-shadow: 0 10px 28px rgba(4, 8, 16, 0.24), inset 0 0 28px rgba(70, 45, 140, 0.08);
  transition: border-color 180ms ease, box-shadow 180ms ease, transform 180ms ease;
}
.section-card p {
  margin: 0 0 0.65rem;
  font-family: "Cormorant Garamond", serif;
  font-size: 1.2rem;
  line-height: 1.68;
}

.section-card p:last-child {
  margin-bottom: 0;
}

[data-cosmic-anchor].is-cosmic-active {
  border-color: rgba(220, 190, 255, 0.55);
  box-shadow: 0 0 0 1px rgba(220, 190, 255, 0.28), 0 10px 28px rgba(4, 8, 16, 0.24), inset 0 0 28px rgba(70, 45, 140, 0.1);
  transform: translateY(-2px);
}

/* --- Restrict width to create boxy cards and vertical scroll --- */
.home-layout {
  display: grid;
  grid-template-columns: 240px minmax(0, 1fr);
  gap: 2rem 2.8rem;
  margin: 2rem auto 5rem auto;
  max-width: 960px;
}

/* Span the about-me card across both columns, flush with the grid edges */
.home-about-me {
  grid-column: 1 / -1;
  padding: 2.4rem 2.8rem;
}

.home-profile-column {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 0.75rem;
  align-self: start;
}

.profile-photo {
    width: 100%; /* Take up the full width of the container */
    max-width: 280px; /* Prevent it from getting too massive */
    height: auto;
    aspect-ratio: 4 / 5; /* Gives it a nice, modern portrait crop */
    object-fit: cover; /* Ensures the image fills the space without stretching */
    border-radius: 12px; /* Soft rounded corners to match the glass cards */
    border: 1px solid rgba(180, 140, 255, 0.3); /* Subtle glowing border */
    box-shadow: 0 8px 24px rgba(4, 8, 16, 0.4);
    filter: brightness(0.9) contrast(1.05);
}
.photo-card {
  width: 100%;
  padding: 0.65rem;
  position: relative;
  overflow: hidden;
}
.photo-card::after {
  content: "";
  position: absolute;
  inset: 0;
  border-radius: 12px;
  /* Casts a dark purple shadow inward to blend the bright green edges */
  box-shadow: inset 0 0 24px rgba(16, 20, 35, 0.6);
  pointer-events: none;
}
.connector-orbit {
  width: 180px;
  height: 58px;
  border-top: 1.5px dashed rgba(180, 140, 255, 0.5);
  border-radius: 999px;
  opacity: 0.72;
}

.cta-book {
  display: inline-block;
  padding: 0.7rem 1.8rem;
  border: 1px solid rgba(180, 140, 255, 0.55);
  border-radius: 999px;
  background: rgba(140, 100, 240, 0.18);
  color: var(--text);
  font-family: "Cinzel", serif;
  font-size: 0.88rem;
  letter-spacing: 0.12em;
  text-decoration: none;
  text-align: center;
  transition: background 200ms ease, border-color 200ms ease, box-shadow 200ms ease;
  box-shadow: 0 0 18px rgba(140, 100, 240, 0.15);
}

.cta-book:hover {
  background: rgba(140, 100, 240, 0.32);
  border-color: rgba(200, 160, 255, 0.8);
  box-shadow: 0 0 28px rgba(160, 110, 255, 0.28);
  color: var(--text);
}

.home-text-column {
  display: grid;
  gap: 1rem;
}

.home-services {
  grid-column: 1 / -1;
  margin-top: 0.2rem;
  border-color: rgba(130, 210, 190, 0.35);
  background:
    radial-gradient(circle at 88% 16%, rgba(120, 200, 176, 0.12), transparent 38%),
    radial-gradient(circle at 12% 76%, rgba(120, 190, 255, 0.11), transparent 36%),
    linear-gradient(140deg, rgba(10, 24, 40, 0.86), rgba(10, 30, 34, 0.86));
  box-shadow: 0 14px 34px rgba(2, 14, 18, 0.34), inset 0 0 24px rgba(80, 150, 150, 0.12);
}

.home-services .section-header::after {
  width: 6.2rem;
  background: linear-gradient(to right, rgba(120, 210, 185, 0.75), rgba(120, 190, 255, 0.3), transparent);
}

.services-intro {
  margin: 0 0 0.95rem;
  color: #cfe8e1;
  font-size: 0.97rem;
  letter-spacing: 0.02em;
}

.services-map-shell {
  position: relative;
  border-radius: 22px;
  overflow: hidden;
  border: 1px solid rgba(130, 210, 190, 0.2);
  background: linear-gradient(130deg, rgba(6, 18, 36, 0.34), rgba(4, 26, 30, 0.22));
}

.services-particles-canvas {
  position: absolute;
  inset: 0;
  z-index: 0;
  pointer-events: none;
}

/* Service labels grid — always visible, particles are purely decorative behind */
.services-list {
  position: relative;
  z-index: 1;
  margin: 0;
  padding: 1.5rem;
  list-style: none;
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 0.75rem;
}

.services-list li {
  padding: 0.85rem 1rem 0.85rem 2.1rem;
  border: 1px solid rgba(120, 210, 185, 0.25);
  border-radius: 16px;
  background:
    radial-gradient(circle at 85% 16%, rgba(140, 220, 210, 0.08), transparent 45%),
    linear-gradient(125deg, rgba(14, 24, 32, 0.82), rgba(10, 20, 28, 0.82));
  backdrop-filter: blur(3px);
  font-family: "Cormorant Garamond", serif;
  font-size: 1.1rem;
  line-height: 1.45;
  box-shadow: 0 4px 14px rgba(3, 12, 18, 0.18);
  position: relative;
  transition: border-color 200ms ease, box-shadow 200ms ease, transform 200ms ease;
}

/* The last item spans both columns when there's an odd count */
.services-list li:last-child:nth-child(odd) {
  grid-column: 1 / -1;
}

.services-list li::before {
  content: "";
  position: absolute;
  left: 0.78rem;
  top: 0.9rem;
  width: 0.68rem;
  height: 0.68rem;
  border-radius: 999px;
  border: 1px solid rgba(148, 240, 213, 0.85);
  background: radial-gradient(circle at 35% 35%, #ddfff3 0%, #93ddc7 55%, #4a8e7e 100%);
  box-shadow: 0 0 8px rgba(120, 225, 190, 0.45);
}

.services-list li:hover {
  transform: translateY(-3px);
  border-color: rgba(165, 240, 220, 0.5);
  box-shadow: 0 8px 18px rgba(3, 12, 18, 0.24), 0 0 14px rgba(120, 210, 190, 0.14);
}

.info-card {
  position: relative;
}

.info-card::before {
  content: "";
  position: absolute;
  left: -10px;
  top: 18px;
  width: 14px;
  height: 14px;
  border-radius: 999px;
}

.info-card-purple::before {
  background: radial-gradient(circle at 40% 38%, #ffd060, #e87520);
  box-shadow: 0 0 10px rgba(255, 180, 30, 0.5);
}

.info-card-teal::before {
  background: radial-gradient(circle at 40% 38%, #a0e8d5, #2d9e7a);
  box-shadow: 0 0 10px rgba(60, 200, 160, 0.5);
}

.info-card-blue {
  border-color: rgba(120, 190, 255, 0.3);
  background: linear-gradient(135deg, rgba(14, 26, 48, 0.88), rgba(20, 40, 60, 0.88));
}

.pricing-layout {
  display: grid;
  grid-template-columns: 360px 1fr;
  gap: 1.5rem;
  max-width: 960px;
  margin: 0 auto;
}

.pricing-left {
  display: grid;
  gap: 1.5rem;
  align-content: start;
}

.section-card .direct-card-intro {
  margin: 0 0 1rem;
  color: var(--muted);
  font-family: "Cormorant Garamond", serif;
  font-size: 1.05rem;
}

.direct-links {
  display: flex;
  flex-direction: column;
  gap: 0.6rem;
}

.direct-link {
  display: flex;
  align-items: center;
  gap: 0.75rem;
  padding: 0.7rem 1rem;
  border: 1px solid rgba(120, 190, 255, 0.25);
  border-radius: 12px;
  background: rgba(255, 255, 255, 0.03);
  color: var(--text);
  text-decoration: none;
  font-family: "Cormorant Garamond", serif;
  font-size: 1.1rem;
  transition: background 150ms ease, border-color 150ms ease;
}

.direct-link:hover {
  background: rgba(120, 190, 255, 0.08);
  border-color: rgba(120, 190, 255, 0.5);
  color: var(--text);
}

.direct-link-icon {
  font-size: 1.2rem;
  flex-shrink: 0;
}

.direct-card p {
  margin: 0.1rem 0;
}

.section-card .contact-form-intro {
  margin: 0 0 1.25rem;
  color: var(--muted);
  font-family: "Cormorant Garamond", serif;
  font-size: 1.05rem;
}

.submit-btn {
  width: 100%;
  margin-top: 0.25rem;
  padding: 0.8rem 1rem;
  font-size: 0.95rem;
  letter-spacing: 0.08em;
  border-color: rgba(180, 140, 255, 0.5);
  background: rgba(140, 100, 240, 0.22);
}

.rate-row {
  display: flex;
  justify-content: space-between;
  align-items: center;
  gap: 1rem;
  background: rgba(255, 255, 255, 0.03);
  border: 1px solid rgba(180, 140, 255, 0.2);
  border-radius: 12px;
  padding: 0.8rem 0.9rem;
  margin-bottom: 0.65rem;
}

.rate-row p {
  margin: 0;
  color: var(--muted);
  font-family: "Cormorant Garamond", serif;
  font-size: 0.95rem;
}

.rate-row h3 {
  font-size: 0.95rem;
  margin: 0 0 0.15rem;
}

.rate-row strong {
  font-size: 1.25rem;
  font-family: "Cinzel", serif;
  letter-spacing: 0.04em;
  color: #ffd060;
  white-space: nowrap;
}

.section-card .note {
  margin: 0.75rem 0 0;
  color: #ffd060;
  font-family: "Cormorant Garamond", serif;
  font-size: 0.95rem;
}

.contact-form {
  display: grid;
  gap: 0.85rem;
}

.form-field {
  display: grid;
  gap: 0.35rem;
}

label {
  color: var(--muted);
  font-size: 0.9rem;
  font-family: "Raleway", sans-serif;
  letter-spacing: 0.08em;
  text-transform: uppercase;
}

input,
textarea {
  width: 100%;
  border: 1px solid rgba(180, 140, 255, 0.28);
  background: rgba(255, 255, 255, 0.04);
  color: var(--text);
  border-radius: 10px;
  padding: 0.65rem 0.75rem;
  font: inherit;
  transition: border-color 180ms ease, background-color 180ms ease;
}

input:focus,
textarea:focus {
  outline: none;
  border-color: rgba(180, 140, 255, 0.6);
  background: rgba(255, 255, 255, 0.06);
  box-shadow: 0 0 0 3px rgba(140, 100, 240, 0.18);
}

textarea {
  min-height: 140px;
  resize: vertical;
}

button {
  border: 1px solid rgba(180, 140, 255, 0.35);
  border-radius: 10px;
  background: rgba(140, 100, 240, 0.2);
  color: var(--text);
  font-weight: 600;
  padding: 0.65rem 0.9rem;
  cursor: pointer;
  font-family: "Raleway", sans-serif;
  letter-spacing: 0.04em;
}

button:hover {
  background: rgba(140, 100, 240, 0.35);
}

.resource-grid {
  display: grid;
  grid-template-columns: repeat(4, minmax(0, 1fr));
  gap: 1.2rem;
  max-width: min(1200px, 92vw);
  margin: 0 auto;
}

.resource-card {
  text-align: left;
  width: 100%;
  display: flex;
  flex-direction: column;
  transition: transform 180ms ease, box-shadow 180ms ease;
}

.resource-card .tagline {
  flex: 1;
  font-size: 1rem;
}

.resource-card:hover {
  transform: translateY(-4px) scale(1.01);
  box-shadow: 0 14px 36px rgba(80, 50, 160, 0.24), inset 0 0 28px rgba(70, 45, 140, 0.08);
}

.resource-card:focus-visible {
  outline: 2px solid rgba(180, 140, 255, 0.5);
  outline-offset: 2px;
}

.resource-emoji {
  font-size: 2rem;
  margin-bottom: 0.2rem;
}

.resource-cta {
  margin: 0.9rem 0 0;
  text-transform: uppercase;
  letter-spacing: 0.09em;
  font-size: 0.72rem;
  color: rgba(200, 180, 255, 0.7);
  font-family: "Raleway", sans-serif;
}

.resource-modal {
  position: fixed;
  inset: 0;
  z-index: 30;
  display: grid;
  place-items: center;
  padding: 1rem;
}

.resource-modal.hidden {
  display: none;
}

.resource-modal-backdrop {
  position: absolute;
  inset: 0;
  background: rgba(5, 8, 20, 0.84);
  backdrop-filter: blur(8px);
}

.resource-modal-card {
  position: relative;
  width: min(760px, 100%);
  max-height: min(88vh, 760px);
  overflow: auto;
  z-index: 1;
}

.resource-modal-title {
  min-height: unset;
  font-size: 1.25rem;
  margin: 0 2.5rem 0.3rem 0; /* leave room for the close button */
}

.resource-modal-items {
  display: grid;
  gap: 0.4rem;
  margin-top: 0.4rem;
}

.resource-link-list {
  list-style: none;
  margin: 0;
  padding: 0;
  display: grid;
  gap: 0.4rem;
}

.resource-item {
  border: 1px solid rgba(180, 140, 255, 0.18);
  border-radius: 10px;
  background: rgba(255, 255, 255, 0.02);
  transition: border-color 80ms ease, background 80ms ease;
}

.resource-item:hover {
  border-color: rgba(200, 170, 255, 0.42);
  background: rgba(140, 100, 240, 0.07);
}

.resource-item a {
  display: block;
  padding: 0.5rem 0.75rem;
  color: inherit;
  text-decoration: none;
}

.resource-item-title {
  display: block;
  color: var(--accent-soft);
  font-family: "Raleway", sans-serif;
  font-size: 0.88rem;
  font-weight: 500;
  letter-spacing: 0.02em;
  line-height: 1.35;
  transition: color 80ms ease;
}

.resource-item a:hover .resource-item-title {
  color: #e0cfff;
}

.resource-item-title::after {
  content: " ↗";
  font-size: 0.72rem;
  opacity: 0.55;
}

.resource-item-desc {
  margin: 0.2rem 0 0 !important; /* override section-card p */
  font-family: "Cormorant Garamond", serif !important;
  font-size: 0.95rem !important;
  color: var(--muted);
  line-height: 1.45;
  opacity: 0.8;
}

.modal-close {
  position: absolute;
  right: 0.65rem;
  top: 0.55rem;
  width: 34px;
  height: 34px;
  border-radius: 50%;
  line-height: 1;
  font-size: 1.45rem;
  padding: 0;
}

.modal-open {
  overflow: hidden;
}

.trainings-wrap {
  max-width: 960px;
  margin: 0 auto;
}

.trainings-card {
  width: 100%;
  max-width: 560px;
  padding: 2.4rem 2.8rem;
  text-align: left;
}

.trainings-sprout {
  font-size: 2.4rem;
  margin-bottom: 0.55rem;
}

.trainings-cta {
  display: inline-block;
  margin-top: 1.25rem;
  padding: 0.65rem 1.4rem;
  border: 1px solid rgba(180, 140, 255, 0.45);
  border-radius: 999px;
  background: rgba(140, 100, 240, 0.16);
  color: var(--text);
  font-family: "Cinzel", serif;
  font-size: 0.85rem;
  letter-spacing: 0.1em;
  text-decoration: none;
  transition: background 180ms ease, border-color 180ms ease;
}

.trainings-cta:hover {
  background: rgba(140, 100, 240, 0.32);
  border-color: rgba(180, 140, 255, 0.7);
  color: var(--text);
}

.success {
  margin: 0 0 0.75rem;
  color: var(--success);
}

.success-state {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 0.5rem;
  padding: 1.5rem 0;
}

.success-emoji {
  font-size: 2rem;
}

.error {
  margin: 0;
  color: var(--error);
  font-size: 0.84rem;
}

.site-footer {
  position: relative;
  z-index: 2;
  flex-shrink: 0;
  margin-top: auto;
  border-top: 1px solid rgba(180, 140, 255, 0.18);
  color: var(--muted);
  text-align: center;
  padding: 1rem;
  background: rgba(5, 8, 20, 0.5);
}

.site-footer p {
  margin: 0.25rem 0;
  font-family: "Cormorant Garamond", serif;
  font-size: 1.02rem;
}

.site-footer a {
  color: var(--muted);
  text-decoration: none;
  border-bottom: 1px solid rgba(200, 184, 232, 0.3);
  transition: color 150ms ease, border-color 150ms ease;
}

.site-footer a:hover {
  color: var(--text);
  border-bottom-color: rgba(200, 184, 232, 0.7);
}

.site-footer .subtitle {
  font-size: 0.8rem;
}
/* --- SCROLL REVEAL ANIMATIONS --- */
.reveal-on-scroll {
  opacity: 0;
  transform: translateY(18px);
  transition: opacity 0.35s ease-out,
              transform 0.35s ease-out;
  will-change: opacity, transform;
}

.reveal-on-scroll.is-visible {
  opacity: 1;
  transform: translateY(0); /* Snaps it back into place */
}
@keyframes dotPulse {
  0%, 100% { box-shadow: 0 0 6px rgba(120, 225, 190, 0.4); }
  50%       { box-shadow: 0 0 14px rgba(120, 225, 190, 0.85), 0 0 22px rgba(120, 225, 190, 0.3); }
}

/* Two-column services grid on medium phones before the full stack breakpoint */
@media (min-width: 480px) and (max-width: 860px) {
  .services-list {
    grid-template-columns: 1fr 1fr;
    padding: 1rem;
    gap: 0.65rem;
  }

  .services-list li:last-child:nth-child(odd) {
    grid-column: 1 / -1;
  }

  .services-list li {
    font-size: 0.97rem;
    padding: 0.7rem 0.75rem 0.7rem 1.9rem;
  }
}

/* Resources: 2-col on tablets */
@media (min-width: 600px) and (max-width: 860px) {
  .resource-grid {
    grid-template-columns: repeat(2, 1fr);
  }
}

@media (max-width: 860px) {
  /* Layouts stack to single column */
  .home-layout,
  .pricing-layout,
  .resource-grid {
    grid-template-columns: 1fr;
    gap: 1rem;
    margin-top: 0.75rem;
  }

  .home-layout {
    margin-bottom: 3rem;
  }

  .home-profile-column {
    max-width: 100%;
    margin: 0 auto;
  }

  /* Photo becomes a compact avatar */
  .profile-photo {
    max-width: 120px;
    aspect-ratio: 1 / 1;
    border-radius: 50%;
  }

  /* Hide the decorative orbit arc on mobile — it looks orphaned */
  .connector-orbit {
    display: none;
  }

  .cta-book {
    font-size: 0.78rem;
    padding: 0.6rem 1.4rem;
    letter-spacing: 0.08em;
  }

  /* Headings */
  .home-intro h1 {
    font-size: clamp(1.5rem, 7vw, 2rem);
  }

  .page-intro h1 {
    font-size: clamp(1.4rem, 6vw, 1.9rem);
  }

  .home-intro .lede {
    font-size: 0.88rem;
    letter-spacing: 0.12em;
  }

  h2 {
    font-size: 1.1rem;
  }

  /* Cards: tighter padding and smaller body text */
  .section-card {
    padding: 1.2rem 1.1rem;
  }

  .home-about-me {
    padding: 1.4rem 1.3rem;
  }

  .section-card p {
    font-size: 1.05rem;
  }

  .services-map-shell {
    border-radius: 16px;
    border-color: rgba(130, 210, 190, 0.15);
  }

  .services-particles-canvas {
    display: none;
  }

  .services-list {
    grid-template-columns: 1fr;
    padding: 0.85rem;
    gap: 0.6rem;
  }

  .services-list li:last-child:nth-child(odd) {
    grid-column: auto;
  }

  .services-intro {
    margin-bottom: 0.65rem;
    font-size: 0.82rem;
    letter-spacing: 0.03em;
  }

  .services-list li {
    font-size: 1.05rem;
    padding: 0.75rem 0.85rem 0.75rem 2rem;
    border-radius: 14px;
    line-height: 1.5;
  }

  .services-list li::before {
    left: 0.65rem;
    top: 0.85rem;
    width: 0.62rem;
    height: 0.62rem;
    animation: dotPulse 2.8s ease-in-out infinite;
    animation-delay: calc(var(--i, 0) * 0.4s);
  }

  .services-list li:nth-child(1)::before { --i: 0; }
  .services-list li:nth-child(2)::before { --i: 1; }
  .services-list li:nth-child(3)::before { --i: 2; }
  .services-list li:nth-child(4)::before { --i: 3; }
  .services-list li:nth-child(5)::before { --i: 4; }
  .services-list li:nth-child(6)::before { --i: 5; }
  .services-list li:nth-child(7)::before { --i: 6; }

  /* Nav: shrink pill labels and tighten spacing so they fit on one row */
  .nav-wrap {
    padding: 0.65rem 0;
    gap: 0.5rem;
  }

  .brand-title {
    font-size: 1rem;
  }

  .brand-subtitle {
    display: none; /* reclaim vertical space */
  }

  .main-nav {
    gap: 0.3rem;
  }

  .main-nav a {
    font-size: 0.68rem;
    padding: 0.35rem 0.55rem;
    letter-spacing: 0.06em;
  }

  /* Footer: tighter and smaller */
  .site-footer p {
    font-size: 0.88rem;
  }

  .site-footer .subtitle {
    font-size: 0.72rem;
  }

  /* Page content top padding */
  .page-content {
    padding: 1.25rem 0 2rem;
  }

  /* --- Pricing page --- */

  /* Rate rows: stack the label/duration and price vertically on very small screens */
  .rate-row {
    flex-wrap: wrap;
    gap: 0.4rem;
    padding: 0.65rem 0.75rem;
  }

  .rate-row h3 {
    font-size: 0.95rem;
    margin: 0;
  }

  .rate-row p {
    font-size: 0.9rem;
  }

  .rate-row strong {
    font-size: 1rem;
  }

  /* Note below rates */
  .section-card .note {
    font-size: 0.85rem;
    margin: 0.5rem 0 0;
  }

  /* Intro text in direct contact and form cards */
  .section-card .direct-card-intro,
  .section-card .contact-form-intro {
    font-size: 0.95rem;
    margin-bottom: 0.85rem;
  }

  /* Direct link rows: shrink text and padding, prevent overflow */
  .direct-link {
    font-size: 0.95rem;
    padding: 0.6rem 0.75rem;
    gap: 0.55rem;
  }

  .direct-link-icon {
    font-size: 1rem;
  }

  /* Contact form: tighter field gaps and smaller labels */
  .contact-form {
    gap: 0.65rem;
  }

  .form-field {
    gap: 0.25rem;
  }

  label {
    font-size: 0.78rem;
    letter-spacing: 0.06em;
  }

  input,
  textarea {
    font-size: 0.95rem;
    padding: 0.55rem 0.65rem;
  }

  textarea {
    min-height: 110px;
  }

  /* Submit button keeps full width and proper padding on mobile */
  .submit-btn {
    padding: 0.75rem 1rem;
    font-size: 0.88rem;
  }

  button {
    font-size: 0.9rem;
    padding: 0.6rem 0.8rem;
  }

  /* Lede subtitle under page title */
  .lede {
    font-size: 1rem;
    letter-spacing: 0.04em;
  }

  /* --- Resources page --- */

  /* Resource cards: tighter internal spacing */
  .resource-emoji {
    font-size: 1.5rem;
    margin-bottom: 0.15rem;
  }

  .resource-card h2 {
    font-size: 1rem;
    margin-bottom: 0.2rem;
  }

  .resource-card .tagline {
    font-size: 0.9rem;
    letter-spacing: 0.02em;
  }

  .resource-cta {
    font-size: 0.75rem;
    margin-top: 0.5rem;
  }

  /* Modal: full-screen on mobile with scrollable content */
  .resource-modal {
    padding: 0;
    align-items: flex-end; /* Sheet slides up from bottom */
  }

  .resource-modal-card {
    width: 100%;
    max-height: 90vh;
    overflow: auto;
    border-radius: 18px 18px 0 0; /* rounded top only, flush to bottom */
    padding: 1.2rem 1rem 1.5rem;
  }

  .resource-modal-card h2 {
    font-size: 1.05rem;
    margin-bottom: 0.25rem;
  }

  .resource-modal-card .tagline {
    font-size: 0.93rem;
    margin-bottom: 0.6rem;
  }

  .resource-modal-items {
    gap: 0.35rem;
  }

  .resource-link-list {
    gap: 0.35rem;
  }

  .resource-item {
    padding: 0; /* padding lives on the anchor now */
  }

  .resource-item a {
    padding: 0.45rem 0.65rem;
    font-size: 0.84rem;
  }

  .resource-item-title {
    font-size: 0.84rem;
  }

  .resource-item-desc {
    font-size: 0.88rem !important;
  }

  .modal-close {
    right: 0.75rem;
    top: 0.6rem;
    font-size: 1.25rem;
    width: 30px;
    height: 30px;
  }

  /* Direct contact card links */
  .direct-card p {
    font-size: 1rem;
  }
}
