class ShAIApp {
  constructor() {
    this.isRecording = false;
    this.recognition = null;
    this.currentHistoryId = null;
    this.initializeElements();
    this.initializeEventListeners();
    this.initializeSpeechRecognition();
    this.loadHistory();
  }

  initializeElements() {
    // Input elements
    this.userInput = document.getElementById("user-input");
    this.generateBtn = document.getElementById("generate-btn");
    this.voiceBtn = document.getElementById("voice-btn");
    this.stopVoiceBtn = document.getElementById("stop-voice-btn");

    // Status elements
    this.voiceControls = document.getElementById("voice-controls");
    this.voiceIcon = document.getElementById("voice-icon");
    this.voiceStatusText = document.getElementById("voice-status-text");
    this.loading = document.getElementById("loading");
    this.results = document.getElementById("results");
    this.pickupLinesList = document.getElementById("pickup-lines-list");
    this.errorMessage = document.getElementById("error-message");

    // History elements
    this.historyList = document.getElementById("history-list");
    this.noHistory = document.getElementById("no-history");
    this.clearHistoryBtn = document.getElementById("clear-history-btn");
  }

  initializeEventListeners() {
    // Generate button
    this.generateBtn.addEventListener("click", () => {
      this.generatePickupLines();
    });

    // Voice button
    this.voiceBtn.addEventListener("click", () => {
      this.toggleVoiceRecording();
    });

    // Stop voice button
    this.stopVoiceBtn.addEventListener("click", () => {
      this.stopVoiceRecording();
    });

    // Clear history button
    this.clearHistoryBtn.addEventListener("click", () => {
      this.clearHistory();
    });

    // Enter key in textarea
    this.userInput.addEventListener("keydown", (e) => {
      if (e.key === "Enter" && !e.shiftKey) {
        e.preventDefault();
        this.generatePickupLines();
      }
    });

    // Auto-resize textarea
    this.userInput.addEventListener("input", () => {
      this.autoResizeTextarea();
    });
  }

  initializeSpeechRecognition() {
    if ("webkitSpeechRecognition" in window || "SpeechRecognition" in window) {
      const SpeechRecognition =
        window.SpeechRecognition || window.webkitSpeechRecognition;
      this.recognition = new SpeechRecognition();

      // Improved settings for better dictation
      this.recognition.continuous = true;
      this.recognition.interimResults = true;
      this.recognition.lang = "en-US";
      this.recognition.maxAlternatives = 3;

      this.recognition.onstart = () => {
        this.isRecording = true;
        this.updateVoiceUI();
      };

      this.recognition.onresult = (event) => {
        let finalTranscript = "";
        let interimTranscript = "";

        for (let i = event.resultIndex; i < event.results.length; i++) {
          const transcript = event.results[i][0].transcript;
          if (event.results[i].isFinal) {
            finalTranscript += transcript;
          } else {
            interimTranscript += transcript;
          }
        }

        // Update the input with final transcript
        if (finalTranscript) {
          this.userInput.value += finalTranscript;
          this.autoResizeTextarea();
        }

        // Show interim results
        if (interimTranscript) {
          this.voiceStatusText.textContent = `Listening: "${interimTranscript}"`;
        } else {
          this.voiceStatusText.textContent = "Listening for your voice...";
        }
      };

      this.recognition.onend = () => {
        this.isRecording = false;
        this.updateVoiceUI();
        if (this.userInput.value.trim()) {
          this.voiceStatusText.textContent = "Voice input completed!";
        } else {
          this.voiceStatusText.textContent = "No speech detected. Try again.";
        }
      };

      this.recognition.onerror = (event) => {
        console.error("Speech recognition error:", event.error);
        this.isRecording = false;
        this.updateVoiceUI();

        let errorMsg = "Voice recognition error occurred.";
        switch (event.error) {
          case "network":
            errorMsg = "Network error. Check your internet connection.";
            break;
          case "not-allowed":
            errorMsg =
              "Microphone access denied. Please allow microphone access.";
            break;
          case "no-speech":
            errorMsg =
              "No speech detected. Try speaking louder or closer to the microphone.";
            break;
          case "audio-capture":
            errorMsg =
              "Microphone not found. Please check your audio settings.";
            break;
          default:
            errorMsg = `Voice recognition error: ${event.error}`;
        }
        this.voiceStatusText.textContent = errorMsg;
        this.showError(errorMsg);
      };
    } else {
      this.voiceBtn.disabled = true;
      this.voiceBtn.innerHTML =
        '<i class="fas fa-microphone-slash"></i> Voice Not Supported';
    }
  }

