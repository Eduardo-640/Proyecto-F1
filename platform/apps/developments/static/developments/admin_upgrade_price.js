document.addEventListener('DOMContentLoaded', function () {
    function q(id) {
        return document.getElementById(id);
    }

    const teamEl = q('id_team');
    const seasonEl = q('id_season');
    const deptEl = q('id_department');
    const costEl = q('id_cost');
    const url = '/admin/developments/purchasedupgrade/compute_price/';

    // ── visual helpers ───────────────────────────────────────────────────
    function pct(mult) {
        const delta = Math.round((mult - 1) * 100);
        if (delta === 0)
            return '<span style="color:#888">sin efecto (×1.00)</span>';
        if (delta < 0)
            return `<span style="color:#2a7ae2;font-weight:bold">${delta}% descuento (×${mult.toFixed(2)})</span>`;
        return `<span style="color:#c0392b;font-weight:bold">+${delta}% recargo (×${mult.toFixed(2)})</span>`;
    }

    function levelBar(current, next, max) {
        let html = '';
        for (let i = 1; i <= max; i++) {
            let color, sym;
            if (i < next) {
                color = '#2a7ae2';
                sym = '■';
            } else if (i === next) {
                color = '#27ae60';
                sym = '▲';
            } else {
                color = '#ccc';
                sym = '□';
            }
            html += `<span style="color:${color};font-size:1.25em;margin-right:1px" title="Nivel ${i}">${sym}</span>`;
        }
        return (
            html +
            `&nbsp;<span style="color:#555">${current} → <strong style="color:#27ae60">${next}</strong></span>`
        );
    }

    function allLevelsBar(levels, activeDept) {
        const depts = [
            'engine',
            'aerodynamics',
            'chassis',
            'suspension',
            'electronics',
        ];
        const labels = {
            engine: 'Motor',
            aerodynamics: 'Aero',
            chassis: 'Chasis',
            suspension: 'Suspensión',
            electronics: 'Electrónica',
        };
        return depts
            .map((d) => {
                const lvl = levels[d] || 1;
                const hi = d === activeDept;
                const color = hi ? '#2a7ae2' : '#555';
                const dots = '●'.repeat(lvl) + '○'.repeat(5 - lvl);
                return `<span style="color:${color};margin-right:10px${hi ? ';font-weight:bold' : ''}">
                        ${labels[d]}: <span style="letter-spacing:1px">${dots}</span> ${lvl}
                    </span>`;
            })
            .join('');
    }

    function sponsorConditionsHtml(sponsor, activeDept) {
        if (!sponsor)
            return '<em style="color:#888">Sin sponsor principal</em>';
        const conds = sponsor.conditions || [];
        let rows = '';
        for (const c of conds) {
            const hi = c.affects_this_dept;
            const color = hi ? (c.value > 0 ? '#2a7ae2' : '#c0392b') : '#666';
            const bg = hi
                ? c.value > 0
                    ? '#eaf4ff'
                    : '#fff0f0'
                : 'transparent';
            const sign = c.value > 0 ? '+1 ✅' : '−1 ⚠️';
            const dept = c.mapped_dept ? ` → <em>${c.mapped_dept}</em>` : '';
            rows += `<tr style="background:${bg}">
                       <td style="padding:2px 8px 2px 0;color:${color}"><strong>${c.category}</strong>${dept}</td>
                       <td style="color:${color}">${sign}</td>
                       <td style="color:${hi ? color : '#999'};font-size:90%">${hi ? (c.value > 0 ? '−5% costo' : '+10% costo') : '—'}</td>
                     </tr>`;
        }
        const moneyRow = `<tr>
            <td style="padding:2px 8px 2px 0;color:#888"><strong>money</strong></td>
            <td style="color:#2a7ae2">+${sponsor.money_value}</td>
            <td style="color:#2a7ae2;font-size:90%">−${sponsor.money_value * 5}% todas las mejoras</td>
          </tr>`;
        return `<strong style="font-size:95%">🏷 ${sponsor.name}</strong>
                <table style="border-collapse:collapse;margin-top:4px;width:100%">
                  <thead><tr style="border-bottom:1px solid #ddd;color:#888;font-size:85%">
                    <th style="text-align:left;padding-bottom:2px">Categoría</th>
                    <th style="text-align:left">Valor</th>
                    <th style="text-align:left">Efecto en costo</th>
                  </tr></thead>
                  <tbody>${rows}${moneyRow}</tbody>
                </table>`;
    }

    // ── main render ──────────────────────────────────────────────────────
    async function updatePrice() {
        if (!teamEl || !seasonEl || !deptEl || !costEl) return;
        const team = teamEl.value;
        const season = seasonEl.value;
        const department = deptEl.value;

        const existing = document.getElementById('upgrade_detail_panel');
        if (!team || !season || !department) {
            if (existing) existing.remove();
            return;
        }

        try {
            const resp = await fetch(
                `${url}?team=${encodeURIComponent(team)}&season=${encodeURIComponent(season)}&department=${encodeURIComponent(department)}`,
                { credentials: 'same-origin' },
            );
            if (!resp.ok) return;
            const d = await resp.json();
            if (d.error) return;

            costEl.value = d.base_cost;

            const prev = d.previous_level || 1;
            const next = prev + 1;
            const maxLvl = d.max_level || 5;
            const moneyMul =
                d.money_multiplier != null ? d.money_multiplier : 1;
            const deptMul = d.dept_multiplier != null ? d.dept_multiplier : 1;
            const combined =
                d.combined_multiplier != null
                    ? d.combined_multiplier
                    : moneyMul;
            const after =
                d.team_credits != null ? d.team_credits - d.charged : null;
            const noFunds = after !== null && after < 0;
            const atMax = next > maxLvl;

            const afterColor = noFunds ? '#c0392b' : '#27ae60';
            const afterText =
                after !== null
                    ? `<span style="color:${afterColor};font-weight:bold">${after.toLocaleString()} cr${noFunds ? ' &nbsp;⚠️ FONDOS INSUFICIENTES' : ''}</span>`
                    : '—';

            let wrap = document.getElementById('upgrade_detail_panel');
            if (!wrap) {
                wrap = document.createElement('div');
                wrap.id = 'upgrade_detail_panel';
                wrap.style.cssText =
                    'margin:16px 0;padding:14px 16px;background:#f9f9f9;border:1px solid #d0d0d0;border-radius:5px;font-size:93%;line-height:1.8;clear:both';
                // Insert before the save button row — always visible in Django admin
                const submitRow = document.querySelector('.submit-row');
                const form =
                    document.querySelector('#content-main form') ||
                    document.querySelector('form[method="post"]');
                if (submitRow) {
                    submitRow.insertAdjacentElement('beforebegin', wrap);
                } else if (form) {
                    form.appendChild(wrap);
                } else {
                    document.body.appendChild(wrap);
                }
            }

            wrap.innerHTML = `
<!-- NIVEL -->
<div style="margin-bottom:10px">
  <span style="font-weight:bold">🔧 ${department.charAt(0).toUpperCase() + department.slice(1)}</span>&nbsp;&nbsp;
  ${
      atMax
          ? '<span style="color:#c0392b;font-weight:bold">⛔ Ya está en nivel máximo (5)</span>'
          : levelBar(prev, next, maxLvl)
  }
</div>

<!-- NIVELES ACTUALES -->
${
    d.all_levels && Object.keys(d.all_levels).length
        ? `<div style="margin-bottom:10px;padding:6px 8px;background:#fff;border:1px solid #e8e8e8;border-radius:3px;font-size:90%">
       <strong>Niveles actuales del equipo:</strong><br>
       <div style="margin-top:4px">${allLevelsBar(d.all_levels, department)}</div>
     </div>`
        : ''
}

<!-- DESGLOSE DE COSTO -->
<table style="border-collapse:collapse;width:100%;margin-bottom:10px">
  <tr>
    <td style="padding:3px 10px 3px 0;color:#555;width:45%">Costo base <small>(nivel ${prev}→${next})</small></td>
    <td><strong>${d.base_cost.toLocaleString()} cr</strong></td>
  </tr>
  <tr>
    <td style="padding:3px 10px 3px 0;color:#555">💰 Descuento money del sponsor</td>
    <td>${pct(moneyMul)}</td>
  </tr>
  <tr>
    <td style="padding:3px 10px 3px 0;color:#555">🏎 Afinidad/penalidad del dpto.</td>
    <td>${pct(deptMul)}</td>
  </tr>
  <tr style="border-top:1px solid #ccc">
    <td style="padding:3px 10px 3px 0;color:#555">Multiplicador combinado</td>
    <td>×${combined.toFixed(3)}</td>
  </tr>
  <tr style="background:#fffbe6;border-top:2px solid #e0c000">
    <td style="padding:5px 10px 5px 0;font-weight:bold;font-size:1.05em">💳 Costo final a cobrar</td>
    <td style="font-size:1.2em;font-weight:bold">${d.charged.toLocaleString()} cr</td>
  </tr>
  <tr style="border-top:1px solid #e0e0e0">
    <td style="padding:3px 10px 3px 0;color:#555">Créditos actuales del equipo</td>
    <td>${d.team_credits != null ? d.team_credits.toLocaleString() + ' cr' : '—'}</td>
  </tr>
  <tr>
    <td style="padding:3px 10px 3px 0;color:#555">Saldo tras la compra</td>
    <td>${afterText}</td>
  </tr>
</table>

<!-- SPONSOR CONDITIONS -->
<details style="margin-top:4px">
  <summary style="cursor:pointer;color:#2a7ae2;font-weight:bold;font-size:92%">📋 Condiciones del sponsor (efecto en esta mejora)</summary>
  <div style="margin-top:8px;padding:8px;background:#fff;border:1px solid #e0e0e0;border-radius:3px">
    ${sponsorConditionsHtml(d.sponsor, department)}
  </div>
</details>`;
        } catch (err) {
            console.error('[upgrade panel]', err);
        }
    }

    [teamEl, seasonEl, deptEl].forEach(function (el) {
        if (!el) return;
        el.addEventListener('change', function () {
            if (window.__updatePriceTimer)
                clearTimeout(window.__updatePriceTimer);
            window.__updatePriceTimer = setTimeout(updatePrice, 250);
        });
    });

    setTimeout(updatePrice, 300);
});
