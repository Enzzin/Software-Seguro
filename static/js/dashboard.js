/* global bootstrap, Chart, fetch, navigator */
document.addEventListener('DOMContentLoaded', () => {
  /* ------------------------------------------------------------------ */
  /* Referências aos elementos                                          */
  /* ------------------------------------------------------------------ */
  const newForm        = document.getElementById('newCampaignForm');
  const nameInput      = document.getElementById('campaignName');
  const descInput      = document.getElementById('campaignDescription');
  const targetInput    = document.getElementById('targetUrl');
  const emailsInput    = document.getElementById('targetEmails');

  const tblBody        = document.getElementById('campaignsTable');
  const cards          = {
    totalCampaigns : document.getElementById('totalCampaigns'),
    totalClicks    : document.getElementById('totalClicks'),
    uniqueVictims  : document.getElementById('uniqueVictims'),
    successRate    : document.getElementById('successRate'),
  };

  const linksModal     = new bootstrap.Modal('#linksModal');
  const linksDiv       = document.getElementById('generatedLinks');

  const campModal      = new bootstrap.Modal('#campaignModal');
  const campDetails    = document.getElementById('campaignDetails');

  let timelineChart;        // instancia Chart.js reutilizável
  let selectedCampaignId;   // usado no botão Export CSV dentro do modal

  /* ------------------------------------------------------------------ */
  /* Utilitário fetch + JSON com tratamento de erro                     */
  /* ------------------------------------------------------------------ */
  async function jsonFetch (url, options = {}) {
    const cfg = {
      headers : {'Content-Type': 'application/json', ...(options.headers || {})},
      ...options,
    };
    const res   = await fetch(url, cfg);
    const isJS  = res.headers.get('content-type')?.includes('application/json');
    const data  = isJS ? await res.json() : {};
    if (!res.ok) throw new Error(data.error || data.message || res.statusText);
    return data;
  }

  /* ------------------------------------------------------------------ */
  /* Cards + tabela (“Home” do dashboard)                               */
  /* ------------------------------------------------------------------ */
  async function refreshDashboard () {
    const d = await jsonFetch('/api/phish/stats');

    cards.totalCampaigns.textContent = d.total_campaigns;
    cards.totalClicks   .textContent = d.total_clicks;
    cards.uniqueVictims .textContent = d.unique_victims;
    cards.successRate   .textContent =
        d.total_clicks
          ? Math.round((d.unique_victims / d.total_clicks) * 100) + '%'
          : '0 %';

    renderCampaignTable(d.campaigns || []);
  }

  function renderCampaignTable (rows) {
    tblBody.innerHTML = '';

    if (!rows.length) {
      tblBody.innerHTML =
        '<tr><td colspan="4" class="text-center text-muted">Nenhuma campanha</td></tr>';
      return;
    }

    rows.forEach(row => {
      const tr = document.createElement('tr');
      tr.innerHTML = `
        <td>${row.name}</td>
        <td>${new Date(row.created_at).toLocaleDateString()}</td>
        <td>${row.clicks}</td>
        <td>
          <button class="btn btn-sm btn-outline-primary view"   data-id="${row.id}">
            <i class="fas fa-eye"></i>
          </button>
          <button class="btn btn-sm btn-outline-success export" data-id="${row.id}">
            <i class="fas fa-download"></i>
          </button>
        </td>`;
      tblBody.appendChild(tr);
    });
  }

  /* ------------------------------------------------------------------ */
  /* Criação de uma nova campanha                                       */
  /* ------------------------------------------------------------------ */
  async function handleNewCampaign (ev) {
    ev.preventDefault();

    const payload = {
      campaign_name : nameInput.value.trim() || undefined,
      description   : descInput.value.trim() || undefined,
      target_url    : targetInput.value.trim() || undefined,
      emails        : emailsInput.value                         // quebra linhas/esp.
                       .split(/\s+/)                            // espaço, \n ou \r\n
                       .filter(Boolean)
                       .slice(0, 100),                         // segurança: máx. 100
    };

    if (!payload.emails.length) {
      alert('Informe pelo menos um e-mail.');
      return;
    }

    try {
      const data = await jsonFetch('/api/phish/generate', {
        method : 'POST',
        body   : JSON.stringify(payload),
      });

      /* mostra links no modal --------------------------------------- */
      linksDiv.innerHTML = data.links.map(
        l => `<div class="small mb-1"><code>${l.email}</code> › 
                <a href="${l.link}" target="_blank">${l.link}</a></div>`
      ).join('');
      linksModal.show();

      /* limpa formulário, fecha o acordeão e atualiza cards ---------- */
      newForm.reset();
      document.getElementById('campaignForm').classList.remove('show');
      await refreshDashboard();
    } catch (err) {
      alert(err.message);
    }
  }

  /* Permite copiar todos os links exibidos no modal */
  window.copyAllLinks = function () {
    const txt = Array.from(linksDiv.querySelectorAll('a'))
                     .map(a => a.href).join('\n');
    navigator.clipboard.writeText(txt);
  };

  /* ------------------------------------------------------------------ */
  /* Detalhes da campanha (modal)                                       */
  /* ------------------------------------------------------------------ */
  async function showCampaign (id) {
    try {
      const d = await jsonFetch('/api/phish/stats?campaign_id=' + id);
      selectedCampaignId = id;       // usado pelo botão “Export CSV”

      /* resumo textual ---------------------------------------------- */
      campDetails.innerHTML = `
        <h5>${d.campaign.name}</h5>
        <p><strong>Total clicks:</strong> ${d.stats.total_clicks}</p>
        <p><strong>Unique users:</strong> ${d.stats.unique_users}</p>
        <hr class="my-3">
        <canvas id="clickChart" height="120"></canvas>`;

      /* timeline ----------------------------------------------------- */
      const ctx   = document.getElementById('clickChart').getContext('2d');
      if (timelineChart) timelineChart.destroy();
      timelineChart = new Chart(ctx, {
        type : 'line',
        data : {
          labels   : d.timeline.map(r => r.date),
          datasets : [{label: 'Clicks', data: d.timeline.map(r => r.clicks)}],
        },
        options : {responsive: true, tension: .3},
      });

      campModal.show();
    } catch (err) {
      alert(err.message);
    }
  }

  /* Export CSV ------------------------------------------------------- */
  window.exportCampaign = () => {
    if (selectedCampaignId) {
      window.location.href = '/api/phish/export/' + selectedCampaignId;
    }
  };

  /* ------------------------------------------------------------------ */
  /* Delegação de cliques na tabela (View / Export)                     */
  /* ------------------------------------------------------------------ */
  tblBody.addEventListener('click', ev => {
    const btn = ev.target.closest('button');
    if (!btn) return;
    const id = btn.dataset.id;
    if (btn.classList.contains('view'))   showCampaign(id);
    if (btn.classList.contains('export')) window.location.href = '/api/phish/export/' + id;
  });

  /* ------------------------------------------------------------------ */
  /* Inicialização                                                     */
  /* ------------------------------------------------------------------ */
  newForm?.addEventListener('submit', handleNewCampaign);
  refreshDashboard().catch(err => console.error(err));
});
