/* ================================================================
   CHATBOT WIDGET – Lógica
   ================================================================ */
(function () {
  "use strict";

  const API_URL = "http://localhost:8000/chat";

  // ── Crear el DOM del widget ──────────────────────────────────────
  function crearWidget() {
    // Botón flotante
    const btn = document.createElement("button");
    btn.id = "chatbot-toggle";
    btn.title = "Abrir chat";
    btn.innerHTML = "💬";

    // Panel
    const panel = document.createElement("div");
    panel.id = "chatbot-panel";
    panel.innerHTML = `
      <div id="chatbot-header">
        <h3>🤖 Asistente Aduanal</h3>
        <button id="chatbot-close" title="Cerrar">✕</button>
      </div>
      <div id="chatbot-messages">
        <div class="cb-welcome">
          ¡Hola! Soy tu asistente de comercio exterior. 🌎<br>
          Pregúntame sobre aranceles, regulaciones o trámites aduanales.
        </div>
      </div>
      <div id="chatbot-input-bar">
        <input
          type="text"
          id="chatbot-input"
          placeholder="Escribe tu pregunta…"
          autocomplete="off"
        />
        <button id="chatbot-send" title="Enviar">➤</button>
      </div>
    `;

    document.body.appendChild(panel);
    document.body.appendChild(btn);

    return { btn, panel };
  }

  // ── Elementos ────────────────────────────────────────────────────
  const { btn, panel } = crearWidget();
  const closeBtn   = document.getElementById("chatbot-close");
  const messagesEl = document.getElementById("chatbot-messages");
  const inputEl    = document.getElementById("chatbot-input");
  const sendBtn    = document.getElementById("chatbot-send");

  // ── Abrir / cerrar ──────────────────────────────────────────────
  function togglePanel() {
    const isOpen = panel.classList.toggle("open");
    btn.classList.toggle("active", isOpen);
    btn.innerHTML = isOpen ? "✕" : "💬";
    if (isOpen) inputEl.focus();
  }

  btn.addEventListener("click", togglePanel);
  closeBtn.addEventListener("click", togglePanel);

  // ── Helpers de mensajes ──────────────────────────────────────────
  function agregarMensaje(texto, tipo) {
    const div = document.createElement("div");
    div.classList.add("cb-msg", tipo);
    div.textContent = texto;
    messagesEl.appendChild(div);
    messagesEl.scrollTop = messagesEl.scrollHeight;
    return div;
  }

  function mostrarEscribiendo() {
    const div = document.createElement("div");
    div.classList.add("cb-typing");
    div.id = "cb-typing-indicator";
    div.innerHTML = "<span></span><span></span><span></span>";
    messagesEl.appendChild(div);
    messagesEl.scrollTop = messagesEl.scrollHeight;
  }

  function ocultarEscribiendo() {
    const el = document.getElementById("cb-typing-indicator");
    if (el) el.remove();
  }

  // ── Enviar mensaje ──────────────────────────────────────────────
  let enviando = false;

  async function enviar() {
    const texto = inputEl.value.trim();
    if (!texto || enviando) return;

    agregarMensaje(texto, "user");
    inputEl.value = "";
    enviando = true;
    sendBtn.disabled = true;

    mostrarEscribiendo();

    try {
      const res = await fetch(API_URL, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ mensaje: texto }),
      });

      ocultarEscribiendo();

      if (!res.ok) {
        const err = await res.json().catch(() => ({}));
        agregarMensaje(
          err.detail || "Error al conectar con el servidor.",
          "bot"
        );
        return;
      }

      const data = await res.json();
      agregarMensaje(data.respuesta, "bot");
    } catch {
      ocultarEscribiendo();
      agregarMensaje("No se pudo conectar con el servidor. ¿Está encendido?", "bot");
    } finally {
      enviando = false;
      sendBtn.disabled = false;
      inputEl.focus();
    }
  }

  sendBtn.addEventListener("click", enviar);
  inputEl.addEventListener("keydown", (e) => {
    if (e.key === "Enter") enviar();
  });
})();
