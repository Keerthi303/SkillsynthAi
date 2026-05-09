/* =========================================================
   SKILL SYNTH AI — admin.js
   Admin panel: tabs, stats, role management, user/report views
   ========================================================= */

(function () {
    "use strict";

    // Tab switching
    const tabs = document.querySelectorAll(".admin-tab");
    const panels = document.querySelectorAll(".tab-panel");

    tabs.forEach((tab) => {
        tab.addEventListener("click", () => {
            tabs.forEach((t) => t.classList.remove("active"));
            panels.forEach((p) => p.classList.remove("active"));
            tab.classList.add("active");
            document.getElementById(`panel-${tab.dataset.tab}`)?.classList.add("active");
        });
    });

    // Load stats
    async function loadStats() {
        try {
            const resp = await fetch("/admin/api/stats");
            const data = await resp.json();
            document.getElementById("statUsers").textContent = data.users || 0;
            document.getElementById("statReports").textContent = data.reports || 0;
            document.getElementById("statDocs").textContent = data.kb_stats?.total_documents || 0;
            document.getElementById("statRoles").textContent = data.kb_stats?.total_roles || 0;
        } catch (e) {
            console.error("Failed to load stats:", e);
        }
    }

    // Load roles
    async function loadRoles() {
        try {
            const resp = await fetch("/admin/api/roles");
            const data = await resp.json();
            const grid = document.getElementById("rolesGrid");
            if (!data.roles?.length) {
                grid.innerHTML = '<p class="text-muted">No roles in knowledge base</p>';
                return;
            }
            grid.innerHTML = data.roles.map((r) => `
                <div class="admin-card glass">
                    <h4>${r.name}</h4>
                    <p class="text-muted">${r.skills_count} required skills</p>
                    <span class="chip">${r.key}</span>
                </div>
            `).join("");
        } catch (e) {
            console.error("Failed to load roles:", e);
        }
    }

    // Load users
    async function loadUsers() {
        try {
            const resp = await fetch("/admin/api/users");
            const data = await resp.json();
            const el = document.getElementById("usersTable");
            if (!data.users?.length) {
                el.innerHTML = '<p class="text-muted">No users yet</p>';
                return;
            }
            el.innerHTML = `<table class="admin-table">
                <thead><tr><th>Name</th><th>Email</th><th>Admin</th><th>Reports</th><th>Joined</th></tr></thead>
                <tbody>${data.users.map((u) => `<tr>
                    <td>${u.name || "—"}</td>
                    <td>${u.email}</td>
                    <td>${u.is_admin ? "✅" : "—"}</td>
                    <td>${u.reports_count}</td>
                    <td>${u.created_at ? new Date(u.created_at).toLocaleDateString() : "—"}</td>
                </tr>`).join("")}</tbody>
            </table>`;
        } catch (e) {
            console.error("Failed to load users:", e);
        }
    }

    // Load reports
    async function loadReports() {
        try {
            const resp = await fetch("/admin/api/reports");
            const data = await resp.json();
            const el = document.getElementById("reportsTable");
            if (!data.reports?.length) {
                el.innerHTML = '<p class="text-muted">No reports yet</p>';
                return;
            }
            el.innerHTML = `<table class="admin-table">
                <thead><tr><th>User</th><th>Role</th><th>ATS</th><th>Readiness</th><th>DSA</th><th>Date</th></tr></thead>
                <tbody>${data.reports.map((r) => `<tr>
                    <td>${r.user_email || "—"}</td>
                    <td>${r.target_role}</td>
                    <td>${r.ats_score}%</td>
                    <td>${r.hiring_readiness}%</td>
                    <td>${r.dsa_level}</td>
                    <td>${r.created_at ? new Date(r.created_at).toLocaleDateString() : "—"}</td>
                </tr>`).join("")}</tbody>
            </table>`;
        } catch (e) {
            console.error("Failed to load reports:", e);
        }
    }

    // Add role form
    const addRoleForm = document.getElementById("addRoleForm");
    if (addRoleForm) {
        addRoleForm.addEventListener("submit", async (e) => {
            e.preventDefault();
            const payload = {
                key: document.getElementById("roleKey").value.trim(),
                role: document.getElementById("roleName").value.trim(),
                required_skills: document.getElementById("roleSkills").value.split(",").map((s) => s.trim()).filter(Boolean),
                interview_topics: document.getElementById("roleTopics").value.split(",").map((s) => s.trim()).filter(Boolean),
                industry_standards: document.getElementById("roleStandards").value.split(",").map((s) => s.trim()).filter(Boolean),
            };
            try {
                const resp = await fetch("/admin/api/roles", {
                    method: "POST",
                    headers: { "Content-Type": "application/json" },
                    body: JSON.stringify(payload),
                });
                const data = await resp.json();
                if (data.success) {
                    alert("Role added successfully!");
                    addRoleForm.reset();
                    loadRoles();
                    loadStats();
                } else {
                    alert(data.error || "Failed to add role");
                }
            } catch (err) {
                alert("Error: " + err.message);
            }
        });
    }

    // Init
    loadStats();
    loadRoles();
    loadUsers();
    loadReports();
})();
