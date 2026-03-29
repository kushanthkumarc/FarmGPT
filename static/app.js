/**
 * FarmGPT - WhatsApp Clone Frontend Logic
 */

const chatBox = document.getElementById("chatBox");
const textInput = document.getElementById("textInput");
const sendBtn = document.getElementById("sendBtn");
const voiceBtn = document.getElementById("voiceBtn");
const langSelect = document.getElementById("langSelect");

let chatHistory = [];
let mediaRecorder;
let audioChunks = [];
let isRecording = false;
let stream;

// Format time HH:MM AM/PM
const getTime = () => {
    return new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' });
};

// UI Rendering
function appendMessage(text, isUser = false, isVoice = false) {
    const msgDiv = document.createElement("div");
    msgDiv.className = `message ${isUser ? 'sent' : 'received'}`;

    // Parse formatting like WhatsApp (basic markdown)
    let formattedText = text ? text.replace(/\n/g, '<br>') : '';
    formattedText = formattedText.replace(/\*(.*?)\*/g, '<strong>$1</strong>');

    let contentHtml = `<span class="text">${formattedText}</span>`;

    if (isVoice) {
        contentHtml = `
            <span class="text" style="display:flex; align-items:center; gap:8px;">
                <i class="fas fa-play-circle" style="color:#008069; font-size:1.5em;"></i> 🎙️ Audio Message
            </span>`;
    }

    msgDiv.innerHTML = `
        ${contentHtml}
        <span class="time">${getTime()}</span>
    `;

    chatBox.appendChild(msgDiv);
    chatBox.scrollTop = chatBox.scrollHeight;
    return msgDiv;
}

function showTyping() {
    const id = "typing-" + Date.now();
    const msgDiv = document.createElement("div");
    msgDiv.id = id;
    msgDiv.className = "message received typing";
    msgDiv.innerHTML = `
        <span class="text">Typing...</span>
    `;
    chatBox.appendChild(msgDiv);
    chatBox.scrollTop = chatBox.scrollHeight;
    return id;
}

function removeTyping(id) {
    const el = document.getElementById(id);
    if (el) el.remove();
}

// Check Input to toggle Mic/Send button
textInput.addEventListener("input", () => {
    if (textInput.value.trim().length > 0) {
        voiceBtn.style.display = "none";
        sendBtn.style.display = "flex";
    } else {
        voiceBtn.style.display = "flex";
        sendBtn.style.display = "none";
    }
});

// Send Message Logic
async function sendMessage(text = null, audioBlob = null) {
    const query = text || "";

    // Optimistic UI updates
    if (audioBlob) {
        appendMessage(null, true, true);
    } else if (query) {
        appendMessage(query, true, false);
    }

    textInput.value = "";
    voiceBtn.style.display = "flex";
    sendBtn.style.display = "none";

    const typingId = showTyping();

    // Prepare Payload
    const formData = new FormData();
    formData.append("language", langSelect.value); // Selected language controls OUTPUT completely
    formData.append("history", JSON.stringify(chatHistory.slice(-6)));

    if (text) formData.append("text", text);
    if (audioBlob) formData.append("audio", audioBlob, "recording.webm");

    try {
        const res = await fetch("/api/chat", {
            method: "POST",
            body: formData
        });

        const data = await res.json();
        removeTyping(typingId);

        if (data.error) {
            appendMessage(`❌ Error: ${data.error}`);
            return;
        }

        // Push to history
        chatHistory.push({ "role": "user", "content": data.query });
        chatHistory.push({ "role": "assistant", "content": data.reply });

        // Render Bot response
        const msgElem = appendMessage(data.reply, false, false);

        // Add TTS play button to the message element inline
        const playBtn = document.createElement("button");
        playBtn.innerHTML = '<i class="fas fa-volume-up"></i> Play Audio';
        playBtn.style.cssText = "display: block; margin-top: 5px; background: transparent; border: none; color: #008069; cursor: pointer; font-size: 13px; font-weight: bold;";

        // Audio hook execution
        playBtn.addEventListener("click", async () => {
            playBtn.innerHTML = '<i class="fas fa-circle-notch fa-spin"></i> Loading...';
            const audioData = new FormData();
            audioData.append("text", data.reply);
            audioData.append("language", langSelect.value);

            try {
                const req = await fetch("/api/tts", { method: "POST", body: audioData });
                const res = await req.json();

                if (res.audio_base64) {
                    const audioSrc = `data:audio/wav;base64,${res.audio_base64}`;
                    const audioEl = document.createElement("audio");
                    audioEl.controls = true;
                    audioEl.src = audioSrc;
                    audioEl.style.marginTop = "8px";
                    audioEl.style.width = "100%";
                    audioEl.style.height = "32px";

                    playBtn.replaceWith(audioEl);
                    audioEl.play();
                } else {
                    playBtn.innerHTML = `❌ ${res.error || "Audio Failed"}`;
                    playBtn.title = res.error || "Audio Failed";
                }
            } catch (err) {
                playBtn.innerHTML = "❌ Network Error";
            }
        });

        msgElem.insertBefore(playBtn, msgElem.querySelector(".time"));
        chatBox.scrollTop = chatBox.scrollHeight;

    } catch (err) {
        removeTyping(typingId);
        appendMessage("❌ Network Error: Could not connect to API.", false, false);
    }
}

