// Se já houver uma sessão salva, pula direto para o dashboard.
if (Auth.isLoggedIn()) {
  window.location.href = "dashboard.html";
}

const form = document.getElementById("login-form");
const emailInput = document.getElementById("email");
const passwordInput = document.getElementById("password");
const submitBtn = document.getElementById("submit-btn");
const submitLabel = document.getElementById("submit-label");
const submitSpinner = document.getElementById("submit-spinner");
const resultBox = document.getElementById("result");

function setLoading(isLoading) {
  submitBtn.disabled = isLoading;
  submitLabel.textContent = isLoading ? "Entrando..." : "Entrar";
  submitSpinner.classList.toggle("hidden", !isLoading);
}

function showError(message) {
  resultBox.textContent = message;
  resultBox.classList.remove("hidden");
}

form.addEventListener("submit", async (event) => {
  event.preventDefault();
  resultBox.classList.add("hidden");
  setLoading(true);

  try {
    const response = await fetch(`${API_BASE_URL}/api/auth/login`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({
        email: emailInput.value.trim(),
        password: passwordInput.value,
      }),
    });

    const body = await response.json().catch(() => null);

    if (!response.ok) {
      throw new Error(extractErrorMessage(body, "Não foi possível entrar."));
    }

    const { access_token, refresh_token } = unwrap(body);
    Auth.setSession({ access_token, refresh_token, email: emailInput.value.trim() });
    window.location.href = "dashboard.html";
  } catch (err) {
    showError(err.message);
  } finally {
    setLoading(false);
  }
});
