requireAuth();

const state = { page: 1, limit: 10, category: "", status: "" };

const userEmailEl = document.getElementById("user-email");
const filterCategory = document.getElementById("filter-category");
const filterStatus = document.getElementById("filter-status");
const filterLimit = document.getElementById("filter-limit");
const listStatusEl = document.getElementById("list-status");
const tbody = document.getElementById("complaints-tbody");
const pageIndicator = document.getElementById("page-indicator");
const prevBtn = document.getElementById("prev-page");
const nextBtn = document.getElementById("next-page");
const filtersSection = document.querySelector(".filters");
const tableSection = document.getElementById("table-section");
const paginationSection = document.querySelector(".pagination");

const overlay = document.getElementById("detail-overlay");
const detailBody = document.getElementById("detail-body");
const detailTitle = document.getElementById("detail-title");

userEmailEl.textContent = Auth.getEmail() || "";

function populateSelect(select, labels) {
  Object.entries(labels).forEach(([value, label]) => {
    const opt = document.createElement("option");
    opt.value = value;
    opt.textContent = label;
    select.appendChild(opt);
  });
}
populateSelect(filterCategory, CATEGORY_LABELS);
populateSelect(filterStatus, STATUS_LABELS);

function formatCpf(cpf) {
  if (!cpf || cpf.length !== 11) return cpf || "-";
  return cpf.replace(/(\d{3})(\d{3})(\d{3})(\d{2})/, "$1.$2.$3-$4");
}

function setAccessDenied(message) {
  filtersSection.classList.add("hidden");
  tableSection.classList.add("hidden");
  paginationSection.classList.add("hidden");
  listStatusEl.innerHTML = `<div class="result error">${message}</div>`;
}

function renderRows(complaints) {
  tbody.innerHTML = "";
  complaints.forEach((c) => {
    const tr = document.createElement("tr");
    tr.innerHTML = `
      <td>#${c.id}</td>
      <td>${CATEGORY_LABELS[c.category] || c.category}</td>
      <td><span class="status-badge ${STATUS_CLASSES[c.status] || ""}">${STATUS_LABELS[c.status] || c.status}</span></td>
      <td>${formatCpf(c.cpf)}</td>
      <td>${formatDateTime(c.created_at)}</td>
      <td><button class="btn-link" data-id="${c.id}">Ver detalhes</button></td>
    `;
    tbody.appendChild(tr);
  });
  tbody.querySelectorAll("button[data-id]").forEach((btn) => {
    btn.addEventListener("click", () => openDetail(btn.dataset.id));
  });
}

async function loadComplaints(targetPage = state.page) {
  const params = new URLSearchParams();
  if (state.category) params.set("category", state.category);
  if (state.status) params.set("status", state.status);
  params.set("page", String(targetPage));
  params.set("limit", String(state.limit));

  listStatusEl.textContent = "Carregando denúncias...";

  let response;
  try {
    response = await apiFetch(`/api/complaint/?${params.toString()}`);
  } catch (err) {
    listStatusEl.textContent = err.message;
    return;
  }

  const body = await response.json().catch(() => null);

  if (response.status === 403) {
    setAccessDenied(
      extractErrorMessage(
        body,
        "Acesso negado. Seu usuário não possui permissão de administrador para gerenciar denúncias."
      )
    );
    return;
  }

  if (response.status === 404) {
    if (targetPage > 1) {
      listStatusEl.textContent = "Não há mais denúncias nesta página.";
      return;
    }
    renderRows([]);
    listStatusEl.textContent = "Nenhuma denúncia encontrada com os filtros atuais.";
    state.page = 1;
    pageIndicator.textContent = `Página ${state.page}`;
    return;
  }

  if (!response.ok) {
    listStatusEl.textContent = extractErrorMessage(body, "Erro ao carregar denúncias.");
    return;
  }

  const complaints = unwrap(body);
  state.page = targetPage;
  renderRows(complaints);
  listStatusEl.textContent = `${complaints.length} denúncia(s) nesta página.`;
  pageIndicator.textContent = `Página ${state.page}`;
  prevBtn.disabled = state.page <= 1;
}

document.getElementById("apply-filters").addEventListener("click", () => {
  state.category = filterCategory.value;
  state.status = filterStatus.value;
  state.limit = Number(filterLimit.value);
  loadComplaints(1);
});

document.getElementById("clear-filters").addEventListener("click", () => {
  filterCategory.value = "";
  filterStatus.value = "";
  filterLimit.value = "10";
  state.category = "";
  state.status = "";
  state.limit = 10;
  loadComplaints(1);
});