  toggleVoiceRecording() {
    if (!this.recognition) {
      this.showError("Speech recognition is not supported in this browser.");
      return;
    }

    if (this.isRecording) {
      this.stopVoiceRecording();
    } else {
      this.startVoiceRecording();
    }
  }

  startVoiceRecording() {
    try {
      this.voiceControls.classList.remove("hidden");
      this.recognition.start();
      this.voiceStatusText.textContent = "Starting voice recognition...";
    } catch (error) {
      console.error("Failed to start voice recognition:", error);
      this.showError("Failed to start voice recognition. Please try again.");
    }
  }

  stopVoiceRecording() {
    if (this.recognition && this.isRecording) {
      this.recognition.stop();
    }
  }

  updateVoiceUI() {
    if (this.isRecording) {
      this.voiceBtn.innerHTML =
        '<i class="fas fa-microphone animate-pulse"></i> Listening...';
      this.voiceBtn.disabled = true;
      this.stopVoiceBtn.classList.remove("hidden");
      this.voiceIcon.className = "fas fa-microphone animate-pulse-slow";
    } else {
      this.voiceBtn.innerHTML = '<i class="fas fa-microphone"></i> Use Voice';
      this.voiceBtn.disabled = false;
      this.stopVoiceBtn.classList.add("hidden");
      this.voiceIcon.className = "fas fa-microphone";
    }
  }

  autoResizeTextarea() {
    this.userInput.style.height = "auto";
    this.userInput.style.height =
      Math.max(120, this.userInput.scrollHeight) + "px";
  }

  async generatePickupLines() {
    const input = this.userInput.value.trim();

    if (!input) {
      this.showError("Please enter some text or use voice input first!");
      this.userInput.focus();
      return;
    }

    try {
      this.setLoadingState(true);
      this.hideError();

      const response = await fetch("/generate", {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify({ input: input }),
      });

      if (!response.ok) {
        throw new Error(`HTTP ${response.status}: ${response.statusText}`);
      }

      const data = await response.json();

      if (!data.success) {
        throw new Error(data.error || "Failed to generate pickup lines");
      }

      this.displayResults(data);
      this.loadHistory(); // Refresh history after generating
    } catch (error) {
      console.error("Error generating pickup lines:", error);
      this.showError(`Failed to generate pickup lines: ${error.message}`);
    } finally {
      this.setLoadingState(false);
    }
  }

  displayResults(data) {
    // Clear previous results
    this.pickupLinesList.innerHTML = "";

    // Create pickup line elements
    data.pickup_lines.forEach((line, index) => {
      const listItem = this.createPickupLineElement(line, index);
      this.pickupLinesList.appendChild(listItem);
    });

    // Show results section with animation
    this.results.classList.remove("hidden");
    this.results.scrollIntoView({ behavior: "smooth", block: "start" });
  }

