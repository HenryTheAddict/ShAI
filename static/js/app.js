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

      this.recognition.continuous = false;
      this.recognition.interimResults = true;
      this.recognition.lang = "en-US";

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

        this.userInput.value = finalTranscript;
        this.voiceStatusText.textContent = interimTranscript || "Listening...";
        this.autoResizeTextarea();
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
            errorMsg = "No speech detected. Try speaking louder.";
            break;
          default:
            errorMsg = `Voice recognition error: ${event.error}`;
        }
        this.voiceStatusText.textContent = errorMsg;
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
      this.voiceControls.style.display = "flex";
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
        '<i class="fas fa-microphone pulse"></i> Listening...';
      this.voiceBtn.disabled = true;
      this.stopVoiceBtn.style.display = "inline-flex";
      this.voiceIcon.className = "fas fa-microphone pulse";
    } else {
      this.voiceBtn.innerHTML = '<i class="fas fa-microphone"></i> Use Voice';
      this.voiceBtn.disabled = false;
      this.stopVoiceBtn.style.display = "none";
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
    this.results.classList.add("show");
    this.results.scrollIntoView({ behavior: "smooth", block: "start" });
  }

  createPickupLineElement(line, index) {
    const listItem = document.createElement("li");
    listItem.className = "pickup-line";
    listItem.style.animationDelay = `${index * 0.1}s`;

    listItem.innerHTML = `
            <div class="pickup-line-text">${this.escapeHtml(line)}</div>
            <div class="pickup-line-actions">
                <button class="action-btn copy-btn" data-text="${this.escapeHtml(line)}">
                    <i class="fas fa-copy"></i> Copy
                </button>
                <button class="action-btn share-btn" data-text="${this.escapeHtml(line)}">
                    <i class="fas fa-share"></i> Share
                </button>
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
    messageEl.className = `temp-message temp-message-${type}`;
    messageEl.textContent = message;
    messageEl.style.cssText = `
            position: fixed;
            top: 20px;
            right: 20px;
            background: ${type === "success" ? "var(--success-color)" : "var(--primary-color)"};
            color: white;
            padding: 1rem 1.5rem;
            border-radius: 0.75rem;
            box-shadow: var(--shadow-lg);
            z-index: 1000;
            animation: slideInRight 0.3s ease-out;
        `;

    // Add animation styles
    const style = document.createElement("style");
    style.textContent = `
            @keyframes slideInRight {
                from { transform: translateX(100%); opacity: 0; }
                to { transform: translateX(0); opacity: 1; }
            }
            @keyframes slideOutRight {
                from { transform: translateX(0); opacity: 1; }
                to { transform: translateX(100%); opacity: 0; }
            }
        `;
    document.head.appendChild(style);

    document.body.appendChild(messageEl);

    setTimeout(() => {
      messageEl.style.animation = "slideOutRight 0.3s ease-in";
      setTimeout(() => {
        document.body.removeChild(messageEl);
        document.head.removeChild(style);
      }, 300);
    }, 3000);
  }

  setLoadingState(loading) {
    if (loading) {
      this.loading.classList.add("show");
      this.results.classList.remove("show");
      this.generateBtn.disabled = true;
      this.generateBtn.innerHTML =
        '<i class="fas fa-heart pulse"></i> Generating...';
    } else {
      this.loading.classList.remove("show");
      this.generateBtn.disabled = false;
      this.generateBtn.innerHTML =
        '<i class="fas fa-heart"></i> Generate Pickup Lines';
    }
  }

  showError(message) {
    this.errorMessage.textContent = message;
    this.errorMessage.classList.add("show");
    setTimeout(() => {
      this.hideError();
    }, 5000);
  }

  hideError() {
    this.errorMessage.classList.remove("show");
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
        this.displayHistory(data.history);
      } else {
        console.error("Failed to load history:", data.error);
      }
    } catch (error) {
      console.error("Error loading history:", error);
    }
  }

  displayHistory(history) {
    this.historyList.innerHTML = "";

    if (!history || history.length === 0) {
      this.noHistory.style.display = "block";
      return;
    }

    this.noHistory.style.display = "none";

    history.forEach((item) => {
      const historyItem = this.createHistoryItem(item);
      this.historyList.appendChild(historyItem);
    });
  }

  createHistoryItem(item) {
    const listItem = document.createElement("li");
    listItem.className = "history-item";
    listItem.dataset.historyId = item.id;

    const timestamp = new Date(item.timestamp).toLocaleString();
    const linesCount = item.pickup_lines.length;

    listItem.innerHTML = `
            <div class="history-input">${this.escapeHtml(item.user_input)}</div>
            <div style="display: flex; justify-content: space-between; align-items: center;">
                <span class="history-lines-count">${linesCount} line${linesCount !== 1 ? "s" : ""}</span>
                <span class="history-timestamp">${timestamp}</span>
            </div>
        `;

    listItem.addEventListener("click", () => {
      this.selectHistoryItem(item);
    });

    return listItem;
  }

  selectHistoryItem(item) {
    // Remove active class from all history items
    this.historyList.querySelectorAll(".history-item").forEach((el) => {
      el.classList.remove("active");
    });

    // Add active class to selected item
    const selectedElement = this.historyList.querySelector(
      `[data-history-id="${item.id}"]`,
    );
    if (selectedElement) {
      selectedElement.classList.add("active");
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
        "Are you sure you want to clear all your pickup line history? This cannot be undone.",
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
        this.noHistory.style.display = "block";
        this.results.classList.remove("show");
        this.userInput.value = "";
        this.currentHistoryId = null;
        this.showTemporaryMessage("History cleared successfully!", "success");
      } else {
        throw new Error(data.error || "Failed to clear history");
      }
    } catch (error) {
      console.error("Error clearing history:", error);
      this.showError(`Failed to clear history: ${error.message}`);
    }
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
