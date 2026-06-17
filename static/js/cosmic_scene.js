(() => {
    const configEl = document.getElementById("cosmic-scene-config");
    const starsHost = document.getElementById("cosmic-stars");
    const constellationHost = document.getElementById("cosmic-constellations");
    const planetsHost = document.getElementById("cosmic-planets");

    if (!configEl || !starsHost || !constellationHost || !planetsHost) {
        return;
    }

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

    const drawPlanets = () => {
        planetsHost.innerHTML = "";
        const planets = Array.isArray(config.planets) ? config.planets : [];

        planets.forEach((planet, index) => {
            const planetEl = document.createElement("div");
            planetEl.className = `cosmic-planet palette-${planet.palette || "violet"}`;
            planetEl.setAttribute("aria-label", planet.label || planet.id || "planet");
            if (planet.anchor) {
                planetEl.dataset.cosmicAnchor = planet.anchor;
            }

            const size = Number(planet.size) || 72;
            const t = (index + 1) / (planets.length + 1);

            // 1. THE INWARD CURVE
            // Starts top-left (20%), swoops INWARD toward the left margin 
            // in the middle of the screen, and arcs out to the bottom-right (85%).
            const basePathX = 20 + (t * 60) - (Math.sin(t * Math.PI) * 28);
            
            // Strictly distribute them from 5% to 95% of the screen height.
            const basePathY = 8 + (t * 84);

            // 2. THE ANTI-COLLISION STAGGER
            // Instead of randomizing the X axis, we deliberately alternate the planets 
            // left and right of the invisible curve by 12%. This guarantees that 
            // massive planets (like Jupiter and Saturn) never touch.
            const staggerX = (index % 2 === 0 ? -1 : 1) * 12; 
            
            // Keep the vertical randomness extremely tiny (just 4%) so they look 
            // slightly organic without destroying our strict vertical spacing.
            const scatterY = (seedValue(90 + index) - 0.5) * 4;

            // Calculate final coordinates, keeping them within the screen bounds
            const pathX = clamp(basePathX + staggerX, 5, 95);
            const pathY = clamp(basePathY + scatterY, 5, 95);


            const anchorEl = planet.anchor ? document.querySelector(`[data-cosmic-anchor="${planet.anchor}"]`) : null;
            const anchorRect = anchorEl ? anchorEl.getBoundingClientRect() : null;
            const anchorX = anchorRect ? ((anchorRect.left + anchorRect.width / 2) / window.innerWidth) * 100 : null;
            const anchorY = anchorRect ? ((anchorRect.top + anchorRect.height / 2) / window.innerHeight) * 100 : null;
            
            // FIX 2: Reduce the anchor "pull" from 55% to 15%. 
            // This keeps planets in the background margins, but allows them to hover/interact safely.
            const x = clamp(anchorX !== null ? pathX * 0.95 + anchorX * 0.05 : pathX, 5, 95);
            const y = clamp(anchorY !== null ? pathY * 0.95 + anchorY * 0.05 : pathY, 5, 95);

            planetEl.style.left = `${x}%`;
            planetEl.style.top = `${y}%`;
            planetEl.style.width = `${size}px`;
            planetEl.style.height = `${size}px`;
            planetEl.style.setProperty("--planet-drift-x", `${(seedValue(120 + index) - 0.5) * 5}px`);
            planetEl.style.setProperty("--planet-drift-y", `${(seedValue(130 + index) - 0.5) * 8}px`);
            planetEl.style.setProperty("--planet-delay", `${seedValue(140 + index) * 4}s`);

            if (planet.ring) {
                const ring = document.createElement("span");
                ring.className = "planet-ring";
                planetEl.appendChild(ring);
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
                planetEl.addEventListener("mouseenter", activate);
                planetEl.addEventListener("mouseleave", deactivate);
            }

            planetsHost.appendChild(planetEl);
        });
    };

    const drawConstellations = () => {
        constellationHost.innerHTML = "";
        
        // FIX 1: Create a master SVG wrapper so coordinates act as fluid percentages
        const svgWrapper = document.createElementNS("http://www.w3.org/2000/svg", "svg");
        svgWrapper.setAttribute("viewBox", "0 0 100 100");
        svgWrapper.setAttribute("preserveAspectRatio", "xMidYMid slice");
        svgWrapper.style.width = "100%";
        svgWrapper.style.height = "100%";
        svgWrapper.style.position = "absolute";
        svgWrapper.style.inset = "0";

        // FIX 2: More organic, spread-out coordinates for a realistic star map look
        const organicPoints = {
            // Shifted to the top-right empty space
            "big_dipper": [
                {x: 62, y: 8}, {x: 68, y: 14}, {x: 75, y: 20}, {x: 70, y: 26}, 
                {x: 82, y: 30}, {x: 90, y: 22}, {x: 86, y: 12}
            ],
            // Shifted entirely into the far-left margin
            "orion": [
                {x: 7, y: 28}, {x: 19, y: 30}, {x: 11, y: 45}, {x: 15, y: 46}, 
                {x: 19, y: 44}, {x: 7, y: 68}, {x: 23, y: 64}, {x: 13, y: 15}
            ],
            // Shifted to the bottom-right corner
            "gemini": [
                {x: 75, y: 70}, {x: 85, y: 75}, {x: 72, y: 85}, {x: 82, y: 87}, 
                {x: 68, y: 97}, {x: 80, y: 100}, {x: 88, y: 93}, {x: 80, y: 60}
            ]
        };

        const constellations = Array.isArray(config.constellations) ? config.constellations : [];

        constellations.forEach((constellation) => {
            const points = organicPoints[constellation.id] || constellation.points;
            if (!points || points.length < 2) return;
            const randomDelay = Math.random() * 4; // Between 0s and 4s delay
            
            const group = document.createElementNS("http://www.w3.org/2000/svg", "g");
            group.setAttribute("class", "constellation-group");
            group.setAttribute("data-constellation", constellation.id || "");
            group.style.animationDelay = `${randomDelay}s`;
            const linePairs =
                constellation.id === "orion"
                    ? [[0, 1], [0, 2], [1, 4], [2, 3], [3, 4], [2, 5], [4, 6], [0, 7], [1, 7]]
                    : constellation.id === "gemini"
                        ? [[0, 2], [1, 3], [2, 4], [3, 5], [4, 7], [5, 7], [5, 6], [0, 1]]
                        : [[0, 1], [1, 2], [2, 3], [3, 0], [3, 4], [4, 5], [5, 6]];

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
                line.setAttribute("style", `stroke: ${constellation.color || "rgba(180, 210, 255, 0.4)"}; stroke-dasharray: 0.5 1.5;`);                
                group.appendChild(line);
            });

            points.forEach((point, index) => {
                const star = document.createElementNS("http://www.w3.org/2000/svg", "circle");
                star.setAttribute("cx", `${point.x}`);
                star.setAttribute("cy", `${point.y}`);
                star.setAttribute("r", index === 0 ? "0.5" : "0.3");
                star.setAttribute("class", "constellation-star");
                group.appendChild(star);
            });

            const label = document.createElementNS("http://www.w3.org/2000/svg", "text");
            label.setAttribute("x", `${points[0].x + 2}`);
            label.setAttribute("y", `${points[0].y + 4}`);
            label.setAttribute("class", "constellation-label");
            label.textContent = (constellation.label || "").toUpperCase(); 
            group.appendChild(label);

            svgWrapper.appendChild(group);
        });
        
        constellationHost.appendChild(svgWrapper);
    };

    const loadScene = async () => {
        if (typeof window.tsParticles === "undefined") return;

        // FIX 3: Removed manualParticles completely to prevent the Slim bundle from crashing.
        // Using the robust standard configuration syntax.
        await window.tsParticles.load({
            id: "cosmic-stars",
            options: {
                fullScreen: { enable: false },
                detectRetina: true,
                fpsLimit: 60,
                particles: {
                    number: {
                        value: Number(config.stars) || 300,
                        density: { enable: true, width: 1920, height: 1080 }, // Spreads them evenly
                    },
                    color: { value: ["#ffffff", "#dbe6ff", "#c8b8e8"] },
                    move: {
                        enable: true,
                        direction: "none",
                        random: true,
                        speed: 0.15, // Slow, ambient float
                        outModes: { default: "out" },
                    },
                    opacity: {
                        value: { min: 0.2, max: 0.9 },
                        animation: { enable: true, speed: 0.5, sync: false },
                    },
                    shape: { type: "circle" },
                    size: { value: { min: 1, max: 3.5 } }, // Big enough to see
                },
                background: {
                    color: { value: "transparent" },
                },
            },
        });
    };
        // --- HIGH-PERFORMANCE PARALLAX ENGINE ---
    const initParallax = () => {
        const allPlanets = document.querySelectorAll('.cosmic-planet');
        if (allPlanets.length === 0) return; // Safety check

        function updateParallax() {
            const scrollY = window.scrollY;
            allPlanets.forEach(planet => {
                if (!planet) return; // Extra defensive check
                const size = parseFloat(planet.style.width) || 70;
                const speed = (size / 150) * 0.35; 
                const yMovement = scrollY * -speed;
                planet.style.setProperty('--parallax-y', `${yMovement}px`);
            });
        }

        window.addEventListener('scroll', updateParallax, { passive: true });
    };
    const render = () => {
        drawPlanets();
        drawConstellations();
        
        initParallax();
        // Check repeatedly until tsParticles is loaded from the CDN
        const initParticles = () => {
            if (typeof window.tsParticles !== "undefined") {
                void loadScene();
            } else {
                setTimeout(initParticles, 50); // check again in 50ms
            }
        };

        initParticles();
    };
    render();
    // Add interactive hover effect for constellations
    window.addEventListener("mousemove", (e) => {
        const groups = document.querySelectorAll(".constellation-group");
        groups.forEach((group) => {
            const rect = group.getBoundingClientRect();
            // Calculate center of the constellation
            const centerX = rect.left + rect.width / 2;
            const centerY = rect.top + rect.height / 2;
            
            // Calculate distance from mouse to center
            const distance = Math.hypot(e.clientX - centerX, e.clientY - centerY);

            // Light up if mouse is within 250px
            if (distance < 250) { 
                group.classList.add("is-lit");
            } else {
                group.classList.remove("is-lit");
            }
        });
    });
    let resizeTimer;
    window.addEventListener("resize", () => {
        window.clearTimeout(resizeTimer);
        resizeTimer = window.setTimeout(() => {
            drawPlanets();
            drawConstellations();
        }, 120);
    });
})();