prevBtn.addEventListener("click", () => {
  if (state.page > 1) loadComplaints(state.page - 1);
});
nextBtn.addEventListener("click", () => loadComplaints(state.page + 1));

document.getElementById("logout-btn").addEventListener("click", () => {
  Auth.clear();
  window.location.href = "index.html";
});

document.getElementById("refresh-btn").addEventListener("click", () => {
  loadComplaints(state.page);
});

// ---------- Painel de detalhes ----------

function actionsFor(status) {
  switch (status) {
    case "PENDING":
      return [
        { label: "Iniciar análise", next: "ANALYSING", cls: "btn-primary" },
        { label: "Rejeitar", next: "REJECTED", cls: "btn-danger" },
      ];
    case "ANALYSING":
      return [
        { label: "Marcar como resolvida", next: "RESOLVED", cls: "btn-success" },
        { label: "Rejeitar", next: "REJECTED", cls: "btn-danger" },
      ];
    default:
      return [];
  }
}

function renderDetail(complaint) {
  detailTitle.textContent = `Denúncia #${complaint.id}`;
  const googleMapsLink = `https://www.google.com/maps/search/?api=1&query=${complaint.latitude},${complaint.longitude}`;
  const actions = actionsFor(complaint.status);

  detailBody.innerHTML = `
    <img class="detail-image" src="${imageUrlFor(complaint.image_url)}" alt="Foto da denúncia" onerror="this.classList.add('broken')" />

    <div class="detail-grid">
      <div><span class="detail-label">Status</span><span class="status-badge ${STATUS_CLASSES[complaint.status] || ""}">${STATUS_LABELS[complaint.status] || complaint.status}</span></div>
      <div><span class="detail-label">Categoria</span>${CATEGORY_LABELS[complaint.category] || complaint.category}</div>
      <div><span class="detail-label">CPF</span>${formatCpf(complaint.cpf)}</div>
      <div><span class="detail-label">Criada em</span>${formatDateTime(complaint.created_at)}</div>
      <div><span class="detail-label">Atualizada em</span>${formatDateTime(complaint.updated_at)}</div>
      <div><span class="detail-label">Localização</span><a href="${googleMapsLink}" target="_blank" rel="noopener">Ver no Google Maps ↗</a></div>
    </div>

    <div class="detail-description">
      <span class="detail-label">Descrição</span>
      <p>${complaint.description ? complaint.description : "<em>Sem descrição.</em>"}</p>
    </div>

    <div id="detail-action-msg"></div>

    <div class="detail-actions">
      ${actions
        .map((a) => `<button class="${a.cls}" data-next="${a.next}">${a.label}</button>`)
        .join("") || '<p class="hint">Esta denúncia está em um estado final e não pode ser alterada.</p>'}
    </div>
  `;

  detailBody.querySelectorAll("button[data-next]").forEach((btn) => {
    btn.addEventListener("click", () => changeStatus(complaint.id, btn.dataset.next));
  });
}

async function openDetail(id) {
  detailTitle.textContent = `Denúncia #${id}`;
  detailBody.innerHTML = "<p>Carregando...</p>";
  overlay.classList.remove("hidden");

  let response;
  try {
    response = await apiFetch(`/api/complaint/${id}`);
  } catch (err) {
    detailBody.innerHTML = `<p class="error-text">${err.message}</p>`;
    return;
  }

  const body = await response.json().catch(() => null);

  if (!response.ok) {
    detailBody.innerHTML = `<p class="error-text">${extractErrorMessage(body, "Erro ao carregar detalhes da denúncia.")}</p>`;
    return;
  }

  renderDetail(unwrap(body));
}

async function changeStatus(id, next) {
  const msgEl = document.getElementById("detail-action-msg");
  msgEl.textContent = "Atualizando status...";

  const response = await apiFetch(`/api/complaint/${id}/status`, {
    method: "PATCH",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ status: next }),
  });

  const body = await response.json().catch(() => null);

  if (!response.ok) {
    msgEl.innerHTML = `<div class="result error">${extractErrorMessage(body, "Não foi possível alterar o status.")}</div>`;
    return;
  }

  await openDetail(id);
  await loadComplaints(state.page);
}

function closeDetail() {
  overlay.classList.add("hidden");
}
document.getElementById("close-detail").addEventListener("click", closeDetail);
overlay.addEventListener("click", (e) => {
  if (e.target === overlay) closeDetail();
});

loadComplaints(1);