  createPickupLineElement(line, index) {
    const listItem = document.createElement("li");
    listItem.className =
      "group pickup-line rounded-lg border border-slate-700 dark:border-slate-700 light:border-slate-300 bg-slate-800/30 dark:bg-slate-800/30 light:bg-white/30 hover:bg-slate-700/30 dark:hover:bg-slate-700/30 light:hover:bg-white/50 transition-all duration-200 cursor-pointer hover:border-purple-500/50 overflow-hidden";
    listItem.style.animationDelay = `${index * 0.1}s`;

    listItem.innerHTML = `
            <div class="pickup-line-content">
                <div class="w-full">
                    <div class="text-slate-100 dark:text-slate-100 light:text-slate-900 mb-3 leading-relaxed text-lg">${this.escapeHtml(line)}</div>
                    <div class="flex gap-2 opacity-0 group-hover:opacity-100 transition-opacity">
                        <button class="inline-flex items-center justify-center rounded-md text-xs font-medium ring-offset-background transition-colors focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-ring focus-visible:ring-offset-2 disabled:pointer-events-none disabled:opacity-50 hover:bg-slate-600 dark:hover:bg-slate-600 light:hover:bg-slate-200 hover:text-slate-100 dark:hover:text-slate-100 light:hover:text-slate-900 h-7 px-2 gap-1 copy-btn" data-text="${this.escapeHtml(line)}">
                            <i class="fas fa-copy text-xs"></i> Copy
                        </button>
                        <button class="inline-flex items-center justify-center rounded-md text-xs font-medium ring-offset-background transition-colors focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-ring focus-visible:ring-offset-2 disabled:pointer-events-none disabled:opacity-50 hover:bg-slate-600 dark:hover:bg-slate-600 light:hover:bg-slate-200 hover:text-slate-100 dark:hover:text-slate-100 light:hover:text-slate-900 h-7 px-2 gap-1 share-btn" data-text="${this.escapeHtml(line)}">
                            <i class="fas fa-share text-xs"></i> Share
                        </button>
                    </div>
                </div>
            </div>
        `;

    // Add event listeners for actions
    const copyBtn = listItem.querySelector(".copy-btn");
    const shareBtn = listItem.querySelector(".share-btn");

    copyBtn.addEventListener("click", (e) => {
      e.stopPropagation();
      this.copyToClipboard(line);
    });

    shareBtn.addEventListener("click", (e) => {
      e.stopPropagation();
      this.sharePickupLine(line);
    });

    // Add click-to-copy functionality to the entire line
    listItem.addEventListener("click", () => {
      this.copyToClipboard(line);
    });

    return listItem;
  }

  async copyToClipboard(text) {
    try {
      if (navigator.clipboard && window.isSecureContext) {
        await navigator.clipboard.writeText(text);
      } else {
        // Fallback for older browsers or non-HTTPS contexts
        const textArea = document.createElement("textarea");
        textArea.value = text;
        textArea.style.position = "fixed";
        textArea.style.left = "-999999px";
        textArea.style.top = "-999999px";
        document.body.appendChild(textArea);
        textArea.focus();
        textArea.select();
        document.execCommand("copy");
        textArea.remove();
      }

      this.showTemporaryMessage("Copied to clipboard!", "success");
    } catch (error) {
      console.error("Failed to copy to clipboard:", error);
      this.showError(
        "Failed to copy to clipboard. Please select and copy manually.",
      );
    }
  }

  async sharePickupLine(text) {
    if (navigator.share) {
      try {
        await navigator.share({
          title: "ShAI Pickup Line",
          text: text,
          url: window.location.href,
        });
      } catch (error) {
        if (error.name !== "AbortError") {
          console.error("Share failed:", error);
          this.copyToClipboard(text);
        }
      }
    } else {
      // Fallback to copying
      this.copyToClipboard(text);
    }
  }

  showTemporaryMessage(message, type = "info") {
    const messageEl = document.createElement("div");
    messageEl.className = `toast-message ${type}`;
    messageEl.innerHTML = `
      <div class="flex items-center gap-2">
        <i class="fas fa-${type === "success" ? "check-circle" : "exclamation-circle"}"></i>
        <span>${this.escapeHtml(message)}</span>
      </div>
    `;

    document.body.appendChild(messageEl);

    // Trigger show animation
    requestAnimationFrame(() => {
      messageEl.classList.add("show");
    });

    // Auto-remove after 3 seconds
    setTimeout(() => {
      messageEl.classList.remove("show");
      setTimeout(() => {
        if (messageEl.parentNode) {
          document.body.removeChild(messageEl);
        }
      }, 300);
    }, 3000);
  }

  setLoadingState(loading) {
    if (loading) {
      this.loading.classList.remove("hidden");
      this.results.classList.add("hidden");
      this.generateBtn.disabled = true;
      this.generateBtn.innerHTML =
        '<i class="fas fa-heart animate-pulse"></i> Generating...';
    } else {
      this.loading.classList.add("hidden");
      this.generateBtn.disabled = false;
      this.generateBtn.innerHTML =
        '<i class="fas fa-heart"></i> Get some lines blud';
    }
  }

