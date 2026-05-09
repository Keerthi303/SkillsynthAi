/* =========================================================
   SKILL SYNTH AI — main.js
   Minimal foundation. Module-specific JS will live in
   /static/js/<module>.js as we add them.
   ========================================================= */

(function () {
    "use strict";

    /* --- Reveal-on-scroll for sections --- */
    const targets = document.querySelectorAll(".step, .feature, .module");
    if (!targets.length || !("IntersectionObserver" in window)) return;

    targets.forEach((el) => {
        el.style.opacity = "0";
        el.style.transform = "translateY(24px)";
        el.style.transition = "opacity 0.7s cubic-bezier(0.16, 1, 0.3, 1), transform 0.7s cubic-bezier(0.16, 1, 0.3, 1)";
    });

    const observer = new IntersectionObserver(
        (entries) => {
            entries.forEach((entry, i) => {
                if (entry.isIntersecting) {
                    setTimeout(() => {
                        entry.target.style.opacity = "1";
                        entry.target.style.transform = "translateY(0)";
                    }, i * 60);
                    observer.unobserve(entry.target);
                }
            });
        },
        { threshold: 0.12, rootMargin: "0px 0px -60px 0px" }
    );

    targets.forEach((el) => observer.observe(el));
})();
