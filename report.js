/* =========================================================
   SKILL SYNTH AI — report.js
   Fetches report data and renders the full report UI with charts
   ========================================================= */

(function () {
    "use strict";

    const reportPage = document.querySelector(".report-page");
    if (!reportPage) return;

    const reportId = reportPage.dataset.reportId;
    const contentEl = document.getElementById("reportContent");

    // Animate score rings
    function animateRing(id, pct, circumference = 327) {
        const el = document.getElementById(id);
        if (!el) return;
        const dashLen = (pct / 100) * circumference;
        setTimeout(() => {
            el.style.transition = "stroke-dasharray 1.5s cubic-bezier(0.16, 1, 0.3, 1)";
            el.setAttribute("stroke-dasharray", `${dashLen}, ${circumference}`);
        }, 300);
    }

    function renderSkillChips(skills, type = "strong") {
        if (!skills || !skills.length) return "<p class='text-muted'>No data available</p>";
        return skills.map((s) => {
            const name = typeof s === "object" ? s.skill || s.name || JSON.stringify(s) : s;
            const cls = type === "strong" ? "chip--green" : type === "missing" ? "chip--red" : "chip--amber";
            return `<span class="chip ${cls}">${name}</span>`;
        }).join("");
    }

    function renderSection(title, icon, content) {
        return `<div class="report-section glass">
            <h2 class="report-section__title"><span>${icon}</span> ${title}</h2>
            <div class="report-section__body">${content}</div>
        </div>`;
    }

    function renderResourceList(items, icon = "🔗") {
        if (!items || !items.length) return "<p class='text-muted'>No recommendations available</p>";
        return `<div class="resource-list">${items.map((item) => {
            const title = item.title || item.name || "Resource";
            const url = item.url || "#";
            const desc = item.description || item.skill || "";
            return `<a href="${url}" target="_blank" class="resource-item glass">
                <span class="resource-icon">${icon}</span>
                <div><strong>${title}</strong><p>${desc}</p></div>
                <span class="resource-arrow">↗</span>
            </a>`;
        }).join("")}</div>`;
    }

    async function loadReport() {
        try {
            const resp = await fetch(`/api/report/${reportId}`);
            const json = await resp.json();
            if (json.error) throw new Error(json.error);

            const data = json.data || {};
            const ai = data.ai_report || {};
            const summary = data.summary || {};
            const resume = data.resume_analysis || {};
            const github = data.github_analysis || {};
            const leetcode = data.leetcode_analysis || {};
            const resources = data.resources || {};
            const skillGap = data.skill_gap || {};

            // Animate rings
            animateRing("readinessRing", summary.hiring_readiness || 0);
            animateRing("atsRing", summary.ats_score || 0);

            let html = "";

            // === Overall Assessment ===
            if (ai.overall_assessment) {
                html += renderSection("Overall Assessment", "🎯", `<p class="assessment-text">${ai.overall_assessment}</p>` +
                    (ai.time_to_ready ? `<p class="time-ready"><strong>Estimated time to ready:</strong> ${ai.time_to_ready}</p>` : ""));
            }

            // === Skills Analysis ===
            html += renderSection("Skill Analysis", "◈", `
                <div class="skills-grid">
                    <div class="skills-col">
                        <h4 class="text-green">Strong Skills</h4>
                        <div class="chip-wrap">${renderSkillChips(ai.strong_skills || skillGap.strong_skills, "strong")}</div>
                    </div>
                    <div class="skills-col">
                        <h4 class="text-amber">Weak Skills</h4>
                        <div class="chip-wrap">${renderSkillChips(ai.weak_skills || [], "weak")}</div>
                    </div>
                    <div class="skills-col">
                        <h4 class="text-red">Missing Skills</h4>
                        <div class="chip-wrap">${renderSkillChips(ai.missing_skills || skillGap.missing_skills, "missing")}</div>
                    </div>
                </div>
            `);

            // === GitHub Analysis ===
            if (github && !github.error) {
                const profile = github.profile || {};
                const langs = github.languages || {};
                const langLabels = Object.keys(langs).slice(0, 8);
                const langValues = langLabels.map((l) => langs[l]);

                let ghContent = `<div class="github-summary">
                    <div class="gh-stat"><strong>${github.total_repos || 0}</strong><span>Repos</span></div>
                    <div class="gh-stat"><strong>${github.total_stars || 0}</strong><span>Stars</span></div>
                    <div class="gh-stat"><strong>${github.commit_consistency || "N/A"}</strong><span>Consistency</span></div>
                    <div class="gh-stat"><strong>${github.ai_ml_usage ? "Yes" : "No"}</strong><span>AI/ML</span></div>
                </div>`;

                if (langLabels.length) {
                    ghContent += `<div class="chart-wrap"><canvas id="langChart" height="200"></canvas></div>`;
                }

                if (github.frameworks?.length) {
                    ghContent += `<div style="margin-top:16px"><h4>Frameworks Detected</h4><div class="chip-wrap">${github.frameworks.map(f => `<span class="chip chip--cyan">${f}</span>`).join("")}</div></div>`;
                }

                html += renderSection("GitHub Analysis", "⌬", ghContent);

                // Render chart after DOM update
                setTimeout(() => {
                    const ctx = document.getElementById("langChart");
                    if (ctx && window.Chart) {
                        new Chart(ctx, {
                            type: "doughnut",
                            data: {
                                labels: langLabels,
                                datasets: [{ data: langValues, backgroundColor: ["#7df9ff","#f5b66c","#ff7fa3","#8bf2c5","#b4a0ff","#ffd166","#06d6a0","#118ab2"], borderWidth: 0 }],
                            },
                            options: {
                                responsive: true,
                                plugins: { legend: { position: "right", labels: { color: "#d4d7e3", font: { family: "'Geist', sans-serif", size: 12 } } } },
                                cutout: "60%",
                            },
                        });
                    }
                }, 100);
            }

            // === LeetCode Analysis ===
            if (leetcode && !leetcode.error && leetcode.total_solved) {
                let lcContent = `<div class="github-summary">
                    <div class="gh-stat"><strong>${leetcode.total_solved}</strong><span>Total Solved</span></div>
                    <div class="gh-stat text-green"><strong>${leetcode.easy_solved || 0}</strong><span>Easy</span></div>
                    <div class="gh-stat text-amber"><strong>${leetcode.medium_solved || 0}</strong><span>Medium</span></div>
                    <div class="gh-stat text-red"><strong>${leetcode.hard_solved || 0}</strong><span>Hard</span></div>
                </div>
                <div class="chart-wrap"><canvas id="lcChart" height="200"></canvas></div>`;

                if (leetcode.contest_rating) {
                    lcContent += `<p style="margin-top:12px"><strong>Contest Rating:</strong> ${leetcode.contest_rating}</p>`;
                }
                if (leetcode.strong_topics?.length) {
                    lcContent += `<div style="margin-top:12px"><h4>Strong Topics</h4><div class="chip-wrap">${leetcode.strong_topics.map(t => `<span class="chip chip--green">${t}</span>`).join("")}</div></div>`;
                }
                if (leetcode.weak_topics?.length) {
                    lcContent += `<div style="margin-top:12px"><h4>Weak Topics</h4><div class="chip-wrap">${leetcode.weak_topics.map(t => `<span class="chip chip--red">${t}</span>`).join("")}</div></div>`;
                }

                html += renderSection("LeetCode / DSA Analysis", "⊹", lcContent);

                setTimeout(() => {
                    const ctx = document.getElementById("lcChart");
                    if (ctx && window.Chart) {
                        new Chart(ctx, {
                            type: "bar",
                            data: {
                                labels: ["Easy", "Medium", "Hard"],
                                datasets: [{ data: [leetcode.easy_solved || 0, leetcode.medium_solved || 0, leetcode.hard_solved || 0], backgroundColor: ["#8bf2c5","#f5b66c","#ff7fa3"], borderRadius: 8, barThickness: 40 }],
                            },
                            options: { responsive: true, plugins: { legend: { display: false } }, scales: { x: { ticks: { color: "#d4d7e3" }, grid: { display: false } }, y: { ticks: { color: "#8b8e9c" }, grid: { color: "rgba(255,255,255,0.05)" } } } },
                        });
                    }
                }, 100);
            }

            // === Improvement Roadmap ===
            if (ai.improvement_roadmap?.length) {
                let roadmapHtml = `<div class="roadmap-timeline">`;
                ai.improvement_roadmap.forEach((phase) => {
                    roadmapHtml += `<div class="roadmap-phase glass">
                        <div class="phase-header"><span class="phase-num">Phase ${phase.phase || ""}</span><strong>${phase.title || ""}</strong><span class="phase-duration">${phase.duration || ""}</span></div>
                        <ul class="phase-tasks">${(phase.tasks || []).map(t => `<li>${t}</li>`).join("")}</ul>
                        ${phase.skills_covered?.length ? `<div class="chip-wrap">${phase.skills_covered.map(s => `<span class="chip chip--cyan">${s}</span>`).join("")}</div>` : ""}
                    </div>`;
                });
                roadmapHtml += `</div>`;
                html += renderSection("Improvement Roadmap", "🗺️", roadmapHtml);
            }

            // === Recommended Projects ===
            if (ai.recommended_projects?.length) {
                let projHtml = `<div class="projects-grid">`;
                ai.recommended_projects.forEach((p) => {
                    projHtml += `<div class="project-card glass">
                        <h4>${p.title || ""}</h4>
                        <p>${p.description || ""}</p>
                        <span class="chip chip--cyan">${p.difficulty || ""}</span>
                        ${p.skills_practiced?.length ? `<div class="chip-wrap" style="margin-top:8px">${p.skills_practiced.map(s => `<span class="chip">${s}</span>`).join("")}</div>` : ""}
                    </div>`;
                });
                projHtml += `</div>`;
                html += renderSection("Recommended Projects", "💡", projHtml);
            }

            // === Resources ===
            if (resources) {
                let resHtml = "";
                if (resources.youtube_playlists?.length) resHtml += `<h4 style="margin-bottom:8px">📺 YouTube</h4>` + renderResourceList(resources.youtube_playlists, "📺");
                if (resources.github_repositories?.length) resHtml += `<h4 style="margin:16px 0 8px">📂 GitHub Repos</h4>` + renderResourceList(resources.github_repositories, "📂");
                if (resources.articles_and_docs?.length) resHtml += `<h4 style="margin:16px 0 8px">📄 Articles & Docs</h4>` + renderResourceList(resources.articles_and_docs, "📄");
                if (resources.courses?.length) resHtml += `<h4 style="margin:16px 0 8px">🎓 Courses</h4>` + renderResourceList(resources.courses, "🎓");
                if (resources.dsa_sheets?.length) resHtml += `<h4 style="margin:16px 0 8px">📋 DSA Sheets</h4>` + renderResourceList(resources.dsa_sheets, "📋");
                if (resHtml) html += renderSection("Personalized Resources", "📚", resHtml);
            }

            // === Coding Practice ===
            if (ai.coding_questions_to_practice?.length) {
                let cqHtml = `<div class="coding-topics">`;
                ai.coding_questions_to_practice.forEach((topic) => {
                    cqHtml += `<div class="coding-topic glass">
                        <h4>${topic.topic || ""} <span class="chip chip--${topic.difficulty === "easy" ? "green" : topic.difficulty === "hard" ? "red" : "amber"}">${topic.difficulty || ""}</span></h4>
                        <ul>${(topic.questions || []).map(q => `<li>${q}</li>`).join("")}</ul>
                    </div>`;
                });
                cqHtml += `</div>`;
                html += renderSection("Coding Questions to Practice", "⌨️", cqHtml);
            }

            contentEl.innerHTML = html;
        } catch (err) {
            contentEl.innerHTML = `<div class="report-section glass"><h2>Error</h2><p>${err.message}</p></div>`;
        }
    }

    loadReport();
})();
