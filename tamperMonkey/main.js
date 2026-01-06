// ==UserScript==
// @name         JKLM Bot - Python Connector
// @namespace    http://tampermonkey.net/
// @version      2.0
// @description  Conecta JKLM.fun con un servidor Python local para automatizar el juego.
// @author       Alpaca
// @match        https://jklm.fun/*
// @match        https://*.jklm.fun/*
// @grant        none
// @run-at       document-start
// ==/UserScript==

(function () {
  "use strict";

  // Ejecutar únicamente en el iframe del juego
  if (window.self === window.top) return;

  // ========================================
  // SISTEMA DE LOGGING
  // ========================================
  const Logger = {
    prefix: "[JKLM Bot]",
    styles: {
      info: "color: #00bfff; font-weight: bold;",
      success: "color: #00ff00; font-weight: bold;",
      error:
        "color: #ff0000; font-weight: bold; background: #220000; padding: 2px;",
      game: "color: #ffa500; font-weight: bold;",
      python: "color: #ffff00; font-weight: bold;",
    },
    log: function (msg, type = "info") {
      console.log(
        `%c${this.prefix} ${msg}`,
        this.styles[type] || this.styles.info
      );
    },
    error: function (msg, err) {
      console.error(
        `%c${this.prefix} [ERROR] ${msg}`,
        this.styles.error,
        err || ""
      );
    },
  };

  Logger.log("Iniciando...", "info");

  // ========================================
  // CONFIGURACIÓN Y ESTADO GLOBAL
  // ========================================
  let gameSocket = null;
  let pythonSocket = null;
  let lastSetupData = null;
  const PYTHON_URL = "ws://localhost:8765";

  // ========================================
  // GESTIÓN DE CONEXIÓN CON SERVIDOR PYTHON
  // ========================================
  function connectToPython() {
    pythonSocket = new WebSocket(PYTHON_URL);

    pythonSocket.onopen = () => {
      Logger.log("Conectado al servidor Python", "success");
      notificarEstado("Python: Conectado");

      sendFullConfig();

      if (lastSetupData) {
        Logger.log("Reenviando configuración inicial a Python", "info");
        pythonSocket.send(
          JSON.stringify({
            event: "setup",
            data: lastSetupData,
          })
        );
      }
    };

    pythonSocket.onmessage = (event) => {
      const mensaje = JSON.parse(event.data);
      procesarOrdenPython(mensaje);
    };

    pythonSocket.onclose = () => {
      Logger.log("Desconectado de Python. Reintentando en 3s...", "error");
      notificarEstado("Python: Desconectado");
      setTimeout(connectToPython, 3000);
    };

    pythonSocket.onerror = (err) => {
      Logger.error("Error en conexión Python", err);
      pythonSocket.close();
    };
  }

  // ========================================
  // PROCESAMIENTO DE ÓRDENES DESDE PYTHON
  // ========================================
  function procesarOrdenPython(orden) {
    if (!gameSocket) {
      Logger.error("Orden recibida pero no hay GameSocket disponible.");
      return;
    }

    if (orden.action === "escribir_palabra") {
      const palabra = orden.word;
      Logger.log(`Enviando palabra: "${palabra}"`, "python");
      gameSocket.emit("setWord", palabra, true);
    }

    if (orden.action === "teclear_texto") {
      const texto = orden.text;
      gameSocket.emit("setWord", texto, false);
    }

    if (orden.action === "unirse_juego") {
      Logger.log("Uniéndose a la partida", "python");
      gameSocket.emit("joinRound");
    }
  }

  // ========================================
  // INTERCEPTACIÓN DE SOCKET.IO DEL JUEGO
  // ========================================
  let originalIo = window.io;

  Object.defineProperty(window, "io", {
    get: function () {
      return originalIo;
    },
    set: function (newValue) {
      originalIo = function (...args) {
        Logger.log("Socket del juego detectado", "game");
        const socket = newValue(...args);

        gameSocket = socket;
        setupGameSocketListeners(socket);

        return socket;
      };
      Object.assign(originalIo, newValue);
    },
    configurable: true,
  });

  function setupGameSocketListeners(socket) {
    const onevent = socket.onevent;
    socket.onevent = function (packet) {
      const args = packet.data || [];
      const eventName = args[0];
      const eventData = args[1];

      if (pythonSocket && pythonSocket.readyState === WebSocket.OPEN) {
        const eventosInteresantes = [
          "setup",
          "nextTurn",
          "correctWord",
          "failWord",
          "setMilestone",
          "setPlayerWord",
          "livesLost",
          "bonusAlphabetCompleted",
          "setRules",
          "addPlayer",
          "removePlayer",
        ];

        if (eventosInteresantes.includes(eventName)) {
          let payload = eventData;
          if (args.length > 2) {
            payload = args.slice(1);
          }

          if (eventName === "setup") {
            lastSetupData = payload;
            Logger.log("⭐ SETUP CAPTURADO - Enviando a Python", "success");
          }

          pythonSocket.send(
            JSON.stringify({
              event: eventName,
              data: payload,
            })
          );
        }
      } else {
        // Python no está conectado, pero si es setup, cachearlo de todos modos
        if (eventName === "setup") {
          lastSetupData = eventData;
          Logger.log("⚠️ SETUP capturado pero Python no conectado (cacheado)", "info");
        }
      }

      if (onevent) onevent.call(this, packet);
    };

    Logger.log("Listeners configurados correctamente", "success");
    notificarEstado("GameSocket: Capturado");
  }

  // ========================================
  // INTERFAZ DE USUARIO
  // ========================================
  let uiContainer = null;
  let statusLabel = null;
  let isExpanded = false;

  function createUI() {
    if (document.getElementById("bot-ui-container")) return;

    // Contenedor Principal
    uiContainer = document.createElement("div");
    uiContainer.id = "bot-ui-container";
    uiContainer.style = `
            position: fixed; top: 10px; right: 10px; z-index: 99999;
            font-family: 'Consolas', monospace; font-size: 12px;
            background: rgba(20, 20, 20, 0.95); color: #00ff00;
            border: 1px solid #00ff00; border-radius: 8px;
            box-shadow: 0 0 10px rgba(0, 255, 0, 0.2);
            transition: all 0.3s ease; overflow: hidden;
            width: 200px;
        `;

    const header = document.createElement("div");
    header.style = `
            padding: 8px 12px; cursor: pointer; user-select: none;
            display: flex; justify-content: space-between; align-items: center;
            background: rgba(0, 50, 0, 0.5); border-bottom: 1px solid #004400;
        `;

    statusLabel = document.createElement("span");
    statusLabel.innerText = "Desconectado";

    const toggleIcon = document.createElement("span");
    toggleIcon.innerText = "▼";
    toggleIcon.style.fontSize = "10px";

    header.appendChild(statusLabel);
    header.appendChild(toggleIcon);
    header.onclick = toggleUI;
    uiContainer.appendChild(header);

    const body = document.createElement("div");
    body.id = "bot-ui-body";
    body.style = `padding: 10px; display: none; flex-direction: column; gap: 8px;`;

    body.appendChild(createCheckbox("active", "Activar Bot", true));
    body.appendChild(createCheckbox("autojoin", "Autounirse a Ronda", false));
    body.appendChild(createCheckbox("suicide", "Suicide (Perder Vida)", false));

    body.appendChild(document.createElement("hr")).style =
      "border: 0; border-top: 1px solid #333; margin: 5px 0; width: 100%;";

    const strategyLabel = document.createElement("div");
    strategyLabel.innerText = "Estrategias:";
    strategyLabel.style = "color: #aaa; margin-bottom: 4px; font-weight: bold;";
    body.appendChild(strategyLabel);

    body.appendChild(
      createCheckbox("strategy_longest", "Maximizar Longitud", false)
    );
    body.appendChild(
      createCheckbox("strategy_alphabet", "Maximizar Alfabeto", false)
    );
    body.appendChild(
      createCheckbox("strategy_shortest", "Modo Pánico (Cortas)", false)
    );

    // Separador
    body.appendChild(document.createElement("hr")).style =
      "border: 0; border-top: 1px solid #333; margin: 5px 0; width: 100%;";

    // Opciones de Tiempos (Delays)
    const timeLabel = document.createElement("div");
    timeLabel.innerText = "Tiempos (segundos):";
    timeLabel.style = "color: #aaa; margin-bottom: 4px; font-weight: bold;";
    body.appendChild(timeLabel);

    body.appendChild(
      createNumberInput("minTypingDelay", "Min Typing Delay", 0.05)
    );
    body.appendChild(
      createNumberInput("maxTypingDelay", "Max Typing Delay", 0.15)
    );
    body.appendChild(
      createNumberInput("startDelayMin", "Start Delay Min", 0.5)
    );
    body.appendChild(
      createNumberInput("startDelayMax", "Start Delay Max", 1.5)
    );

    // Separador
    body.appendChild(document.createElement("hr")).style =
      "border: 0; border-top: 1px solid #333; margin: 5px 0; width: 100%;";

    // Input de Texto Manual (Frase Extra)
    const manualInputWrapper = document.createElement("div");
    manualInputWrapper.style =
      "display: flex; flex-direction: column; gap: 2px; margin-bottom: 5px;";

    const manualLabel = document.createElement("label");
    manualLabel.innerText = "Enviar Frase (Enter):";
    manualLabel.style = "color: #ccc; font-size: 11px;";

    const manualInput = document.createElement("input");
    manualInput.type = "text";
    manualInput.id = "bot-manual-input";
    manualInput.placeholder = "Escribe y pulsa Enter...";
    manualInput.style =
      "background: #222; color: #fff; border: 1px solid #004400; padding: 4px; border-radius: 4px; width: 100%; box-sizing: border-box; font-size: 11px;";

    let focusInterval = null;

    manualInput.onfocus = () => {
      focusInterval = setInterval(() => {
        if (document.activeElement !== manualInput) {
          manualInput.focus();
        }
      }, 100);

      manualInput.style.borderColor = "#00ff00";
    };

    manualInput.onblur = () => {
      if (focusInterval) {
        clearInterval(focusInterval);
        focusInterval = null;
      }
      manualInput.style.borderColor = "#004400";
    };

    manualInput.onkeydown = (e) => {
      if (e.key === "Enter") {
        sendCustomMessage(manualInput.value);
        manualInput.value = "";

        // Quitar foco y detener interval
        if (focusInterval) {
          clearInterval(focusInterval);
          focusInterval = null;
        }

        // Feedback visual
        setTimeout(() => (manualInput.style.borderColor = "#004400"), 200);
      }

      if (e.key === "Escape") {
        // Cancelar: limpiar y salir
        manualInput.blur();
      }
    };

    manualInputWrapper.appendChild(manualLabel);
    manualInputWrapper.appendChild(manualInput);
    body.appendChild(manualInputWrapper);

    uiContainer.appendChild(body);
    document.body.appendChild(uiContainer);
  }

  function createCheckbox(id, labelText, checked) {
    const wrapper = document.createElement("div");
    wrapper.style = "display: flex; align-items: center; gap: 8px;";

    const input = document.createElement("input");
    input.type = "checkbox";
    input.id = "bot-cfg-" + id;
    input.checked = checked;
    input.style = "cursor: pointer;";
    input.onchange = (e) => sendConfigUpdate(id, e.target.checked);

    const label = document.createElement("label");
    label.htmlFor = "bot-cfg-" + id;
    label.innerText = labelText;
    label.style = "cursor: pointer; color: white;";

    wrapper.appendChild(input);
    wrapper.appendChild(label);
    return wrapper;
  }

  function createNumberInput(id, labelText, defaultValue) {
    const wrapper = document.createElement("div");
    wrapper.style =
      "display: flex; flex-direction: column; gap: 2px; margin-bottom: 5px;";

    const label = document.createElement("label");
    label.htmlFor = "bot-cfg-" + id;
    label.innerText = labelText;
    label.style = "color: #ccc; font-size: 11px;";

    const input = document.createElement("input");
    input.type = "number";
    input.id = "bot-cfg-" + id;
    input.value = defaultValue;
    input.step = "0.01";
    input.style =
      "background: #222; color: #0f0; border: 1px solid #004400; padding: 2px 4px; border-radius: 4px; width: 100%; box-sizing: border-box;";
    input.onchange = (e) => sendConfigUpdate(id, parseFloat(e.target.value));

    wrapper.appendChild(label);
    wrapper.appendChild(input);
    return wrapper;
  }

  function toggleUI() {
    const body = document.getElementById("bot-ui-body");
    isExpanded = !isExpanded;
    body.style.display = isExpanded ? "flex" : "none";
    uiContainer.querySelector("span:last-child").innerText = isExpanded
      ? "▲"
      : "▼";
  }

  function updateStatus(text, color) {
    if (!statusLabel) createUI();
    statusLabel.innerText = text;
    statusLabel.style.color = color || "#00ff00";
    uiContainer.style.borderColor = color || "#00ff00";
  }

  // ========================================
  // SINCRONIZACIÓN DE CONFIGURACIÓN
  // ========================================
  function sendFullConfig() {
    if (!pythonSocket || pythonSocket.readyState !== WebSocket.OPEN) return;

    const config = {};

    [
      "active",
      "autojoin",
      "suicide",
      "strategy_longest",
      "strategy_alphabet",
      "strategy_shortest",
    ].forEach((id) => {
      const el = document.getElementById("bot-cfg-" + id);
      if (el) config[id] = el.checked;
    });

    [
      "minTypingDelay",
      "maxTypingDelay",
      "startDelayMin",
      "startDelayMax",
    ].forEach((id) => {
      const el = document.getElementById("bot-cfg-" + id);
      if (el) config[id] = parseFloat(el.value);
    });

    pythonSocket.send(
      JSON.stringify({
        event: "configUpdate",
        data: config,
      })
    );
    Logger.log("Configuración sincronizada con Python", "info");
  }

  function sendConfigUpdate(key, value) {
    if (pythonSocket && pythonSocket.readyState === WebSocket.OPEN) {
      pythonSocket.send(
        JSON.stringify({
          event: "configUpdate",
          data: { [key]: value },
        })
      );
      Logger.log(`Configuración actualizada: ${key}=${value}`, "info");
    }
  }

  function sendCustomMessage(text) {
    if (
      pythonSocket &&
      pythonSocket.readyState === WebSocket.OPEN &&
      text.trim().length > 0
    ) {
      pythonSocket.send(
        JSON.stringify({
          event: "customMessage",
          data: text,
        })
      );
      Logger.log(`Mensaje personalizado enviado: "${text}"`, "info");
    }
  }

  function notificarEstado(texto) {
    let color = "#00ff00";
    if (texto.includes("Desconectado")) color = "#ff0000";
    if (texto.includes("Capturado")) color = "#00bfff";

    updateStatus(texto.split(":")[0], color);
  }

  // ========================================
  // INICIALIZACIÓN
  // ========================================
  const checkBody = setInterval(() => {
    if (document.body) {
      clearInterval(checkBody);
      createUI();
    }
  }, 500);

  connectToPython();
})();
