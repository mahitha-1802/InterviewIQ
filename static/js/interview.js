const interviewState = {
    id: null,
    totalQuestions: 5,
    currentQuestionIndex: 0,
    currentQuestionId: null,
    isVoiceMode: true,
    isListening: false,
    timerInterval: null,
    secondsElapsed: 0,
    recognition: null,
    synthesisUtterance: null,
    stream: null,
    autoSubmitTimeout: null
};

document.addEventListener("DOMContentLoaded", () => {
    const interviewDataElement = document.getElementById("interviewData");
    if (!interviewDataElement) return;

    interviewState.id = interviewDataElement.dataset.id;
    interviewState.totalQuestions = parseInt(interviewDataElement.dataset.total);
    interviewState.isVoiceMode = interviewDataElement.dataset.type === "Voice";

    initializeInterview();
});

async function initializeInterview() {
    startTimer();
    initWebcam();
    initSpeechRecognition();
    setupEventListeners();
    await fetchNextQuestion();
}

function startTimer() {
    const timerElement = document.getElementById("interviewTimer");
    interviewState.timerInterval = setInterval(() => {
        interviewState.secondsElapsed++;
        const mins = String(Math.floor(interviewState.secondsElapsed / 60)).padStart(2, "0");
        const secs = String(interviewState.secondsElapsed % 60).padStart(2, "0");
        if (timerElement) {
            timerElement.textContent = `${mins}:${secs}`;
        }
    }, 1000);
}

async function initWebcam() {
    const videoElement = document.getElementById("candidateVideo");
    if (!videoElement) return;
    try {
        const stream = await navigator.mediaDevices.getUserMedia({ video: true, audio: false });
        interviewState.stream = stream;
        videoElement.srcObject = stream;
    } catch (err) {
        const avatarFallback = document.getElementById("candidateAvatarFallback");
        if (avatarFallback) {
            avatarFallback.style.display = "flex";
            videoElement.style.display = "none";
        }
    }
}

function initSpeechRecognition() {
    const SpeechRecognition = window.SpeechRecognition || window.webkitSpeechRecognition;
    if (!SpeechRecognition) {
        interviewState.isVoiceMode = false;
        showSystemMessage("Speech recognition is not supported in this browser. Switching to text mode.");
        return;
    }

    const rec = new SpeechRecognition();
    rec.continuous = true;
    rec.interimResults = true;
    rec.lang = "en-US";

    rec.onstart = () => {
        interviewState.isListening = true;
        setListeningUI(true);
    };

    rec.onresult = (event) => {
        let interimTranscript = "";
        let finalTranscript = "";

        for (let i = event.resultIndex; i < event.results.length; ++i) {
            if (event.results[i].isFinal) {
                finalTranscript += event.results[i][0].transcript;
            } else {
                interimTranscript += event.results[i][0].transcript;
            }
        }

        const inputField = document.getElementById("answerInput");
        if (inputField) {
            inputField.value = finalTranscript || interimTranscript;
            resetAutoSubmitTimer();
        }
    };

    rec.onerror = () => {
        stopSpeechRecognition();
    };

    rec.onend = () => {
        interviewState.isListening = false;
        setListeningUI(false);
    };

    interviewState.recognition = rec;
}

function setupEventListeners() {
    const micBtn = document.getElementById("toggleMicBtn");
    if (micBtn) {
        micBtn.addEventListener("click", () => {
            if (interviewState.isListening) {
                stopSpeechRecognition();
            } else {
                startSpeechRecognition();
            }
        });
    }

    const submitBtn = document.getElementById("submitAnswerBtn");
    if (submitBtn) {
        submitBtn.addEventListener("click", () => {
            submitAnswer();
        });
    }

    const inputField = document.getElementById("answerInput");
    if (inputField) {
        inputField.addEventListener("keydown", (e) => {
            if (e.key === "Enter" && !e.shiftKey) {
                e.preventDefault();
                submitAnswer();
            }
        });
        inputField.addEventListener("input", () => {
            resetAutoSubmitTimer();
        });
    }

    const endBtn = document.getElementById("endInterviewBtn");
    if (endBtn) {
        endBtn.addEventListener("click", () => {
            endInterview();
        });
    }
}

function startSpeechRecognition() {
    if (interviewState.recognition && !interviewState.isListening) {
        window.speechSynthesis.cancel();
        setSpeakingUI(false);
        try {
            interviewState.recognition.start();
        } catch (e) {}
    }
}

function stopSpeechRecognition() {
    if (interviewState.recognition && interviewState.isListening) {
        try {
            interviewState.recognition.stop();
        } catch (e) {}
    }
}

function setListeningUI(active) {
    const micBtn = document.getElementById("toggleMicBtn");
    const userPanel = document.getElementById("userPanel");
    if (micBtn) {
        if (active) {
            micBtn.classList.add("active");
            micBtn.querySelector("i").className = "ri-mic-fill";
        } else {
            micBtn.classList.remove("active");
            micBtn.querySelector("i").className = "ri-mic-off-line";
        }
    }
    if (userPanel) {
        if (active) {
            userPanel.classList.add("listening");
        } else {
            userPanel.classList.remove("listening");
        }
    }
}

function setSpeakingUI(active) {
    const aiPanel = document.getElementById("aiPanel");
    if (aiPanel) {
        if (active) {
            aiPanel.classList.add("speaking");
        } else {
            aiPanel.classList.remove("speaking");
        }
    }
}

