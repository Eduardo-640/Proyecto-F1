document.addEventListener('DOMContentLoaded', function () {
    function q(id) {
        return document.getElementById(id);
    }

    const teamEl = q('id_team');
    const seasonEl = q('id_season');
    const deptEl = q('id_department');
    const costEl = q('id_cost');

    // Use a fixed admin compute endpoint path so it works reliably.
    const url = '/admin/developments/purchasedupgrade/compute_price/';

    async function updatePrice() {
        if (!teamEl || !seasonEl || !deptEl || !costEl) return;
        const team = teamEl.value;
        const season = seasonEl.value;
        const department = deptEl.value;
        if (!team || !season || !department) return;

        try {
            const resp = await fetch(
                url +
                    '?team=' +
                    encodeURIComponent(team) +
                    '&season=' +
                    encodeURIComponent(season) +
                    '&department=' +
                    encodeURIComponent(department),
                {
                    credentials: 'same-origin',
                },
            );
            if (!resp.ok) return;
            const data = await resp.json();
            if (data.error) return;
            // Update cost input placeholder and autofill the value
            costEl.placeholder = data.charged;
            // Always present the suggested price to the user by setting the value
            costEl.value = data.charged;
            // Show a small badge with details
            let info = document.getElementById('upgrade_price_info');
            if (!info) {
                info = document.createElement('div');
                info.id = 'upgrade_price_info';
                info.style.marginTop = '6px';
                info.style.fontSize = '90%';
                costEl.parentNode.appendChild(info);
            }
            info.textContent = `Precio sugerido: ${data.charged} (base ${data.base_cost} × mult ${data.multiplier.toFixed(2)})`;
            // Show team credits and resulting balance
            let econ = document.getElementById('upgrade_economy_info');
            if (!econ) {
                econ = document.createElement('div');
                econ.id = 'upgrade_economy_info';
                econ.style.marginTop = '4px';
                econ.style.fontSize = '90%';
                costEl.parentNode.appendChild(econ);
            }
            const teamCredits =
                data.team_credits != null ? data.team_credits : '—';
            const after =
                data.team_credits != null
                    ? data.team_credits - data.charged
                    : '—';
            econ.textContent = `Créditos equipo: ${teamCredits}  ·  Saldo tras compra: ${after}`;
            // Show levels summary
            let lvl = document.getElementById('upgrade_level_info');
            if (!lvl) {
                lvl = document.createElement('div');
                lvl.id = 'upgrade_level_info';
                lvl.style.marginTop = '4px';
                lvl.style.fontSize = '90%';
                costEl.parentNode.appendChild(lvl);
            }
            const prev = data.previous_level || 1;
            const next = prev + 1;
            lvl.textContent = `Nivel actual: ${prev} → Nivel tras compra: ${next}`;
        } catch (err) {
            // ignore
        }
    }

    [teamEl, seasonEl, deptEl].forEach(function (el) {
        if (!el) return;
        el.addEventListener('change', function () {
            // small debounce
            if (window.__updatePriceTimer)
                clearTimeout(window.__updatePriceTimer);
            window.__updatePriceTimer = setTimeout(updatePrice, 250);
        });
    });

    // initial attempt
    setTimeout(updatePrice, 300);
});