// Listeners
sendBtn.addEventListener("click", () => {
    const txt = textInput.value.trim();
    if (txt) sendMessage(txt, null);
});

textInput.addEventListener("keypress", (e) => {
    if (e.key === "Enter") {
        const txt = textInput.value.trim();
        if (txt) sendMessage(txt, null);
    }
});

// Voice Recording Logic
voiceBtn.addEventListener("click", async () => {
    if (!isRecording) {
        // Start Recording
        try {
            stream = await navigator.mediaDevices.getUserMedia({ audio: true });
            mediaRecorder = new MediaRecorder(stream);

            mediaRecorder.ondataavailable = e => {
                if (e.data.size > 0) audioChunks.push(e.data);
            };

            mediaRecorder.onstop = () => {
                const audioBlob = new Blob(audioChunks, { type: 'audio/webm' });
                audioChunks = [];
                sendMessage(null, audioBlob);
                stream.getTracks().forEach(track => track.stop());
            };

            audioChunks = [];
            mediaRecorder.start();
            isRecording = true;
            voiceBtn.classList.add("recording");

            // Show recording animation inside chat box
            const id = "recording-" + Date.now();
            const msgDiv = document.createElement("div");
            msgDiv.id = id;
            msgDiv.className = "message sent";
            msgDiv.innerHTML = `
                <span class="text waveform">
                    <span></span><span></span><span></span>
                </span>
            `;
            chatBox.appendChild(msgDiv);
            chatBox.scrollTop = chatBox.scrollHeight;
            voiceBtn.dataset.recId = id;

        } catch (err) {
            alert("Microphone access denied or not available");
        }
    } else {
        // Stop Recording
        mediaRecorder.stop();
        isRecording = false;
        voiceBtn.classList.remove("recording");
        removeTyping(voiceBtn.dataset.recId);
    }
});

// 📍 AUTOMATIC GPS & WEATHER SYNC
function syncLocation() {
    if ("geolocation" in navigator) {
        navigator.geolocation.getCurrentPosition(async (position) => {
            const { latitude, longitude } = position.coords;
            try {
                const res = await fetch("/api/location", {
                    method: "POST",
                    headers: { "Content-Type": "application/json" },
                    body: JSON.stringify({ lat: latitude, lon: longitude })
                });
                const data = await res.json();
                console.log("📍 Location & Weather Synced:", data.weather);
            } catch (err) {
                console.error("GPS Sync Failed");
            }
        });
    }
}

// Start Sync
syncLocation();

document.getElementById("locationBtn").addEventListener("click", () => {
    syncLocation();
    alert("Refreshing your location & weather context... Done!");
});

// Sync Languages
fetch("/api/languages")
    .then(res => res.json())
    .then(langs => {
        langSelect.innerHTML = "";
        for (const [key, val] of Object.entries(langs)) {
            const opt = document.createElement("option");
            opt.value = key;
            opt.textContent = key;
            if (key.includes("Hindi")) opt.selected = true; // Default
            langSelect.appendChild(opt);
        }
    });
