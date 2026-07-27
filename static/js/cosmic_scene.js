(() => {
    const configEl = document.getElementById("cosmic-scene-config");
    const starsHost = document.getElementById("cosmic-stars");
    const constellationHost = document.getElementById("cosmic-constellations");
    const planetsHost = document.getElementById("cosmic-planets");

    if (!configEl || !starsHost || !constellationHost || !planetsHost) {
        return;
    }

    // Respect prefers-reduced-motion — skip all JS animation work entirely
    const prefersReducedMotion = window.matchMedia("(prefers-reduced-motion: reduce)").matches;

    // Runtime perf monitor — runs *during* real animation load, not on an empty page.
    // Watches for stutter frames (>50ms = below 20fps) over 3 seconds after render.
    // If stutter frames make up >10% of measured frames, switch to low-perf mode.
    const monitorPerfDuringAnimations = () => {
        let stutters = 0;
        let total = 0;
        let lastTime = performance.now();
        const start = lastTime;
        const worstFrames = [];

        const tick = (now) => {
            const delta = now - lastTime;
            lastTime = now;
            total++;
            if (delta > 50) {
                stutters++;
                worstFrames.push(delta);
            }
            if (now - start < 3000) {
                requestAnimationFrame(tick);
            } else {
                const stutterRate = stutters / total;
                console.log(
                    "[cosmic] perf monitor —",
                    "frames:", total,
                    "stutters:", stutters,
                    "rate:", (stutterRate * 100).toFixed(1) + "%",
                    "worst:", worstFrames.length ? Math.max(...worstFrames).toFixed(1) + "ms" : "none",
                );
                if (stutterRate > 0.1) {
                    console.log("[cosmic] switching to low-perf mode");
                    document.documentElement.classList.add("low-perf");

                    // Reload tsParticles with a lightweight config (60 particles instead of 420,
                    // no per-particle opacity animation, 30fps cap)
                    if (window.tsParticles && typeof window.tsParticles.dom === "function") {
                        window.tsParticles.dom().forEach(instance => instance.destroy());
                        void loadScene({ lowPerf: true });
                    }
                }
            }
        };
        requestAnimationFrame(tick);
    };

    let config;
    try {
        config = JSON.parse(configEl.textContent || "{}");
    } catch (_error) {
        return;
    }

    const seedValue = (seed) => {
        const value = Math.sin(seed * 37.31 + 11.71) * 10000;
        return value - Math.floor(value);
    };

    const clamp = (value, min, max) => Math.min(Math.max(value, min), max);

    // Cached planet/constellation refs — refreshed after any redraw
    let allWraps = [];
    let allConstellations = [];

    const refreshParallaxTargets = () => {
        allWraps = Array.from(document.querySelectorAll('.cosmic-planet-wrap'));
        allConstellations = Array.from(document.querySelectorAll('.constellation-group'));
    };

    // ── Planet SVG bands flag ──────────────────────────────────────────────
    // Set to true for curved SVG bands, false to fall back to CSS ::after bands
    const PLANET_SVG_BANDS = true;
    // ──────────────────────────────────────────────────────────────────────

    // Band definitions per palette: [yOffset (fraction of r), ry (fraction of r), opacity, color]
    // yOffset: 0 = equator, negative = north, positive = south
    // Palette keys must match:
    //   views.py:  "palette" field in SOLAR_SYSTEM
    //   site.css:  .palette-{name} class
    const BAND_CONFIGS = {
        "sage":      [ // Saturn — warm ochre/tan, prominent
            [ 0.00, 0.18, 0.20, "rgba(210, 195, 155, 1)"],
            [-0.18, 0.14, 0.16, "rgba(140, 120,  80, 1)"],
            [ 0.22, 0.16, 0.18, "rgba(200, 180, 130, 1)"],
            [-0.38, 0.12, 0.14, "rgba(100,  85,  55, 1)"],
            [ 0.42, 0.13, 0.15, "rgba(190, 170, 120, 1)"],
            [-0.58, 0.10, 0.12, "rgba(160, 145, 100, 1)"],
        ],
        "midnight":  [ // Jupiter — bold colorful bands
            [-0.55, 0.10, 0.28, "rgba(200, 160, 120, 1)"],
            [-0.38, 0.14, 0.32, "rgba(160, 100,  70, 1)"],
            [-0.18, 0.16, 0.30, "rgba(210, 180, 140, 1)"],
            [ 0.00, 0.18, 0.35, "rgba(170, 110,  80, 1)"],
            [ 0.20, 0.16, 0.28, "rgba(200, 165, 125, 1)"],
            [ 0.38, 0.14, 0.30, "rgba(140,  90,  60, 1)"],
            [ 0.56, 0.10, 0.24, "rgba(190, 150, 110, 1)"],
        ],
        "dusk-teal": [ // Uranus — faint ice giant
            [-0.20, 0.28, 0.08, "rgba(160, 210, 205, 1)"],
            [ 0.15, 0.22, 0.07, "rgba(100, 170, 165, 1)"],
            [ 0.45, 0.18, 0.06, "rgba( 80, 150, 145, 1)"],
        ],
        "violet":    [ // Neptune — deep blue
            [-0.30, 0.20, 0.12, "rgba(100, 130, 200, 1)"],
            [ 0.05, 0.24, 0.14, "rgba( 80, 100, 180, 1)"],
            [ 0.38, 0.18, 0.10, "rgba(120, 150, 210, 1)"],
        ],
        "blue":      [ // Earth — faint cloud layers
            [-0.25, 0.22, 0.07, "rgba(180, 210, 240, 1)"],
            [ 0.10, 0.28, 0.08, "rgba(140, 180, 220, 1)"],
            [ 0.40, 0.20, 0.06, "rgba(160, 200, 235, 1)"],
        ],
        "champagne": [ // Mars — subtle rusty surface
            [-0.15, 0.20, 0.08, "rgba(200, 150, 110, 1)"],
            [ 0.25, 0.18, 0.07, "rgba(170, 120,  85, 1)"],
        ],
        "rose":      [ // Venus — thick cloud bands
            [-0.30, 0.20, 0.12, "rgba(230, 210, 180, 1)"],
            [ 0.00, 0.26, 0.14, "rgba(210, 185, 150, 1)"],
            [ 0.32, 0.20, 0.11, "rgba(225, 200, 165, 1)"],
        ],
        "slate":     [], // Mercury + Pluto — rocky, no bands
    };

    const buildPlanetBandsSvg = (size, palette) => {
        const bands = BAND_CONFIGS[palette];
        if (!bands || bands.length === 0) return null;

        const ns  = "http://www.w3.org/2000/svg";
        const svg = document.createElementNS(ns, "svg");
        svg.setAttribute("viewBox", `0 0 ${size} ${size}`);
        svg.style.cssText = "position:absolute;inset:0;width:100%;height:100%;z-index:1;pointer-events:none;";

        const cx     = size / 2;
        const cy     = size / 2;
        const r      = size / 2;
        const clipId = `planet-clip-${palette}-${size}`;

        const defs       = document.createElementNS(ns, "defs");
        const clip       = document.createElementNS(ns, "clipPath");
        clip.setAttribute("id", clipId);
        const clipCircle = document.createElementNS(ns, "circle");
        clipCircle.setAttribute("cx", cx);
        clipCircle.setAttribute("cy", cy);
        clipCircle.setAttribute("r",  r);
        clip.appendChild(clipCircle);
        defs.appendChild(clip);
        svg.appendChild(defs);

        const g = document.createElementNS(ns, "g");
        g.setAttribute("clip-path", `url(#${clipId})`);
        g.setAttribute("transform", `rotate(-20, ${cx}, ${cy})`);

        bands.forEach(([yFrac, ryFrac, opacity, color]) => {
            const ellipse = document.createElementNS(ns, "ellipse");
            ellipse.setAttribute("cx",           cx);
            ellipse.setAttribute("cy",           cy + yFrac * r);
            ellipse.setAttribute("rx",           r * 0.98);
            ellipse.setAttribute("ry",           r * ryFrac);
            ellipse.setAttribute("fill",         "none");
            ellipse.setAttribute("stroke",       color);
            ellipse.setAttribute("stroke-width", r * 0.13);
            ellipse.setAttribute("opacity",      opacity);
            g.appendChild(ellipse);
        });

        svg.appendChild(g);
        return svg;
    };

    const drawPlanets = () => {
        planetsHost.innerHTML = "";
        const planets = Array.isArray(config.planets) ? config.planets : [];

        planets.forEach((planet, index) => {
            // Outer wrapper — handles position + parallax only
            const wrapEl = document.createElement("div");
            wrapEl.className = "cosmic-planet-wrap";
            wrapEl.style.setProperty("--parallax-y", "0px");

            // Inner planet — handles breathe animation + visuals
            const planetEl = document.createElement("div");
            planetEl.className = `cosmic-planet palette-${planet.palette || "violet"}`;
            planetEl.setAttribute("aria-label", planet.label || planet.id || "planet");
            if (planet.anchor) {
                wrapEl.dataset.cosmicAnchor = planet.anchor;
            }

            const size = Number(planet.size) || 72;
            const mobileFactor = window.innerWidth <= 860 ? 0.5 : 1;
            const scaledSize = Math.round(size * mobileFactor);
            const t = (index + 1) / (planets.length + 1);

            // Quadratic bezier arc: P0=(10,5) control=(15,90) P1=(90,92)
            // Control point bottom-left makes the curve concave (bowing inward).
            const bx = (1 - t) * (1 - t) * 10 + 2 * (1 - t) * t * 15 + t * t * 90;
            const by = (1 - t) * (1 - t) *  5 + 2 * (1 - t) * t * 90 + t * t * 92;
            const pathX = clamp(bx, 5, 95);
            const pathY = clamp(by, 5, 95);

            const anchorEl = planet.anchor ? document.querySelector(`[data-cosmic-anchor="${planet.anchor}"]`) : null;
            const anchorRect = anchorEl ? anchorEl.getBoundingClientRect() : null;
            const anchorX = anchorRect ? ((anchorRect.left + anchorRect.width / 2) / window.innerWidth) * 100 : null;
            const anchorY = anchorRect ? ((anchorRect.top + anchorRect.height / 2) / window.innerHeight) * 100 : null;

            const x = clamp(pathX, 5, 95);
            const y = clamp(pathY, 5, 95);

            wrapEl.style.left = `${x}%`;
            wrapEl.style.top = `${y}%`;
            planetEl.style.width = `${scaledSize}px`;
            planetEl.style.height = `${scaledSize}px`;
            planetEl.style.setProperty("--planet-delay", `-${seedValue(140 + index) * 8}s`);

            if (planet.ring) {
                const ring = document.createElement("span");
                ring.className = "planet-ring";
                planetEl.appendChild(ring);
            }

            // Planet SVG bands — injected when flag is on, CSS ::after used when off
            if (PLANET_SVG_BANDS) {
                const bandsSvg = buildPlanetBandsSvg(scaledSize, planet.palette || "violet");
                if (bandsSvg) {
                    planetEl.classList.add("has-svg-bands");
                    planetEl.appendChild(bandsSvg);
                }
            }

            if (anchorEl) {
                const activate = () => {
                    anchorEl.classList.add("is-cosmic-active");
                    planetEl.classList.add("is-active");
                };
                const deactivate = () => {
                    anchorEl.classList.remove("is-cosmic-active");
                    planetEl.classList.remove("is-active");
                };
                anchorEl.addEventListener("mouseenter", activate);
                anchorEl.addEventListener("mouseleave", deactivate);
                wrapEl.addEventListener("mouseenter", activate);
                wrapEl.addEventListener("mouseleave", deactivate);
            }

            wrapEl.appendChild(planetEl);
            planetsHost.appendChild(wrapEl);
        });
    };
    const drawConstellations = () => {
        constellationHost.innerHTML = "";

        const constellations = Array.isArray(config.constellations) ? config.constellations : [];

        // ── Placement presets ──────────────────────────────────────────────
        // Each preset is an array of {left, top} (in %) — one entry per constellation.
        // Add new presets here; set config.constellation_layout in views.py to switch.
        const PLACEMENT_PRESETS = {
            "home":[
                { left: 85, top: 12 },   // top-right
                { left: 10, top: 35 },   // upper-centre
                { left: 19, top: 58 },   // lower-centre
                { left: 78, top: 78 },   // bottom-left
            ],
            // Spacious quad spread — one in each quadrant
            "default": [
                { left: 18, top: 22 },   // top-left
                { left: 78, top: 30 },   // top-right
                { left: 22, top: 70 },   // bottom-left
                { left: 72, top: 72 },   // bottom-right
            ],
            // Scattered across top two-thirds, nothing near the bottom edge
            "top-heavy": [
                { left: 15, top: 19 },   // top-left
                { left: 78, top: 22 },   // top-right
                { left: 42, top: 44 },   // centre
                { left: 20, top: 62 },   // mid-left
            ],
            // True diagonal sweep — evenly spaced top-right to bottom-left
            "diagonal": [
                { left: 85, top: 12 },   // top-right
                { left: 55, top: 35 },   // upper-centre
                { left: 30, top: 58 },   // lower-centre
                { left: 12, top: 78 },   // bottom-left
            ],
        };

        const layoutKey = config.constellation_layout || "default";
        const placements = PLACEMENT_PRESETS[layoutKey] || PLACEMENT_PRESETS["default"];
        // ──────────────────────────────────────────────────────────────────

        constellations.forEach((constellation, index) => {
            const points = Array.isArray(constellation.points) ? constellation.points : [];
            if (points.length < 2) return;

            const placement = placements[index] || {
                left: index % 2 === 0 ? 20 : 80,
                top: 15 + ((index + 1) / (constellations.length + 1)) * 70,
            };

            const groupWrapper = document.createElement("div");
            groupWrapper.className = "constellation-group";
            groupWrapper.dataset.constellation = constellation.id || "";

            groupWrapper.style.left = `${placement.left}%`;
            groupWrapper.style.top  = `${placement.top}%`;
            groupWrapper.style.setProperty("--parallax-y", "0px");

            const randomDelay = -(seedValue(200 + index) * 4);
            groupWrapper.style.animationDelay = `${randomDelay}s`;

            const svg = document.createElementNS("http://www.w3.org/2000/svg", "svg");
            svg.setAttribute("viewBox", "0 0 100 100");
            svg.style.width = "100%";
            svg.style.height = "100%";
            svg.style.overflow = "visible";

            const linePairs =
                constellation.id === "orion"
                    ? [[0, 1], [0, 2], [1, 4], [2, 3], [3, 4], [2, 5], [4, 6], [0, 7], [1, 7]]
                    : constellation.id === "nurtured_story"
                        ? [
                            [0, 1], [1, 2],           // spine top→mid→bottom
                            [3, 0], [4, 2], [3, 4],   // left page
                            [5, 0], [6, 2], [5, 6],   // right page (mirror)
                          ]
                        : constellation.id === "canis_major"
                        ? [
                            [0,1],     // Muliphein-Sirius-Mirzam (head line)
                            [0,2],[2,3],[3,4],[2,4],
                            [0,5],[5,6], //body
                            [6,7],[6,8],
                            [8,9]
                          ]
                        : [[0, 1], [1, 2], [2, 3], [3, 0], [2, 4], [4, 5], [5, 6]];

            linePairs.forEach(([a, b]) => {
                const from = points[a];
                const to = points[b];
                if (!from || !to) return;

                const line = document.createElementNS("http://www.w3.org/2000/svg", "line");
                line.setAttribute("x1", `${from.x}`);
                line.setAttribute("y1", `${from.y}`);
                line.setAttribute("x2", `${to.x}`);
                line.setAttribute("y2", `${to.y}`);
                line.setAttribute("class", "constellation-line");
                line.setAttribute("style", `stroke: ${constellation.color || "rgba(180, 210, 255, 0.4)"}; stroke-dasharray: 2 4;`);
                svg.appendChild(line);
            });

            points.forEach((point, i) => {
                const star = document.createElementNS("http://www.w3.org/2000/svg", "circle");
                star.setAttribute("cx", `${point.x}`);
                star.setAttribute("cy", `${point.y}`);
                star.setAttribute("r", "1.2");
                star.setAttribute("class", "constellation-star");
                svg.appendChild(star);
            });

            const label = document.createElementNS("http://www.w3.org/2000/svg", "text");
            const labelX = points[0].x + 5;
            const labelY = points[0].y + 7;
            const words = (constellation.label || "").toUpperCase().split(" ");

            if (words.length > 1) {
                // Two-line label using tspan elements
                const mid = Math.ceil(words.length / 2);
                const line1 = words.slice(0, mid).join(" ");
                const line2 = words.slice(mid).join(" ");

                const span1 = document.createElementNS("http://www.w3.org/2000/svg", "tspan");
                span1.setAttribute("x", labelX);
                span1.setAttribute("dy", "0");
                span1.textContent = line1;

                const span2 = document.createElementNS("http://www.w3.org/2000/svg", "tspan");
                span2.setAttribute("x", labelX);
                span2.setAttribute("dy", "10");
                span2.textContent = line2;

                label.appendChild(span1);
                label.appendChild(span2);
            } else {
                label.textContent = words[0];
            }

            label.setAttribute("x", `${labelX}`);
            label.setAttribute("y", `${labelY}`);
            label.setAttribute("class", "constellation-label");
            svg.appendChild(label);

            groupWrapper.appendChild(svg);
            constellationHost.appendChild(groupWrapper);
        });
    };

    const loadScene = async (options = {}) => {
        if (typeof window.tsParticles === "undefined") return;

        const isLowPerf = options.lowPerf || false;

        await window.tsParticles.load({
            id: "cosmic-stars",
            options: {
                fullScreen: { enable: false },
                detectRetina: !isLowPerf,   // skip retina scaling on low-perf
                fpsLimit: 60,
                particles: {
                    number: {
                        value: isLowPerf ? 60 : (Number(config.stars) || 300),
                        density: { enable: true, width: 1920, height: 1080 },
                    },
                    color: { value: ["#ffffff", "#dbe6ff", "#c8b8e8"] },
                    move: {
                        enable: true,
                        direction: "none",
                        random: true,
                        speed: 0.15,
                        outModes: { default: "out" },
                    },
                    opacity: {
                        value: { min: 0.2, max: 0.9 },
                        // Per-particle opacity animation is expensive without GPU — skip it in low-perf
                        animation: isLowPerf
                            ? { enable: false }
                            : { enable: true, speed: 0.5, sync: false },
                    },
                    shape: { type: "circle" },
                    size: { value: { min: 0.4, max: 1.4 } },
                },
                background: {
                    color: { value: "transparent" },
                },
            },
        });
    };
    const initParallax = () => {
        const sceneEl = document.getElementById("cosmic-scene");
        const pinSceneHeight = () => {
            if (sceneEl) sceneEl.style.height = `${document.body.scrollHeight}px`;
        };
        pinSceneHeight();

        let currentScroll = window.scrollY;
        let targetScroll = window.scrollY;
        let rafId = null;
        let lastInnerWidth = window.innerWidth;

        const lerp = (a, b, t) => a + (b - a) * t;

        const applyParallax = () => {
            currentScroll = lerp(currentScroll, targetScroll, 0.08);

            // Uses shared allWraps / allConstellations — always up to date after redraws
            allWraps.forEach(wrap => {
                wrap.style.setProperty('--parallax-y', `${currentScroll * -0.6}px`);
            });

            allConstellations.forEach(constellation => {
                constellation.style.setProperty('--parallax-y', `${currentScroll * -0.15}px`);
            });

            if (Math.abs(currentScroll - targetScroll) > 0.5) {
                rafId = requestAnimationFrame(applyParallax);
            } else {
                rafId = null;
            }
        };

        window.addEventListener('scroll', () => {
            targetScroll = window.scrollY;
            if (!rafId) {
                rafId = requestAnimationFrame(applyParallax);
            }
        }, { passive: true });

        // Only repin on genuine width change — height-only = mobile address bar, ignore
        window.addEventListener('resize', () => {
            if (window.innerWidth !== lastInnerWidth) {
                lastInnerWidth = window.innerWidth;
                pinSceneHeight();
            }
        }, { passive: true });
    };
    const render = () => {
        drawPlanets();
        drawConstellations();
        refreshParallaxTargets();

        // If user explicitly wants reduced motion, skip everything
        if (prefersReducedMotion) {
            document.documentElement.classList.add("low-perf");
            return;
        }

        initParallax();

        // Check repeatedly until tsParticles is loaded from the CDN
        const initParticles = () => {
            if (typeof window.tsParticles !== "undefined") {
                void loadScene();
            } else {
                setTimeout(initParticles, 50);
            }
        };
        initParticles();

        // Start perf monitoring under real animation load. If jank detected,
        // .low-perf class gets added and CSS animations freeze.
        monitorPerfDuringAnimations();
    };
    render();
    // Add interactive hover effect for constellations
    window.addEventListener("mousemove", (e) => {
        const groups = document.querySelectorAll(".constellation-group");
        groups.forEach((group) => {
            const rect = group.getBoundingClientRect();
            const centerX = rect.left + rect.width / 2;
            const centerY = rect.top + rect.height / 2;
            const distance = Math.hypot(e.clientX - centerX, e.clientY - centerY);
            if (distance < 250) { 
                group.classList.add("is-lit");
            } else {
                group.classList.remove("is-lit");
            }
        });
    });
    let resizeTimer;
    let lastResizeWidth = window.innerWidth;
    window.addEventListener("resize", () => {
        // Ignore height-only changes (mobile address bar show/hide)
        if (window.innerWidth === lastResizeWidth) return;
        lastResizeWidth = window.innerWidth;
        window.clearTimeout(resizeTimer);
        resizeTimer = window.setTimeout(() => {
            drawPlanets();
            drawConstellations();
            refreshParallaxTargets();
            const sceneEl = document.getElementById("cosmic-scene");
            if (sceneEl) sceneEl.style.height = `${document.body.scrollHeight}px`;
        }, 120);
    });
})();