function setThinkingUI(active) {
    const messagesContainer = document.getElementById("chatMessages");
    const existingLoader = document.getElementById("aiLoader");

    if (active) {
        if (!existingLoader && messagesContainer) {
            const loader = document.createElement("div");
            loader.id = "aiLoader";
            loader.className = "typing-indicator";
            loader.innerHTML = `
                <div class="typing-dot"></div>
                <div class="typing-dot"></div>
                <div class="typing-dot"></div>
            `;
            messagesContainer.appendChild(loader);
            messagesContainer.scrollTop = messagesContainer.scrollHeight;
        }
    } else {
        if (existingLoader) {
            existingLoader.remove();
        }
    }
}

async function fetchNextQuestion() {
    setThinkingUI(true);
    try {
        const response = await fetch(`/api/get_question?interview_id=${interviewState.id}`);
        const data = await response.json();
        setThinkingUI(false);

        if (data.status === "completed") {
            redirectToReport();
            return;
        }

        interviewState.currentQuestionId = data.question_id;
        interviewState.currentQuestionIndex = data.question_order;

        displayQuestion(data.question_text);
        updateProgress();
        speakQuestion(data.question_text);
    } catch (err) {
        setThinkingUI(false);
        showSystemMessage("Error fetching question. Please try again.");
    }
}

function displayQuestion(text) {
    const questionTextElement = document.getElementById("currentQuestionText");
    if (questionTextElement) {
        questionTextElement.textContent = text;
    }

    addChatBubble(text, "ai");
}

function speakQuestion(text) {
    if (!interviewState.isVoiceMode) return;

    window.speechSynthesis.cancel();
    setSpeakingUI(true);

    const utterance = new SpeechSynthesisUtterance(text);
    const voices = window.speechSynthesis.getVoices();
    const englishVoice = voices.find(voice => voice.lang.includes("en-US") || voice.lang.includes("en-GB"));
    if (englishVoice) {
        utterance.voice = englishVoice;
    }
    utterance.rate = 1.0;
    utterance.pitch = 1.0;

    utterance.onend = () => {
        setSpeakingUI(false);
        startSpeechRecognition();
    };

    utterance.onerror = () => {
        setSpeakingUI(false);
    };

    interviewState.synthesisUtterance = utterance;
    window.speechSynthesis.speak(utterance);
}

async function submitAnswer() {
    if (interviewState.autoSubmitTimeout) {
        clearTimeout(interviewState.autoSubmitTimeout);
        interviewState.autoSubmitTimeout = null;
    }

    const inputField = document.getElementById("answerInput");
    if (!inputField) return;

    const answer = inputField.value.trim();
    if (!answer) return;

    stopSpeechRecognition();
    inputField.value = "";

    addChatBubble(answer, "user");
    setThinkingUI(true);

    try {
        const response = await fetch("/api/submit_answer", {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({
                interview_id: interviewState.id,
                question_id: interviewState.currentQuestionId,
                answer_text: answer
            })
        });

        const data = await response.json();
        setThinkingUI(false);

        if (data.status === "completed") {
            redirectToReport();
            return;
        }

        await fetchNextQuestion();
    } catch (err) {
        setThinkingUI(false);
        showSystemMessage("Failed to submit answer. Please retry.");
    }
}

function resetAutoSubmitTimer() {
    if (interviewState.autoSubmitTimeout) {
        clearTimeout(interviewState.autoSubmitTimeout);
        interviewState.autoSubmitTimeout = null;
    }

    const inputField = document.getElementById("answerInput");
    if (!inputField) return;

    if (inputField.value.trim().length > 0) {
        interviewState.autoSubmitTimeout = setTimeout(() => {
            submitAnswer();
        }, 5000);
    }
}

function updateProgress() {
    const percent = Math.round((interviewState.currentQuestionIndex / interviewState.totalQuestions) * 100);
    const bar = document.getElementById("progressBarFill");
    const label = document.getElementById("progressBarLabel");

    if (bar) bar.style.width = `${percent}%`;
    if (label) label.textContent = `Question ${interviewState.currentQuestionIndex} of ${interviewState.totalQuestions}`;
}

function addChatBubble(text, sender) {
    const container = document.getElementById("chatMessages");
    if (!container) return;

    const bubble = document.createElement("div");
    bubble.className = `chat-bubble ${sender}`;
    bubble.textContent = text;
    container.appendChild(bubble);
    container.scrollTop = container.scrollHeight;
}

function showSystemMessage(text) {
    const container = document.getElementById("chatMessages");
    if (!container) return;

    const message = document.createElement("div");
    message.style.textAlign = "center";
    message.style.fontSize = "12px";
    message.style.color = "var(--text-muted)";
    message.style.margin = "8px 0";
    message.textContent = text;
    container.appendChild(message);
    container.scrollTop = container.scrollHeight;
}

async function endInterview() {
    stopSpeechRecognition();
    window.speechSynthesis.cancel();

    if (interviewState.stream) {
        interviewState.stream.getTracks().forEach(track => track.stop());
    }
    if (interviewState.timerInterval) {
        clearInterval(interviewState.timerInterval);
    }

    setThinkingUI(true);

    try {
        await fetch("/api/end_interview", {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({
                interview_id: interviewState.id,
                duration_seconds: interviewState.secondsElapsed
            })
        });
        redirectToReport();
    } catch (err) {
        redirectToReport();
    }
}

function redirectToReport() {
    window.location.href = `/feedback/${interviewState.id}`;
}
