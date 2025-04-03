let selectedRating = null;
let recognition = null;
let isListening = false;

// Highlight selected smiley and store the rating value
function selectSmiley(rating) {
  selectedRating = rating;
  const smileys = document.querySelectorAll(".smiley-row span");
  smileys.forEach((el, idx) => {
    el.classList.toggle("selected", idx + 1 === rating);
  });
}

function hideFeedback() {
  document.getElementById("feedback-container").style.display = "none";
  document.getElementById("show-feedback-btn").style.display = "block";
}

function showFeedback() {
  document.getElementById("feedback-container").style.display = "block";
  document.getElementById("show-feedback-btn").style.display = "none";
}

function enableEditMode() {
  document.getElementById("feedback-comment").disabled = false;
  const message = document.getElementById("feedback-message");
  message.innerText = "You can now edit your comment. Submit again to update.";
  message.style.color = "blue";
}

function sendMessage() {
  let userInputField = document.getElementById("user-input");
  let userInput = userInputField.value.trim();
  if (userInput === "") return;

  let chatBox = document.getElementById("chat-box");
  let spinner = document.getElementById("spinner");

  chatBox.innerHTML += `<p class="message user-message">${userInput}</p>`;
  userInputField.value = "";

  spinner.style.display = "block";
  let startTime = performance.now();
  let elapsed = 0;
  spinner.textContent = "⏳ Typing...";
  let timerInterval = setInterval(() => {
    elapsed = (performance.now() - startTime) / 1000;
    spinner.textContent = `⏳ Typing... ${elapsed.toFixed(1)}s`;
  }, 100);

  chatBox.scrollTop = chatBox.scrollHeight;

  const formData = new URLSearchParams({
    "user_input": userInput,
    "session_id": currentSessionId
  });

  fetch("/api/v1/chat", {
    method: "POST",
    body: formData,
    headers: { "Content-Type": "application/x-www-form-urlencoded" }
  })
    .then(response => {
      if (!response.body) throw new Error("ReadableStream not supported.");
      const reader = response.body.getReader();
      const decoder = new TextDecoder("utf-8");

      let botMsg = document.createElement("p");
      botMsg.className = "message bot-message";
      chatBox.appendChild(botMsg);

      function readChunk() {
        return reader.read().then(({ done, value }) => {
          if (done) {
            clearInterval(timerInterval);
            const finalTime = (performance.now() - startTime) / 1000;
            spinner.textContent = `🕒 Responded in ${finalTime.toFixed(1)}s`;
            setTimeout(() => {
              spinner.style.display = "none";
              spinner.textContent = "";
            }, 2000);
            chatBox.scrollTop = chatBox.scrollHeight;
            return;
          }
          const chunk = decoder.decode(value);
          botMsg.textContent += chunk;
          return readChunk();
        });
      }

      return readChunk();
    })
    .catch(error => {
      console.error("Error:", error);
      clearInterval(timerInterval);
      spinner.style.display = "none";
      chatBox.innerHTML += `<p class="message bot-message">Something went wrong. Try again!</p>`;
    });
}

function submitFeedback() {
  const commentBox = document.getElementById("feedback-comment");
  const comment = commentBox.value;
  const messageDiv = document.getElementById("feedback-message");

  if (!selectedRating) {
    messageDiv.innerText = "Please select a rating before submitting.";
    messageDiv.style.color = "red";
    return;
  }

  const formData = new URLSearchParams({
    "session_id": currentSessionId,
    "rating": selectedRating,
    "comment": comment
  });

  fetch("/api/v1/feedback", {
    method: "POST",
    body: formData,
    headers: { "Content-Type": "application/x-www-form-urlencoded" }
  })
    .then(res => res.json())
    .then(data => {
      messageDiv.innerText = data.message;
      messageDiv.style.color = "green";
      commentBox.disabled = true;
      document.getElementById("edit-feedback-btn").style.display = "block";
    })
    .catch(err => {
      messageDiv.innerText = "Feedback failed. Try again later.";
      messageDiv.style.color = "red";
    });
}

function loadMessageHistory() {
  fetch(`/api/v1/history?session_id=${currentSessionId}`)
    .then(res => res.json())
    .then(data => {
      const chatBox = document.getElementById("chat-box");
      data.messages.forEach(msg => {
        const p = document.createElement("p");
        p.className = "message";
        if (msg.type === "user") {
          p.classList.add("user-message");
        } else if (msg.type === "bot") {
          p.classList.add("bot-message");
        } else {
          p.classList.add("system-message");
        }
        p.textContent = msg.content;
        chatBox.appendChild(p);
      });
      chatBox.scrollTop = chatBox.scrollHeight;
    });
}

document.getElementById("voice-chat-btn").addEventListener("click", function() {
    // Check if browser supports the Web Speech API
    if (!('webkitSpeechRecognition' in window) && !('SpeechRecognition' in window)) {
        alert("Your browser doesn't support speech recognition. Try Chrome or Edge.");
        return;
    }

    if (isListening) {
        // If already listening, stop it
        stopSpeechRecognition();
        return;
    }

    // Initialize speech recognition
    recognition = new (window.SpeechRecognition || window.webkitSpeechRecognition)();
    recognition.lang = 'en-US';
    recognition.interimResults = false;
    recognition.maxAlternatives = 1;

    // Start visual feedback
    isListening = true;
    const voiceChatBtn = document.getElementById("voice-chat-btn");
    voiceChatBtn.textContent = "🎙️ Listening...";
    voiceChatBtn.classList.add("listening");

    // Handle results
    recognition.onresult = function(event) {
        const transcript = event.results[0][0].transcript;
        document.getElementById("user-input").value = transcript;

        // Small delay before sending to show the recognized text to the user
        setTimeout(() => {
            sendMessage();
        }, 500);
    };

    // Handle end of speech recognition
    recognition.onend = function() {
        stopSpeechRecognition();
    };

    // Handle errors
    recognition.onerror = function(event) {
        console.error("Speech recognition error:", event.error);

        let errorMessage = "Speech recognition error. ";
        if (event.error === 'not-allowed') {
            errorMessage += "Please allow microphone access.";
        } else if (event.error === 'no-speech') {
            errorMessage += "No speech detected. Try again.";
        } else {
            errorMessage += "Try again later.";
        }

        alert(errorMessage);
        stopSpeechRecognition();
    };

    // Start recognition
    try {
        recognition.start();
    } catch (error) {
        console.error("Error starting speech recognition:", error);
        alert("Could not start speech recognition. Try again.");
        stopSpeechRecognition();
    }
});

// Helper function to stop speech recognition and reset UI
function stopSpeechRecognition() {
    isListening = false;
    const voiceChatBtn = document.getElementById("voice-chat-btn");
    voiceChatBtn.textContent = "🎤";
    voiceChatBtn.classList.remove("listening");

    if (recognition) {
        try {
            recognition.stop();
        } catch (e) {
            // Ignore errors when stopping
        }
    }
}

window.onload = function () {
  document.getElementById("chat-box").innerHTML =
    '<p class="message bot-message">Welcome to Bravur AI Chatbot! How can I help you today?</p>';

  document.getElementById("user-input").addEventListener("keydown", function (event) {
    if (event.key === "Enter") {
      event.preventDefault();
      sendMessage();
    }
  });

  console.log("Current Session ID:", currentSessionId);
  loadMessageHistory();
};