  showError(message) {
    this.errorMessage.textContent = message;
    this.errorMessage.classList.remove("hidden");
    setTimeout(() => {
      this.hideError();
    }, 5000);
  }

  hideError() {
    this.errorMessage.classList.add("hidden");
  }

  escapeHtml(text) {
    const div = document.createElement("div");
    div.textContent = text;
    return div.innerHTML;
  }

  async loadHistory() {
    try {
      const response = await fetch("/history");
      if (!response.ok) {
        throw new Error(`HTTP ${response.status}: ${response.statusText}`);
      }

      const data = await response.json();
      if (data.success) {
        this.displayHistory(data.history, data.current_session_id);
      } else {
        console.error("Failed to load history:", data.error);
      }
    } catch (error) {
      console.error("Error loading history:", error);
    }
  }

  displayHistory(history, currentSessionId) {
    this.historyList.innerHTML = "";

    if (!history || history.length === 0) {
      this.noHistory.classList.remove("hidden");
      this.syncMobileHistory([]);
      return;
    }

    this.noHistory.classList.add("hidden");

    history.forEach((item) => {
      const historyItem = this.createHistoryItem(item, currentSessionId);
      this.historyList.appendChild(historyItem);
    });

    // Sync with mobile history
    this.syncMobileHistory(history, currentSessionId);
  }

  createHistoryItem(item, currentSessionId) {
    const listItem = document.createElement("li");
    const isCurrentSession = item.session_id === currentSessionId;
    listItem.className = isCurrentSession
      ? "p-3 rounded-md border border-purple-500/30 bg-purple-500/5 dark:bg-purple-500/5 light:bg-purple-100/50 hover:bg-purple-500/10 dark:hover:bg-purple-500/10 light:hover:bg-purple-100/70 cursor-pointer transition-colors"
      : "p-3 rounded-md border border-slate-700 dark:border-slate-700 light:border-slate-300 bg-slate-800/30 dark:bg-slate-800/30 light:bg-white/50 hover:bg-slate-700/30 dark:hover:bg-slate-700/30 light:hover:bg-white/70 cursor-pointer transition-colors";
    listItem.dataset.historyId = item.id;

    const timestamp = new Date(item.timestamp).toLocaleString();
    const linesCount = item.pickup_lines.length;
    const sessionIndicator = isCurrentSession
      ? '<i class="fas fa-user text-purple-400 text-xs" title="Your session"></i>'
      : '<i class="fas fa-users text-slate-500 dark:text-slate-500 light:text-slate-400 text-xs" title="Other user"></i>';

    listItem.innerHTML = `
            <div class="text-sm text-slate-200 dark:text-slate-200 light:text-slate-800 mb-2 line-clamp-2 leading-relaxed">${this.escapeHtml(item.user_input)}</div>
            <div class="flex justify-between items-center text-xs">
                <div class="flex items-center gap-2">
                    ${sessionIndicator}
                    <span class="text-slate-400 dark:text-slate-400 light:text-slate-600 font-medium">${linesCount} line${linesCount !== 1 ? "s" : ""}</span>
                </div>
                <span class="text-slate-500 dark:text-slate-500 light:text-slate-500">${timestamp}</span>
            </div>
        `;

    listItem.addEventListener("click", () => {
      this.selectHistoryItem(item);
    });

    return listItem;
  }

  selectHistoryItem(item) {
    // Remove active class from all history items
    this.historyList.querySelectorAll("li").forEach((el) => {
      el.classList.remove("ring-2", "ring-purple-500");
    });

    // Add active class to selected item
    const selectedElement = this.historyList.querySelector(
      `[data-history-id="${item.id}"]`,
    );
    if (selectedElement) {
      selectedElement.classList.add("ring-2", "ring-purple-500");
    }

    // Update the input field and display results
    this.userInput.value = item.user_input;
    this.autoResizeTextarea();
    this.currentHistoryId = item.id;

    // Create a data object similar to what the generate endpoint returns
    const data = {
      success: true,
      input: item.user_input,
      pickup_lines: item.pickup_lines,
      timestamp: item.timestamp,
      using_local: item.using_local,
    };

    this.displayResults(data);
  }

