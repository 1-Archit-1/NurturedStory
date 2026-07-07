(() => {
  const host = document.getElementById("services-particles-canvas");
  if (!host || typeof window.tsParticles === "undefined") return;

  let loaded = false;

  const init = async () => {
    if (loaded) return;
    loaded = true;

    await window.tsParticles.load({
      id: "services-particles-canvas",
      options: {
        fullScreen: { enable: false },
        detectRetina: true,
        fpsLimit: 60,
        background: { color: "transparent" },
        particles: {
          number: {
            value: 40,
            density: { enable: true, width: 900, height: 380 },
          },
          color: { value: ["#d2ece5", "#b6dff7", "#d9c9ff"] },
          size: { value: { min: 0.8, max: 2.2 } },
          opacity: {
            value: { min: 0.2, max: 0.65 },
            animation: { enable: true, speed: 0.4, sync: false },
          },
          links: {
            enable: true,
            distance: 110,
            color: "rgba(160, 235, 220, 0.22)",
            opacity: 0.28,
            width: 0.7,
          },
          move: {
            enable: true,
            speed: 0.15,
            direction: "none",
            random: true,
            outModes: { default: "out" },
          },
        },
        interactivity: {
          events: {
            onHover: { enable: true, mode: "grab" },
          },
          modes: {
            grab: {
              distance: 120,
              links: { opacity: 0.45 },
            },
          },
        },
      },
    });
  };

  if (typeof window.tsParticles !== "undefined") {
    void init();
    return;
  }

  let attempts = 0;
  const timer = window.setInterval(() => {
    attempts += 1;
    if (typeof window.tsParticles !== "undefined") {
      window.clearInterval(timer);
      void init();
    } else if (attempts > 120) {
      window.clearInterval(timer);
    }
  }, 50);
})();
