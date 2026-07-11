// API_BASE_URL e MAX_COMPLAINTS_PER_CPF vêm de config.js

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
    // Erros de validação do Pydantic
    return body.detail
      .map((e) => e.msg || JSON.stringify(e))
      .join(" | ");
  }
  return fallback;
}

const form = document.getElementById("complaint-form");
const categorySelect = document.getElementById("category");
const cpfInput = document.getElementById("cpf");
const cepInput = document.getElementById("cep");
const descriptionInput = document.getElementById("description");
const descCount = document.getElementById("desc-count");
const imageInput = document.getElementById("image");
const imagePreview = document.getElementById("image-preview");
const submitBtn = document.getElementById("submit-btn");
const submitLabel = document.getElementById("submit-label");
const submitSpinner = document.getElementById("submit-spinner");
const resultBox = document.getElementById("result");

function populateCategories() {
  Object.entries(CATEGORY_LABELS).forEach(([value, label]) => {
    const opt = document.createElement("option");
    opt.value = value;
    opt.textContent = label;
    categorySelect.appendChild(opt);
  });
}
populateCategories();

function onlyDigits(value) {
  return value.replace(/\D/g, "");
}

document.getElementById("cpf-hint").textContent =
  `Cada CPF pode registrar até ${MAX_COMPLAINTS_PER_CPF} denúncias por dia.`;

cpfInput.addEventListener("input", () => {
  const digits = onlyDigits(cpfInput.value).slice(0, 11);
  let formatted = digits;
  if (digits.length > 9) {
    formatted = digits.replace(/(\d{3})(\d{3})(\d{3})(\d{1,2})/, "$1.$2.$3-$4");
  } else if (digits.length > 6) {
    formatted = digits.replace(/(\d{3})(\d{3})(\d{1,3})/, "$1.$2.$3");
  } else if (digits.length > 3) {
    formatted = digits.replace(/(\d{3})(\d{1,3})/, "$1.$2");
  }
  cpfInput.value = formatted;
});

cepInput.addEventListener("input", () => {
  const digits = onlyDigits(cepInput.value).slice(0, 8);
  cepInput.value = digits.length > 5 ? digits.replace(/(\d{5})(\d{1,3})/, "$1-$2") : digits;
});

descriptionInput.addEventListener("input", () => {
  descCount.textContent = String(descriptionInput.value.length);
});

imageInput.addEventListener("change", () => {
  const file = imageInput.files[0];
  if (!file) {
    imagePreview.classList.add("hidden");
    imagePreview.src = "";
    return;
  }
  imagePreview.src = URL.createObjectURL(file);
  imagePreview.classList.remove("hidden");
});

function clearErrors() {
  document.querySelectorAll(".error").forEach((el) => (el.textContent = ""));
}

function setFieldError(field, message) {
  const el = document.querySelector(`[data-error-for="${field}"]`);
  if (el) el.textContent = message;
}

function showResult(type, title, message) {
  resultBox.className = `result ${type}`;
  resultBox.innerHTML = `<strong>${title}</strong>${message}`;
  resultBox.classList.remove("hidden");
  resultBox.scrollIntoView({ behavior: "smooth", block: "nearest" });
}

function setLoading(isLoading) {
  submitBtn.disabled = isLoading;
  submitLabel.textContent = isLoading ? "Enviando..." : "Enviar denúncia";
  submitSpinner.classList.toggle("hidden", !isLoading);
}

function validateForm() {
  clearErrors();
  let valid = true;

  const cpfDigits = onlyDigits(cpfInput.value);
  if (cpfDigits.length !== 11) {
    setFieldError("cpf", "Informe um CPF válido com 11 dígitos.");
    valid = false;
  }

  const cepDigits = onlyDigits(cepInput.value);
  if (cepDigits.length !== 8) {
    setFieldError("cep", "Informe um CEP válido com 8 dígitos.");
    valid = false;
  }

  if (!categorySelect.value) {
    setFieldError("category", "Selecione uma categoria.");
    valid = false;
  }

  if (descriptionInput.value.length > 200) {
    setFieldError("description", "Descrição deve ter no máximo 200 caracteres.");
    valid = false;
  }

  if (!imageInput.files[0]) {
    setFieldError("image", "Selecione uma foto do problema.");
    valid = false;
  }

  return valid;
}

async function uploadImage(file) {
  const formData = new FormData();
  formData.append("file", file);

  const response = await fetch(`${API_BASE_URL}/api/minio/upload/image`, {
    method: "POST",
    body: formData,
  });

  const body = await response.json().catch(() => null);

  if (!response.ok) {
    throw new Error(extractErrorMessage(body, "Não foi possível enviar a imagem."));
  }

  return unwrap(body).object_name;
}

async function createComplaint(payload) {
  const response = await fetch(`${API_BASE_URL}/api/complaint/`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(payload),
  });

  const body = await response.json().catch(() => null);

  if (!response.ok) {
    throw new Error(extractErrorMessage(body, "Não foi possível registrar a denúncia."));
  }

  return unwrap(body);
}

form.addEventListener("submit", async (event) => {
  event.preventDefault();
  resultBox.classList.add("hidden");

  if (!validateForm()) return;

  setLoading(true);

  try {
    const imagePath = await uploadImage(imageInput.files[0]);

    const complaint = await createComplaint({
      cpf: onlyDigits(cpfInput.value),
      cep: onlyDigits(cepInput.value),
      category: categorySelect.value,
      image_path: imagePath,
      description: descriptionInput.value || "",
    });

    showResult(
      "success",
      "Denúncia registrada com sucesso!",
      `Protocolo #${complaint.id} — status atual: <strong>${complaint.status}</strong>. Guarde esse número para acompanhamento.`
    );
    form.reset();
    descCount.textContent = "0";
    imagePreview.classList.add("hidden");
    imagePreview.src = "";
  } catch (err) {
    showResult("error", "Não foi possível enviar sua denúncia", err.message);
  } finally {
    setLoading(false);
  }
});