  async clearHistory() {
    if (
      !confirm(
        "Are you sure you want to clear ALL pickup line history for everyone? This cannot be undone and will affect all users.",
      )
    ) {
      return;
    }

    try {
      const response = await fetch("/history", {
        method: "DELETE",
      });

      if (!response.ok) {
        throw new Error(`HTTP ${response.status}: ${response.statusText}`);
      }

      const data = await response.json();
      if (data.success) {
        this.historyList.innerHTML = "";
        this.noHistory.classList.remove("hidden");
        this.results.classList.add("hidden");
        this.userInput.value = "";
        this.currentHistoryId = null;
        this.syncMobileHistory([]);
        this.showTemporaryMessage(
          "All history cleared successfully!",
          "success",
        );
      } else {
        throw new Error(data.error || "Failed to clear history");
      }
    } catch (error) {
      console.error("Error clearing history:", error);
      this.showError(`Failed to clear history: ${error.message}`);
    }
  }

  syncMobileHistory(history, currentSessionId) {
    const mobileHistoryContainer = document.querySelector(
      ".lg\\:hidden .space-y-3",
    );
    if (!mobileHistoryContainer) return;

    mobileHistoryContainer.innerHTML = "";

    if (!history || history.length === 0) {
      mobileHistoryContainer.innerHTML = `
        <div class="text-center py-8 text-slate-400">
          <i class="fas fa-heart text-2xl mb-2 opacity-50"></i>
          <p class="text-xs">No pickup lines yet.<br>Start creating!</p>
        </div>
      `;
      return;
    }

    history.forEach((item) => {
      const mobileHistoryItem = this.createMobileHistoryItem(
        item,
        currentSessionId,
      );
      mobileHistoryContainer.appendChild(mobileHistoryItem);
    });
  }

  createMobileHistoryItem(item, currentSessionId) {
    const listItem = document.createElement("div");
    const isCurrentSession = item.session_id === currentSessionId;
    listItem.className = isCurrentSession
      ? "p-3 rounded-md border border-purple-500/30 bg-purple-500/5 dark:bg-purple-500/5 light:bg-purple-100/50 hover:bg-purple-500/10 dark:hover:bg-purple-500/10 light:hover:bg-purple-100/70 cursor-pointer transition-colors"
      : "p-3 rounded-md border border-slate-700 dark:border-slate-700 light:border-slate-300 bg-slate-800/30 dark:bg-slate-800/30 light:bg-white/50 hover:bg-slate-700/30 dark:hover:bg-slate-700/30 light:hover:bg-white/70 cursor-pointer transition-colors";
    listItem.dataset.historyId = item.id;

    const timestamp = new Date(item.timestamp).toLocaleString();
    const linesCount = item.pickup_lines.length;
    const sessionIndicator = isCurrentSession
      ? '<i class="fas fa-user text-purple-400 text-xs" title="Your session"></i>'
      : '<i class="fas fa-users text-slate-500 dark:text-slate-500 light:text-slate-400 text-xs" title="Other user"></i>';

    listItem.innerHTML = `
      <div class="text-sm text-slate-200 dark:text-slate-200 light:text-slate-800 mb-2 line-clamp-2 leading-relaxed">${this.escapeHtml(item.user_input)}</div>
      <div class="flex justify-between items-center text-xs">
        <div class="flex items-center gap-2">
          ${sessionIndicator}
          <span class="text-slate-400 dark:text-slate-400 light:text-slate-600 font-medium">${linesCount} line${linesCount !== 1 ? "s" : ""}</span>
        </div>
        <span class="text-slate-500 dark:text-slate-500 light:text-slate-500">${timestamp}</span>
      </div>
    `;

    listItem.addEventListener("click", () => {
      this.selectHistoryItem(item);
    });

    return listItem;
  }
}

// Initialize the app when the DOM is loaded
document.addEventListener("DOMContentLoaded", () => {
  new ShAIApp();
});

// Add some additional utility functions
window.addEventListener("error", (event) => {
  console.error("Global error:", event.error);
});

// Handle online/offline status
window.addEventListener("online", () => {
  console.log("Back online");
});

window.addEventListener("offline", () => {
  console.log("Gone offline");
});
