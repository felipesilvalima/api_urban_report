// Endereço base da API. Ajuste caso o backend não esteja em localhost:8000.
const API_BASE_URL = "http://localhost:8000";

// Endereço público do bucket MinIO usado para exibir as fotos das denúncias.
// Corresponde a MINIO_BUCKET no .env do backend (padrão de desenvolvimento: "reports").
const MINIO_PUBLIC_BASE_URL = "http://localhost:9000/reports";

const CATEGORY_LABELS = {
  BURACO_RUA: "Buraco na rua",
  LIXO: "Lixo acumulado",
  ILUMINACAO: "Iluminação pública",
  ESGOTO: "Esgoto a céu aberto",
  ENCHENTE: "Alagamento / enchente",
  ANIMAL: "Animal abandonado",
  ARVORE_CAIDA: "Árvore caída",
  SEMAFORO: "Semáforo com defeito",
};

const STATUS_LABELS = {
  PENDING: "Pendente",
  ANALYSING: "Em análise",
  RESOLVED: "Resolvida",
  REJECTED: "Rejeitada",
};

const STATUS_CLASSES = {
  PENDING: "status-pending",
  ANALYSING: "status-analysing",
  RESOLVED: "status-resolved",
  REJECTED: "status-rejected",
};

const TOKEN_KEY = "urban_report_access_token";
const REFRESH_KEY = "urban_report_refresh_token";
const EMAIL_KEY = "urban_report_user_email";

const Auth = {
  getToken: () => localStorage.getItem(TOKEN_KEY),
  getRefreshToken: () => localStorage.getItem(REFRESH_KEY),
  getEmail: () => localStorage.getItem(EMAIL_KEY),
  setSession: ({ access_token, refresh_token, email }) => {
    if (access_token) localStorage.setItem(TOKEN_KEY, access_token);
    if (refresh_token) localStorage.setItem(REFRESH_KEY, refresh_token);
    if (email) localStorage.setItem(EMAIL_KEY, email);
  },
  clear: () => {
    localStorage.removeItem(TOKEN_KEY);
    localStorage.removeItem(REFRESH_KEY);
    localStorage.removeItem(EMAIL_KEY);
  },
  isLoggedIn: () => Boolean(localStorage.getItem(TOKEN_KEY)),
};

// A API sempre serializa `return payload, codigo` como um array [payload, codigo]
// e devolve o status HTTP padrão (200). Essa função extrai o payload real.
function unwrap(body) {
  return Array.isArray(body) ? body[0] : body;
}

function extractErrorMessage(body, fallback) {
  if (!body) return fallback;
  if (typeof body.message === "string") return body.message; // DomainException
  if (typeof body.detail === "string") return body.detail; // HTTPException simples
  if (Array.isArray(body.detail)) {
    return body.detail.map((e) => e.msg || JSON.stringify(e)).join(" | ");
  }
  return fallback;
}

function redirectToLogin() {
  Auth.clear();
  window.location.href = "index.html";
}

async function tryRefreshToken() {
  const refreshToken = Auth.getRefreshToken();
  if (!refreshToken) return false;

  try {
    const response = await fetch(`${API_BASE_URL}/api/auth/refresh_token`, {
      method: "POST",
      headers: { Authorization: `Bearer ${refreshToken}` },
    });
    if (!response.ok) return false;
    const body = unwrap(await response.json());
    Auth.setSession({ access_token: body.access_token });
    return true;
  } catch {
    return false;
  }
}

/**
 * Wrapper de fetch autenticado. Em caso de 401, tenta renovar o token
 * uma vez via refresh_token antes de desistir e redirecionar ao login.
 */
async function apiFetch(path, options = {}, { retry = true } = {}) {
  const token = Auth.getToken();
  const headers = { ...(options.headers || {}) };
  if (token) headers.Authorization = `Bearer ${token}`;

  const response = await fetch(`${API_BASE_URL}${path}`, { ...options, headers });

  if (response.status === 401 && retry) {
    const refreshed = await tryRefreshToken();
    if (refreshed) {
      return apiFetch(path, options, { retry: false });
    }
    redirectToLogin();
    throw new Error("Sessão expirada. Faça login novamente.");
  }

  return response;
}

function requireAuth() {
  if (!Auth.isLoggedIn()) {
    redirectToLogin();
  }
}

function imageUrlFor(imagePath) {
  if (!imagePath) return "";
  return `${MINIO_PUBLIC_BASE_URL}/${imagePath}`;
}

function formatDateTime(isoString) {
  if (!isoString) return "-";
  const date = new Date(isoString);
  if (Number.isNaN(date.getTime())) return isoString;
  return date.toLocaleString("pt-BR");
}
