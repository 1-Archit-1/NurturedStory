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
            const mobileFactor = window.innerWidth <= 860 ? 0.5 : 1;
            const scaledSize = Math.round(size * mobileFactor);
            const t = (index + 1) / (planets.length + 1);

            // 1. THE INWARD CURVE
            const basePathX = 20 + (t * 60) - (Math.sin(t * Math.PI) * 26);
            const basePathY = 8 + (t * 84);

            // 2. THE ANTI-COLLISION STAGGER
            const staggerX = (index % 2 === 0 ? -1 : 1) * 12; 
            const scatterY = (seedValue(90 + index) - 0.5) * 4;

            const pathX = clamp(basePathX + staggerX, 5, 95);
            const pathY = clamp(basePathY + scatterY, 5, 95);

            const anchorEl = planet.anchor ? document.querySelector(`[data-cosmic-anchor="${planet.anchor}"]`) : null;
            const anchorRect = anchorEl ? anchorEl.getBoundingClientRect() : null;
            const anchorX = anchorRect ? ((anchorRect.left + anchorRect.width / 2) / window.innerWidth) * 100 : null;
            const anchorY = anchorRect ? ((anchorRect.top + anchorRect.height / 2) / window.innerHeight) * 100 : null;
            
            const x = clamp(anchorX !== null ? pathX * 0.95 + anchorX * 0.05 : pathX, 5, 95);
            const y = clamp(anchorY !== null ? pathY * 0.95 + anchorY * 0.05 : pathY, 5, 95);

            planetEl.style.left = `${x}%`;
            planetEl.style.top = `${y}%`;
            planetEl.style.width = `${scaledSize}px`;
            planetEl.style.height = `${scaledSize}px`;
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
        
        // Local coordinates for perfect squares
        const localPoints = {
            "big_dipper": [
                {x: 5, y: 20}, {x: 25, y: 35}, {x: 50, y: 45}, {x: 40, y: 65},
                {x: 75, y: 80}, {x: 95, y: 50}, {x: 80, y: 25}
            ],
            "orion": [
                {x: 10, y: 15}, {x: 35, y: 20}, {x: 20, y: 50}, {x: 30, y: 55},
                {x: 40, y: 50}, {x: 10, y: 95}, {x: 55, y: 90}, {x: 25, y: 5}
            ],
            "gemini": [
                {x: 20, y: 10}, {x: 50, y: 25}, {x: 10, y: 60}, {x: 40, y: 65},
                {x: 5, y: 95}, {x: 30, y: 100}, {x: 60, y: 80}, {x: 40, y: 5}
            ]
        };

        const constellations = Array.isArray(config.constellations) ? config.constellations : [];

        constellations.forEach((constellation, index) => {
            const points = localPoints[constellation.id] || [];
            if (points.length < 2) return;

            // Distribute down the page safely
            const t = (index + 1) / (constellations.length + 1);
            const topPercent = 15 + (t * 70); 
            const leftPercent = index % 2 === 0 ? 20 : 80;

            const groupWrapper = document.createElement("div");
            groupWrapper.className = "constellation-group";
            groupWrapper.dataset.constellation = constellation.id || "";
            
            groupWrapper.style.left = `${leftPercent}%`;
            groupWrapper.style.top = `${topPercent}%`;

            const randomDelay = Math.random() * 4;
            groupWrapper.style.animationDelay = `${randomDelay}s`;

            const svg = document.createElementNS("http://www.w3.org/2000/svg", "svg");
            svg.setAttribute("viewBox", "0 0 100 100");
            svg.style.width = "100%";
            svg.style.height = "100%";
            svg.style.overflow = "visible"; 

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
                line.setAttribute("style", `stroke: ${constellation.color || "rgba(180, 210, 255, 0.4)"}; stroke-dasharray: 2 4;`);
                svg.appendChild(line);
            });

            points.forEach((point, i) => {
                const star = document.createElementNS("http://www.w3.org/2000/svg", "circle");
                star.setAttribute("cx", `${point.x}`);
                star.setAttribute("cy", `${point.y}`);
                star.setAttribute("r", i === 0 ? "1.2" : "1.2");
                star.setAttribute("class", "constellation-star");
                svg.appendChild(star);
            });

            const label = document.createElementNS("http://www.w3.org/2000/svg", "text");
            label.setAttribute("x", `${points[0].x + 5}`);
            label.setAttribute("y", `${points[0].y + 7}`);
            label.setAttribute("class", "constellation-label");
            label.textContent = (constellation.label || "").toUpperCase();
            svg.appendChild(label);

            groupWrapper.appendChild(svg);
            constellationHost.appendChild(groupWrapper);
        });
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
                        value: Number(config.stars) || 420,
                        density: { enable: true, width: 1920, height: 1080 },
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
                    size: { value: { min: 0.4, max: 1.4 } },
                },
                background: {
                    color: { value: "transparent" },
                },
            },
        });
    };
    const initParallax = () => {
        const allPlanets = document.querySelectorAll('.cosmic-planet');
        const allConstellations = document.querySelectorAll('.constellation-group');

        let ticking = false;

        const applyParallax = () => {
            const scrollY = window.scrollY;

            allPlanets.forEach(planet => {
                if (!planet) return;
                const size = parseFloat(planet.style.width) || 70;
                const speed = (size / 150) * 0.35;
                planet.style.setProperty('--parallax-y', `${scrollY * -speed}px`);
            });

            allConstellations.forEach(constellation => {
                constellation.style.setProperty('--parallax-y', `${scrollY * -0.12}px`);
            });

            ticking = false;
        };

        window.addEventListener('scroll', () => {
            if (!ticking) {
                requestAnimationFrame(applyParallax);
                ticking = true;
            }
        }, { passive: true });
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
