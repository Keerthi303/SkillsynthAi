/* =========================================================
   SKILL SYNTH AI — analyze.js
   Analysis form handler with drag-drop, loading animation
   ========================================================= */

(function () {
    "use strict";

    // Load roles into selector
    async function loadRoles() {
        try {
            const resp = await fetch("/api/roles");
            const data = await resp.json();
            const select = document.getElementById("targetRoleSelect");
            if (data.roles) {
                data.roles.forEach((r) => {
                    const opt = document.createElement("option");
                    opt.value = r.name;
                    opt.textContent = `${r.name} (${r.skills_count} skills)`;
                    select.appendChild(opt);
                });
            }
        } catch (e) {
            console.warn("Failed to load roles:", e);
        }
    }

    // Role selector → input sync
    const roleSelect = document.getElementById("targetRoleSelect");
    const roleInput = document.getElementById("targetRole");
    if (roleSelect && roleInput) {
        roleSelect.addEventListener("change", () => {
            if (roleSelect.value) roleInput.value = roleSelect.value;
        });
    }

    // File upload UI
    const fileInput = document.getElementById("resume");
    const zone = document.getElementById("fileUploadZone");
    const content = zone?.querySelector(".file-upload__content");
    const selected = zone?.querySelector(".file-upload__selected");
    const fileName = zone?.querySelector(".file-upload__name");
    const removeBtn = zone?.querySelector(".file-upload__remove");

    if (fileInput && zone) {
        // Drag & drop
        zone.addEventListener("dragover", (e) => { e.preventDefault(); zone.classList.add("drag-over"); });
        zone.addEventListener("dragleave", () => zone.classList.remove("drag-over"));
        zone.addEventListener("drop", (e) => {
            e.preventDefault();
            zone.classList.remove("drag-over");
            if (e.dataTransfer.files.length) {
                fileInput.files = e.dataTransfer.files;
                showFile(e.dataTransfer.files[0]);
            }
        });

        fileInput.addEventListener("change", () => {
            if (fileInput.files.length) showFile(fileInput.files[0]);
        });

        removeBtn?.addEventListener("click", (e) => {
            e.stopPropagation();
            fileInput.value = "";
            content.style.display = "";
            selected.style.display = "none";
        });
    }

    function showFile(file) {
        if (content && selected && fileName) {
            content.style.display = "none";
            selected.style.display = "flex";
            fileName.textContent = `📄 ${file.name} (${(file.size / 1024).toFixed(1)} KB)`;
        }
    }

    // Loading steps animation
    function animateLoader() {
        const steps = document.querySelectorAll(".loader-step");
        let i = 0;
        const interval = setInterval(() => {
            if (i < steps.length) {
                steps[i].classList.add("active");
                i++;
            } else {
                clearInterval(interval);
            }
        }, 3000);
        return interval;
    }

    // Check authentication before allowing analysis
    async function checkAuth() {
        try {
            const resp = await fetch("/auth/api/me");
            const data = await resp.json();
            if (!data.authenticated) {
                window.location.href = "/auth/login?next=" + encodeURIComponent(window.location.pathname);
                return false;
            }
            return true;
        } catch (e) {
            console.error("Auth check failed:", e);
            window.location.href = "/auth/login";
            return false;
        }
    }

    // Form submission
    const form = document.getElementById("analyzeForm");
    const loader = document.getElementById("analysisLoader");
    const errorDiv = document.getElementById("analyzeError");

    if (form) {
        form.addEventListener("submit", async (e) => {
            e.preventDefault();
            const btn = document.getElementById("analyzeBtn");
            errorDiv.style.display = "none";

            // Check auth first
            if (!await checkAuth()) {
                return;
            }

            // Validate
            const targetRole = roleInput.value.trim();
            if (!targetRole) {
                errorDiv.textContent = "Please select or type a target role.";
                errorDiv.style.display = "block";
                return;
            }

            // Show loader
            form.style.display = "none";
            loader.style.display = "flex";
            const loaderInterval = animateLoader();

            try {
                const formData = new FormData(form);
                const resp = await fetch("/api/analyze", {
                    method: "POST",
                    body: formData,
                });

                clearInterval(loaderInterval);

                if (!resp.ok) {
                    let errorMsg = `Error ${resp.status}`;
                    try {
                        const respClone = resp.clone();
                        const data = await respClone.json();
                        errorMsg = data.error || data.message || errorMsg;
                    } catch (_) {
                        errorMsg = resp.statusText || errorMsg;
                    }
                    throw new Error(errorMsg);
                }

                let data;
                try {
                    data = await resp.json();
                } catch (parseErr) {
                    throw new Error("Server returned invalid response.");
                }

                if (data.report_id) {
                    window.location.href = `/dashboard/report/${data.report_id}`;
                } else if (data.error) {
                    throw new Error(data.error);
                } else {
                    const errors = data.errors || [];
                    if (errors.length) {
                        throw new Error(errors.join("\n"));
                    }
                    throw new Error("Analysis completed but no report was generated.");
                }
            } catch (err) {
                clearInterval(loaderInterval);
                loader.style.display = "none";
                form.style.display = "";
                errorDiv.textContent = err.message;
                errorDiv.style.display = "block";
            }
        });
    }

    // Init
    loadRoles();
})();
