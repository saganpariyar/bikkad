// Main Frontend App Controller for Bikkad Card Game
let API_BASE = (typeof getBackendUrl === "function") ? getBackendUrl() : "";
function refreshApiBase() {
    API_BASE = (typeof getBackendUrl === "function") ? getBackendUrl() : "";
    return API_BASE;
}

let gameState = null;
let autoPlayInterval = null;
let autoAiTimeout = null;
let autoPlaySpeed = 500; // ms
let isDemandCutMode = false;
let soundEnabled = true;

function stopAutoPlay() {
    if (autoAiTimeout) {
        clearTimeout(autoAiTimeout);
        autoAiTimeout = null;
    }
    if (autoPlayInterval) {
        clearInterval(autoPlayInterval);
        autoPlayInterval = null;
    }
}

// Dealing Animation State
let animatedDealRound = 0;
let isDealingAnimationActive = false;
let displayedCardBatch = 13; // 5, 10, or 13

let gameCounter = 1;
let activeView = "home";

// View Elements
const viewHome = document.getElementById("view-home");
const viewTable = document.getElementById("view-table");

// Room Management & Entry State
let currentRoomId = String(Math.floor(1000 + Math.random() * 9000));
let currentGameId = currentRoomId;
let myPlayerSeat = "P1";
let myPlayerName = "Sagan";

// Rajasthani Bot Names Pool (G. Prefix)
const BOT_NAMES_POOL = [
    "Bhimaram", "Jitu", "Dinesh", "Geeta", "Suraj", "Kantilal",
    "Prakash", "S Kumar", "Sangeeta", "Anita", "Mangilal", "Lumbaram",
    "Chogaram", "Sukhi", "Naresh", "Ganaram", "Sagan"
];

function getRandomBotNames(count = 3, excludeName = "") {
    const cleanEx = (excludeName || "").toLowerCase().replace(/^g\.\s*/i, "").replace(/^bot\s*/i, "").trim();
    const available = BOT_NAMES_POOL.filter(n => {
        const nl = n.toLowerCase();
        return !cleanEx || (nl !== cleanEx && !cleanEx.includes(nl) && !nl.includes(cleanEx));
    });
    const pool = (available.length >= count) ? available : [...BOT_NAMES_POOL];
    const shuffled = [...pool].sort(() => 0.5 - Math.random());
    return shuffled.slice(0, count).map(n => `G. ${n}`);
}

// Entry & Lobby Elements
const inputYourName = document.getElementById("input-your-name");
const tabBtnCreate = document.getElementById("tab-btn-create");
const tabBtnJoin = document.getElementById("tab-btn-join");
const tabContentCreate = document.getElementById("tab-content-create");
const tabContentJoin = document.getElementById("tab-content-join");
const selectSetupMode = document.getElementById("select-setup-mode");
const selectTrumpHider = document.getElementById("select-trump-hider");
const displayRoomId = document.getElementById("display-room-id");
const btnCopyRoomId = document.getElementById("btn-copy-room-id");
const displayP1Name = document.getElementById("display-p1-name");
const selectTypeP3 = document.getElementById("select-type-p3");
const inputNameP3 = document.getElementById("input-name-p3");
const selectTypeP2 = document.getElementById("select-type-p2");
const inputNameP2 = document.getElementById("input-name-p2");
const selectTypeP4 = document.getElementById("select-type-p4");
const inputNameP4 = document.getElementById("input-name-p4");
const inputJoinId = document.getElementById("input-join-id");
const btnSubmitJoin = document.getElementById("btn-submit-join");
const joinStatusMsg = document.getElementById("join-status-msg");

// Dual Center Pot Elements
const potCardsVal = document.getElementById("pot-cards-val");
const potTricksVal = document.getElementById("pot-tricks-val");
const potAccumulatorBox = document.getElementById("pot-accumulator-box");

// Home Form Elements
const inputGameName = document.getElementById("input-game-name");
const selectHomeMatchType = document.getElementById("select-home-match-type");
const inputPlayerP1 = document.getElementById("input-player-p1");
const inputPlayerP2 = document.getElementById("input-player-p2");
const inputPlayerP3 = document.getElementById("input-player-p3");
const inputPlayerP4 = document.getElementById("input-player-p4");
const btnStartGame = document.getElementById("btn-start-game");
const btnHeaderNewGame = document.getElementById("btn-header-new-game");
const btnModalNewGame = document.getElementById("btn-modal-new-game");
const gameNameBadge = document.getElementById("game-name-badge");

// DOM Elements
const modeBadge = document.getElementById("mode-badge");
const dealerBadge = document.getElementById("dealer-badge");
const turnBadge = document.getElementById("turn-badge");

const trumpHideBanner = document.getElementById("trump-hide-banner");
const gameAnnouncementBanner = document.getElementById("game-announcement-banner");
const btnCloseAnnouncement = document.getElementById("btn-close-announcement");
const announcementTitle = document.getElementById("announcement-title");
const announcementSub = document.getElementById("announcement-sub");
const playerContractBar = document.getElementById("player-contract-bar");
const btnBidTera = document.getElementById("btn-bid-tera");
const btnBidDoubleTera = document.getElementById("btn-bid-double-tera");

const handP1 = document.getElementById("hand-P1");
const countP1 = document.getElementById("count-P1");
const countP2 = document.getElementById("count-P2");
const countP3 = document.getElementById("count-P3");
const countP4 = document.getElementById("count-P4");

const nameP1 = document.getElementById("name-P1");
const nameP2 = document.getElementById("name-P2");
const nameP3 = document.getElementById("name-P3");
const nameP4 = document.getElementById("name-P4");

const trickP1 = document.getElementById("trick-P1");
const trickP2 = document.getElementById("trick-P2");
const trickP3 = document.getElementById("trick-P3");
const trickP4 = document.getElementById("trick-P4");

const potCount = document.getElementById("pot-count");
const potStreak = document.getElementById("pot-streak");
const trumpSlotLabel = document.getElementById("trump-slot-label");
const trumpContainer = document.getElementById("trump-card-container");
const btnDemandCut = document.getElementById("btn-demand-cut");

// Trump Reveal & Highlights
const trumpSlotBox = document.getElementById("trump-slot");
const trumpCallerBadge = document.getElementById("trump-revealed-caller-badge");
const trumpCallerName = document.getElementById("trump-caller-name");
const trumpRevealToast = document.getElementById("trump-reveal-toast");
const trumpRevealCaller = document.getElementById("trump-reveal-caller");
const trumpRevealSuitVal = document.getElementById("trump-reveal-suit-val");
const trumpRevealCardBox = document.getElementById("trump-reveal-card-box");
const btnCloseTrumpReveal = document.getElementById("btn-close-trump-reveal");
let previousTrumpRevealed = false;
let trumpRevealToastTimeout = null;
let lastAnnouncedContract = null;

const tricksTeamA = document.getElementById("tricks-team-a");
const cardsTeamA = document.getElementById("cards-team-a");
const tricksTeamB = document.getElementById("tricks-team-b");
const cardsTeamB = document.getElementById("cards-team-b");
const titleTeamA = document.getElementById("title-team-a");
const titleTeamB = document.getElementById("title-team-b");

const ladderDealer = document.getElementById("ladder-dealer");
const ladderScore = document.getElementById("ladder-score");
const ladderFill = document.getElementById("ladder-fill");
const logBox = document.getElementById("log-box");

const btnPauseBots = document.getElementById("btn-pause-bots") || document.getElementById("btn-auto-play");
const botStatusText = document.getElementById("bot-status-text");
let isBotPlayPaused = false;
const btnNextDeal = document.getElementById("btn-next-deal");
const btnConfig = document.getElementById("btn-config");
const btnSound = document.getElementById("btn-sound");
const speedSlider = document.getElementById("speed-slider");
const speedValue = document.getElementById("speed-value");

// Mobile Drawer Elements
const btnToggleScoreboard = document.getElementById("btn-toggle-scoreboard");
const btnCloseSidebar = document.getElementById("btn-close-sidebar");
const sidebarDrawer = document.getElementById("sidebar-drawer");
const sidebarBackdrop = document.getElementById("sidebar-backdrop");
const mobileScorePill = document.getElementById("mobile-score-pill");

// Modal Elements
const modalTrumpSelect = document.getElementById("modal-trump-select");
const modalConfig = document.getElementById("modal-config");
const selectMatchType = document.getElementById("select-match-type");
const chkOllama = document.getElementById("chk-ollama");
const btnSaveConfig = document.getElementById("btn-save-config");
const btnCloseConfig = document.getElementById("btn-close-config");

const modalDealComplete = document.getElementById("modal-deal-complete");
const dealCompleteTitle = document.getElementById("deal-complete-title");
const dealCompleteWinner = document.getElementById("deal-complete-winner");
const dealCompleteDesc = document.getElementById("deal-complete-desc");
const summaryValA = document.getElementById("summary-val-a");
const summaryValB = document.getElementById("summary-val-b");
const summaryLblA = document.getElementById("summary-lbl-a");
const summaryLblB = document.getElementById("summary-lbl-b");
const dealCompleteLadder = document.getElementById("deal-complete-ladder");
const btnModalNextDeal = document.getElementById("btn-modal-next-deal");
const btnDeclareRuntimeTrump = document.getElementById("btn-declare-runtime-trump");
const btnAskTrump = document.getElementById("btn-ask-trump");

// Initialization
document.addEventListener("DOMContentLoaded", () => {
    initServerSettingsModal();
    setupEventListeners();
    if (typeof applyLanguageToDOM === "function") {
        applyLanguageToDOM();
    }

    const urlParams = new URLSearchParams(window.location.search);
    const qGameId = urlParams.get("game_id");
    const qSeat = urlParams.get("seat");
    const qName = urlParams.get("name");
    const qGameType = urlParams.get("game");

    // Ping backend in background (show modal if joining via shared game link)
    checkAndWakeBackend(Boolean(qGameId));

    if (qGameType === "tikdi" || (qGameId && qGameId.toUpperCase().startsWith("TK-"))) {
        if (typeof switchActiveGame === "function") switchActiveGame("tikdi");
    }

    if (qGameId) {
        currentGameId = qGameId.toUpperCase();
        currentRoomId = currentGameId;
        if (qSeat) myPlayerSeat = qSeat;
        if (qName) myPlayerName = qName;
        switchView("table");
        if (gameNameBadge) {
            gameNameBadge.textContent = `🏷️ ${currentGameId}`;
        }
        fetchState();
    } else {
        switchView("home");
        fetchState();
    }
    startSyncPolling();
});

function switchView(targetView) {
    activeView = targetView;
    lastAnnouncedContract = null;
    const currentBase = window.location.pathname.endsWith(".html")
        ? window.location.pathname.substring(0, window.location.pathname.lastIndexOf("/") + 1)
        : (window.location.pathname.endsWith("/") ? window.location.pathname : window.location.pathname + "/");

    if (targetView === "home") {
        if (viewHome) viewHome.classList.remove("hidden");
        if (viewTable) viewTable.classList.add("hidden");
        if (modalDealComplete) modalDealComplete.classList.add("hidden");
        if (window.history && window.history.pushState) {
            window.history.pushState({}, "", currentBase);
        }
    } else {
        if (viewHome) viewHome.classList.add("hidden");
        if (viewTable) viewTable.classList.remove("hidden");
        if (window.history && window.history.pushState && currentGameId) {
            const seatParam = myPlayerSeat || "P1";
            const nameParam = encodeURIComponent(myPlayerName || "Sagan");
            const gameParam = currentGameType === "tikdi" ? "&game=tikdi" : "";
            window.history.pushState({}, "", `${currentBase}?game_id=${encodeURIComponent(currentGameId)}&seat=${seatParam}&name=${nameParam}${gameParam}`);
        }
    }
    if (typeof applyLanguageToDOM === "function") {
        applyLanguageToDOM();
    }
}

// ── Standardized Header Brand & Table Mode Updater ──────────────────────────
function updateHeaderBrand(gameType) {
    const titleEl = document.getElementById("header-game-title");
    const subEl = document.getElementById("header-game-sub");
    const iconEl = document.getElementById("header-game-icon");
    const feltTable = document.querySelector(".felt-table");

    if (feltTable) {
        feltTable.classList.toggle("jhuthaniya-mode", gameType === "jhuthaniya");
        feltTable.classList.toggle("bindicoat-mode", gameType === "bindicoat");
    }

    if (!titleEl) return;

    if (gameType === "bindicoat") {
        titleEl.textContent = "BINDI COAT";
        if (subEl) subEl.textContent = "Dehla Pakad · Mindikot";
        if (iconEl) iconEl.textContent = "🔴";
    } else if (gameType === "jhuthaniya") {
        titleEl.textContent = "JHUTHANIYA";
        if (subEl) subEl.textContent = "Bluff & Challenge Card Game";
        if (iconEl) iconEl.textContent = "🃏";
    } else if (gameType === "tikdi") {
        titleEl.textContent = "TIKDI";
        if (subEl) subEl.textContent = "Teen Do Paanch (3-2-5)";
        if (iconEl) iconEl.textContent = "🔺";
    } else {
        titleEl.textContent = "BIKKAD";
        if (subEl) subEl.textContent = "Apna Rajasthan Ka Bikkad";
        if (iconEl) iconEl.textContent = "🂠";
    }
}

let hubToastTimer = null;
function showHubToast(msg) {
    const toast = document.getElementById("hub-toast");
    if (!toast) return;
    toast.textContent = msg;
    toast.classList.remove("hidden");
    if (hubToastTimer) clearTimeout(hubToastTimer);
    hubToastTimer = setTimeout(() => {
        toast.classList.add("hidden");
    }, 3200);
}

// =========================================================================
// ==================== SERVER HEALTH & WAKE-UP MANAGER ====================
// =========================================================================
let isServerAwake = false;
let serverWakeInterval = null;
let serverWakeSeconds = 0;
let isWakingUpServer = false;

function updateServerNavStatus(status, text) {
    const dot = document.getElementById("server-status-dot");
    const label = document.getElementById("server-status-label");
    if (!dot || !label) return;

    dot.classList.remove("online", "waking", "offline");
    if (status === "online") {
        dot.classList.add("online");
        label.textContent = text || "Online";
    } else if (status === "waking") {
        dot.classList.add("waking");
        label.textContent = text || "Waking...";
    } else {
        dot.classList.add("offline");
        label.textContent = text || "Offline";
    }
}

async function checkAndWakeBackend(forceModal = false) {
    refreshApiBase();
    const modal = document.getElementById("modal-server-wakeup");
    const urlDisplay = document.getElementById("server-wakeup-url-display");
    const elapsedText = document.getElementById("server-elapsed-text");
    const pingStatus = document.getElementById("server-ping-status");
    const progressBar = document.getElementById("server-progress-bar");
    const titleEl = document.getElementById("server-wakeup-title");
    const descEl = document.getElementById("server-wakeup-desc");
    const isLocal = (API_BASE || "").includes("localhost") || (API_BASE || "").includes("127.0.0.1");

    if (descEl) {
        descEl.textContent = isLocal
            ? "Waiting for local backend server (127.0.0.1:8000) to start up... Automatic reconnect active."
            : "Free cloud servers sleep after inactivity. Waking up backend, please hold on (~30–50s)...";
    }

    // Fast initial check (2500ms timeout)
    const initialCheck = await checkBackendHealth(API_BASE, 2500);
    if (initialCheck.ok) {
        isServerAwake = true;
        updateServerNavStatus("online", "Online");
        if (modal) modal.classList.add("hidden");
        return true;
    }

    // Backend is asleep / cold / offline
    isServerAwake = false;
    updateServerNavStatus("waking", isLocal ? "Waiting..." : "Waking...");

    if (forceModal && modal) {
        modal.classList.remove("hidden");
        if (progressBar) progressBar.style.width = "10%";
        if (elapsedText) elapsedText.textContent = "⏱ Elapsed: 0s";
        if (pingStatus) pingStatus.textContent = "Pinging Server...";
    }

    if (isWakingUpServer) {
        if (forceModal && modal) modal.classList.remove("hidden");
        return false;
    }
    isWakingUpServer = true;
    serverWakeSeconds = 0;

    return new Promise((resolve) => {
        const updateUIProgress = () => {
            serverWakeSeconds += 2;
            if (elapsedText) elapsedText.textContent = `⏱ Elapsed: ${serverWakeSeconds}s`;
            // Smooth curve reaching ~92% around 45s
            const progress = Math.min(94, Math.round(100 * (1 - Math.exp(-serverWakeSeconds / 24))));
            if (progressBar) progressBar.style.width = `${progress}%`;
        };

        const pollLoop = async () => {
            updateUIProgress();
            if (pingStatus) pingStatus.textContent = "Pinging Server...";

            const check = await checkBackendHealth(API_BASE, 3000);
            if (check.ok) {
                isServerAwake = true;
                isWakingUpServer = false;
                if (serverWakeInterval) {
                    clearInterval(serverWakeInterval);
                    serverWakeInterval = null;
                }

                updateServerNavStatus("online", "Online");
                if (progressBar) progressBar.style.width = "100%";
                if (pingStatus) {
                    pingStatus.textContent = "✓ Server Connected!";
                    pingStatus.style.background = "rgba(16, 185, 129, 0.25)";
                    pingStatus.style.color = "#34d399";
                }
                if (titleEl) titleEl.textContent = "Game Server Ready!";
                if (descEl) descEl.textContent = "Backend is online and connected. Launching game now...";

                setTimeout(() => {
                    if (modal) modal.classList.add("hidden");
                    if (pingStatus) {
                        pingStatus.textContent = "Pinging Server...";
                        pingStatus.style.background = "";
                        pingStatus.style.color = "";
                    }
                    if (titleEl) titleEl.textContent = "Connecting to Game Server...";
                    resolve(true);
                }, 800);
            } else {
                if (pingStatus) pingStatus.textContent = `Retrying (${serverWakeSeconds}s)...`;
            }
        };

        serverWakeInterval = setInterval(pollLoop, 2500);
    });
}

function initServerSettingsModal() {
    const btnNavServer = document.getElementById("btn-server-settings");
    const modalSettings = document.getElementById("modal-server-settings");
    const btnCloseSettings = document.getElementById("btn-close-server-settings");
    const inputUrl = document.getElementById("input-custom-backend-url");
    const btnPresetRender = document.getElementById("btn-preset-render");
    const btnPresetLocal = document.getElementById("btn-preset-local");
    const btnTest = document.getElementById("btn-test-backend-connection");
    const btnSave = document.getElementById("btn-save-backend-url");
    const testResult = document.getElementById("server-test-result");
    const btnFromWakeup = document.getElementById("btn-open-server-settings-from-wakeup");

    function openSettings() {
        if (inputUrl) inputUrl.value = getBackendUrl();
        if (testResult) {
            testResult.classList.add("hidden");
            testResult.textContent = "";
        }
        if (modalSettings) modalSettings.classList.remove("hidden");
    }

    function closeSettings() {
        if (modalSettings) modalSettings.classList.add("hidden");
    }

    if (btnNavServer) btnNavServer.addEventListener("click", openSettings);
    if (btnFromWakeup) {
        btnFromWakeup.addEventListener("click", () => {
            const modalWakeup = document.getElementById("modal-server-wakeup");
            if (modalWakeup) modalWakeup.classList.add("hidden");
            openSettings();
        });
    }
    if (btnCloseSettings) btnCloseSettings.addEventListener("click", closeSettings);

    if (btnPresetRender && inputUrl) {
        btnPresetRender.addEventListener("click", () => {
            inputUrl.value = "https://sagan-czyf.onrender.com";
        });
    }
    if (btnPresetLocal && inputUrl) {
        btnPresetLocal.addEventListener("click", () => {
            inputUrl.value = "http://localhost:8000";
        });
    }

    if (btnTest && inputUrl && testResult) {
        btnTest.addEventListener("click", async () => {
            const testUrl = inputUrl.value.trim().replace(/\/+$/, "");
            if (!testUrl) {
                testResult.className = "server-test-result error";
                testResult.textContent = "Please enter a valid backend URL.";
                testResult.classList.remove("hidden");
                return;
            }
            testResult.className = "server-test-result";
            testResult.textContent = "🔌 Pinging health endpoint...";
            testResult.classList.remove("hidden");

            const res = await checkBackendHealth(testUrl, 6000);
            if (res.ok) {
                testResult.className = "server-test-result success";
                testResult.textContent = `✓ Connected successfully! Response time: ${res.elapsedMs}ms (${res.data?.service || "Desi Games Backend"})`;
            } else {
                testResult.className = "server-test-result error";
                testResult.textContent = `⚠️ Connection failed: ${res.error}. If using Render free tier, server may be sleeping and need ~40s to wake up.`;
            }
        });
    }

    if (btnSave && inputUrl) {
        btnSave.addEventListener("click", () => {
            const newUrl = inputUrl.value.trim().replace(/\/+$/, "");
            setBackendUrl(newUrl);
            refreshApiBase();
            closeSettings();
            updateServerNavStatus("waking", "Connecting...");
            checkAndWakeBackend(false);
        });
    }
}

function setupEventListeners() {
    // Games Hub Click Handlers
    const cardBikkad = document.getElementById("card-game-bikkad");
    const btnGotoBikkad = document.getElementById("btn-goto-bikkad");
    const onBikkadSelect = (e) => {
        if (e) e.preventDefault();
        if (typeof switchActiveGame === "function") switchActiveGame("bikkad");
        const setupCard = document.getElementById("home-setup-card");
        if (setupCard) {
            setupCard.scrollIntoView({ behavior: "smooth", block: "center" });
            setupCard.classList.remove("setup-card-highlight");
            void setupCard.offsetWidth; // force CSS reflow
            setupCard.classList.add("setup-card-highlight");
            setTimeout(() => setupCard.classList.remove("setup-card-highlight"), 3000);
        }
        if (inputYourName) inputYourName.focus();
    };

    if (cardBikkad) cardBikkad.addEventListener("click", onBikkadSelect);
    if (btnGotoBikkad) btnGotoBikkad.addEventListener("click", (e) => {
        e.stopPropagation();
        onBikkadSelect(e);
    });

    const cardTikdi = document.getElementById("card-game-tikdi");
    const btnGotoTikdi = document.getElementById("btn-goto-tikdi");
    const onTikdiSelect = (e) => {
        if (e) e.preventDefault();
        if (typeof switchActiveGame === "function") switchActiveGame("tikdi");
        const setupCard = document.getElementById("home-setup-card");
        if (setupCard) {
            setupCard.scrollIntoView({ behavior: "smooth", block: "center" });
            setupCard.classList.remove("setup-card-highlight");
            void setupCard.offsetWidth; // force CSS reflow
            setupCard.classList.add("setup-card-highlight");
            setTimeout(() => setupCard.classList.remove("setup-card-highlight"), 3000);
        }
        if (inputYourName) inputYourName.focus();
    };

    if (cardTikdi) cardTikdi.addEventListener("click", onTikdiSelect);
    if (btnGotoTikdi) btnGotoTikdi.addEventListener("click", (e) => {
        e.stopPropagation();
        onTikdiSelect(e);
    });

    document.querySelectorAll(".coming-soon-game").forEach(card => {
        card.addEventListener("click", () => {
            const gameName = card.getAttribute("data-game") || "Game";
            const template = typeof t === "function" ? t("toastComingSoon") : "{game} is coming soon! Stay tuned.";
            showHubToast(template.replace("{game}", gameName));
        });
    });

    // Room and Identity listeners
    if (displayRoomId) displayRoomId.textContent = currentRoomId;
    if (displayP1Name) displayP1Name.textContent = myPlayerName;

    if (inputYourName) {
        inputYourName.addEventListener("input", (e) => {
            myPlayerName = e.target.value.trim() || "Sagan";
            if (displayP1Name) displayP1Name.textContent = myPlayerName;
            updateTrumpHiderOptionLabels();
        });
    }
    if (inputNameP2) inputNameP2.addEventListener("input", updateTrumpHiderOptionLabels);
    if (inputNameP3) inputNameP3.addEventListener("input", updateTrumpHiderOptionLabels);
    if (inputNameP4) inputNameP4.addEventListener("input", updateTrumpHiderOptionLabels);

    // Initialize with default preset (Solo vs 3 Bots)
    setHumanCount(1);
    updateTrumpHiderOptionLabels();

    if (tabBtnCreate && tabBtnJoin) {
        tabBtnCreate.addEventListener("click", () => {
            tabBtnCreate.classList.add("active");
            tabBtnJoin.classList.remove("active");
            tabContentCreate.classList.remove("hidden");
            tabContentJoin.classList.add("hidden");
        });
        tabBtnJoin.addEventListener("click", () => {
            tabBtnJoin.classList.add("active");
            tabBtnCreate.classList.remove("active");
            tabContentJoin.classList.remove("hidden");
            tabContentCreate.classList.add("hidden");
        });
    }

    if (btnCopyRoomId) {
        btnCopyRoomId.addEventListener("click", () => {
            navigator.clipboard.writeText(currentRoomId).then(() => {
                const orig = btnCopyRoomId.textContent;
                btnCopyRoomId.textContent = "Copied! ✓";
                setTimeout(() => { btnCopyRoomId.textContent = orig; }, 1500);
            }).catch(() => {
                prompt("Copy Room ID:", currentRoomId);
            });
        });
    }

    // No selectSetupMode dropdown anymore — seat types are set via setSeatType()/applyPreset() toggle buttons

    if (selectTrumpHider) {
        selectTrumpHider.addEventListener("change", () => {
            syncHostRoomToBackend();
        });
    }

    // Automatically ensure room is registered on server for joined friends
    syncHostRoomToBackend();

    if (btnSubmitJoin) btnSubmitJoin.addEventListener("click", async () => {
        if (!isServerAwake) {
            const ok = await checkAndWakeBackend(true);
            if (!ok) return;
        }
        handleJoinGame();
    });

    if (btnStartGame) btnStartGame.addEventListener("click", async () => {
        if (!isServerAwake) {
            const ok = await checkAndWakeBackend(true);
            if (!ok) return;
        }
        if (typeof activeSelectedGame !== "undefined" && activeSelectedGame === "tikdi") {
            handleStartTikdiGame();
        } else if (typeof activeSelectedGame !== "undefined" && activeSelectedGame === "jhuthaniya") {
            handleStartJhuthaniyaGame();
        } else if (typeof activeSelectedGame !== "undefined" && activeSelectedGame === "bindicoat") {
            handleStartBindiCoatGame();
        } else {
            handleStartNewGame();
        }
    });
    if (btnHeaderNewGame) btnHeaderNewGame.addEventListener("click", handleReturnToHomeNewGame);
    if (btnModalNewGame) btnModalNewGame.addEventListener("click", handleReturnToHomeNewGame);

    const btnGoHome = document.getElementById("btn-go-home");
    if (btnGoHome) btnGoHome.addEventListener("click", () => {
        stopAutoPlay();
        handleReturnToHomeNewGame();
    });

    const btnRestartDeal = document.getElementById("btn-restart-deal");
    if (btnRestartDeal) btnRestartDeal.addEventListener("click", () => {
        if (currentGameType === "tikdi") {
            handleNextTikdiRound();
        } else {
            handleRestartDeal();
        }
    });

    if (btnPauseBots) btnPauseBots.addEventListener("click", togglePauseBots);
    btnNextDeal.addEventListener("click", () => {
        if (currentGameType === "tikdi") {
            handleNextTikdiRound();
        } else {
            handleNextDeal();
        }
    });
    if (btnConfig) btnConfig.addEventListener("click", () => modalConfig.classList.remove("hidden"));

    // Standardized Game Options Dropdown Menu
    const btnOptionsToggle = document.getElementById("btn-game-options-toggle");
    const gameOptionsDropdown = document.getElementById("game-options-dropdown");
    if (btnOptionsToggle && gameOptionsDropdown) {
        btnOptionsToggle.addEventListener("click", (e) => {
            e.stopPropagation();
            gameOptionsDropdown.classList.toggle("hidden");
        });
        document.addEventListener("click", (e) => {
            if (!gameOptionsDropdown.contains(e.target) && e.target !== btnOptionsToggle) {
                gameOptionsDropdown.classList.add("hidden");
            }
        });
        document.addEventListener("keydown", (e) => {
            if (e.key === "Escape") {
                gameOptionsDropdown.classList.add("hidden");
            }
        });
        gameOptionsDropdown.querySelectorAll("button").forEach(btn => {
            btn.addEventListener("click", () => {
                gameOptionsDropdown.classList.add("hidden");
            });
        });
    }

    // Mobile Scoreboard & Ledger Drawer Toggle
    if (btnToggleScoreboard && sidebarDrawer && sidebarBackdrop) {
        btnToggleScoreboard.addEventListener("click", () => {
            sidebarDrawer.classList.toggle("mobile-open");
            const isOpen = sidebarDrawer.classList.contains("mobile-open");
            sidebarBackdrop.classList.toggle("active", isOpen);
            sidebarBackdrop.classList.toggle("hidden", !isOpen);
        });
        if (btnCloseSidebar) {
            btnCloseSidebar.addEventListener("click", () => {
                sidebarDrawer.classList.remove("mobile-open");
                sidebarBackdrop.classList.remove("active");
                sidebarBackdrop.classList.add("hidden");
            });
        }
        sidebarBackdrop.addEventListener("click", () => {
            sidebarDrawer.classList.remove("mobile-open");
            sidebarBackdrop.classList.remove("active");
            sidebarBackdrop.classList.add("hidden");
        });
    }

    if (btnModalNextDeal) {
        btnModalNextDeal.addEventListener("click", () => {
            if (modalDealComplete) modalDealComplete.classList.add("hidden");
            handleNextDeal();
        });
    }

    if (btnDeclareRuntimeTrump) {
        btnDeclareRuntimeTrump.addEventListener("click", () => {
            modalTrumpSelect.classList.remove("hidden");
        });
    }

    if (btnAskTrump) {
        btnAskTrump.addEventListener("click", handleAskTrump);
    }

    btnBidTera.addEventListener("click", () => handleBid("Tera"));
    btnBidDoubleTera.addEventListener("click", () => handleBid("Double Tera"));

    if (btnCloseAnnouncement) {
        btnCloseAnnouncement.addEventListener("click", (e) => {
            e.stopPropagation();
            if (gameAnnouncementBanner) gameAnnouncementBanner.classList.add("hidden");
        });
    }

    if (btnCloseTrumpReveal && trumpRevealToast) {
        btnCloseTrumpReveal.addEventListener("click", (e) => {
            e.stopPropagation();
            trumpRevealToast.classList.add("hidden");
        });
        trumpRevealToast.addEventListener("click", () => {
            trumpRevealToast.classList.add("hidden");
        });
    }
    if (gameAnnouncementBanner) {
        gameAnnouncementBanner.addEventListener("click", () => {
            gameAnnouncementBanner.classList.add("hidden");
        });
    }

    // Trump suit picker buttons for runtime trump on void (or Tikdi trump selection)
    document.querySelectorAll(".suit-btn").forEach(btn => {
        btn.addEventListener("click", (e) => {
            const suit = e.target.getAttribute("data-suit");
            if (typeof currentGameType !== "undefined" && currentGameType === "tikdi") {
                handleSelectTikdiTrump(suit);
            } else {
                handleSelectRuntimeTrump(suit);
            }
        });
    });

    btnSound.addEventListener("click", () => {
        soundEnabled = !soundEnabled;
        sfx.enabled = soundEnabled;
        btnSound.textContent = soundEnabled ? "🔊 Sound On" : "🔇 Sound Off";
    });

    const btnLangToggle = document.getElementById("btn-lang-toggle");
    if (btnLangToggle) {
        btnLangToggle.addEventListener("click", () => {
            if (typeof toggleLanguage === "function") toggleLanguage();
        });
    }

    const btnHomeLangToggle = document.getElementById("btn-home-lang-toggle");
    if (btnHomeLangToggle) {
        btnHomeLangToggle.addEventListener("click", () => {
            if (typeof toggleLanguage === "function") toggleLanguage();
        });
    }

    // Playing Card Deck Style Switcher (Royal Desert / Classic Vector)
    function updateDeckThemeUI() {
        const theme = (typeof getDeckTheme === "function") ? getDeckTheme() : "royal";
        const isRoyal = (theme === "royal");

        const iconEl = document.getElementById("deck-theme-icon");
        const labelEl = document.getElementById("deck-theme-label");
        const menuIcon = document.getElementById("menu-deck-icon");
        const menuTitle = document.getElementById("menu-deck-title");

        if (iconEl) iconEl.textContent = isRoyal ? "🏜️" : "🃏";
        if (labelEl) labelEl.textContent = isRoyal ? "Royal Deck" : "Classic Deck";
        if (menuIcon) menuIcon.textContent = isRoyal ? "🏜️" : "🃏";
        if (menuTitle) menuTitle.textContent = isRoyal ? "Deck Style: Royal Desert" : "Deck Style: Classic Vector";
    }

    function toggleDeckTheme() {
        const current = (typeof getDeckTheme === "function") ? getDeckTheme() : "royal";
        const next = (current === "royal") ? "classic" : "royal";
        if (typeof setDeckTheme === "function") setDeckTheme(next);
        updateDeckThemeUI();

        if (typeof showHubToast === "function") {
            showHubToast(next === "royal" ? "Playing Cards: 🏜️ Royal Desert (Rajasthani)" : "Playing Cards: 🃏 Classic Vector");
        }

        // Re-render active table/view cards immediately
        if (gameState) {
            if (typeof currentGameType !== "undefined" && currentGameType === "tikdi") {
                if (typeof renderTikdiState === "function") renderTikdiState(gameState);
            } else if (typeof currentGameType !== "undefined" && currentGameType === "jhuthaniya") {
                if (typeof renderJhuthaniyaState === "function") renderJhuthaniyaState(gameState);
            } else if (typeof currentGameType !== "undefined" && currentGameType === "bindicoat") {
                if (typeof renderBindiCoatState === "function") renderBindiCoatState(gameState);
            } else if (typeof renderState === "function") {
                renderState(gameState);
            }
        }
    }

    const btnDeckToggle = document.getElementById("btn-deck-theme-toggle");
    if (btnDeckToggle) btnDeckToggle.addEventListener("click", toggleDeckTheme);

    const btnMenuDeckToggle = document.getElementById("btn-menu-deck-toggle");
    if (btnMenuDeckToggle) btnMenuDeckToggle.addEventListener("click", () => {
        toggleDeckTheme();
        const dropdown = document.getElementById("game-options-dropdown");
        if (dropdown) dropdown.classList.add("hidden");
    });

    updateDeckThemeUI();

    speedSlider.addEventListener("input", (e) => {
        autoPlaySpeed = parseInt(e.target.value);
        speedValue.textContent = `${autoPlaySpeed}ms`;
        if (autoPlayInterval) {
            stopAutoPlay();
            startAutoPlay();
        }
    });

    btnDemandCut.addEventListener("click", async () => {
        try {
            const res = await fetch(`${API_BASE}/api/open_trump`, {
                method: "POST",
                headers: { "Content-Type": "application/json" },
                body: JSON.stringify({
                    player_id: myPlayerSeat || "P1",
                    game_id: currentGameId
                })
            });
            if (res.ok) {
                sfx.playHukumDikhao();
                const data = await res.json();
                renderState(data);
            }
        } catch (e) {
            console.error("Open trump error:", e);
        }
    });

    if (trumpContainer) {
        trumpContainer.addEventListener("click", () => {
            if (btnDemandCut && !btnDemandCut.classList.contains("hidden")) {
                btnDemandCut.click();
            }
        });
    }

    btnSaveConfig.addEventListener("click", saveConfigFromModal);
    btnCloseConfig.addEventListener("click", () => modalConfig.classList.add("hidden"));
}

async function fetchState() {
    if (typeof currentGameType !== "undefined") {
        if (currentGameType === "tikdi") return await fetchTikdiState();
        if (currentGameType === "jhuthaniya") return await fetchJhuthaniyaState();
        if (currentGameType === "bindicoat") return await fetchBindiCoatState();
    }
    try {
        const res = await fetch(`${API_BASE}/api/state?game_id=${currentGameId}`);
        const data = await res.json();
        
        // Trigger step-by-step deal animation on new round
        if (animatedDealRound !== data.round_number) {
            startStepByStepDealAnimation(data);
        } else {
            renderState(data);
        }
    } catch (e) {
        console.error("Failed to fetch state:", e);
    }
}

async function startStepByStepDealAnimation(state) {
    animatedDealRound = state.round_number;
    isDealingAnimationActive = true;
    previousTrumpRevealed = false;
    if (trumpRevealToast) trumpRevealToast.classList.add("hidden");
    if (trumpCallerBadge) trumpCallerBadge.classList.add("hidden");
    if (trumpCallerName) trumpCallerName.textContent = "";
    if (trumpSlotBox) trumpSlotBox.classList.remove("trump-revealed-active");
    if (btnNextDeal) btnNextDeal.classList.remove("btn-highlight-pulse");
    if (turnBadge) turnBadge.classList.remove("turn-badge-winner");
    if (modalDealComplete) modalDealComplete.classList.add("hidden");
    document.querySelectorAll(".seat").forEach(s => {
        s.classList.remove("seat-deal-winner", "seat-caller-highlight");
    });

    // Step 1: 5 cards
    displayedCardBatch = 5;
    sfx.playDeal();
    renderState(state);

    if (state.deal_stage === "SELECT_TRUMP" && state.current_turn_player === (myPlayerSeat || 'P1')) {
        // Pause here for user to click 1 card to hide trump
        isDealingAnimationActive = false;
        return;
    }

    // Step 2: Next 5 cards (10 cards total)
    await new Promise(r => setTimeout(r, 1000));
    displayedCardBatch = 10;
    sfx.playDeal();
    renderState(state);

    // Step 3: Final 3 cards (13 cards total)
    await new Promise(r => setTimeout(r, 800));
    displayedCardBatch = 13;
    sfx.playDeal();
    isDealingAnimationActive = false;
    renderState(state);
}

function getRelativeSeats(mySeat) {
    const seats = ['P1', 'P2', 'P3', 'P4'];
    const myIdx = seats.indexOf(mySeat || 'P1');
    const safeIdx = myIdx >= 0 ? myIdx : 0;
    return {
        south: seats[safeIdx],
        west: seats[(safeIdx + 1) % 4],
        north: seats[(safeIdx + 2) % 4],
        east: seats[(safeIdx + 3) % 4]
    };
}

function renderState(state) {
    gameState = state;
    window.gameState = state;
    window.renderState = renderState;

    const mySeat = myPlayerSeat || "P1";
    const rel = getRelativeSeats(mySeat);
    const isMyTurn = state.current_turn_player === mySeat;

    updateHeaderBrand("bikkad");

    // Active Game Name Header Badge
    if (gameNameBadge) {
        gameNameBadge.textContent = `🏷️ ${state.game_id || currentGameId}`;
    }

    // Mode / Contract Header Badge
    let modeText = typeof t === "function" ? t("contractRegular") : "Contract: 🃏 Regular";
    if (state.mode === "Tera") {
        modeText = `${typeof t === "function" ? t("contractTera") : "Contract: 🔥 TERA"} (${state.player_names[state.declarer_id] || state.declarer_id})`;
    } else if (state.mode === "Double Tera") {
        modeText = `${typeof t === "function" ? t("contractDoubleTera") : "Contract: ⚡ DOUBLE TERA"} (${state.player_names[state.declarer_id] || state.declarer_id})`;
    }
    if (modeBadge) {
        modeBadge.textContent = modeText;
        modeBadge.classList.remove("hidden");
    }
    const dealerWord = typeof t === "function" ? t("dealerLabel") : "Dealer";
    if (dealerBadge) {
        dealerBadge.textContent = `🃏 ${dealerWord}: ${state.player_names[state.dealer_id] || state.dealer_id} (${state.dealer_score} pts)`;
    }
    
    // Calculate winning team if round is complete
    let winningTeam = null;
    if (state.round_complete) {
        const tricksA = (state.team_tricks_won && state.team_tricks_won['Team A']) || 0;
        const tricksB = (state.team_tricks_won && state.team_tricks_won['Team B']) || 0;
        if (state.mode in { "Tera": 1, "Double Tera": 1 }) {
            const declTeam = (state.declarer_id === 'P1' || state.declarer_id === 'P3') ? 'Team A' : 'Team B';
            const oppTeam = declTeam === 'Team A' ? 'Team B' : 'Team A';
            const lastLog = state.logs && state.logs.length > 0 ? state.logs[state.logs.length - 1] : "";
            const secondLastLog = state.logs && state.logs.length > 1 ? state.logs[state.logs.length - 2] : "";
            const isTeraFail = lastLog.includes("Tera FAILED") || secondLastLog.includes("Tera FAILED") || lastLog.includes("TERA FAILED") || secondLastLog.includes("TERA FAILED");
            winningTeam = isTeraFail ? oppTeam : declTeam;
        } else {
            const dealerTeam = state.dealer_team;
            const leadTeam = state.lead_team;
            const dealerTricks = state.team_tricks_won ? state.team_tricks_won[dealerTeam] || 0 : 0;
            const leadTricks = state.team_tricks_won ? state.team_tricks_won[leadTeam] || 0 : 0;

            if (dealerTricks >= 5) {
                winningTeam = dealerTeam;
            } else if (leadTricks >= 9) {
                winningTeam = leadTeam;
            } else if (tricksA > tricksB) {
                winningTeam = 'Team A';
            } else if (tricksB > tricksA) {
                winningTeam = 'Team B';
            }
        }
    }

    if (state.round_complete) {
        const lastLog = state.logs && state.logs.length > 0 ? state.logs[state.logs.length - 1] : "";
        const secondLastLog = state.logs && state.logs.length > 1 ? state.logs[state.logs.length - 2] : "";
        const isTeraFail = lastLog.includes("Tera FAILED") || secondLastLog.includes("Tera FAILED") || lastLog.includes("TERA FAILED") || secondLastLog.includes("TERA FAILED");
        let winMsg = "";
        if (state.mode === "Double Tera" && !isTeraFail) {
            const declName = (state.player_names && state.player_names[state.declarer_id]) || state.declarer_id;
            winMsg = `${declName} Won Solo!`;
        } else {
            winMsg = winningTeam ? `${winningTeam} Won!` : (typeof t === "function" ? t("dealFinished") : "Deal Complete!");
        }
        turnBadge.textContent = `🏆 ${winMsg}`;
        turnBadge.classList.add("turn-badge-winner");
        if (btnNextDeal) {
            btnNextDeal.classList.remove("hidden");
            btnNextDeal.classList.add("btn-highlight-pulse");
        }
    } else {
        turnBadge.classList.remove("turn-badge-winner");
        if (btnNextDeal) {
            btnNextDeal.classList.add("hidden");
            btnNextDeal.classList.remove("btn-highlight-pulse");
        }
        if (state.deal_stage === "SELECT_TRUMP") {
            const hiderName = state.player_names[state.current_turn_player] || state.current_turn_player;
            turnBadge.textContent = isMyTurn ? "🃏 Select Trump" : `⏳ ${hiderName} choosing Trump`;
        } else {
            const activeName = state.player_names[state.current_turn_player] || state.current_turn_player;
            turnBadge.textContent = isMyTurn ? "🟢 Your Turn" : `Turn: ${activeName}`;
        }
    }

    // Announcement Banner & Voice SFX (Tera / Double Tera declarations)
    if (state.announcement) {
        if (state.announcement.title !== lastAnnouncedContract) {
            lastAnnouncedContract = state.announcement.title;
            const declId = state.announcement.declarer_id || state.declarer_id;
            const declName = (state.player_names && declId ? state.player_names[declId] : declId) || "Player";
            if (state.announcement.mode === "Double Tera" || state.mode === "Double Tera") {
                sfx.playDoubleTera(declName);
            } else if (state.announcement.mode === "Tera" || state.mode === "Tera") {
                sfx.playTera(declName);
            }
        }
        showAnnouncement(state.announcement.title, state.announcement.sub);
    } else if (gameAnnouncementBanner && state.mode === "Regular") {
        gameAnnouncementBanner.classList.add("hidden");
        lastAnnouncedContract = null;
    }

    // Trump Hiding Banner (Stage 1: Initial 5 cards)
    if (state.deal_stage === "SELECT_TRUMP" && state.current_turn_player === mySeat) {
        trumpHideBanner.classList.remove("hidden");
    } else {
        trumpHideBanner.classList.add("hidden");
    }

    // Prominent In-Hand Contract Bar: Visible during Trick 1 before player plays card
    const hasPlayerPlayedInTrick1 = state.current_trick && state.current_trick.some(play => play.player_id === mySeat);
    const showContractBar = state.deal_stage === "READY" && state.trick_number === 1 && !hasPlayerPlayedInTrick1 && state.mode === "Regular" && !isDealingAnimationActive;
    
    if (playerContractBar) {
        if (showContractBar) {
            playerContractBar.classList.remove("hidden");
        } else {
            playerContractBar.classList.add("hidden");
        }
    }

    // Dealer, Trump Setter, and Declarer IDs
    const dealerId = state.dealer_id;
    const isSpecialContract = state.mode in { "Tera": 1, "Double Tera": 1 };
    const declarerId = state.declarer_id;
    const trumpSetterId = isSpecialContract ? null : (state.hidden_trump_setter || state.eldest_hand);

    // Dynamic relative seat layout mapping:
    // South DOM slot (seat-P1) = mySeat (You)
    // West DOM slot (seat-P2) = Left Opponent
    // North DOM slot (seat-P3) = Partner
    // East DOM slot (seat-P4) = Right Opponent
    const seatSlotMap = [
        { domP: 'P1', player: rel.south, isSelf: true },
        { domP: 'P2', player: rel.west, isSelf: false },
        { domP: 'P3', player: rel.north, isPartner: true },
        { domP: 'P4', player: rel.east, isSelf: false }
    ];

    seatSlotMap.forEach(slot => {
        const p = slot.player;
        const seatEl = document.getElementById(`seat-${slot.domP}`);
        const roleEl = document.getElementById(`role-${slot.domP}`);
        const nameEl = document.getElementById(`name-${slot.domP}`);
        const countEl = document.getElementById(`count-${slot.domP}`);

        const isDealer = (p === dealerId);
        const isTrumpSetter = (p === trumpSetterId);
        const isDeclarer = (isSpecialContract && p === declarerId);
        const isSittingOut = state.active_players && !state.active_players.includes(p);
        let isWinner = false;
        if (state.round_complete && winningTeam) {
            const lastLog = state.logs && state.logs.length > 0 ? state.logs[state.logs.length - 1] : "";
            const secondLastLog = state.logs && state.logs.length > 1 ? state.logs[state.logs.length - 2] : "";
            const isTeraFail = lastLog.includes("Tera FAILED") || secondLastLog.includes("Tera FAILED") || lastLog.includes("TERA FAILED") || secondLastLog.includes("TERA FAILED");
            if (state.mode === "Double Tera" && !isTeraFail) {
                // In Double Tera victory, ONLY the solo declarer won!
                isWinner = (p === state.declarer_id);
            } else {
                isWinner = (
                    (winningTeam === 'Team A' && (p === 'P1' || p === 'P3')) ||
                    (winningTeam === 'Team B' && (p === 'P2' || p === 'P4'))
                );
            }
        }

        if (seatEl) {
            seatEl.classList.toggle("active-turn", p === state.current_turn_player && state.deal_stage !== "SELECT_TRUMP" && !state.round_complete);
            seatEl.classList.toggle("is-dealer", isDealer);
            seatEl.classList.toggle("is-trump-setter", isTrumpSetter);
            seatEl.classList.toggle("is-declarer", isDeclarer);
            seatEl.classList.toggle("is-sitting-out", isSittingOut);
            seatEl.classList.toggle("seat-deal-winner", !!isWinner);
        }

        if (nameEl) {
            let label = state.player_names[p] || p;
            if (slot.isSelf) label += ` ${typeof t === "function" ? t("youTag") : "(You)"}`;
            else if (slot.isPartner) label += ` ${typeof t === "function" ? t("partnerTag") : "(Partner)"}`;
            nameEl.textContent = label;
        }

        if (countEl) {
            const count = (p === rel.south && !isDealingAnimationActive) ? 
                ((state.hands && state.hands[p]) || []).length : 
                ((state.hands && state.hands[p]) || []).length;
            countEl.textContent = `${count} ${typeof t === "function" ? t("cardsCount") : "cards"}`;
        }

        if (roleEl) {
            roleEl.innerHTML = "";
            if (isSittingOut) {
                const bSit = document.createElement("span");
                bSit.className = "badge-role badge-sits-out";
                bSit.textContent = typeof t === "function" ? t("sitsOutRole") : "💤 SITS OUT (Solo)";
                roleEl.appendChild(bSit);
            }
            if (isWinner) {
                const bWin = document.createElement("span");
                bWin.className = "badge-role badge-winner";
                bWin.textContent = typeof t === "function" ? t("dealWinnerRole") : "🏆 DEAL WINNER";
                roleEl.appendChild(bWin);
            }
            if (isDealer) {
                const b = document.createElement("span");
                b.className = "badge-role badge-dealer";
                b.title = "Dealer: Deals / gives cards to all players";
                b.textContent = typeof t === "function" ? t("dealerRole") : "🎴 DEALER (Gives Cards)";
                roleEl.appendChild(b);
            }
            if (isTrumpSetter) {
                const b = document.createElement("span");
                b.className = "badge-role badge-trump-setter";
                b.title = "Eldest Hand: Hides the trump card";
                b.textContent = typeof t === "function" ? t("hidesTrumpRole") : "🃏 HIDES TRUMP";
                roleEl.appendChild(b);
            }
            if (isDeclarer) {
                const b = document.createElement("span");
                b.className = "badge-role badge-declarer";
                b.title = `${state.mode} Declarer: Leads the first card!`;
                b.textContent = `👑 ${state.mode.toUpperCase()} (${typeof t === "function" ? t("playsFirstRole") : "Plays First"})`;
                roleEl.appendChild(b);
            }
        }
    });

    // Turn & Void Context for current client
    const isHumanTurn = state.player_types && state.player_types[state.current_turn_player] === 'human';
    const hasLedSuit = !!state.led_suit;
    const isVoid = isMyTurn && hasLedSuit && state.hands && state.hands[mySeat] && !state.hands[mySeat].some(c => c.suit === state.led_suit);

    // Hidden / Runtime Trump Slot
    trumpContainer.innerHTML = "";
    const suitSymbols = { 'S': '♠', 'H': '♥', 'D': '♦', 'C': '♣' };
    const suitNames = { 
        'S': typeof t === "function" ? t("suitSpades") : 'SPADES', 
        'H': typeof t === "function" ? t("suitHearts") : 'HEARTS', 
        'D': typeof t === "function" ? t("suitDiamonds") : 'DIAMONDS', 
        'C': typeof t === "function" ? t("suitClubs") : 'CLUBS' 
    };

    if (state.mode in { "Tera": 1, "Double Tera": 1 }) {
        if (state.trump_revealed && state.trump_suit) {
            trumpSlotLabel.innerHTML = `TRUMP: <span style="color:${state.trump_suit in {'H':1,'D':1} ? '#ef4444' : '#fff'};">${suitSymbols[state.trump_suit]} ${suitNames[state.trump_suit]}</span>`;
            trumpContainer.innerHTML = `<span style="font-size:28px; color: ${state.trump_suit in {'H':1,'D':1} ? '#dc2626' : '#fff'};">${suitSymbols[state.trump_suit]}</span>`;
        } else {
            trumpSlotLabel.textContent = typeof t === "function" ? t("runtimeTrump") : "RUNTIME TRUMP";
            trumpContainer.innerHTML = `<span style="font-size:10px; color:#94a3b8; text-align:center; padding:4px;">${typeof t === "function" ? t("noHiddenTrump") : "NO HIDDEN TRUMP"}</span>`;
        }
    } else {
        if (state.trump_revealed && state.hidden_trump_card) {
            trumpSlotLabel.innerHTML = `TRUMP: <span style="color:${state.trump_suit in {'H':1,'D':1} ? '#ef4444' : '#fff'};">${suitSymbols[state.trump_suit]} ${suitNames[state.trump_suit]}</span>`;
            trumpContainer.appendChild(createCardSVG(state.hidden_trump_card.code));
            trumpContainer.title = `Trump revealed: ${state.hidden_trump_card.code} (${state.trump_suit})`;
            trumpContainer.style.cursor = "default";
        } else if (state.hidden_trump_card) {
            trumpSlotLabel.textContent = typeof t === "function" ? t("hiddenTrump") : "HIDDEN TRUMP";
            trumpContainer.appendChild(createCardSVG("BACK"));
            trumpContainer.title = isVoid && isMyTurn ? "Click to Open Trump!" : "Trump card hidden under saucer (Bandh Hukum)";
            trumpContainer.style.cursor = isVoid && isMyTurn ? "pointer" : "default";
        } else {
            trumpSlotLabel.textContent = typeof t === "function" ? t("hiddenTrump") : "HIDDEN TRUMP";
            trumpContainer.innerHTML = `<span style="font-size:10px; color:#94a3b8; text-align:center; padding:4px;">${typeof t === "function" ? t("selectingTrump") : "SELECTING..."}</span>`;
            trumpContainer.style.cursor = "default";
        }
    }

    // Trump Slot Box & Caller Badge Highlight
    if (trumpSlotBox) {
        if (state.trump_revealed) {
            trumpSlotBox.classList.add("trump-revealed-active");
        } else {
            trumpSlotBox.classList.remove("trump-revealed-active");
        }
    }
    if (trumpCallerBadge && trumpCallerName) {
        if (state.trump_revealed && state.trump_opener_id) {
            const openerName = state.trump_opener_name || (state.player_names && state.player_names[state.trump_opener_id]) || state.trump_opener_id;
            const cleanName = openerName.split('(')[0].trim();
            trumpCallerName.textContent = `Show: ${cleanName}`;
            trumpCallerBadge.classList.remove("hidden");
            trumpCallerBadge.title = `Trump revealed by ${openerName}`;
        } else {
            trumpCallerBadge.classList.add("hidden");
            trumpCallerName.textContent = "";
        }
    }

    // Trigger Animated Trump Reveal Toast on transition
    handleTrumpRevealNotification(state);

    // Regular Open Trump
    if (isMyTurn && isVoid && !state.trump_revealed && state.mode === "Regular" && state.deal_stage === "READY") {
        btnDemandCut.classList.remove("hidden");
    } else {
        btnDemandCut.classList.add("hidden");
        isDemandCutMode = false;
    }

    // Tera: Declarer can pick Trump whenever desired before it is revealed
    // Tera / Double Tera: Pick Trump / Ask Trump buttons
    if (btnDeclareRuntimeTrump) {
        if (isSpecialContract && !state.trump_revealed && state.declarer_id === mySeat && state.deal_stage === "READY" && !state.round_complete) {
            btnDeclareRuntimeTrump.classList.remove("hidden");
        } else {
            btnDeclareRuntimeTrump.classList.add("hidden");
        }
    }

    // In Tera / Double Tera: Any player whose turn it is and who is void can ask for / demand Trump!
    if (btnAskTrump) {
        if (isSpecialContract && !state.trump_revealed && isMyTurn && isVoid && state.deal_stage === "READY" && !state.round_complete) {
            btnAskTrump.textContent = state.declarer_id === mySeat ? "🎯 Pick Trump" : (typeof t === "function" ? t("askTrumpBtn") : "🎺 Ask Trump");
            btnAskTrump.classList.remove("hidden");
        } else {
            btnAskTrump.classList.add("hidden");
        }
    }

    // Auto-open Trump Select modal if Declarer is void, OR if another player demanded Trump from Declarer!
    if (isSpecialContract && !state.trump_revealed && state.deal_stage === "READY") {
        if (state.declarer_id === mySeat && (isVoid || state.trump_selection_pending_from === mySeat)) {
            modalTrumpSelect.classList.remove("hidden");
            const modalTitle = modalTrumpSelect.querySelector("h2, h3, .modal-title");
            if (modalTitle) {
                if (state.trump_demanded_by) {
                    const demanderName = (state.player_names && state.player_names[state.trump_demanded_by]) || state.trump_demanded_by;
                    modalTitle.textContent = `🎺 ${demanderName} Demanded Trump! Choose Suit:`;
                } else {
                    modalTitle.textContent = `🃏 Choose Runtime Trump Suit:`;
                }
            }
        }
    }

    // Deal Complete: Table cards and state remain visible, winners highlighted, no popup modal
    if (modalDealComplete) {
        modalDealComplete.classList.add("hidden");
    }

    // Determine cards to render for South (You)
    let myCards = (state.hands && state.hands[rel.south]) || [];
    if (isDealingAnimationActive) {
        if (displayedCardBatch === 5 && state.phase1_deals && state.phase1_deals[rel.south]) {
            myCards = state.phase1_deals[rel.south];
        } else if (displayedCardBatch === 10 && state.phase1_deals && state.phase2_deals && state.phase1_deals[rel.south] && state.phase2_deals[rel.south]) {
            let b10 = state.phase1_deals[rel.south].concat(state.phase2_deals[rel.south]);
            if (state.hidden_trump_card && state.hidden_trump_setter === rel.south && !state.trump_revealed) {
                b10 = b10.filter(c => c.code !== state.hidden_trump_card.code);
            }
            myCards = b10;
        }
    }

    // Render Hands
    const mustPlayTrumpSuit = (state.must_play_trump_player === rel.south && state.trump_revealed) ? state.trump_suit : null;
    renderSouthHand(
        myCards,
        state.led_suit,
        isHumanTurn && isMyTurn && !isDealingAnimationActive,
        state.deal_stage === "SELECT_TRUMP" && state.eldest_hand === rel.south,
        mustPlayTrumpSuit
    );
    
    countP1.textContent = `${myCards.length} cards`;
    countP2.textContent = `${((state.hands && state.hands[rel.west]) || []).length} cards`;
    countP3.textContent = `${((state.hands && state.hands[rel.north]) || []).length} cards`;
    countP4.textContent = `${((state.hands && state.hands[rel.east]) || []).length} cards`;

    // Render Played Cards in Center Trick Slots (Visible on Table)
    renderTableTrickCards(state.current_trick, state.last_completed_trick, state.last_trick_winner, state.last_trick_winning_card, (state.active_players && state.active_players.length) || 4);

    // Center Pot Dual Metrics (Cards & Tricks)
    const potBox = document.getElementById("pot-accumulator-box");
    if (potBox) {
        potBox.classList.remove("hidden");
        potBox.style.display = "flex";
        const potTitle = potBox.querySelector(".pot-title");
        if (potTitle) potTitle.textContent = "POT";
        const potCardsLbl = potBox.querySelector(".pot-lbl");
        if (potCardsLbl) potCardsLbl.textContent = typeof t === "function" ? t("potCards") : "Cards";
    }
    if (potCardsVal) potCardsVal.textContent = state.pot_card_count ?? 0;
    if (potTricksVal) potTricksVal.textContent = state.pot_trick_count ?? 0;
    if (potCount) potCount.textContent = `${state.pot_card_count ?? 0} CARDS (${state.pot_trick_count ?? 0} TRICKS)`;
    if (potStreak) {
        if (state.pot_streak_holder && state.pot_streak_count > 0) {
            potStreak.textContent = `🔥 ${state.pot_streak_count}`;
            potStreak.title = `Streak: ${state.pot_streak_holder} (${state.pot_streak_count} win)`;
            potStreak.classList.remove("hidden");
        } else {
            potStreak.textContent = "";
            potStreak.classList.add("hidden");
        }
    }

    // Scoreboard
    const bikkadScorePanel = document.getElementById("bikkad-scoreboard-panel");
    const tikdiScorePanel = document.getElementById("tikdi-scoreboard-panel");
    const scoreboardTitle = document.getElementById("scoreboard-title");
    if (bikkadScorePanel) bikkadScorePanel.classList.remove("hidden");
    if (tikdiScorePanel) tikdiScorePanel.classList.add("hidden");
    if (scoreboardTitle) scoreboardTitle.textContent = "🏆 Scoreboard & Ladder";

    if (tricksTeamA) tricksTeamA.textContent = `Tricks: ${state.team_tricks_won['Team A']}`;
    cardsTeamA.textContent = `Cards: ${state.team_cards_collected['Team A']}`;
    tricksTeamB.textContent = `Tricks: ${state.team_tricks_won['Team B']}`;
    cardsTeamB.textContent = `Cards: ${state.team_cards_collected['Team B']}`;

    if (mobileScorePill && state.team_tricks_won) {
        const tA = state.team_tricks_won['Team A'] ?? 0;
        const tB = state.team_tricks_won['Team B'] ?? 0;
        mobileScorePill.textContent = `A:${tA} | B:${tB}`;
    }

    if (titleTeamA && state.player_names) {
        const p1 = state.player_names['P1'] || 'P1';
        const p3 = state.player_names['P3'] || 'P3';
        titleTeamA.textContent = `Team A (${p1} + ${p3})`;
    }
    if (titleTeamB && state.player_names) {
        const p2 = state.player_names['P2'] || 'P2';
        const p4 = state.player_names['P4'] || 'P4';
        titleTeamB.textContent = `Team B (${p2} + ${p4})`;
    }

    ladderDealer.textContent = `${state.player_names[state.dealer_id] || state.dealer_id} (${state.dealer_team})`;
    ladderScore.textContent = `${state.dealer_score} / 52`;
    const pct = Math.min(100, Math.max(0, (state.dealer_score / 52) * 100));
    ladderFill.style.width = `${pct}%`;

    // Logs
    logBox.innerHTML = "";
    state.logs.forEach(log => {
        const p = document.createElement("div");
        p.textContent = log;
        logBox.appendChild(p);
    });
    logBox.scrollTop = logBox.scrollHeight;

    // Automatic AI Turn Trigger (when current_turn_player is AI and deal animation finished)
    if (!isDealingAnimationActive) {
        scheduleAutoAiTurn(state);
    }
}

function renderTableTrickCards(currentTrick, lastTrick, lastWinner, lastWinningCard, requiredCards = 4) {
    const activeTrick = (currentTrick && currentTrick.length > 0) ? currentTrick : (lastTrick || []);
    [trickP1, trickP2, trickP3, trickP4].forEach(el => {
        el.innerHTML = "";
        el.classList.remove("trick-winner-card", "trick-non-winner-card");
    });

    const mySeat = myPlayerSeat || "P1";
    const rel = getRelativeSeats(mySeat);
    const slotMap = {
        [rel.south]: trickP1,
        [rel.west]: trickP2,
        [rel.north]: trickP3,
        [rel.east]: trickP4
    };

    const isTrickComplete = activeTrick.length === requiredCards;

    activeTrick.forEach(play => {
        const slotEl = slotMap[play.player_id];
        const cardCode = (typeof play.card === "string") ? play.card : (play.card && play.card.code ? play.card.code : play.card);
        if (slotEl && cardCode) {
            slotEl.appendChild(createCardSVG(cardCode));

            if (isTrickComplete) {
                const isWinner = (lastWinner && play.player_id === lastWinner) || 
                                 (lastWinningCard && cardCode === lastWinningCard);
                if (isWinner) {
                    slotEl.classList.add("trick-winner-card");
                    const badge = document.createElement("div");
                    badge.className = "trick-winner-badge";
                    badge.innerHTML = `<span class="crown-icon">👑</span> <strong>WINNER</strong>`;
                    slotEl.appendChild(badge);
                } else {
                    slotEl.classList.add("trick-non-winner-card");
                }
            }
        }
    });
}

function handleTrumpRevealNotification(state) {
    if (state.trump_revealed && !previousTrumpRevealed) {
        previousTrumpRevealed = true;
        sfx.playHukumDikhao();

        const openerId = state.trump_opener_id;
        const openerName = state.trump_opener_name || (state.player_names && openerId ? state.player_names[openerId] : openerId) || "Player";
        const cleanName = openerName.split('(')[0].trim();

        showTrumpRevealToast(state, cleanName);

        // Highlight caller's seat for 4.5 seconds
        if (openerId) {
            const seatEl = document.getElementById(`seat-${openerId}`);
            if (seatEl) {
                seatEl.classList.add("seat-caller-highlight");
                setTimeout(() => seatEl.classList.remove("seat-caller-highlight"), 4500);
            }
        }
    } else if (!state.trump_revealed) {
        previousTrumpRevealed = false;
    }
}

function showTrumpRevealToast(state, openerName) {
    if (!trumpRevealToast || !trumpRevealCaller) return;

    const demandPhrase = typeof t === "function" ? t("demandedTrumpShow") : "demanded Trump Show!";
    trumpRevealCaller.textContent = `${openerName} ${demandPhrase}`;

    const suitNames = { 
        'S': `♠ ${typeof t === "function" ? t("suitSpades") : 'SPADES'}`, 
        'H': `♥ ${typeof t === "function" ? t("suitHearts") : 'HEARTS'}`, 
        'D': `♦ ${typeof t === "function" ? t("suitDiamonds") : 'DIAMONDS'}`, 
        'C': `♣ ${typeof t === "function" ? t("suitClubs") : 'CLUBS'}` 
    };
    const suitColors = { 'S': '#ffffff', 'H': '#ef4444', 'D': '#ef4444', 'C': '#ffffff' };
    const suit = state.trump_suit || (state.hidden_trump_card && state.hidden_trump_card.suit);
    if (suit && trumpRevealSuitVal) {
        trumpRevealSuitVal.textContent = suitNames[suit] || suit;
        trumpRevealSuitVal.style.color = suitColors[suit] || '#f59e0b';
    }

    if (trumpRevealCardBox) {
        trumpRevealCardBox.innerHTML = "";
        if (state.hidden_trump_card) {
            trumpRevealCardBox.appendChild(createCardSVG(state.hidden_trump_card.code));
        } else if (suit) {
            trumpRevealCardBox.innerHTML = `<span style="font-size:32px; color:${suitColors[suit]}; display:flex; justify-content:center; align-items:center; height:100%;">${suitNames[suit]?.slice(0, 1) || ''}</span>`;
        }
    }

    trumpRevealToast.classList.remove("hidden");

    if (trumpRevealToastTimeout) clearTimeout(trumpRevealToastTimeout);
    trumpRevealToastTimeout = setTimeout(() => {
        trumpRevealToast.classList.add("hidden");
    }, 4500);
}

function renderSouthHand(cards, ledSuit, isMyTurn, isTrumpSelectStage, mustPlayTrumpSuit = null) {
    handP1.innerHTML = "";
    if (!cards || cards.length === 0) return;

    // Dynamic responsive overlap calculation for mobile devices
    const isMobile = window.innerWidth <= 768;
    let customMarginLeft = null;

    if (isMobile && cards.length > 1) {
        // Table usable width on mobile (screen minus table padding & borders)
        const availWidth = Math.min(window.innerWidth - 16, 480);
        // Effective card width on mobile (matches clamp(40px, 10.5vw, 56px))
        const cardWidth = Math.min(Math.max(40, Math.floor(window.innerWidth * 0.105)), 56);
        
        // Target step so cards span comfortably without exceeding availWidth
        const neededStep = (availWidth - cardWidth - 8) / (cards.length - 1);
        const maxStep = Math.min(cardWidth * 0.75, 34); // comfortable fan step when hand is smaller
        const actualStep = Math.min(maxStep, Math.max(14, neededStep));
        const overlap = cardWidth - actualStep;
        customMarginLeft = -Math.round(overlap);
    }

    cards.forEach((card, index) => {
        const wrapper = document.createElement("div");
        wrapper.className = "card-wrapper";
        wrapper.style.zIndex = index + 1;

        wrapper.addEventListener("mouseenter", () => {
            wrapper.style.zIndex = "100";
        });
        wrapper.addEventListener("mouseleave", () => {
            wrapper.style.zIndex = index + 1;
        });
        wrapper.addEventListener("touchstart", () => {
            handP1.querySelectorAll(".card-wrapper").forEach((w, i) => {
                w.style.zIndex = i + 1;
            });
            wrapper.style.zIndex = "100";
        }, { passive: true });

        if (index > 0 && customMarginLeft !== null) {
            wrapper.style.setProperty("margin-left", `${customMarginLeft}px`, "important");
        }

        if (isTrumpSelectStage) {
            wrapper.classList.add("legal-card");
            wrapper.appendChild(createCardSVG(card.code));
            wrapper.addEventListener("click", () => handleSelectHiddenTrumpCard(card.code));
        } else {
            const isSameSuit = ledSuit ? (card.suit === ledSuit) : true;
            const hasSameSuitCards = ledSuit ? cards.some(c => c.suit === ledSuit) : false;
            
            let isLegal = true;
            if (isMyTurn && ledSuit && hasSameSuitCards && !isSameSuit) {
                isLegal = false;
            }

            // Trump play obligation: If player asked/opened trump and has no led suit, must play trump if held!
            if (isMyTurn && mustPlayTrumpSuit && !hasSameSuitCards) {
                const hasTrumpCards = cards.some(c => c.suit === mustPlayTrumpSuit);
                if (hasTrumpCards && card.suit !== mustPlayTrumpSuit) {
                    isLegal = false;
                }
            }

            wrapper.classList.add(isLegal ? "legal-card" : "illegal-card");
            wrapper.appendChild(createCardSVG(card.code));

            if (isMyTurn) {
                if (isLegal) {
                    wrapper.addEventListener("click", () => handleCardClick(card.code));
                } else {
                    wrapper.addEventListener("click", () => {
                        if (mustPlayTrumpSuit && !hasSameSuitCards && cards.some(c => c.suit === mustPlayTrumpSuit)) {
                            showHubToast(typeof t === "function" ? t("mustPlayTrumpToast") : "You asked for Trump! Must play a Trump card from your hand.");
                        } else if (ledSuit && hasSameSuitCards && card.suit !== ledSuit) {
                            showHubToast(typeof t === "function" ? t("mustFollowSuit") : "Must follow led suit!");
                        }
                    });
                }
            }
        }

        handP1.appendChild(wrapper);
    });
}

let announcementTimer = null;
function showAnnouncement(title, sub) {
    if (!gameAnnouncementBanner) return;
    if (announcementTitle) announcementTitle.textContent = title;
    if (announcementSub) announcementSub.textContent = sub;
    gameAnnouncementBanner.classList.remove("hidden");

    if (announcementTimer) clearTimeout(announcementTimer);
    announcementTimer = setTimeout(() => {
        if (gameAnnouncementBanner) gameAnnouncementBanner.classList.add("hidden");
    }, 5500);
}

function scheduleAutoAiTurn(state) {
    if (autoAiTimeout) {
        clearTimeout(autoAiTimeout);
        autoAiTimeout = null;
    }

    if (isBotPlayPaused) return;
    if (!state || state.round_complete || state.deal_stage === "SELECT_TRUMP" || isDealingAnimationActive) return;

    const currentP = state.current_turn_player;
    if (state.player_types && state.player_types[currentP] === 'ai') {
        const isTrickCompleted = (!state.current_trick || state.current_trick.length === 0) && (state.last_completed_trick && state.last_completed_trick.length === 4);
        const delay = isTrickCompleted ? Math.max(autoPlaySpeed, 1200) : autoPlaySpeed;
        autoAiTimeout = setTimeout(() => {
            triggerAiStep();
        }, delay);
    }
}

async function handleSelectHiddenTrumpCard(cardCode) {
    try {
        const res = await fetch(`${API_BASE}/api/select_hidden_trump`, {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({ card_code: cardCode, game_id: currentGameId })
        });
        if (res.ok) {
            sfx.playCard();
            const data = await res.json();
            
            // Continue deal animation: deal next 5 cards then final 3 cards
            isDealingAnimationActive = true;
            displayedCardBatch = 10;
            sfx.playDeal();
            renderState(data);

            await new Promise(r => setTimeout(r, 800));
            displayedCardBatch = 13;
            sfx.playDeal();
            isDealingAnimationActive = false;
            renderState(data);
        }
    } catch (e) {
        console.error("Select hidden trump error:", e);
    }
}

async function handleSelectRuntimeTrump(suitChar) {
    try {
        const res = await fetch(`${API_BASE}/api/set_runtime_trump`, {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({ suit: suitChar, game_id: currentGameId })
        });
        if (res.ok) {
            modalTrumpSelect.classList.add("hidden");
            const data = await res.json();
            renderState(data);
        }
    } catch (e) {
        console.error("Runtime trump error:", e);
    }
}

async function handleBid(contract) {
    try {
        const myName = myPlayerName || "Sagan";
        if (contract === "Double Tera") {
            sfx.playDoubleTera(myName);
        } else if (contract === "Tera") {
            sfx.playTera(myName);
        }
        lastAnnouncedContract = `${myName} declared ${contract.toUpperCase()}!`;

        await fetch(`${API_BASE}/api/declare`, {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({ player_id: myPlayerSeat || "P1", contract: contract, game_id: currentGameId })
        });

        const res = await fetch(`${API_BASE}/api/resolve_bidding?game_id=${currentGameId}`, { method: "POST" });
        const data = await res.json();
        renderState(data);
    } catch (e) {
        console.error("Bidding error:", e);
    }
}

async function handleNextDeal() {
    try {
        lastAnnouncedContract = null;
        if (modalDealComplete) modalDealComplete.classList.add("hidden");
        if (currentGameType === "jhuthaniya") {
            const modalJh = document.getElementById("modal-jhuthaniya-summary");
            if (modalJh) modalJh.classList.add("hidden");
            const res = await fetch(`${API_BASE}/api/jhuthaniya/new-game`, {
                method: "POST",
                headers: { "Content-Type": "application/json" },
                body: JSON.stringify({ game_id: currentGameId })
            });
            if (res.ok) {
                const data = await res.json();
                renderJhuthaniyaState(data.state || data);
                scheduleJhuthaniyaBotTurn(data.state || data);
            }
            return;
        }
        const res = await fetch(`${API_BASE}/api/next_deal?game_id=${currentGameId}`, { method: "POST" });
        if (res.ok) {
            const data = await res.json();
            startStepByStepDealAnimation(data);
        }
    } catch (e) {
        console.error("Next deal error:", e);
    }
}

async function handleRestartDeal() {
    try {
        lastAnnouncedContract = null;
        if (modalDealComplete) modalDealComplete.classList.add("hidden");
        const res = await fetch(`${API_BASE}/api/restart_deal?game_id=${currentGameId}`, { method: "POST" });
        if (res.ok) {
            const data = await res.json();
            startStepByStepDealAnimation(data);
        }
    } catch (e) {
        console.error("Restart deal error:", e);
    }
}

// ===================== SEAT SETUP: 2-STEP FLOW =====================

let currentHumanCount = 1;  // how many humans the host selected
const SEAT_IDS = ['P2', 'P3', 'P4'];

function setHumanCount(count) {
    currentHumanCount = count;

    // Highlight the chosen count button
    [1, 2, 3, 4].forEach(n => {
        const btn = document.getElementById(`hcount-${n}`);
        if (btn) btn.classList.toggle('active', n === count);
    });

    const pickerBox = document.getElementById('seat-picker-box');
    const namesBox  = document.getElementById('seat-names-box');

    if (count === 1) {
        // All bots
        if (pickerBox) pickerBox.classList.add('hidden');
        if (namesBox)  namesBox.classList.add('hidden');
        SEAT_IDS.forEach(s => {
            _setSeatHidden(s, 'ai');
            const btn = document.getElementById(`spick-${s}`);
            if (btn) btn.classList.remove('active');
        });
    } else if (count === 4) {
        // All human
        if (pickerBox) pickerBox.classList.add('hidden');
        if (namesBox)  namesBox.classList.remove('hidden');
        SEAT_IDS.forEach(s => {
            _setSeatHidden(s, 'human');
            _showNameRow(s, true);
            const btn = document.getElementById(`spick-${s}`);
            if (btn) btn.classList.add('active');
        });
    } else if (count === 2) {
        // 2 humans: host + 1 friend (show picker, default to P3 Partner)
        if (pickerBox) pickerBox.classList.remove('hidden');
        let currentHuman = SEAT_IDS.find(s => {
            const el = document.getElementById(`select-type-${s.toLowerCase()}`);
            return el && el.value === 'human';
        }) || 'P3';

        SEAT_IDS.forEach(s => {
            const isTarget = (s === currentHuman);
            _setSeatHidden(s, isTarget ? 'human' : 'ai');
            const btn = document.getElementById(`spick-${s}`);
            if (btn) btn.classList.toggle('active', isTarget);
        });
        _refreshNameBox([currentHuman]);
    } else if (count === 3) {
        // 3 humans: host + 2 friends (show picker, default to P3 and P2)
        if (pickerBox) pickerBox.classList.remove('hidden');
        let humanSeats = SEAT_IDS.filter(s => {
            const el = document.getElementById(`select-type-${s.toLowerCase()}`);
            return el && el.value === 'human';
        });
        if (humanSeats.length !== 2) {
            humanSeats = ['P3', 'P2'];
        }
        SEAT_IDS.forEach(s => {
            const isTarget = humanSeats.includes(s);
            _setSeatHidden(s, isTarget ? 'human' : 'ai');
            const btn = document.getElementById(`spick-${s}`);
            if (btn) btn.classList.toggle('active', isTarget);
        });
        _refreshNameBox(humanSeats);
    }

    updateTrumpHiderOptionLabels();
    syncHostRoomToBackend();
}

function toggleSeatPick(seat) {
    const maxHuman = currentHumanCount - 1; // 1 for count=2, 2 for count=3
    if (maxHuman <= 0) return;

    const el = document.getElementById(`select-type-${seat.toLowerCase()}`);
    if (!el) return;
    const isCurrentlyHuman = el.value === 'human';

    if (maxHuman === 1) {
        // Exactly 1 seat chosen: clicking any seat selects it and deselects all others
        SEAT_IDS.forEach(s => {
            const isTarget = (s === seat);
            _setSeatHidden(s, isTarget ? 'human' : 'ai');
            const btn = document.getElementById(`spick-${s}`);
            if (btn) btn.classList.toggle('active', isTarget);
        });
    } else if (maxHuman === 2) {
        // 2 seats chosen: if clicking an AI seat, swap it with one of the human seats
        if (!isCurrentlyHuman) {
            const currentHumanSeats = SEAT_IDS.filter(s => {
                const e = document.getElementById(`select-type-${s.toLowerCase()}`);
                return e && e.value === 'human';
            });
            if (currentHumanSeats.length >= 2) {
                const toRemove = currentHumanSeats[0];
                _setSeatHidden(toRemove, 'ai');
                const oldBtn = document.getElementById(`spick-${toRemove}`);
                if (oldBtn) oldBtn.classList.remove('active');
            }
            _setSeatHidden(seat, 'human');
            const btn = document.getElementById(`spick-${seat}`);
            if (btn) btn.classList.add('active');
        }
    }

    const humanSeats = SEAT_IDS.filter(s => {
        const e = document.getElementById(`select-type-${s.toLowerCase()}`);
        return e && e.value === 'human';
    });
    _refreshNameBox(humanSeats);
    updateTrumpHiderOptionLabels();
    syncHostRoomToBackend();
}

function _setSeatHidden(seat, type) {
    const el = document.getElementById(`select-type-${seat.toLowerCase()}`);
    if (el) el.value = type;
}

function _showNameRow(seat, show) {
    const row = document.getElementById(`name-row-${seat}`);
    if (row) row.classList.toggle('hidden', !show);
}

function _refreshNameBox(humanSeats) {
    const namesBox = document.getElementById('seat-names-box');
    if (!namesBox) return;
    if (!humanSeats || humanSeats.length === 0) {
        namesBox.classList.add('hidden');
        return;
    }
    namesBox.classList.remove('hidden');
    SEAT_IDS.forEach(s => _showNameRow(s, humanSeats.includes(s)));
}

function getSetupModeFromSeats() {
    const p2 = (document.getElementById('select-type-p2') || {}).value || 'ai';
    const p3 = (document.getElementById('select-type-p3') || {}).value || 'ai';
    const p4 = (document.getElementById('select-type-p4') || {}).value || 'ai';
    const humanCount = [p2, p3, p4].filter(t => t === 'human').length;
    if (humanCount === 0) return '1-3 com';
    if (humanCount === 1) return '2-2 com';
    if (humanCount === 2) return '3-1 com';
    return '4-0 com';
}

window.setHumanCount = setHumanCount;
window.toggleSeatPick = toggleSeatPick;
// keep old names as no-ops so no reference errors if called
window.setSeatType = () => {};
window.applyPreset = (p) => {};

async function syncHostRoomToBackend() {
    if (activeView !== "home" || (myPlayerSeat && myPlayerSeat !== "P1")) return;
    const hostName = (inputYourName && inputYourName.value.trim()) || "Sagan";
    const gameName = (inputGameName && inputGameName.value.trim()) || `game${gameCounter}`;
    const setupMode = getSetupModeFromSeats();
    const trumpHider = (selectTrumpHider && selectTrumpHider.value) || "P1";

    const p2Type = (document.getElementById('select-type-p2') || {}).value || 'ai';
    const p3Type = (document.getElementById('select-type-p3') || {}).value || 'ai';
    const p4Type = (document.getElementById('select-type-p4') || {}).value || 'ai';

    const p2Name = (inputNameP2 && inputNameP2.value.trim()) || "";
    const p3Name = (inputNameP3 && inputNameP3.value.trim()) || "";
    const p4Name = (inputNameP4 && inputNameP4.value.trim()) || "";

    try {
        await fetch(`${API_BASE}/api/room/create`, {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({
                game_id: currentRoomId,
                host_name: hostName,
                game_name: gameName,
                setup_mode: setupMode,
                trump_hider: trumpHider,
                seats_config: { P2: p2Type, P3: p3Type, P4: p4Type },
                seat_names: { P2: p2Name, P3: p3Name, P4: p4Name }
            })
        });
    } catch (e) {
        // quiet background sync
    }
}

async function handleJoinGame() {
    const playerName = (inputYourName && inputYourName.value.trim()) || "Guest";
    const gameId = (inputJoinId && inputJoinId.value.trim().toUpperCase());

    if (!gameId) {
        if (joinStatusMsg) {
            joinStatusMsg.textContent = "⚠️ Please enter a valid Game ID / Room Code.";
            joinStatusMsg.className = "join-status-msg error";
        }
        return;
    }

    if (joinStatusMsg) {
        joinStatusMsg.textContent = "Connecting to room...";
        joinStatusMsg.className = "join-status-msg";
    }

    try {
        const res = await fetch(`${API_BASE}/api/room/join`, {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({
                game_id: gameId,
                player_name: playerName
            })
        });

        if (!res.ok) {
            const err = await res.json();
            if (joinStatusMsg) {
                joinStatusMsg.textContent = `❌ ${err.detail || "Failed to join room."}`;
                joinStatusMsg.className = "join-status-msg error";
            }
            return;
        }

        const data = await res.json();
        currentGameId = data.game_id;
        myPlayerSeat = data.seat_id; // Never default to P1 for a joining friend!
        myPlayerName = playerName;

        if (data.room && data.room.status === "playing") {
            if (joinStatusMsg) {
                joinStatusMsg.textContent = `✓ Joined Room ${currentGameId}! Assigned to ${myPlayerSeat || "your seat"}. Entering table...`;
                joinStatusMsg.className = "join-status-msg success";
            }
            setTimeout(async () => {
                switchView("table");
                await fetchState();
            }, 600);
        } else {
            // Room in lobby state — friend joined, wait for host to start
            const assignedSeat = data.seat_id;
            if (!assignedSeat) {
                if (joinStatusMsg) {
                    joinStatusMsg.textContent = `✓ You're in the lobby for Room ${currentGameId}! Waiting for host to start...`;
                    joinStatusMsg.className = "join-status-msg success";
                }
            } else {
                if (joinStatusMsg) {
                    joinStatusMsg.textContent = `✓ Joined Room ${currentGameId}! You are ${myPlayerName} (Seat ${assignedSeat}). Waiting for host to start...`;
                    joinStatusMsg.className = "join-status-msg success";
                }
            }
            // Poll until host clicks Start Match
            const joinPollTimer = setInterval(async () => {
                try {
                    const pollRes = await fetch(`${API_BASE}/api/room/status?game_id=${currentGameId}`);
                    if (!pollRes.ok) return;
                    const pollData = await pollRes.json();
                    if (pollData.room) {
                        if (!myPlayerSeat) {
                            for (const [sId, sInfo] of Object.entries(pollData.room.seats || {})) {
                                if (sId !== "P1" && sInfo.type === "human" && sInfo.name && sInfo.name.toLowerCase() === myPlayerName.toLowerCase()) {
                                    myPlayerSeat = sId;
                                    break;
                                }
                            }
                        }
                        if (pollData.room.status === "playing") {
                            clearInterval(joinPollTimer);
                            if (joinStatusMsg) joinStatusMsg.textContent = "🎮 Game started! Entering table...";
                            setTimeout(async () => {
                                switchView("table");
                                if (pollData.game_state) {
                                    startStepByStepDealAnimation(pollData.game_state);
                                } else {
                                    await fetchState();
                                }
                            }, 500);
                        }
                    }
                } catch (e) { /* ignore */ }
            }, 1000);
        }
    } catch (e) {
        console.error("Join room error:", e);
        if (joinStatusMsg) {
            joinStatusMsg.textContent = "❌ Connection error. Check server status.";
            joinStatusMsg.className = "join-status-msg error";
        }
    }
}

let syncPollInterval = null;

function startSyncPolling() {
    if (syncPollInterval) clearInterval(syncPollInterval);
    syncPollInterval = setInterval(async () => {
        if (activeView === "table") {
            if (typeof currentGameType !== "undefined" && currentGameType === "tikdi") {
                try {
                    const res = await fetch(`${API_BASE}/api/tikdi/state?game_id=${currentGameId}`);
                    if (res.ok) {
                        const data = await res.json();
                        const stateChanged = !gameState ||
                            gameState.current_turn !== data.current_turn ||
                            gameState.phase !== data.phase ||
                            gameState.trick_number !== data.trick_number ||
                            gameState.round_number !== data.round_number ||
                            (gameState.current_trick && data.current_trick && gameState.current_trick.length !== data.current_trick.length);
                        if (stateChanged) {
                            renderTikdiState(data);
                        } else if (!tikdiBotTimeout && !isBotPlayPaused && data.phase !== "ROUND_OVER") {
                            scheduleTikdiBotTurn(data);
                        }
                    }
                } catch (e) {}
            } else if (typeof currentGameType !== "undefined" && currentGameType === "jhuthaniya") {
                try {
                    const res = await fetch(`${API_BASE}/api/jhuthaniya/state?game_id=${currentGameId}&seat=P1`);
                    if (res.ok) {
                        const data = await res.json();
                        const st = data.state || data;
                        const stateChanged = !jhuthaniyaCurrentState ||
                            jhuthaniyaCurrentState.current_turn !== st.current_turn ||
                            jhuthaniyaCurrentState.phase !== st.phase ||
                            jhuthaniyaCurrentState.center_pot_size !== st.center_pot_size ||
                            jhuthaniyaCurrentState.deal_number !== st.deal_number ||
                            (st.challenge && (!jhuthaniyaCurrentState.challenge || Object.keys(st.challenge.challenge_decisions || {}).length !== Object.keys(jhuthaniyaCurrentState.challenge.challenge_decisions || {}).length));
                        if (stateChanged) {
                            renderJhuthaniyaState(st);
                        } else if (!jhuthaniyaBotTimeout && st.phase !== "ROUND_OVER") {
                            scheduleJhuthaniyaBotTurn(st);
                        }
                    }
                } catch (e) {}
            } else if (typeof currentGameType !== "undefined" && currentGameType === "bindicoat") {
                try {
                    const res = await fetch(`${API_BASE}/api/bindi-coat/state?game_id=${currentGameId}&seat=P1`);
                    if (res.ok) {
                        const data = await res.json();
                        const st = data.state || data;
                        renderBindiCoatState(st);
                    }
                } catch (e) {}
            } else if (!isDealingAnimationActive) {
                try {
                    const res = await fetch(`${API_BASE}/api/state?game_id=${currentGameId}`);
                    if (res.ok) {
                        const data = await res.json();
                        const stateChanged = !gameState ||
                            gameState.current_turn_player !== data.current_turn_player ||
                            gameState.deal_stage !== data.deal_stage ||
                            gameState.trump_revealed !== data.trump_revealed ||
                            gameState.trick_number !== data.trick_number ||
                            gameState.round_number !== data.round_number ||
                            (gameState.current_trick && data.current_trick && gameState.current_trick.length !== data.current_trick.length);

                        if (stateChanged) {
                            renderState(data);
                        } else if (data.player_types && data.player_types[data.current_turn_player] === 'ai' && !autoAiTimeout && !isBotPlayPaused && !data.round_complete && data.deal_stage !== "SELECT_TRUMP") {
                            scheduleAutoAiTurn(data);
                        }
                    }
                } catch (e) {}
            }
        } else if (activeView === "home" && currentGameId) {
            try {
                const res = await fetch(`${API_BASE}/api/room/status?game_id=${currentGameId}`);
                if (res.ok) {
                    const data = await res.json();
                    if (myPlayerSeat && myPlayerSeat !== "P1") {
                        // Guest waiting in lobby
                        if (data.room && data.room.status === "playing" && activeView !== "table") {
                            switchView("table");
                            if (data.game_state) {
                                startStepByStepDealAnimation(data.game_state);
                            } else {
                                await fetchState();
                            }
                        }
                    } else if (data.room && data.room.seats) {
                        // Host view: update joined players in lobby chips and inputs
                        updateLobbyWaitingChips(data.room);
                    }
                }
            } catch (e) {}
        }
    }, 1000);
}

function updateLobbyWaitingChips(room) {
    const box = document.getElementById("lobby-waiting-box");
    const chips = document.getElementById("waiting-players-chips");
    if (!box || !chips || !room || !room.seats) return;

    const joinedHumans = Object.values(room.seats).filter(s => s.type === "human" && s.seat_id !== "P1" && s.connected
        && s.name && !s.name.includes("Waiting"));
    if (joinedHumans.length > 0) {
        box.classList.remove("hidden");
        chips.innerHTML = joinedHumans.map(s => `<span class="waiting-chip">✓ ${s.position} (${s.seat_id}): <strong>${s.name}</strong></span>`).join(" ");
    } else {
        box.classList.add("hidden");
    }

    // Update each seat's inputs to reflect joined friends
    const seatMap = [
        { id: "P2", nameEl: inputNameP2, typeEl: selectTypeP2 },
        { id: "P3", nameEl: inputNameP3, typeEl: selectTypeP3 },
        { id: "P4", nameEl: inputNameP4, typeEl: selectTypeP4 },
    ];
    for (const { id, nameEl, typeEl } of seatMap) {
        const seat = room.seats[id];
        if (!seat) continue;
        const isRealHumanFriend = seat.type === "human" && seat.connected
            && seat.name && !seat.name.includes("Waiting")
            && !seat.name.startsWith("G. ") && !seat.name.startsWith("BOT ") && !seat.name.startsWith("COM ");
        if (isRealHumanFriend) {
            if (nameEl) nameEl.value = seat.name;
            if (typeEl) typeEl.value = "human";
            const btn = document.getElementById(`spick-${id}`);
            if (btn) btn.classList.add('active');
            _showNameRow(id, true);
        }
    }
}

function updateTrumpHiderOptionLabels() {
    if (!selectTrumpHider) return;
    const p1 = (inputYourName && inputYourName.value.trim()) || "Sagan";
    const p2 = (inputNameP2 && inputNameP2.value.trim()) || "G. Dinesh";
    const p3 = (inputNameP3 && inputNameP3.value.trim()) || "G. Bhimaram";
    const p4 = (inputNameP4 && inputNameP4.value.trim()) || "G. Geeta";

    const optP1 = selectTrumpHider.querySelector("option[value='P1']");
    const optP2 = selectTrumpHider.querySelector("option[value='P2']");
    const optP3 = selectTrumpHider.querySelector("option[value='P3']");
    const optP4 = selectTrumpHider.querySelector("option[value='P4']");
    const optRand = selectTrumpHider.querySelector("option[value='random']");
    const lblHider = document.querySelector("label[for='select-trump-hider']");

    const isHi = (typeof getCurrentLanguage === "function" && getCurrentLanguage() === "hi");

    if (activeSelectedGame === "tikdi") {
        const grpPenalty = document.getElementById("group-tikdi-penalty-mode");
        if (grpPenalty) grpPenalty.classList.remove("hidden");
        if (lblHider) lblHider.textContent = isHi ? "🃏 पहले दौर में हुकुम कौन चुनेगा और पहली चाल चलेगा:" : "🃏 Who Chooses Trump (Quota 5) & Leads Deal 1:";
        if (optP1) optP1.textContent = isHi ? `Khiladi 1 (${p1} / South - Aap) — Hukum chunega (Quota 5) aur pehli chaal chalega` : `Player 1 (${p1} / South - You) — Chooses Trump (Quota 5) & leads Trick 1`;
        if (optP2) optP2.textContent = isHi ? `Khiladi 2 (${p2} / West) — Hukum chunega (Quota 5) aur pehli chaal chalega` : `Player 2 (${p2} / West) — Chooses Trump (Quota 5) & leads Trick 1`;
        if (optP3) optP3.textContent = isHi ? `Khiladi 3 (${p3} / North) — Hukum chunega (Quota 5) aur pehli chaal chalega` : `Player 3 (${p3} / North) — Chooses Trump (Quota 5) & leads Trick 1`;
        if (optP4) {
            optP4.style.display = "none";
            if (selectTrumpHider.value === "P4") selectTrumpHider.value = "P1";
        }
        if (optRand) optRand.textContent = isHi ? `🎲 Random (P1, P2 ya P3 chunenge)` : `🎲 Random (Player 1, 2, or 3 chosen randomly)`;
    } else if (activeSelectedGame === "bindicoat") {
        const grpPenalty = document.getElementById("group-tikdi-penalty-mode");
        if (grpPenalty) grpPenalty.classList.add("hidden");
        if (lblHider) lblHider.textContent = isHi ? "🃏 पहले दौर में कौन चाल चलेगा (हुकुम बंद रहेगा):" : "🃏 Who Leads First Deal (Bandh Hukum):";
        if (optP1) optP1.textContent = isHi ? `Khiladi 1 (${p1} / South - Aap) — Pehli chaal chalega` : `Player 1 (${p1} / South - You) — Leads Trick 1`;
        if (optP2) optP2.textContent = isHi ? `Khiladi 2 (${p2} / West) — Pehli chaal chalega` : `Player 2 (${p2} / West) — Leads Trick 1`;
        if (optP3) optP3.textContent = isHi ? `Khiladi 3 (${p3} / North) — Pehli chaal chalega` : `Player 3 (${p3} / North) — Leads Trick 1`;
        if (optP4) {
            optP4.style.display = "";
            optP4.textContent = isHi ? `Khiladi 4 (${p4} / East) — Pehli chaal chalega` : `Player 4 (${p4} / East) — Leads Trick 1`;
        }
        if (optRand) optRand.textContent = isHi ? `🎲 Random (Kisi bhi khiladi se shuru)` : `🎲 Random (Player 1, 2, 3, or 4 chosen randomly)`;
    } else {
        const grpPenalty = document.getElementById("group-tikdi-penalty-mode");
        if (grpPenalty) grpPenalty.classList.add("hidden");
        if (lblHider) lblHider.textContent = isHi ? "🃏 Pehli Baant Me Hukum Kaun Chhupayega:" : "🃏 Who Hides Trump & Leads First Deal:";
        if (optP1) optP1.textContent = isHi ? `Khiladi 1 (${p1} / South - Aap) — hukum chhupayega aur pehli chaali chalega` : `Player 1 (${p1} / South - You) — hides trump & leads Trick 1`;
        if (optP2) optP2.textContent = isHi ? `Khiladi 2 (${p2} / West) — hukum chhupayega aur pehli chaali chalega` : `Player 2 (${p2} / West) — hides trump & leads Trick 1`;
        if (optP3) optP3.textContent = isHi ? `Khiladi 3 (${p3} / North - Saathi) — hukum chhupayega aur pehli chaali chalega` : `Player 3 (${p3} / North - Partner) — hides trump & leads Trick 1`;
        if (optP4) {
            optP4.style.display = "";
            optP4.textContent = isHi ? `Khiladi 4 (${p4} / East) — hukum chhupayega aur pehli chaali chalega` : `Player 4 (${p4} / East) — hides trump & leads Trick 1`;
        }
        if (optRand) optRand.textContent = isHi ? `🎲 Random (Kisi bhi khiladi se shuru)` : `🎲 Random (Player 1, 2, 3, or 4 chosen randomly)`;
    }
}
window.updateTrumpHiderOptionLabels = updateTrumpHiderOptionLabels;

async function handleStartNewGame() {
    const hostName = (inputYourName && inputYourName.value.trim()) || "Sagan";
    const gameName = (inputGameName && inputGameName.value.trim()) || `game${gameCounter}`;
    const setupMode = getSetupModeFromSeats();
    const trumpHider = (selectTrumpHider && selectTrumpHider.value) || "P1";

    const p2Type = (document.getElementById('select-type-p2') || {}).value || 'ai';
    const p3Type = (document.getElementById('select-type-p3') || {}).value || 'ai';
    const p4Type = (document.getElementById('select-type-p4') || {}).value || 'ai';

    const p2Name = (inputNameP2 && inputNameP2.value.trim()) || "";
    const p3Name = (inputNameP3 && inputNameP3.value.trim()) || "";
    const p4Name = (inputNameP4 && inputNameP4.value.trim()) || "";

    try {
        // 1. Create or ensure Room exists with explicit seat configs
        const createRes = await fetch(`${API_BASE}/api/room/create`, {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({
                game_id: currentRoomId,
                host_name: hostName,
                game_name: gameName,
                setup_mode: setupMode,
                trump_hider: trumpHider,
                seats_config: { P2: p2Type, P3: p3Type, P4: p4Type },
                seat_names: { P2: p2Name, P3: p3Name, P4: p4Name }
            })
        });

        if (!createRes.ok) {
            const err = await createRes.json();
            alert(`Error creating room: ${err.detail}`);
            return;
        }

        const createData = await createRes.json();
        const gameId = createData.game_id || currentRoomId;
        currentGameId = gameId;
        currentRoomId = gameId;
        myPlayerSeat = "P1";
        myPlayerName = hostName;

        // 2. Assign customized seats ONLY if not already joined by a connected human friend
        const roomSeats = (createData.room && createData.room.seats) || {};

        const seatConfigs = [
            { id: "P2", input: inputNameP2, select: selectTypeP2, defaultName: "G. Dinesh" },
            { id: "P3", input: inputNameP3, select: selectTypeP3, defaultName: "G. Bhimaram" },
            { id: "P4", input: inputNameP4, select: selectTypeP4, defaultName: "G. Geeta" }
        ];

        for (const cfg of seatConfigs) {
            const existingSeat = roomSeats[cfg.id];
            const isJoinedHumanFriend = existingSeat && existingSeat.type === "human" && existingSeat.connected &&
                                       !existingSeat.name.includes("Waiting") && !existingSeat.name.startsWith("BOT ") && !existingSeat.name.startsWith("COM ") && !existingSeat.name.startsWith("G. ");

            if (!isJoinedHumanFriend) {
                const pType = (cfg.select && cfg.select.value) || "ai";
                const pName = (cfg.input && cfg.input.value.trim()) || (pType === "human" ? "Waiting for Friend (or BOT)" : cfg.defaultName);
                await fetch(`${API_BASE}/api/room/assign_seat`, {
                    method: "POST",
                    headers: { "Content-Type": "application/json" },
                    body: JSON.stringify({ game_id: gameId, seat_id: cfg.id, player_name: pName, player_type: pType })
                });
            }
        }

        // 3. Start Room Table
        const startRes = await fetch(`${API_BASE}/api/room/start`, {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({ game_id: gameId, trump_hider: trumpHider })
        });

        if (startRes.ok) {
            const startData = await startRes.json();
            switchView("table");
            if (gameNameBadge) {
                gameNameBadge.textContent = `🏷️ ${gameId} | ${gameName}`;
            }
            startStepByStepDealAnimation(startData.state);
        }
    } catch (e) {
        console.error("Failed to start new game:", e);
    }
}

function handleReturnToHomeNewGame() {
    stopAutoPlay();
    if (modalDealComplete) modalDealComplete.classList.add("hidden");
    gameCounter++;
    currentRoomId = String(Math.floor(1000 + Math.random() * 9000));
    if (displayRoomId) displayRoomId.textContent = currentRoomId;
    if (inputGameName) inputGameName.value = `game${gameCounter}`;
    if (joinStatusMsg) joinStatusMsg.textContent = "";
    setHumanCount(1); // reset seats to default on returning home
    switchView("home");
    window.scrollTo({ top: 0, behavior: "smooth" });
}

function showDealCompleteModal(state) {
    if (!modalDealComplete) return;

    const lastLog = state.logs && state.logs.length > 0 ? state.logs[state.logs.length - 1] : "";
    const secondLastLog = state.logs && state.logs.length > 1 ? state.logs[state.logs.length - 2] : "";

    const isTeraFail = lastLog.includes("Tera FAILED") || secondLastLog.includes("Tera FAILED") || lastLog.includes("TERA FAILED") || secondLastLog.includes("TERA FAILED");
    const isTeraSuccess = lastLog.includes("TERA SUCCEEDED") || secondLastLog.includes("TERA SUCCEEDED");

    let winnerText = "Deal Finished";
    let descText = "";

    const tricksA = (state.team_tricks_won && state.team_tricks_won['Team A']) || 0;
    const tricksB = (state.team_tricks_won && state.team_tricks_won['Team B']) || 0;

    if (state.mode in { "Tera": 1, "Double Tera": 1 }) {
        const declTeam = (state.declarer_id === 'P1' || state.declarer_id === 'P3') ? 'Team A' : 'Team B';
        const oppTeam = declTeam === 'Team A' ? 'Team B' : 'Team A';
        const declName = (state.player_names && state.player_names[state.declarer_id]) || state.declarer_id;
        if (isTeraFail) {
            winnerText = `💥 ${oppTeam} Wins the Deal!`;
            descText = `${state.mode} FAILED! ${oppTeam} captured a trick. Penalty applied.`;
            const trophyEl = document.getElementById("deal-complete-trophy");
            if (trophyEl) trophyEl.textContent = "💥";
        } else {
            if (state.mode === "Double Tera") {
                winnerText = `👑 ${declName} Wins Solo!`;
                descText = `${declName} conquered all 13 tricks solo in Double Tera! Opponents won 0 tricks.`;
            } else {
                winnerText = `👑 ${declTeam} Wins the Deal!`;
                descText = `${declTeam} (${state.mode}) successfully conquered all tricks!`;
            }
            const trophyEl = document.getElementById("deal-complete-trophy");
            if (trophyEl) trophyEl.textContent = "🏆";
        }
    } else {
        const dealerTeam = state.dealer_team;
        const leadTeam = state.lead_team;
        const dealerTricks = state.team_tricks_won ? state.team_tricks_won[dealerTeam] || 0 : 0;
        const leadTricks = state.team_tricks_won ? state.team_tricks_won[leadTeam] || 0 : 0;

        if (dealerTricks >= 5) {
            winnerText = `🏆 ${dealerTeam} Wins the Deal! (${dealerTricks} tricks - Dealer Target Met)`;
        } else if (leadTricks >= 9) {
            winnerText = `🏆 ${leadTeam} Wins the Deal! (${leadTricks} tricks - Lead Target Met)`;
        } else if (tricksA > tricksB) {
            winnerText = `🏆 Team A Wins the Deal! (${tricksA} tricks)`;
        } else if (tricksB > tricksA) {
            winnerText = `🏆 Team B Wins the Deal! (${tricksB} tricks)`;
        } else {
            winnerText = `🏆 Deal Complete!`;
        }
        descText = lastLog.replace("ROUND END: ", "");
        const trophyEl = document.getElementById("deal-complete-trophy");
        if (trophyEl) trophyEl.textContent = "🏆";
    }

    if (dealCompleteWinner) dealCompleteWinner.textContent = winnerText;
    if (dealCompleteDesc) dealCompleteDesc.textContent = descText;

    if (summaryValA) summaryValA.textContent = `${tricksA} Tricks (${(state.team_cards_collected && state.team_cards_collected['Team A']) || 0} cards)`;
    if (summaryValB) summaryValB.textContent = `${tricksB} Tricks (${(state.team_cards_collected && state.team_cards_collected['Team B']) || 0} cards)`;

    if (summaryLblA && state.player_names) {
        summaryLblA.textContent = `Team A (${state.player_names['P1'] || 'P1'})`;
        summaryLblB.textContent = `Team B (${state.player_names['P2'] || 'P2'})`;
    }

    if (dealCompleteLadder && state.player_names) {
        const dealerName = state.player_names[state.dealer_id] || state.dealer_id;
        dealCompleteLadder.textContent = `Dealer: ${dealerName} (${state.dealer_team}) | Score: ${state.dealer_score} / 52`;
    }

    modalDealComplete.classList.remove("hidden");
}

async function handleAskTrump() {
    if (!gameState) return;
    const mySeat = myPlayerSeat || "P1";
    if (gameState.mode in { "Tera": 1, "Double Tera": 1 }) {
        if (gameState.declarer_id === mySeat) {
            modalTrumpSelect.classList.remove("hidden");
        } else {
            try {
                // Non-declarer demands trump -> call /api/ask_trump
                const res = await fetch(`${API_BASE}/api/ask_trump`, {
                    method: "POST",
                    headers: { "Content-Type": "application/json" },
                    body: JSON.stringify({
                        player_id: mySeat,
                        game_id: currentGameId
                    })
                });
                if (res.ok) {
                    sfx.playHukumDikhao();
                    const data = await res.json();
                    renderState(data);
                    if (data.trump_suit) {
                        showHubToast(`🎺 Trump Revealed: ${data.trump_suit}! You must play Trump if held.`);
                    }
                } else {
                    const err = await res.json();
                    showHubToast(err.detail || "Cannot ask trump at this time.");
                }
            } catch (e) {
                console.error("Ask trump error:", e);
            }
        }
    }
}

async function handleCardClick(cardCode) {
    if (!gameState || gameState.current_turn_player !== (myPlayerSeat || 'P1') || isDealingAnimationActive) return;

    // Trump play obligation: if user asked for / opened trump, must play trump if held!
    const mySeat = myPlayerSeat || "P1";
    if (gameState.must_play_trump_player === mySeat && gameState.trump_revealed && gameState.trump_suit) {
        const myHand = (gameState.hands && gameState.hands[mySeat]) || [];
        const hasLedSuit = gameState.led_suit && myHand.some(c => c.suit === gameState.led_suit);
        if (!hasLedSuit) {
            const hasTrump = myHand.some(c => c.suit === gameState.trump_suit);
            const clickedCard = myHand.find(c => c.code === cardCode);
            if (hasTrump && clickedCard && clickedCard.suit !== gameState.trump_suit) {
                showHubToast(typeof t === "function" ? t("mustPlayTrumpToast") : "Must play a Trump card after asking for Trump!");
                return;
            }
        }
    }

    try {
        const res = await fetch(`${API_BASE}/api/play`, {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({
                player_id: myPlayerSeat || "P1",
                card_code: cardCode,
                demand_cut: isDemandCutMode,
                game_id: currentGameId
            })
        });

        if (!res.ok) {
            const err = await res.json();
            alert(err.detail || "Illegal card play.");
            return;
        }

        if (cardCode.startsWith("A")) {
            sfx.playAkka();
        } else {
            sfx.playCard();
        }
        isDemandCutMode = false;
        btnDemandCut.textContent = typeof t === "function" ? t("openTrumpBtn") : "🔓 Open Trump";
        btnDemandCut.classList.remove("btn-primary");
        btnDemandCut.classList.add("btn-warning");

        const data = await res.json();
        renderState(data);

    } catch (e) {
        console.error("Play error:", e);
    }
}

async function triggerAiStep() {
    if (!gameState || gameState.round_complete || isDealingAnimationActive) return;

    try {
        const res = await fetch(`${API_BASE}/api/ai_turn?game_id=${currentGameId}`, { method: "POST" });
        if (res.ok) {
            const data = await res.json();
            const lastPlay = (data.current_trick && data.current_trick.length > 0) ? 
                data.current_trick[data.current_trick.length - 1] : 
                (data.last_completed_trick && data.last_completed_trick.length > 0 ? data.last_completed_trick[data.last_completed_trick.length - 1] : null);
            
            if (lastPlay && lastPlay.card && lastPlay.card.code && lastPlay.card.code.startsWith('A')) {
                sfx.playAkka();
            } else {
                sfx.playCard();
            }
            renderState(data);
        } else {
            console.warn("AI turn response non-200:", res.status);
            setTimeout(fetchState, 800);
        }
    } catch (e) {
        console.error("AI turn error:", e);
        setTimeout(fetchState, 1200);
    }
}

function togglePauseBots() {
    isBotPlayPaused = !isBotPlayPaused;
    if (isBotPlayPaused) {
        if (autoAiTimeout) {
            clearTimeout(autoAiTimeout);
            autoAiTimeout = null;
        }
        if (btnPauseBots) {
            btnPauseBots.textContent = "▶ Resume Bots";
            btnPauseBots.classList.add("btn-warning");
        }
        if (botStatusText) botStatusText.textContent = "🤖 BOTs: Paused";
    } else {
        if (btnPauseBots) {
            btnPauseBots.textContent = "⏸ Pause Bots";
            btnPauseBots.classList.remove("btn-warning");
        }
        if (botStatusText) botStatusText.textContent = "🤖 BOTs: Auto-Playing";
        if (gameState) scheduleAutoAiTurn(gameState);
    }
}

async function saveConfigFromModal() {
    const matchType = selectMatchType.value;
    let playerTypes = {};

    if (matchType === "1h3ai") {
        playerTypes = { P1: "human", P2: "ai", P3: "ai", P4: "ai" };
    } else if (matchType === "2h2ai") {
        playerTypes = { P1: "human", P2: "ai", P3: "human", P4: "ai" };
    } else if (matchType === "4ai") {
        playerTypes = { P1: "ai", P2: "ai", P3: "ai", P4: "ai" };
    }

    try {
        const res = await fetch(`${API_BASE}/api/config`, {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({
                player_types: playerTypes,
                use_ollama: chkOllama.checked
            })
        });

        if (res.ok) {
            modalConfig.classList.add("hidden");
            const data = await res.json();
            renderState(data);
        }
    } catch (e) {
        console.error("Failed to save config:", e);
    }
}

// Automatically re-render state on window resize (e.g. mobile orientation change)
window.addEventListener("resize", () => {
    if (gameState) {
        if (typeof currentGameType !== "undefined" && currentGameType === "tikdi") {
            renderTikdiState(gameState);
        } else if (typeof renderState === "function") {
            renderState(gameState);
        }
    }
});

// =========================================================================
// ==================== TIKDI (3-2-5) GAME CONTROLLER ======================
// =========================================================================

var currentGameType = "bikkad"; // "bikkad" | "tikdi" | "jhuthaniya" | "bindicoat"
var activeSelectedGame = "bikkad";
var tikdiPendingReturnTarget = null;
var tikdiBotTimeout = null;

async function handleStartTikdiGame() {
    const hostName = (inputYourName && inputYourName.value.trim()) || "Sagan";
    const gameName = (inputGameName && inputGameName.value.trim()) || `Tikdi-${Math.floor(100 + Math.random() * 900)}`;

    const p2Type = (document.getElementById('select-type-p2') || {}).value || 'ai';
    const p3Type = (document.getElementById('select-type-p3') || {}).value || 'ai';

    const p2Name = (inputNameP2 && inputNameP2.value.trim()) || "G. Dinesh";
    const p3Name = (inputNameP3 && inputNameP3.value.trim()) || "G. Bhimaram";

    const selectHider = document.getElementById("select-trump-hider");
    const trumpChooser = (selectHider && selectHider.value) ? selectHider.value : "P1";

    const selectPenalty = document.getElementById("select-tikdi-penalty-mode");
    const penaltyMode = (selectPenalty && selectPenalty.value) ? selectPenalty.value : "card_swap";

    const payload = {
        game_id: currentRoomId,
        host_name: hostName,
        game_name: gameName,
        trump_chooser: trumpChooser,
        penalty_mode: penaltyMode,
        player_types: {
            "P1": "human",
            "P2": p2Type,
            "P3": p3Type
        },
        player_names: {
            "P1": hostName,
            "P2": p2Name,
            "P3": p3Name
        }
    };

    try {
        const res = await fetch(`${API_BASE}/api/tikdi/create-room`, {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify(payload)
        });

        if (!res.ok) {
            const err = await res.json();
            alert(`Error starting Tikdi: ${err.detail || "Server error"}`);
            return;
        }

        const data = await res.json();
        currentGameId = data.game_id;
        currentRoomId = data.game_id;
        myPlayerSeat = "P1";
        myPlayerName = hostName;
        currentGameType = "tikdi";

        switchView("table");
        const feltTable = document.querySelector(".felt-table");
        if (feltTable) feltTable.classList.add("tikdi-mode");
        if (gameNameBadge) {
            gameNameBadge.textContent = `🏷️ ${currentGameId} | Tikdi (3-2-5)`;
        }

        renderTikdiState(data.state);
    } catch (e) {
        console.error("Failed to start Tikdi match:", e);
    }
}

async function fetchTikdiState() {
    try {
        const res = await fetch(`${API_BASE}/api/tikdi/state?game_id=${currentGameId}`);
        if (!res.ok) return;
        const data = await res.json();
        renderTikdiState(data);
    } catch (e) {
        console.error("Failed to fetch Tikdi state:", e);
    }
}

function renderTikdiState(state) {
    gameState = state;
    window.gameState = state;
    currentGameType = "tikdi";

    const feltTable = document.querySelector(".felt-table");
    if (feltTable) feltTable.classList.add("tikdi-mode");

    // Hide Bikkad specific banners & controls
    if (trumpHideBanner) trumpHideBanner.classList.add("hidden");
    if (playerContractBar) playerContractBar.classList.add("hidden");
    if (btnDemandCut) btnDemandCut.classList.add("hidden");
    if (btnDeclareRuntimeTrump) btnDeclareRuntimeTrump.classList.add("hidden");
    if (btnAskTrump) btnAskTrump.classList.add("hidden");
    if (trumpSlotBox) trumpSlotBox.classList.remove("trump-revealed-active");
    if (trumpCallerBadge) trumpCallerBadge.classList.add("hidden");
    const potBox = document.getElementById("pot-accumulator-box");
    if (potBox) {
        potBox.classList.remove("hidden");
        potBox.style.display = "flex";
        const potTitle = potBox.querySelector(".pot-title");
        if (potTitle) potTitle.textContent = "ROUND PROGRESS";

        const potCardsVal = document.getElementById("pot-cards-val");
        const potTricksVal = document.getElementById("pot-tricks-val");
        const potStreak = document.getElementById("pot-streak");

        const potCardsLbl = potBox.querySelectorAll(".pot-lbl")[0];
        if (potCardsLbl) potCardsLbl.textContent = "Trick";
        if (potCardsVal) potCardsVal.textContent = `${state.current_trick_number || state.trick_number || 1}/10`;

        const totalWon = Object.values(state.tricks_won || {}).reduce((a, b) => a + b, 0);
        const potTricksLbl = potBox.querySelectorAll(".pot-lbl")[1];
        if (potTricksLbl) potTricksLbl.textContent = "Tricks Won";
        if (potTricksVal) potTricksVal.textContent = `${totalWon}/10`;

        if (potStreak) {
            potStreak.textContent = `Round #${state.round_number || state.round_num || 1} • 10 Tricks`;
        }
    }

    updateHeaderBrand("tikdi");

    // Header Badges
    if (gameNameBadge) {
        gameNameBadge.textContent = `🏷️ 3-2-5 · Round #${state.round_num || 1}`;
    }
    if (modeBadge) {
        modeBadge.textContent = state.trump_suit ? `Hukum: ${state.trump_suit}` : `Hukum: —`;
        modeBadge.classList.remove("hidden");
    }
    if (dealerBadge) {
        const dealerName = state.player_names[state.dealer_id] || state.dealer_id;
        dealerBadge.textContent = `🃏 Dealer: ${dealerName} (Quota: ${state.quotas[state.dealer_id]})`;
    }

    // Turn badge
    const isMyTurn = state.current_turn === (myPlayerSeat || "P1");
    if (state.phase === "TRUMP_SELECTION") {
        const chooserName = state.player_names[state.trump_chooser_id] || state.trump_chooser_id;
        turnBadge.textContent = state.trump_chooser_id === (myPlayerSeat || "P1") ?
            "🃏 Select Trump" :
            `⏳ ${chooserName} choosing Trump`;
        turnBadge.classList.remove("turn-badge-winner");
        if (btnNextDeal) btnNextDeal.classList.add("hidden");
    } else if (state.phase === "PENALTY_RESOLUTION") {
        turnBadge.textContent = "⚖️ Settling Penalties...";
        turnBadge.classList.remove("turn-badge-winner");
        if (btnNextDeal) btnNextDeal.classList.add("hidden");
    } else if (state.phase === "PENALTY_ADJUSTMENT") {
        turnBadge.textContent = "⚖️ Reviewing Quota Adjustments...";
        turnBadge.classList.remove("turn-badge-winner");
        if (btnNextDeal) btnNextDeal.classList.add("hidden");
    } else if (state.phase === "ROUND_OVER") {
        turnBadge.textContent = "🏆 Round Complete!";
        turnBadge.classList.add("turn-badge-winner");
        if (btnNextDeal) {
            btnNextDeal.classList.remove("hidden");
            btnNextDeal.classList.add("btn-highlight-pulse");
        }
    } else {
        const activeName = state.player_names[state.current_turn] || state.current_turn;
        turnBadge.textContent = isMyTurn ? "🟢 Your Turn" : `Turn: ${activeName}`;
        turnBadge.classList.remove("turn-badge-winner");
        if (btnNextDeal) {
            btnNextDeal.classList.add("hidden");
            btnNextDeal.classList.remove("btn-highlight-pulse");
        }
    }

    // Update Seats: P1 (South), P2 (West), P3 (North)
    const seats = [
        { id: "P1", domP: "P1", quota: state.quotas["P1"], won: state.tricks_won["P1"] || 0 },
        { id: "P2", domP: "P2", quota: state.quotas["P2"], won: state.tricks_won["P2"] || 0 },
        { id: "P3", domP: "P3", quota: state.quotas["P3"], won: state.tricks_won["P3"] || 0 }
    ];

    seats.forEach(s => {
        const seatEl = document.getElementById(`seat-${s.domP}`);
        const nameEl = document.getElementById(`name-${s.domP}`);
        const countEl = document.getElementById(`count-${s.domP}`);
        const roleEl = document.getElementById(`role-${s.domP}`);

        if (seatEl) {
            seatEl.classList.toggle("active-turn", s.id === state.current_turn && (state.phase === "TRICK_PLAY" || state.phase === "TRICK_PLAYING"));
            seatEl.classList.toggle("is-dealer", s.id === state.dealer_id);
        }

        if (nameEl) {
            let label = state.player_names[s.id] || s.id;
            if (s.id === (myPlayerSeat || "P1")) label += " (You)";
            nameEl.innerHTML = `${label} <span class="quota-badge">Quota: ${s.quota}</span> <span class="quota-won-badge">Won: ${s.won}</span>`;
        }

        if (countEl) {
            const count = (state.hands && state.hands[s.id]) ? state.hands[s.id].length : 0;
            countEl.textContent = `${count} cards`;
        }

        if (roleEl) {
            roleEl.innerHTML = "";
            if (s.id === state.dealer_id) {
                const b = document.createElement("span");
                b.className = "badge-role badge-dealer";
                b.textContent = "🎴 DEALER (Quota 2)";
                roleEl.appendChild(b);
            }
            if (s.id === state.trump_chooser_id) {
                const b = document.createElement("span");
                b.className = "badge-role badge-trump-setter";
                b.textContent = "👑 CHOOSER (Quota 5)";
                roleEl.appendChild(b);
            }
            if (s.id !== state.dealer_id && s.id !== state.trump_chooser_id) {
                const b = document.createElement("span");
                b.className = "badge-role badge-declarer";
                b.textContent = "🛡️ BYSTANDER (Quota 3)";
                roleEl.appendChild(b);
            }
        }
    });

    // Center Trump Card Slot (Top-Left Corner)
    const suitSymbols = { 'S': '♠', 'H': '♥', 'D': '♦', 'C': '♣' };
    const suitNames = { 'S': 'SPADES', 'H': 'HEARTS', 'D': 'DIAMONDS', 'C': 'CLUBS' };
    const isRedSuit = (state.trump_suit === 'H' || state.trump_suit === 'D');

    if (state.trump_suit) {
        trumpSlotLabel.innerHTML = `<span style="color:${isRedSuit ? '#fca5a5' : '#7dd3fc'}; font-size:10.5px; font-weight:800; letter-spacing:0.5px;">HUKUM: ${suitSymbols[state.trump_suit]} ${suitNames[state.trump_suit]}</span>`;
        trumpContainer.innerHTML = "";
        // Show the Ace / Ekka of the selected trump suit (e.g. AD, AH, AS, AC)
        const trumpCardEl = createCardSVG("A" + state.trump_suit);
        trumpContainer.appendChild(trumpCardEl);
        trumpContainer.title = `Hukum (Trump): ${suitNames[state.trump_suit]} (${suitSymbols[state.trump_suit]})`;
        trumpContainer.style.cursor = "default";
        if (trumpSlotBox) trumpSlotBox.classList.add("trump-revealed-active");
    } else {
        trumpSlotLabel.textContent = "CHOOSING TRUMP";
        trumpContainer.innerHTML = "";
        const backCard = createCardSVG("BACK");
        trumpContainer.appendChild(backCard);
        trumpContainer.title = "Choosing Trump...";
        trumpContainer.style.cursor = "default";
        if (trumpSlotBox) trumpSlotBox.classList.remove("trump-revealed-active");
    }

    // Center Trick Cards (3 Slots for Tikdi: South P1, West P2, North P3)
    renderTikdiTrickCards(state.current_trick, state.last_completed_trick, state.last_trick_winner, state.last_trick_winning_card);

    // South Player Hand Cards
    renderTikdiSouthHand(state);

    // Dedicated Tikdi (3-Player) Scoreboard
    const bikkadScorePanel = document.getElementById("bikkad-scoreboard-panel");
    const tikdiScorePanel = document.getElementById("tikdi-scoreboard-panel");
    const scoreboardTitle = document.getElementById("scoreboard-title");

    if (bikkadScorePanel) bikkadScorePanel.classList.add("hidden");
    if (tikdiScorePanel) tikdiScorePanel.classList.remove("hidden");
    if (scoreboardTitle) scoreboardTitle.textContent = "🏆 Tikdi (3-2-5) Scoreboard";

    const tikdiPlayersContainer = document.getElementById("tikdi-scoreboard-players");
    if (tikdiPlayersContainer) {
        const order = ["P1", "P2", "P3"];
        const currentDealerId = state.dealer || state.dealer_id || "P1";
        const currentChooserId = state.trump_chooser || state.trump_chooser_id || "P2";
        const currentBystanderId = state.bystander || state.bystander_id || "P3";

        let html = "";
        order.forEach(pid => {
            const rawName = (state.player_names && state.player_names[pid]) || pid;
            const isMe = (pid === (myPlayerSeat || "P1"));
            const isTurn = (state.current_turn === pid);
            const quota = (state.quotas && state.quotas[pid]) ?? (pid === currentChooserId ? 5 : (pid === currentDealerId ? 2 : 3));
            const won = (state.tricks_won && state.tricks_won[pid]) ?? 0;
            const net = won - quota;
            const cum = (state.cumulative_scores && state.cumulative_scores[pid]) ?? 0;

            let roleName = "Bystander";
            let roleEmoji = "🛡️";
            let roleClass = "role-bystander";
            if (pid === currentChooserId) {
                roleName = "Chooser";
                roleEmoji = "👑";
                roleClass = "role-chooser";
            } else if (pid === currentDealerId) {
                roleName = "Dealer";
                roleEmoji = "🃏";
                roleClass = "role-dealer";
            }

            const seatClass = `seat-${pid.toLowerCase()}`;
            const turnClass = isTurn ? "active-turn" : "";

            let netClass = "score-neutral";
            let netDisplay = "0";
            if (net > 0) {
                netClass = "score-positive";
                netDisplay = `+${net}`;
            } else if (net < 0) {
                netClass = "score-negative";
                netDisplay = `${net}`;
            }

            const cumDisplay = cum > 0 ? `+${cum}` : `${cum}`;

            html += `
                <div class="tikdi-player-card ${roleClass} ${turnClass}">
                    <div class="tikdi-card-header">
                        <div class="tikdi-player-identity">
                            <span class="tikdi-seat-badge ${seatClass}">${pid}</span>
                            <span class="tikdi-player-name" title="${rawName}">${rawName}</span>
                            ${isMe ? '<span class="you-tag">(You)</span>' : ''}
                        </div>
                        <span class="tikdi-role-pill ${roleClass}">${roleEmoji} ${roleName} [Q: ${quota}]</span>
                    </div>
                    <div class="tikdi-card-stats">
                        <div class="tikdi-stat-box">
                            <span class="tikdi-stat-label">Tricks</span>
                            <span class="tikdi-stat-val">${won} <span class="tikdi-stat-sub">/ ${quota}</span></span>
                        </div>
                        <div class="tikdi-stat-box">
                            <span class="tikdi-stat-label">Round Net</span>
                            <span class="tikdi-stat-val ${netClass}">${netDisplay}</span>
                        </div>
                        <div class="tikdi-stat-box">
                            <span class="tikdi-stat-label">Match Pts</span>
                            <span class="tikdi-stat-val">${cumDisplay}</span>
                        </div>
                    </div>
                </div>
            `;
        });
        tikdiPlayersContainer.innerHTML = html;
    }

    // Tikdi Status Box
    const stRound = document.getElementById("tikdi-status-round");
    const stDealer = document.getElementById("tikdi-status-dealer");
    const stTrump = document.getElementById("tikdi-status-trump");
    const stTricks = document.getElementById("tikdi-status-tricks");
    const stFill = document.getElementById("tikdi-ladder-fill");

    const currentDealerId = state.dealer || state.dealer_id || "P1";
    const dealerName = (state.player_names && state.player_names[currentDealerId]) || currentDealerId;
    if (stRound) stRound.textContent = `Round ${state.round_number || 1}`;
    if (stDealer) stDealer.textContent = `${dealerName} (${currentDealerId})`;

    if (stTrump) {
        if (state.trump_suit) {
            const suitMap = {
                "S": "♠ Spades",
                "H": "♥ Hearts",
                "D": "♦ Diamonds",
                "C": "♣ Clubs"
            };
            stTrump.textContent = suitMap[state.trump_suit] || state.trump_suit;
            stTrump.style.color = (state.trump_suit === "H" || state.trump_suit === "D") ? "#f87171" : "#60a5fa";
        } else {
            stTrump.textContent = "Selecting Trump...";
            stTrump.style.color = "#fcd34d";
        }
    }

    const completedTricks = Math.max(0, (state.trick_number || 1) - 1);
    if (stTricks) stTricks.textContent = `${completedTricks} / 10`;
    if (stFill) {
        const pct = Math.min(100, Math.max(0, (completedTricks / 10) * 100));
        stFill.style.width = `${pct}%`;
    }

    // Logs
    if (logBox) {
        logBox.innerHTML = "";
        (state.logs || []).forEach(log => {
            const p = document.createElement("div");
            p.textContent = log;
            logBox.appendChild(p);
        });
        logBox.scrollTop = logBox.scrollHeight;
    }

    // Modals
    if (state.phase === "TRUMP_SELECTION") {
        if (state.trump_chooser_id === (myPlayerSeat || "P1")) {
            if (modalTrumpSelect) {
                modalTrumpSelect.classList.remove("hidden");
                const tTitle = document.getElementById("trump-select-title");
                const tDesc = document.getElementById("trump-select-desc");
                const previewBox = document.getElementById("trump-hand-preview");
                if (tTitle) tTitle.textContent = "🎺 CHOOSE TRUMP SUIT";
                if (tDesc) tDesc.textContent = "You are the Trump Chooser! Inspect your first 5 cards below and declare the Trump Suit for this round:";

                if (previewBox) {
                    const cards = (state.first_5_cards && state.first_5_cards.length > 0) ?
                        state.first_5_cards :
                        ((state.hands && state.hands[myPlayerSeat || "P1"]) || []);

                    previewBox.innerHTML = "";
                    const cardsRow = document.createElement("div");
                    cardsRow.className = "trump-cards-row";
                    const suitCounts = { "S": 0, "H": 0, "D": 0, "C": 0 };
                    cards.forEach(c => {
                        const code = c.code || `${c.rank}${c.suit}`;
                        const suit = (c.suit && c.suit.length === 1) ? c.suit : code.slice(-1);
                        if (suitCounts[suit] !== undefined) suitCounts[suit]++;
                        const cardEl = createCardSVG(code);
                        cardEl.classList.add("trump-preview-card");
                        cardEl.title = code;
                        cardsRow.appendChild(cardEl);
                    });
                    previewBox.appendChild(cardsRow);

                    const summaryDiv = document.createElement("div");
                    summaryDiv.className = "trump-suits-summary";
                    summaryDiv.innerHTML = `
                        <span class="suit-count-pill spades">♠ Spades: ${suitCounts['S'] || 0}</span>
                        <span class="suit-count-pill hearts">♥ Hearts: ${suitCounts['H'] || 0}</span>
                        <span class="suit-count-pill diamonds">♦ Diamonds: ${suitCounts['D'] || 0}</span>
                        <span class="suit-count-pill clubs">♣ Clubs: ${suitCounts['C'] || 0}</span>
                    `;
                    previewBox.appendChild(summaryDiv);
                }
            }
        } else {
            if (modalTrumpSelect) modalTrumpSelect.classList.add("hidden");
        }
    } else {
        if (modalTrumpSelect) modalTrumpSelect.classList.add("hidden");
    }

    if (state.phase === "DEBT_SETTLEMENT_CHOICE") {
        renderTikdiDebtChoiceModal(state);
    } else {
        const dcModal = document.getElementById("modal-tikdi-debt-choice");
        if (dcModal) dcModal.classList.add("hidden");
    }

    if (state.phase === "PENALTY_RESOLUTION") {
        renderTikdiPenaltyModal(state);
    } else {
        const penModal = document.getElementById("modal-tikdi-penalty");
        if (penModal) penModal.classList.add("hidden");
    }

    if (state.phase === "PENALTY_ADJUSTMENT") {
        renderTikdiQuotaAdjustmentModal(state);
    } else {
        const qaModal = document.getElementById("modal-tikdi-quota-adjustment");
        if (qaModal) qaModal.classList.add("hidden");
    }

    if (state.phase === "ROUND_OVER") {
        showTikdiRoundOverModal(state);
    } else {
        if (modalDealComplete && modalDealComplete.classList.contains("tikdi-deal-modal")) {
            modalDealComplete.classList.add("hidden");
        }
    }

    // AI Bot Step Schedule
    scheduleTikdiBotTurn(state);
}

function renderTikdiTrickCards(currentTrick, lastTrick, lastWinner, lastWinningCard) {
    const activeTrick = (currentTrick && currentTrick.length > 0) ? currentTrick : (lastTrick || []);
    [trickP1, trickP2, trickP3, trickP4].forEach(el => {
        if (el) {
            el.innerHTML = "";
            el.classList.remove("trick-winner-card", "trick-non-winner-card");
        }
    });

    const slotMap = {
        "P1": trickP1,
        "P2": trickP2,
        "P3": trickP3
    };

    const isTrickComplete = activeTrick.length === 3;

    activeTrick.forEach(play => {
        const pid = play.player_id || play.player;
        const slotEl = slotMap[pid];
        const cardCode = (play.card && play.card.code) ? play.card.code : (typeof play.card === "string" ? play.card : "");
        if (slotEl && cardCode) {
            slotEl.appendChild(createCardSVG(cardCode));
            if (isTrickComplete) {
                const isWinner = (lastWinner && pid === lastWinner) ||
                                 (lastWinningCard && cardCode === lastWinningCard);
                if (isWinner) {
                    slotEl.classList.add("trick-winner-card");
                    const badge = document.createElement("div");
                    badge.className = "trick-winner-badge";
                    badge.innerHTML = `<span class="crown-icon">👑</span> <strong>WINNER</strong>`;
                    slotEl.appendChild(badge);
                } else {
                    slotEl.classList.add("trick-non-winner-card");
                }
            }
        }
    });
}

function renderTikdiSouthHand(state) {
    if (!handP1) return;
    handP1.innerHTML = "";
    const mySeat = myPlayerSeat || "P1";
    const cards = (state.hands && state.hands[mySeat]) || [];
    if (!cards || cards.length === 0) return;

    const isMyTurn = state.current_turn === mySeat && (state.phase === "TRICK_PLAY" || state.phase === "TRICK_PLAYING");
    const ledSuit = state.led_suit;
    const hasLedSuitCards = ledSuit ? cards.some(c => c.suit === ledSuit) : false;

    const isMobile = window.innerWidth <= 768;
    let customMarginLeft = null;
    if (isMobile && cards.length > 1) {
        const availWidth = Math.min(window.innerWidth - 16, 480);
        const cardWidth = Math.min(Math.max(40, Math.floor(window.innerWidth * 0.105)), 56);
        const neededStep = (availWidth - cardWidth - 8) / (cards.length - 1);
        const maxStep = Math.min(cardWidth * 0.75, 34);
        const actualStep = Math.min(maxStep, Math.max(14, neededStep));
        customMarginLeft = -Math.round(cardWidth - actualStep);
    }

    cards.forEach((card, index) => {
        const wrapper = document.createElement("div");
        wrapper.className = "card-wrapper";
        wrapper.style.zIndex = index + 1;

        if (index > 0 && customMarginLeft !== null) {
            wrapper.style.setProperty("margin-left", `${customMarginLeft}px`, "important");
        }

        let isLegal = true;
        if (isMyTurn && ledSuit && hasLedSuitCards && card.suit !== ledSuit) {
            isLegal = false;
        }

        wrapper.classList.add(isLegal && isMyTurn ? "legal-card" : "illegal-card");
        wrapper.appendChild(createCardSVG(card.code));

        if (isMyTurn && isLegal) {
            wrapper.addEventListener("click", () => handleTikdiCardClick(card.code));
        }

        handP1.appendChild(wrapper);
    });
}

let isTikdiPlayCardInFlight = false;

async function handleTikdiCardClick(cardCode) {
    if (isTikdiPlayCardInFlight) return;
    if (!gameState || !(gameState.phase === "TRICK_PLAY" || gameState.phase === "TRICK_PLAYING") || gameState.current_turn !== (myPlayerSeat || "P1")) return;

    isTikdiPlayCardInFlight = true;
    try {
        const res = await fetch(`${API_BASE}/api/tikdi/play-card`, {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({
                game_id: currentGameId,
                player_id: myPlayerSeat || "P1",
                card_code: cardCode
            })
        });

        if (!res.ok) {
            const err = await res.json().catch(() => ({ detail: "Illegal play" }));
            const msg = err.detail || "Illegal card play.";
            if (msg.toLowerCase().includes("turn")) {
                await fetchTikdiState();
            } else if (typeof showHubToast === "function") {
                showHubToast(msg);
            } else {
                console.warn(msg);
            }
            return;
        }

        if (cardCode.startsWith("A")) {
            sfx.playAkka();
        } else {
            sfx.playCard();
        }

        const data = await res.json();
        renderTikdiState(data.state || data);
    } catch (e) {
        console.error("Tikdi play card error:", e);
    } finally {
        isTikdiPlayCardInFlight = false;
    }
}

async function handleSelectTikdiTrump(suit) {
    try {
        const res = await fetch(`${API_BASE}/api/tikdi/select-trump`, {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({
                game_id: currentGameId,
                player_id: myPlayerSeat || "P1",
                suit: suit
            })
        });

        if (!res.ok) {
            const err = await res.json();
            alert(err.detail || "Failed to select trump.");
            return;
        }

        if (modalTrumpSelect) modalTrumpSelect.classList.add("hidden");
        const data = await res.json();
        renderTikdiState(data.state);
    } catch (e) {
        console.error("Tikdi select trump error:", e);
    }
}

function renderTikdiDebtChoiceModal(state) {
    const modal = document.getElementById("modal-tikdi-debt-choice");
    const titleEl = document.getElementById("debt-choice-title");
    const descEl = document.getElementById("debt-choice-desc");
    const infoText = document.getElementById("debt-choice-info-text");
    const actionsBox = document.getElementById("debt-choice-actions");
    const waitingBox = document.getElementById("debt-choice-waiting");
    const waitingMsg = document.getElementById("debt-choice-waiting-msg");
    const btnSwap = document.getElementById("btn-debt-choice-swap");
    const btnTricks = document.getElementById("btn-debt-choice-tricks");
    const swapDesc = document.getElementById("debt-choice-swap-desc");
    const tricksDesc = document.getElementById("debt-choice-tricks-desc");

    if (!modal) return;

    const currentDebt = state.current_debt_choice || (state.debt_choice_list && state.debt_choice_list[state.debt_choice_idx || 0]);
    if (!currentDebt) {
        modal.classList.add("hidden");
        return;
    }

    const debtor = currentDebt.debtor;
    const creditor = currentDebt.creditor;
    const count = currentDebt.count || 1;
    const debtorName = (state.player_names && state.player_names[debtor]) || currentDebt.debtor_name || debtor;
    const creditorName = (state.player_names && state.player_names[creditor]) || currentDebt.creditor_name || creditor;
    const isHumanDebtor = (debtor === (myPlayerSeat || "P1"));

    modal.classList.remove("hidden");

    if (infoText) {
        infoText.innerHTML = `<strong>${debtorName}</strong> fell short by <strong>${count} trick(s)</strong> and owes them to <strong>${creditorName}</strong>.`;
    }

    if (isHumanDebtor) {
        if (titleEl) titleEl.textContent = "⚖️ YOU OWE TRICKS — CHOOSE SETTLEMENT";
        if (descEl) descEl.textContent = `You took less tricks last round! Choose how you wish to settle ${count} trick(s) owed to ${creditorName}:`;
        if (swapDesc) swapDesc.textContent = `${creditorName} will pull ${count} card(s) blindly from your hand and return card(s).`;
        if (tricksDesc) tricksDesc.textContent = `I don't want Tash Khinchai! I will give ${count} extra trick(s) in contract (Your quota +${count}, ${creditorName} quota -${count}).`;

        if (actionsBox) actionsBox.classList.remove("hidden");
        if (waitingBox) waitingBox.classList.add("hidden");

        if (btnSwap) {
            btnSwap.onclick = () => sendTikdiDebtChoice("card_swap");
        }
        if (btnTricks) {
            btnTricks.onclick = () => sendTikdiDebtChoice("quota_adjustment");
        }
    } else {
        if (titleEl) titleEl.textContent = "⚖️ DEBT SETTLEMENT IN PROGRESS";
        if (descEl) descEl.textContent = `Player with less tricks is deciding their settlement option:`;
        if (actionsBox) actionsBox.classList.add("hidden");
        if (waitingBox) waitingBox.classList.remove("hidden");
        if (waitingMsg) waitingMsg.textContent = `Waiting for ${debtorName} to choose between Tash Khinchai and Extra Tricks...`;
    }
}

async function sendTikdiDebtChoice(choice) {
    try {
        const res = await fetch(`${API_BASE}/api/tikdi/make-debt-choice`, {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({
                game_id: currentGameId,
                player_id: myPlayerSeat || "P1",
                choice: choice
            })
        });

        if (!res.ok) {
            const err = await res.json();
            alert(err.detail || "Error recording debt choice.");
            return;
        }

        const data = await res.json();
        const modal = document.getElementById("modal-tikdi-debt-choice");
        if (modal) modal.classList.add("hidden");
        renderTikdiState(data.state || data);
    } catch (e) {
        console.error("Tikdi send debt choice error:", e);
    }
}

function renderTikdiPenaltyModal(state) {
    const modal = document.getElementById("modal-tikdi-penalty");
    const titleEl = document.getElementById("tikdi-penalty-title");
    const descEl = document.getElementById("tikdi-penalty-desc");
    const cardsBox = document.getElementById("tikdi-penalty-cards-container");
    const statusEl = document.getElementById("tikdi-penalty-status");

    if (!modal || !cardsBox) return;

    if (!state.penalty_queue || state.penalty_queue.length === 0) {
        modal.classList.add("hidden");
        return;
    }

    const pen = state.current_penalty || (state.penalty_queue && state.penalty_queue[0]);
    if (!pen) {
        modal.classList.add("hidden");
        return;
    }

    const puller = pen.puller || pen.creditor;
    const target = pen.target || pen.debtor;
    const pullerName = (state.player_names && state.player_names[puller]) || puller || "Player";
    const targetName = (state.player_names && state.player_names[target]) || target || "Opponent";
    const isHumanPuller = puller === (myPlayerSeat || "P1");
    const isHumanTarget = target === (myPlayerSeat || "P1");

    modal.classList.remove("hidden");
    cardsBox.innerHTML = "";

    if (isHumanPuller) {
        if (!tikdiPendingReturnTarget) {
            if (titleEl) titleEl.textContent = "⚡ PULL PENALTY CARD";
            if (descEl) descEl.textContent = `You exceeded your quota! Click any face-down card from ${targetName}'s hand to pull blindly:`;
            if (statusEl) statusEl.textContent = "Click a card to pull blindly:";

            const targetHandLen = (state.hands && state.hands[target]) ? state.hands[target].length : 10;
            for (let i = 0; i < targetHandLen; i++) {
                const cardImg = createCardSVG("BACK");
                cardImg.className = "playing-card-svg tikdi-pullable-card";
                cardImg.title = `Click to pull card #${i + 1} from ${targetName}`;
                cardImg.style.cursor = "pointer";
                const cardIdx = i;
                cardImg.addEventListener("click", () => handleTikdiPullCard(cardIdx, target));
                cardsBox.appendChild(cardImg);
            }
        } else {
            if (titleEl) titleEl.textContent = "🔄 RETURN UNWANTED CARD";
            if (descEl) descEl.textContent = `Select 1 card from your hand below to return to ${targetName}:`;
            if (statusEl) statusEl.textContent = "Choose card to give back:";

            const myCards = (state.hands && state.hands[myPlayerSeat || "P1"]) || [];
            myCards.forEach(c => {
                const cardImg = createCardSVG(c.code);
                cardImg.className = "playing-card-svg tikdi-pullable-card";
                cardImg.title = `Click to return ${c.code} to ${targetName}`;
                cardImg.style.cursor = "pointer";
                cardImg.addEventListener("click", () => handleTikdiReturnCard(c.code, tikdiPendingReturnTarget));
                cardsBox.appendChild(cardImg);
            });
        }
    } else {
        if (titleEl) titleEl.textContent = "⚖️ SETTLING PENALTY";
        if (isHumanTarget) {
            if (descEl) descEl.textContent = `${pullerName} is pulling a penalty card from your hand...`;
        } else {
            if (descEl) descEl.textContent = `${pullerName} is pulling a penalty card from ${targetName}...`;
        }
        if (statusEl) statusEl.textContent = "Please wait while cards are swapped...";
    }

    const btnSwitchTricks = document.getElementById("btn-tikdi-switch-to-tricks");
    if (btnSwitchTricks) {
        btnSwitchTricks.onclick = async () => {
            try {
                const res = await fetch(`${API_BASE}/api/tikdi/switch-penalty-mode`, {
                    method: "POST",
                    headers: { "Content-Type": "application/json" },
                    body: JSON.stringify({
                        game_id: currentGameId,
                        penalty_mode: "quota_adjustment",
                        player_id: myPlayerSeat || "P1"
                    })
                });
                if (!res.ok) return;
                const data = await res.json();
                modal.classList.add("hidden");
                renderTikdiState(data.state || data);
            } catch (e) {
                console.error("Switch penalty mode error:", e);
            }
        };
    }
}

function renderTikdiQuotaAdjustmentModal(state) {
    const modal = document.getElementById("modal-tikdi-quota-adjustment");
    const titleEl = document.getElementById("quota-adj-title");
    const descEl = document.getElementById("quota-adj-desc");
    const detailsBox = document.getElementById("quota-adj-details");
    const summaryEl = document.getElementById("quota-adj-summary");
    const btnContinue = document.getElementById("btn-quota-adj-continue");

    if (!modal || !detailsBox) return;

    const adjustments = state.pending_adjustments || [];
    const adjustedQuotas = state.adjusted_quotas || {};
    const baseQuotas = state.base_quotas || state.quotas || {};
    const playerNames = state.player_names || {};
    const players = ["P1", "P2", "P3"];

    if (titleEl) titleEl.textContent = "⚖️ QUOTA ADJUSTMENT";
    if (descEl) descEl.textContent = adjustments.length > 0
        ? "Debts from the last round will adjust your trick quotas for this round:"
        : "No debts to settle. Quotas remain at base values.";

    // Build rows showing old → new quota for each player
    let rowsHtml = '';
    players.forEach(p => {
        const name = playerNames[p] || p;
        const oldQ = baseQuotas[p] || 0;
        const newQ = (adjustments.length > 0 && adjustedQuotas[p] !== undefined) ? adjustedQuotas[p] : oldQ;
        const delta = newQ - oldQ;
        const dirClass = delta > 0 ? 'quota-up' : (delta < 0 ? 'quota-down' : 'quota-same');
        const deltaClass = delta > 0 ? 'delta-pos' : (delta < 0 ? 'delta-neg' : '');
        const deltaText = delta > 0 ? `+${delta}` : (delta < 0 ? `${delta}` : '—');

        rowsHtml += `
            <div class="quota-adj-row">
                <span class="quota-adj-player-name">${name}</span>
                <span class="quota-adj-old">${oldQ}</span>
                <span class="quota-adj-arrow">→</span>
                <span class="quota-adj-new ${dirClass}">${newQ}</span>
                <span class="quota-adj-delta ${deltaClass}">(${deltaText})</span>
            </div>`;
    });
    detailsBox.innerHTML = rowsHtml;

    // Build debt summary lines
    let summaryHtml = '';
    adjustments.forEach(adj => {
        const credName = adj.creditor_name || playerNames[adj.creditor] || adj.creditor;
        const debtName = adj.debtor_name || playerNames[adj.debtor] || adj.debtor;
        summaryHtml += `
            <div class="quota-adj-debt-line">
                <span>🏷️</span>
                <span>${debtName} owes ${adj.count} trick(s) to ${credName}</span>
            </div>`;
    });
    if (summaryEl) summaryEl.innerHTML = summaryHtml;

    // Wire up Continue button
    if (btnContinue) {
        btnContinue.onclick = async () => {
            try {
                const res = await fetch(`${API_BASE}/api/tikdi/acknowledge-adjustment`, {
                    method: "POST",
                    headers: { "Content-Type": "application/json" },
                    body: JSON.stringify({
                        game_id: currentGameId,
                        player_id: myPlayerSeat || "P1"
                    })
                });
                if (!res.ok) {
                    const err = await res.json();
                    alert(err.detail || "Error acknowledging adjustment.");
                    return;
                }
                const data = await res.json();
                modal.classList.add("hidden");
                renderTikdiState(data.state || data);
            } catch (e) {
                console.error("Acknowledge adjustment error:", e);
            }
        };
    }

    modal.classList.remove("hidden");
}

async function handleTikdiPullCard(cardIndex, targetId) {
    try {
        const res = await fetch(`${API_BASE}/api/tikdi/pull-card`, {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({
                game_id: currentGameId,
                puller_id: myPlayerSeat || "P1",
                card_index: cardIndex
            })
        });

        if (!res.ok) {
            const err = await res.json();
            alert(err.detail || "Error pulling card.");
            return;
        }

        const data = await res.json();
        sfx.playCard();
        tikdiPendingReturnTarget = targetId;
        renderTikdiState(data.state);
    } catch (e) {
        console.error("Tikdi pull card error:", e);
    }
}

async function handleTikdiReturnCard(cardCode, targetId) {
    try {
        const res = await fetch(`${API_BASE}/api/tikdi/return-card`, {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({
                game_id: currentGameId,
                returner_id: myPlayerSeat || "P1",
                card_code: cardCode,
                target_id: targetId
            })
        });

        if (!res.ok) {
            const err = await res.json();
            alert(err.detail || "Error returning card.");
            return;
        }

        const data = await res.json();
        sfx.playCard();
        tikdiPendingReturnTarget = null;
        renderTikdiState(data.state);
    } catch (e) {
        console.error("Tikdi return card error:", e);
    }
}

function scheduleTikdiBotTurn(state) {
    if (tikdiBotTimeout) {
        clearTimeout(tikdiBotTimeout);
        tikdiBotTimeout = null;
    }

    if (isBotPlayPaused || !state || state.phase === "ROUND_OVER") return;

    const chooser = state.trump_chooser || state.trump_chooser_id;
    const penPuller = state.current_penalty ? (state.current_penalty.creditor || state.current_penalty.puller) : (state.penalty_queue && state.penalty_queue[0] ? (state.penalty_queue[0].creditor || state.penalty_queue[0].puller) : null);

    const isBotTurn = (state.phase === "TRUMP_SELECTION" && state.player_types && chooser && state.player_types[chooser] === "ai") ||
                      (state.phase === "DEBT_SETTLEMENT_CHOICE" && state.player_types && state.current_turn && state.player_types[state.current_turn] === "ai") ||
                      (state.phase === "PENALTY_RESOLUTION" && penPuller && state.player_types && state.player_types[penPuller] === "ai") ||
                      (state.phase === "PENALTY_ADJUSTMENT") ||
                      ((state.phase === "TRICK_PLAY" || state.phase === "TRICK_PLAYING") && state.player_types && state.player_types[state.current_turn] === "ai");

    if (isBotTurn) {
        const isTrickComplete = (!state.current_trick || state.current_trick.length === 0) && (state.last_completed_trick && state.last_completed_trick.length === 3);
        const isPenaltyAdj = state.phase === "PENALTY_ADJUSTMENT";
        const delay = isPenaltyAdj ? Math.max(autoPlaySpeed, 2000) : (isTrickComplete ? Math.max(autoPlaySpeed, 1200) : autoPlaySpeed);
        tikdiBotTimeout = setTimeout(async () => {
            await triggerTikdiBotStep();
        }, delay);
    }
}

async function triggerTikdiBotStep() {
    if (!gameState || currentGameType !== "tikdi" || gameState.phase === "ROUND_OVER") return;
    try {
        const res = await fetch(`${API_BASE}/api/tikdi/bot-step?game_id=${currentGameId}`, {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({ game_id: currentGameId })
        });
        if (res.ok) {
            const data = await res.json();
            sfx.playCard();
            renderTikdiState(data.state || data);
        } else {
            console.error("Tikdi bot step error:", res.status, await res.text());
        }
    } catch (e) {
        console.error("Tikdi bot step error:", e);
    }
}

function showTikdiRoundOverModal(state) {
    if (!modalDealComplete) return;

    modalDealComplete.classList.add("tikdi-deal-modal");

    const scores = state.scores || {};
    const p1Score = scores["P1"] || 0;
    const p2Score = scores["P2"] || 0;
    const p3Score = scores["P3"] || 0;

    let winnerText = "Tikdi Round Complete!";
    if (p1Score > p2Score && p1Score > p3Score) {
        winnerText = `🏆 ${state.player_names["P1"]} Wins the Round (+${p1Score})!`;
    } else if (p2Score > p1Score && p2Score > p3Score) {
        winnerText = `🏆 ${state.player_names["P2"]} Wins the Round (+${p2Score})!`;
    } else if (p3Score > p1Score && p3Score > p2Score) {
        winnerText = `🏆 ${state.player_names["P3"]} Wins the Round (+${p3Score})!`;
    }

    if (dealCompleteWinner) dealCompleteWinner.textContent = winnerText;
    if (dealCompleteDesc) dealCompleteDesc.textContent = `Net Points: P1 (${p1Score >= 0 ? '+' : ''}${p1Score}) | P2 (${p2Score >= 0 ? '+' : ''}${p2Score}) | P3 (${p3Score >= 0 ? '+' : ''}${p3Score})`;

    if (summaryValA) summaryValA.textContent = `P1: Won ${state.tricks_won["P1"] || 0} / Quota ${state.quotas["P1"]}`;
    if (summaryValB) summaryValB.textContent = `P2: Won ${state.tricks_won["P2"] || 0} / Quota ${state.quotas["P2"]}`;
    if (summaryLblA) summaryLblA.textContent = state.player_names["P1"] || "P1";
    if (summaryLblB) summaryLblB.textContent = state.player_names["P2"] || "P2";

    if (dealCompleteLadder) {
        dealCompleteLadder.textContent = `P3 (${state.player_names["P3"]}): Won ${state.tricks_won["P3"] || 0} / Quota ${state.quotas["P3"]} (Net: ${p3Score >= 0 ? '+' : ''}${p3Score})`;
    }

    if (btnNextDeal) btnNextDeal.classList.add("btn-highlight-pulse");

    if (btnModalNextDeal) {
        btnModalNextDeal.textContent = "⏭ Start Next Tikdi Round";
        btnModalNextDeal.classList.add("btn-highlight-pulse");
        btnModalNextDeal.onclick = async () => {
            modalDealComplete.classList.add("hidden");
            await handleNextTikdiRound();
        };
    }

    modalDealComplete.classList.remove("hidden");
}

async function handleNextTikdiRound() {
    if (btnNextDeal) btnNextDeal.classList.remove("btn-highlight-pulse");
    if (btnModalNextDeal) btnModalNextDeal.classList.remove("btn-highlight-pulse");
    if (modalDealComplete) modalDealComplete.classList.add("hidden");
    try {
        const res = await fetch(`${API_BASE}/api/tikdi/next-round?game_id=${currentGameId}`, {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({ game_id: currentGameId })
        });
        if (res.ok) {
            const data = await res.json();
            renderTikdiState(data.state || data);
        }
    } catch (e) {
        console.error("Next Tikdi round error:", e);
    }
}

// =========================================================================
// ==================== JHUTHANIYA (BLUFF) GAME CONTROLLER =================
// =========================================================================

var jhuthaniyaBotTimeout = null;
var jhuthaniyaCurrentState = null;

function switchActiveGame(gameKey) {
    activeSelectedGame = gameKey;

    // Highlight the game selector tab
    document.querySelectorAll(".gsel-card").forEach(card => {
        card.classList.toggle("gsel-active", card.dataset.game === gameKey);
    });

    const homeSetupCard = document.getElementById("home-setup-card");
    const homeWipCard = document.getElementById("home-wip-card");

    // Handle coming soon / WIP games
    if (gameKey === "gadhabaji" || gameKey === "sarkari") {
        if (homeSetupCard) homeSetupCard.classList.add("hidden");
        if (homeWipCard) {
            homeWipCard.classList.remove("hidden");
            const wipIcon = document.getElementById("wip-game-icon");
            const wipTitle = document.getElementById("wip-game-title");
            const wipDesc = document.getElementById("wip-game-desc");
            if (gameKey === "gadhabaji") {
                if (wipIcon) wipIcon.textContent = "🐴";
                if (wipTitle) wipTitle.textContent = "Gadha Baji — Work in Progress";
                if (wipDesc) wipDesc.innerHTML = "Gadha Baji (Donkey / Get Away) is currently in development with authentic Rajasthani card rules, custom AI bots, and online multiplayer.<br>Enjoy other games like Bikkad, Jhuthaniya, or Tikdi below in the meantime!";
            } else {
                if (wipIcon) wipIcon.textContent = "⚖️";
                if (wipTitle) wipTitle.textContent = "Sarkari — Work in Progress";
                if (wipDesc) wipDesc.innerHTML = "Sarkari (Sarkari Hukam) is a high-stakes 4-player trump trick-taking clash currently in development.<br>Enjoy other games like Bikkad, Jhuthaniya, or Tikdi below in the meantime!";
            }
        }
        return;
    }

    // For live games:
    if (homeSetupCard) homeSetupCard.classList.remove("hidden");
    if (homeWipCard) homeWipCard.classList.add("hidden");

    // Legacy tab support (if old buttons still exist anywhere)
    ["bikkad","jhuthaniya","bindicoat","tikdi"].forEach(k => {
        const btn = document.getElementById("btn-tab-game-" + k);
        if (btn) btn.classList.toggle("active", k === gameKey);
    });

    const bannerBadge = document.getElementById("active-game-banner-badge");
    const bannerDesc = document.getElementById("active-game-banner-desc");
    const btnHowToPlay = document.getElementById("btn-how-to-play-inline");
    const hcount4 = document.getElementById("hcount-4");
    const spickP4 = document.getElementById("spick-P4");
    const selectHider = document.getElementById("select-trump-hider");
    const trumpHiderGroup = selectHider ? selectHider.closest(".form-group-home") : null;
    const feltTable = document.querySelector(".felt-table");
    const optP4 = document.getElementById("opt-seat-p4");
    const btnStart = document.getElementById("btn-start-game");

    // Reset table class
    if (feltTable) {
        feltTable.classList.remove("tikdi-mode");
        feltTable.classList.remove("jhuthaniya-mode");
        feltTable.classList.remove("bindicoat-mode");
    }

    // Show/hide groups based on game
    const showP4 = (gameKey === "bikkad" || gameKey === "bindicoat");
    if (hcount4) hcount4.classList.toggle("hidden", !showP4);
    if (spickP4) spickP4.classList.toggle("hidden", !showP4);
    if (optP4) optP4.classList.toggle("hidden", !showP4);

    const jhCountGroup = document.getElementById("group-jhuthaniya-player-count");
    if (jhCountGroup) jhCountGroup.classList.toggle("hidden", gameKey !== "jhuthaniya");
    const tikdiPenaltyGroup = document.getElementById("group-tikdi-penalty-mode");
    if (tikdiPenaltyGroup) tikdiPenaltyGroup.classList.toggle("hidden", gameKey !== "tikdi");
    if (trumpHiderGroup) trumpHiderGroup.classList.toggle("hidden", gameKey === "jhuthaniya" || gameKey === "tikdi");

    const seatAllocHeader = document.querySelector(".seat-allocation-header");
    const humanCountRow = document.querySelector(".human-count-row");
    if (seatAllocHeader) seatAllocHeader.classList.toggle("hidden", gameKey === "jhuthaniya");
    if (humanCountRow) humanCountRow.classList.toggle("hidden", gameKey === "jhuthaniya");

    if (gameKey === "tikdi") {
        currentGameType = "tikdi";
        if (bannerBadge) bannerBadge.textContent = "Now playing Tikdi (3-2-5):";
        if (bannerDesc) bannerDesc.innerHTML = "3-Player Quota Classic (5-3-2). Click on <strong>How to Play</strong> above to know more!";
        if (btnHowToPlay) btnHowToPlay.textContent = "📖 How to Play →";
        if (feltTable) feltTable.classList.add("tikdi-mode");
        if (typeof currentHumanCount !== "undefined" && currentHumanCount === 4) setHumanCount(1);
        currentRoomId = "TK-" + Math.floor(1000 + Math.random() * 9000);
        const p2Btn = document.getElementById("spick-P2");
        const p3Btn = document.getElementById("spick-P3");
        if (p2Btn) p2Btn.textContent = "P2 (West)";
        if (p3Btn) p3Btn.textContent = "P3 (North)";
        if (btnStart) btnStart.textContent = "▶ Start Tikdi Match";

    } else if (gameKey === "jhuthaniya") {
        currentGameType = "jhuthaniya";
        if (bannerBadge) bannerBadge.textContent = "Now playing Jhuthaniya (Bluff):";
        if (bannerDesc) bannerDesc.innerHTML = "2–7 Player Bluff Game. Play cards face-down &amp; catch bluffs! Click on <strong>How to Play</strong> above to know more!";
        if (btnHowToPlay) btnHowToPlay.textContent = "📖 How to Play →";
        if (feltTable) feltTable.classList.add("jhuthaniya-mode");
        currentRoomId = "JH-" + Math.floor(1000 + Math.random() * 9000);
        const p2Btn = document.getElementById("spick-P2");
        const p3Btn = document.getElementById("spick-P3");
        if (p2Btn) p2Btn.textContent = "P2 Player";
        if (p3Btn) p3Btn.textContent = "P3 Player";
        if (btnStart) btnStart.textContent = "▶ Start Jhuthaniya Match";

    } else if (gameKey === "bindicoat") {
        currentGameType = "bindicoat";
        if (bannerBadge) bannerBadge.textContent = "Now playing Bindi Coat:";
        if (bannerDesc) bannerDesc.innerHTML = "4-Player Partnership. Capture the four 10s (Mindis)! Click on <strong>How to Play</strong> above to know more!";
        if (btnHowToPlay) btnHowToPlay.textContent = "📖 How to Play →";
        if (feltTable) feltTable.classList.add("bindicoat-mode");
        currentRoomId = "BC-" + Math.floor(1000 + Math.random() * 9000);
        const p2Btn = document.getElementById("spick-P2");
        const p3Btn = document.getElementById("spick-P3");
        if (p2Btn) p2Btn.textContent = "P2 (East / EW)";
        if (p3Btn) p3Btn.textContent = "P3 (North / NS Partner)";
        if (btnStart) btnStart.textContent = "▶ Start Bindi Coat Match";

    } else {
        currentGameType = "bikkad";
        if (bannerBadge) bannerBadge.textContent = "Now playing Bikkad:";
        if (bannerDesc) bannerDesc.innerHTML = "Apna Rajasthan ka traditional pot-sweep card game. Click on <strong>How to Play</strong> above to know more!";
        if (btnHowToPlay) btnHowToPlay.textContent = "📖 How to Play →";
        currentRoomId = String(Math.floor(1000 + Math.random() * 9000));
        const p2Btn = document.getElementById("spick-P2");
        const p3Btn = document.getElementById("spick-P3");
        if (p2Btn) p2Btn.textContent = "P2 (Opponent 1)";
        if (p3Btn) p3Btn.textContent = "P3 (Partner)";
        if (btnStart) btnStart.textContent = "▶ Start Bikkad Match";
    }

    if (displayRoomId) displayRoomId.textContent = currentRoomId;
    updateTrumpHiderOptionLabels();
}
window.switchActiveGame = switchActiveGame;

async function startActiveGame() {
    if (!isServerAwake) {
        const ok = await checkAndWakeBackend(true);
        if (!ok) return;
    }
    const g = (typeof activeSelectedGame !== "undefined" && activeSelectedGame) ? activeSelectedGame : (typeof currentGameType !== "undefined" ? currentGameType : "bikkad");
    if (g === "tikdi") {
        handleStartTikdiGame();
    } else if (g === "jhuthaniya") {
        handleStartJhuthaniyaGame();
    } else if (g === "bindicoat") {
        handleStartBindiCoatGame();
    } else {
        handleStartNewGame();
    }
}
window.startActiveGame = startActiveGame;

function showGameToast(gameName) {
    if (typeof showHubToast === "function") {
        showHubToast(`${gameName} is coming soon to Desi Card Arena!`);
    }
}
window.showGameToast = showGameToast;

// ── Jhuthaniya: Start ──────────────────────────────────────────────────────
async function handleStartJhuthaniyaGame() {
    stopAutoPlay();
    currentGameType = "jhuthaniya";
    window.currentGameType = "jhuthaniya";

    const hostName = (inputYourName && inputYourName.value.trim()) || "Player";
    const countSelect = document.getElementById("select-jhuthaniya-player-count");
    const numPlayers = countSelect ? parseInt(countSelect.value, 10) : 4;

    const payload = {
        game_id: currentRoomId,
        host_name: hostName,
        num_players: numPlayers,
        player_types: { "P1": "human" },
        player_names: { "P1": hostName }
    };

    try {
        const res = await fetch(`${API_BASE}/api/jhuthaniya/create-room`, {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify(payload)
        });
        if (!res.ok) { alert("Error starting Jhuthaniya"); return; }
        const data = await res.json();
        currentGameId = data.game_id || currentRoomId;
        switchView("table");
        const st = data.state || data;
        jhuthaniyaCurrentState = st;
        renderJhuthaniyaState(st);
        scheduleJhuthaniyaBotTurn(st);
    } catch (e) {
        console.error("Jhuthaniya start error:", e);
    }
}

// ── Jhuthaniya: Fetch State ────────────────────────────────────────────────
async function fetchJhuthaniyaState() {
    try {
        const res = await fetch(`${API_BASE}/api/jhuthaniya/state?game_id=${currentGameId}&seat=P1`);
        if (!res.ok) return;
        const data = await res.json();
        const st = data.state || data;
        renderJhuthaniyaState(st);
        return st;
    } catch (e) { console.error("Fetch Jhuthaniya state error:", e); }
}

// ── Jhuthaniya: State Variables ───────────────────────────────────────────
var jhuthaniyaSelectedCards = [];
var jhuthaniyaClaimedRank = "A";
var lastShownJhResolutionId = null;

// ── Jhuthaniya: Render ─────────────────────────────────────────────────────
function renderJhuthaniyaState(state) {
    if (!state) return;
    jhuthaniyaCurrentState = state;
    currentGameType = "jhuthaniya";
    window.currentGameType = "jhuthaniya";

    const feltTable = document.querySelector(".felt-table");
    if (feltTable) {
        feltTable.classList.remove("tikdi-mode", "bindicoat-mode");
        feltTable.classList.add("jhuthaniya-mode");
    }

    // Ensure all Bikkad / Tikdi elements are hidden
    if (trumpHideBanner) trumpHideBanner.classList.add("hidden");
    if (playerContractBar) playerContractBar.classList.add("hidden");
    if (btnDemandCut) btnDemandCut.classList.add("hidden");
    if (btnDeclareRuntimeTrump) btnDeclareRuntimeTrump.classList.add("hidden");
    // Render Center Pot in Top-Right Corner Box
    const potBox = document.getElementById("pot-accumulator-box");
    if (potBox) {
        potBox.classList.remove("hidden");
        potBox.style.display = "flex";
        const potTitle = potBox.querySelector(".pot-title");
        if (potTitle) potTitle.textContent = "CENTER POT";

        const potCardsVal = document.getElementById("pot-cards-val");
        const potTricksVal = document.getElementById("pot-tricks-val");
        const potStreak = document.getElementById("pot-streak");

        const potCardsLbl = potBox.querySelectorAll(".pot-lbl")[0];
        if (potCardsLbl) potCardsLbl.textContent = "Cards";
        if (potCardsVal) potCardsVal.textContent = state.center_pot_size || 0;

        const safeCount = (state.players && Object.values(state.players).filter(p => p.is_safe).length) || 0;
        const totalP = state.num_players || (state.players && Object.keys(state.players).length) || 4;
        const potTricksLbl = potBox.querySelectorAll(".pot-lbl")[1];
        if (potTricksLbl) potTricksLbl.textContent = "Safe";
        if (potTricksVal) potTricksVal.textContent = `${safeCount}/${totalP}`;

        if (potStreak) {
            if (state.challenge && state.challenge.claimant_name) {
                potStreak.textContent = `Claim: ${state.challenge.claimed_count}× ${state.challenge.rank_display}`;
            } else {
                potStreak.textContent = `${state.center_pot_size || 0} cards at stake`;
            }
        }
    }

    const trumpSlot = document.getElementById("trump-slot");
    if (trumpSlot) {
        trumpSlot.classList.add("hidden");
        trumpSlot.style.display = "none";
    }
    const trickArena = document.querySelector(".trick-arena");
    if (trickArena) trickArena.classList.add("hidden");
    const bhModal = document.getElementById("modal-bandh-hukum");
    if (bhModal) bhModal.classList.add("hidden");

    // Unhide Jhuthaniya arena
    const jhArena = document.getElementById("jhuthaniya-arena");
    if (jhArena) jhArena.classList.remove("hidden");

    // Clear Bikkad role tags from all seats
    ["P1", "P2", "P3", "P4"].forEach(pid => {
        const rEl = document.getElementById(`role-${pid}`);
        if (rEl) rEl.innerHTML = "";
    });

    updateHeaderBrand("jhuthaniya");

    // Update Header Badges
    const gameNameBadge = document.getElementById("game-name-badge");
    const modeBadge = document.getElementById("mode-badge");
    const turnBadge = document.getElementById("turn-badge");
    const dealerBadge = document.getElementById("dealer-badge");

    const jhDealerName = state.dealer_name || (state.players && state.players[state.dealer] && state.players[state.dealer].name) || state.dealer || "P1";
    if (gameNameBadge) gameNameBadge.textContent = `🏷️ ${state.num_players}P · Deal #${state.deal_number || 1}`;
    if (dealerBadge) dealerBadge.textContent = `🃏 Dealer: ${jhDealerName}`;
    if (modeBadge) {
        modeBadge.textContent = `🏺 Pot: ${state.center_pot_size || 0} cards`;
        modeBadge.classList.remove("hidden");
    }
    if (turnBadge) {
        const turnName = state.current_turn_name || state.current_turn || "";
        if (state.phase === "PLAYING") {
            turnBadge.textContent = state.is_my_turn ? "🟢 Your Turn to Claim" : `Turn: ${turnName}`;
            turnBadge.classList.toggle("turn-badge-winner", state.is_my_turn);
            if (btnNextDeal) btnNextDeal.classList.add("hidden");
        } else if (state.phase === "CHALLENGE_WINDOW") {
            turnBadge.textContent = "⏱️ Challenge: JHUTH or Pass";
            turnBadge.classList.remove("turn-badge-winner");
            if (btnNextDeal) btnNextDeal.classList.add("hidden");
        } else if (state.phase === "ROUND_OVER") {
            turnBadge.textContent = "🏆 Deal Finished!";
            turnBadge.classList.add("turn-badge-winner");
            if (btnNextDeal) {
                btnNextDeal.classList.remove("hidden");
                btnNextDeal.classList.add("btn-highlight-pulse");
            }
        }
    }

    // ── Render 2 to 7 Players Roster ──
    const rosterEl = document.getElementById("jhuthaniya-roster");
    if (rosterEl && state.players) {
        rosterEl.innerHTML = "";
        const pids = Object.keys(state.players);
        pids.forEach(pid => {
            const pInfo = state.players[pid];
            if (!pInfo) return;

            const card = document.createElement("div");
            card.className = "jh-player-card";
            if (pid === state.current_turn && state.phase === "PLAYING") {
                card.classList.add("is-active-turn");
            }
            if (pInfo.is_safe) {
                card.classList.add("is-safe");
            }

            // Name
            const nameSpan = document.createElement("span");
            nameSpan.className = "jh-player-name";
            nameSpan.textContent = (pid === "P1") ? `${pInfo.name} (You)` : pInfo.name;

            // Card Count
            const countBadge = document.createElement("span");
            countBadge.className = "jh-player-count-badge";
            countBadge.textContent = `🃏 ${pInfo.card_count}`;

            card.appendChild(nameSpan);
            card.appendChild(countBadge);

            // Tags
            if (pInfo.is_dealer) {
                const dTag = document.createElement("span");
                dTag.className = "jh-player-status-tag jh-status-turn";
                dTag.textContent = "🎴 Dealer";
                card.appendChild(dTag);
            }
            if (pInfo.is_safe) {
                const sTag = document.createElement("span");
                sTag.className = "jh-player-status-tag jh-status-safe";
                sTag.textContent = `✅ Safe #${pInfo.safe_rank}`;
                card.appendChild(sTag);
            } else if (state.phase === "CHALLENGE_WINDOW" && state.challenge) {
                const ch = state.challenge;
                const dec = ch.challenge_decisions && ch.challenge_decisions[pid];
                if (dec) {
                    const decTag = document.createElement("span");
                    decTag.className = "jh-player-status-tag " + (dec === "challenge" ? "jh-status-challenged" : "jh-status-passed");
                    decTag.textContent = (dec === "challenge") ? "🔥 JHUTH!" : "Passed";
                    card.appendChild(decTag);
                }
            }

            rosterEl.appendChild(card);
        });
    }

    // ── Render Center Pot & Claim Stage ──
    const potBadge = document.getElementById("jh-pot-badge");
    if (potBadge) {
        potBadge.textContent = `🃏 ${state.center_pot_size || 0} Cards in Pot`;
    }
    const potStack = document.getElementById("jh-pot-card-stack");
    if (potStack) {
        potStack.innerHTML = "";
        const potSize = state.center_pot_size || 0;
        if (potSize === 0) {
            potStack.innerHTML = `<div class="jh-pot-empty-slot"><span>Empty Pot</span></div>`;
        } else {
            const showCards = Math.min(potSize, 5);
            const rotations = [-8, 4, -4, 7, 2];
            for (let i = 0; i < showCards; i++) {
                const cardEl = createCardSVG("BACK");
                cardEl.className = `playing-card-svg jh-pot-img jh-img-${i + 1}`;
                cardEl.style.transform = `rotate(${rotations[i % rotations.length]}deg) translate(${i * 2}px, ${-i * 2}px)`;
                cardEl.style.width = "60px";
                cardEl.style.height = "84px";
                potStack.appendChild(cardEl);
            }
        }
    }

    // Claim display
    const claimDisplay = document.getElementById("jh-claim-display");
    const claimSpeaker = document.getElementById("jh-claim-speaker");
    const claimText = document.getElementById("jh-claim-text");
    if (claimDisplay && claimSpeaker && claimText) {
        if (state.challenge && state.challenge.claimant_name) {
            const ch = state.challenge;
            claimDisplay.classList.remove("hidden");
            claimSpeaker.textContent = `📢 ${ch.claimant_name} Claimed`;
            claimText.innerHTML = `Placed <strong>${ch.claimed_count}</strong> card(s) and claims: <span style="color:#ffd700;font-size:1.25rem;">${ch.claimed_count} × ${ch.rank_display}</span>${ch.is_final_play ? " 🚨 (FINAL PLAY!)" : ""}`;
        } else {
            claimDisplay.classList.add("hidden");
        }
    }

    // Challenge action bar (for human when someone else claims)
    const challengeBar = document.getElementById("jh-challenge-bar");
    const inspectContainer = document.getElementById("jh-inspect-container");
    const btnJhChallenge = document.getElementById("btn-jh-challenge");
    const btnJhPass = document.getElementById("btn-jh-pass");
    if (challengeBar && btnJhChallenge && btnJhPass) {
        const ch = state.challenge;
        const waitingForMe = ch && ch.waiting_for && ch.waiting_for.includes("P1") && !ch.my_decision;
        if (state.phase === "CHALLENGE_WINDOW" && waitingForMe) {
            challengeBar.classList.remove("hidden");
            const count = ch.claimed_count || ch.played_cards_count || 1;

            if (inspectContainer) {
                inspectContainer.innerHTML = "";
                const promptText = document.getElementById("jh-challenge-prompt");
                if (count > 1) {
                    if (promptText) promptText.textContent = `Claim of ${count} cards: Pick 1 card position to inspect or pass:`;
                    for (let i = 0; i < count; i++) {
                        const btnInspect = document.createElement("button");
                        btnInspect.className = "btn btn-danger btn-sm jh-inspect-btn";
                        btnInspect.style.cssText = "margin: 2px 4px; padding: 6px 12px; font-weight: 600;";
                        btnInspect.textContent = `🔍 Inspect Card #${i + 1}`;
                        btnInspect.onclick = async () => {
                            challengeBar.classList.add("hidden");
                            await submitJhuthaniyaDecision("challenge", i);
                        };
                        inspectContainer.appendChild(btnInspect);
                    }
                } else {
                    if (promptText) promptText.textContent = "Do you believe this claim or want to inspect?";
                }
            }

            btnJhChallenge.onclick = async () => {
                challengeBar.classList.add("hidden");
                await submitJhuthaniyaDecision("challenge", 0);
            };
            btnJhPass.onclick = async () => {
                challengeBar.classList.add("hidden");
                await submitJhuthaniyaDecision("pass");
            };
        } else {
            challengeBar.classList.add("hidden");
        }
    }

    // Play action bar (when it is human's turn to play cards)
    const playBar = document.getElementById("jh-play-bar");
    const rankPillsContainer = document.getElementById("jh-rank-pills");
    const lockedRankBadge = document.getElementById("jh-locked-rank-badge");
    const rankStepTitle = document.getElementById("jh-rank-step-title");
    const btnPlaySubmit = document.getElementById("btn-jh-play-submit");
    if (playBar && rankPillsContainer && btnPlaySubmit) {
        if (state.is_my_turn && state.phase === "PLAYING") {
            playBar.classList.remove("hidden");

            const isRankLocked = !state.can_choose_rank && !!state.current_round_rank;
            if (isRankLocked) {
                // Option A: Rank is locked for the trick sequence
                jhuthaniyaClaimedRank = state.current_round_rank;
                rankPillsContainer.classList.add("hidden");
                if (lockedRankBadge) {
                    lockedRankBadge.classList.remove("hidden");
                    const rankDisp = state.current_round_rank_display || state.current_round_rank;
                    lockedRankBadge.innerHTML = `🔒 Round Rank Locked: <strong>${rankDisp}</strong> <span style="opacity:0.85;font-weight:400;font-size:0.85rem;">(Option A: Must claim ${rankDisp})</span>`;
                }
                if (rankStepTitle) rankStepTitle.textContent = `2. Rank Locked (${state.current_round_rank_display || state.current_round_rank})`;
            } else {
                // Free choice for the trick lead
                if (lockedRankBadge) lockedRankBadge.classList.add("hidden");
                rankPillsContainer.classList.remove("hidden");
                if (rankStepTitle) rankStepTitle.textContent = "2. Pick Claimed Rank:";
                // Build rank pills if empty
                if (rankPillsContainer.children.length === 0) {
                    const ranks = ["2", "3", "4", "5", "6", "7", "8", "9", "10", "J", "Q", "K", "A"];
                    ranks.forEach(r => {
                        const pill = document.createElement("button");
                        pill.className = "jh-rank-pill" + (jhuthaniyaClaimedRank === r ? " active" : "");
                        pill.textContent = (r === "J" ? "J (Jack)" : r === "Q" ? "Q (Begam)" : r === "K" ? "K (Badshah)" : r === "A" ? "A (Ace)" : r);
                        pill.onclick = () => {
                            jhuthaniyaClaimedRank = r;
                            rankPillsContainer.querySelectorAll(".jh-rank-pill").forEach(p => p.classList.remove("active"));
                            pill.classList.add("active");
                            updateJhuthaniyaPlayButton();
                        };
                        rankPillsContainer.appendChild(pill);
                    });
                } else {
                    rankPillsContainer.querySelectorAll(".jh-rank-pill").forEach(p => {
                        const r = p.textContent.split(" ")[0];
                        p.classList.toggle("active", r === jhuthaniyaClaimedRank);
                    });
                }
            }
            updateJhuthaniyaPlayButton();
            btnPlaySubmit.onclick = async () => {
                await submitJhuthaniyaPlayAction();
            };
        } else {
            playBar.classList.add("hidden");
        }
    }

    // ── Render Human South Hand (id="hand-P1") using Standard Vector SVG Cards ──
    const southHand = document.getElementById("hand-P1");
    if (southHand) {
        southHand.innerHTML = "";
        const myHand = state.my_hand || [];
        const isMobile = window.innerWidth <= 768;
        let customMarginLeft = null;
        if (isMobile && myHand.length > 1) {
            const availWidth = Math.min(window.innerWidth - 16, 480);
            const cardWidth = Math.min(Math.max(40, Math.floor(window.innerWidth * 0.105)), 56);
            const neededStep = (availWidth - cardWidth - 8) / (myHand.length - 1);
            const maxStep = Math.min(cardWidth * 0.75, 34);
            const actualStep = Math.min(maxStep, Math.max(14, neededStep));
            customMarginLeft = -Math.round(cardWidth - actualStep);
        }

        myHand.forEach((code, index) => {
            const wrapper = document.createElement("div");
            wrapper.className = "card-wrapper jh-card-wrapper legal-card" + (jhuthaniyaSelectedCards.includes(code) ? " jh-selected" : "");
            wrapper.dataset.code = code;
            wrapper.style.zIndex = index + 1;
            if (index > 0 && customMarginLeft !== null) {
                wrapper.style.setProperty("margin-left", `${customMarginLeft}px`, "important");
            }
            
            const img = (typeof createCardSVG === "function") ? createCardSVG(code) : null;
            if (img) {
                wrapper.appendChild(img);
            } else {
                const fallbackImg = document.createElement("img");
                fallbackImg.src = `cards/${code}.svg`;
                fallbackImg.alt = code;
                wrapper.appendChild(fallbackImg);
            }

            wrapper.onclick = () => {
                toggleJhuthaniyaCardSelection(code, wrapper);
            };
            southHand.appendChild(wrapper);
        });
    }

    // Challenge resolution toast
    if (state.last_resolution) {
        showJhuthaniyaResolutionToast(state.last_resolution);
    }

    // Summary modal when ROUND_OVER
    if (state.phase === "ROUND_OVER" && state.round_summary) {
        showJhuthaniyaSummary(state.round_summary, state.players);
    }

    renderGameLogs(state.logs);
}

function toggleJhuthaniyaCardSelection(code, el) {
    const idx = jhuthaniyaSelectedCards.indexOf(code);
    if (idx > -1) {
        jhuthaniyaSelectedCards.splice(idx, 1);
        if (el) el.classList.remove("jh-selected");
    } else {
        if (jhuthaniyaSelectedCards.length >= 4) {
            alert("You can play at most 4 cards at a time!");
            return;
        }
        jhuthaniyaSelectedCards.push(code);
        if (el) el.classList.add("jh-selected");
    }
    updateJhuthaniyaPlayButton();
}

function updateJhuthaniyaPlayButton() {
    const btn = document.getElementById("btn-jh-play-submit");
    if (!btn) return;
    const count = jhuthaniyaSelectedCards.length;
    if (count > 0 && jhuthaniyaClaimedRank) {
        btn.disabled = false;
        const rankName = (jhuthaniyaClaimedRank === "J" ? "Jacks (Ghulams)" : jhuthaniyaClaimedRank === "Q" ? "Queens (Begams)" : jhuthaniyaClaimedRank === "K" ? "Kings (Badshahs)" : jhuthaniyaClaimedRank === "A" ? "Aces (Ikkas)" : `${jhuthaniyaClaimedRank}s`);
        btn.textContent = `🚀 Place ${count} Card(s) & Claim ${count} × ${rankName}`;
    } else {
        btn.disabled = true;
        btn.textContent = count === 0 ? "Select 1 to 4 Cards from Hand" : "Pick Claimed Rank";
    }
}

async function submitJhuthaniyaPlayAction() {
    if (jhuthaniyaSelectedCards.length === 0) {
        alert("Select at least 1 card to play!");
        return;
    }
    if (!jhuthaniyaClaimedRank) {
        alert("Select a claimed rank!");
        return;
    }
    try {
        const payload = {
            game_id: currentGameId,
            player_id: "P1",
            card_codes: [...jhuthaniyaSelectedCards],
            claimed_rank: jhuthaniyaClaimedRank,
            claimed_count: jhuthaniyaSelectedCards.length
        };
        jhuthaniyaSelectedCards = [];
        const res = await fetch(`${API_BASE}/api/jhuthaniya/play`, {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify(payload)
        });
        if (!res.ok) {
            const err = await res.json();
            alert(err.detail || "Play failed");
            return;
        }
        const data = await res.json();
        const st = data.state || data;
        renderJhuthaniyaState(st);
        scheduleJhuthaniyaBotTurn(st);
    } catch (e) {
        console.error("Jhuthaniya play error:", e);
    }
}

async function submitJhuthaniyaDecision(decision, cardIndex = 0) {
    try {
        const res = await fetch(`${API_BASE}/api/jhuthaniya/challenge`, {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({
                game_id: currentGameId,
                player_id: "P1",
                decision: decision,
                card_index: cardIndex
            })
        });
        if (!res.ok) return;
        const data = await res.json();
        const st = data.state || data;
        renderJhuthaniyaState(st);
        scheduleJhuthaniyaBotTurn(st);
    } catch (e) {
        console.error("Challenge decision error:", e);
    }
}

function showJhuthaniyaResolutionToast(res) {
    if (!res || !res.message) return;
    const resId = `${res.challenger}_${res.verdict}_${res.pot_taken}_${res.loser}`;
    if (lastShownJhResolutionId === resId) return;
    lastShownJhResolutionId = resId;

    const toast = document.getElementById("hub-toast");
    if (!toast) return;
    const isBluff = res.verdict === "CAUGHT_BLUFF";
    toast.innerHTML = `<div style="font-size:1.15rem;font-weight:700;margin-bottom:4px;">${isBluff ? "🚨 JHUTH CAUGHT!" : "✅ HONEST CLAIM!"}</div>
        <div style="font-size:0.95rem;">${res.message}</div>`;
    toast.style.cssText = `position:fixed;top:80px;left:50%;transform:translateX(-50%);
        background:${isBluff ? "linear-gradient(135deg,#dc2626,#991b1b)" : "linear-gradient(135deg,#16a34a,#15803d)"};
        color:#fff;padding:14px 28px;border-radius:14px;z-index:9999;box-shadow:0 8px 30px rgba(0,0,0,0.6);text-align:center;max-width:90vw;`;
    toast.classList.remove("hidden");
    setTimeout(() => toast.classList.add("hidden"), 3500);
}

function showJhuthaniyaSummary(summary, players) {
    const modal = document.getElementById("modal-jhuthaniya-summary");
    if (!modal) return;
    const loserEl = document.getElementById("jhuthaniya-summary-loser");
    const rankEl = document.getElementById("jhuthaniya-summary-rankings");
    if (loserEl) loserEl.textContent = `🎯 LOSER: ${summary.loser_name} (${summary.loser_cards} cards remaining)`;
    if (rankEl && summary.rankings) {
        rankEl.innerHTML = summary.rankings.map(r =>
            `<div style="padding:6px 12px;color:#ffd700;background:rgba(255,255,255,0.06);border-radius:6px;margin:2px 0;">🏅 #${r.place}: ${r.name}</div>`
        ).join("");
    }
    modal.classList.remove("hidden");
}

function scheduleJhuthaniyaBotTurn(state) {
    if (!state || state.phase === "ROUND_OVER") return;
    if (jhuthaniyaBotTimeout) {
        clearTimeout(jhuthaniyaBotTimeout);
        jhuthaniyaBotTimeout = null;
    }

    const needsBot = (state.phase === "PLAYING" && state.current_turn !== "P1") ||
        (state.phase === "CHALLENGE_WINDOW" && state.challenge &&
            state.challenge.waiting_for && !state.challenge.waiting_for.includes("P1") &&
            state.challenge.waiting_for.length > 0);

    if (needsBot) {
        jhuthaniyaBotTimeout = setTimeout(triggerJhuthaniyaBotStep, 950);
    }
}

async function triggerJhuthaniyaBotStep() {
    jhuthaniyaBotTimeout = null;
    if (currentGameType !== "jhuthaniya") return;
    try {
        const res = await fetch(`${API_BASE}/api/jhuthaniya/bot-step`, {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({ game_id: currentGameId })
        });
        if (!res.ok) return;
        const data = await res.json();
        const st = data.state || data;
        renderJhuthaniyaState(st);
        scheduleJhuthaniyaBotTurn(st);
    } catch (e) {
        console.error("Jhuthaniya bot step error:", e);
    }
}

function formatCardCode(code) {
    if (!code) return "";
    const suitMap = { H: "♥", D: "♦", C: "♣", S: "♠" };
    const suit = code.slice(-1);
    const rank = code.slice(0, -1);
    return rank + (suitMap[suit] || suit);
}

function renderGameLogs(logs) {
    const logArea = document.getElementById("log-area") || document.getElementById("game-log-text");
    if (logArea && logs) {
        logArea.textContent = logs.slice(-20).join("\n");
    }
}

// =========================================================================
// ==================== BINDI COAT (MINDIKOT) GAME CONTROLLER ==============
// =========================================================================

var bindiCoatBotTimeout = null;
var bindiCoatCurrentState = null;

// ── Bindi Coat: Start ─────────────────────────────────────────────────────
async function handleStartBindiCoatGame() {
    const hostName = (inputYourName && inputYourName.value.trim()) || "Player";
    const p2Type = (document.getElementById("select-type-p2") || {}).value || "ai";
    const p3Type = (document.getElementById("select-type-p3") || {}).value || "ai";
    const p4Type = (document.getElementById("select-type-p4") || {}).value || "ai";
    const p2Name = (inputNameP2 && inputNameP2.value.trim()) || "G. Dinesh";
    const p3Name = (inputNameP3 && inputNameP3.value.trim()) || "G. Bhimaram";
    const p4Name = (inputNameP4 && inputNameP4.value.trim()) || "G. Geeta";

    const payload = {
        game_id: currentRoomId,
        host_name: hostName,
        player_types: { "P1": "human", "P2": p2Type, "P3": p3Type, "P4": p4Type },
        player_names: { "P1": hostName, "P2": p2Name, "P3": p3Name, "P4": p4Name }
    };

    try {
        const res = await fetch(`${API_BASE}/api/bindi-coat/create-room`, {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify(payload)
        });
        if (!res.ok) { alert("Error starting Bindi Coat"); return; }
        const data = await res.json();
        currentGameId = data.game_id || currentRoomId;
        switchView("table");
        const st = data.state || data;
        bindiCoatCurrentState = st;
        renderBindiCoatState(st);
        scheduleBindiCoatBotTurn(st);
    } catch (e) {
        console.error("Bindi Coat start error:", e);
    }
}

// ── Bindi Coat: Fetch State ────────────────────────────────────────────────
async function fetchBindiCoatState() {
    try {
        const res = await fetch(`${API_BASE}/api/bindi-coat/state?game_id=${currentGameId}&seat=P1`);
        if (!res.ok) return;
        const data = await res.json();
        const st = data.state || data;
        renderBindiCoatState(st);
        return st;
    } catch (e) { console.error("Fetch Bindi Coat state error:", e); }
}

// ── Bindi Coat: Render ─────────────────────────────────────────────────────
function renderBindiCoatState(state) {
    if (!state) return;
    bindiCoatCurrentState = state;
    currentGameType = "bindicoat";
    window.currentGameType = "bindicoat";

    updateHeaderBrand("bindicoat");

    const feltTable = document.querySelector(".felt-table");
    if (feltTable) {
        feltTable.classList.remove("tikdi-mode", "jhuthaniya-mode");
        feltTable.classList.add("bindicoat-mode");
    }

    // Clean out Bikkad-only widgets
    if (trumpHideBanner) trumpHideBanner.classList.add("hidden");
    if (playerContractBar) playerContractBar.classList.add("hidden");
    if (btnDemandCut) btnDemandCut.classList.add("hidden");
    if (btnDeclareRuntimeTrump) btnDeclareRuntimeTrump.classList.add("hidden");
    const jhArena = document.getElementById("jhuthaniya-arena");
    if (jhArena) jhArena.classList.add("hidden");

    const gameNameBadge = document.getElementById("game-name-badge");
    const modeBadge = document.getElementById("mode-badge");
    const turnBadge = document.getElementById("turn-badge");
    const dealerBadge = document.getElementById("dealer-badge");
    const bh = state.bandh_hukum || {};

    const dealerId = state.dealer_id || "P1";
    const dName = (state.players && state.players[dealerId] && state.players[dealerId].name) || dealerId;

    if (gameNameBadge) gameNameBadge.textContent = `🏷️ 4P · Deal #${state.deal_num || 1}`;
    if (dealerBadge) dealerBadge.textContent = `🃏 Dealer: ${dName}`;
    if (modeBadge) {
        modeBadge.textContent = bh.revealed ? `🔓 Hukum: ${bh.trump_suit_name}` : `🔒 Bandh Hukum`;
        modeBadge.classList.remove("hidden");
    }

    if (turnBadge) {
        if (state.phase === "BANDH_HUKUM_SELECTION") {
            turnBadge.textContent = state.is_trump_placer ? "🃏 Select Bandh Hukum" : `⏳ ${state.bandh_hukum_placer_name || "Placer"} choosing Hukum`;
            turnBadge.classList.remove("turn-badge-winner");
            if (btnNextDeal) btnNextDeal.classList.add("hidden");
        } else if (state.phase === "GAME_OVER") {
            turnBadge.textContent = "🏆 Deal Complete!";
            turnBadge.classList.add("turn-badge-winner");
            if (btnNextDeal) {
                btnNextDeal.classList.remove("hidden");
                btnNextDeal.classList.add("btn-highlight-pulse");
            }
        } else {
            const isMyTurn = state.current_turn === (myPlayerSeat || "P1");
            turnBadge.textContent = isMyTurn ? "🟢 Your Turn" : `Turn: ${state.current_turn_name || state.current_turn || ""}`;
            turnBadge.classList.remove("turn-badge-winner");
            if (btnNextDeal) {
                btnNextDeal.classList.add("hidden");
                btnNextDeal.classList.remove("btn-highlight-pulse");
            }
        }
    }

    // Player positions & cards count (Mindikot is 4-player partnership)
    ["P1", "P2", "P3", "P4"].forEach(pid => {
        const pInfo = state.players && state.players[pid];
        const nameEl = document.getElementById(`name-${pid}`);
        const countEl = document.getElementById(`count-${pid}`);
        const roleEl = document.getElementById(`role-${pid}`);
        if (roleEl) roleEl.innerHTML = "";
        if (pInfo && nameEl) {
            const team = pInfo.team === "NS" ? "🔵 NS" : "🔴 EW";
            nameEl.textContent = `${pInfo.name} (${team})`;
        }
        if (pInfo && countEl) {
            countEl.textContent = `${pInfo.card_count} cards | ${pInfo.tricks_won || 0}T`;
        }
    });

    // Top-Left Corner: Bandh Hukum (Hidden Trump) Card Slot
    const trumpSlotBox = document.getElementById("trump-slot");
    const trumpSlotLabel = document.getElementById("trump-slot-label");
    const trumpContainer = document.getElementById("trump-card-container");
    const trumpCallerBadge = document.getElementById("trump-revealed-caller-badge");
    const trumpCallerName = document.getElementById("trump-caller-name");

    const suitSymbols = { 'S': '♠', 'H': '♥', 'D': '♦', 'C': '♣' };
    const suitNames = { 'S': 'SPADES', 'H': 'HEARTS', 'D': 'DIAMONDS', 'C': 'CLUBS' };

    if (trumpSlotBox && trumpContainer && trumpSlotLabel) {
        trumpSlotBox.classList.remove("hidden");
        trumpSlotBox.style.display = "flex";

        if (bh.revealed && bh.trump_suit) {
            const isRed = (bh.trump_suit === 'H' || bh.trump_suit === 'D');
            trumpSlotLabel.innerHTML = `<span style="color:${isRed ? '#fca5a5' : '#7dd3fc'}; font-size:10.5px; font-weight:800; letter-spacing:0.5px;">HUKUM: ${suitSymbols[bh.trump_suit] || ''} ${bh.trump_suit_name || suitNames[bh.trump_suit] || ''}</span>`;
            trumpContainer.innerHTML = "";
            const trumpCardEl = createCardSVG(bh.card_code || ("A" + bh.trump_suit));
            trumpContainer.appendChild(trumpCardEl);
            trumpContainer.title = `Hukum: ${bh.trump_suit_name || bh.trump_suit}`;
            trumpSlotBox.classList.add("trump-revealed-active");

            if (trumpCallerBadge && trumpCallerName) {
                if (bh.placer_name || bh.placer) {
                    trumpCallerName.textContent = `Placer: ${bh.placer_name || bh.placer}`;
                    trumpCallerBadge.classList.remove("hidden");
                } else {
                    trumpCallerBadge.classList.add("hidden");
                }
            }
        } else if (bh.placer) {
            trumpSlotLabel.textContent = "BANDH HUKUM";
            trumpContainer.innerHTML = "";
            const backCard = createCardSVG("BACK");
            trumpContainer.appendChild(backCard);
            trumpContainer.title = "Bandh Hukum (Hidden Trump)";
            trumpSlotBox.classList.remove("trump-revealed-active");
            if (trumpCallerBadge && trumpCallerName) {
                trumpCallerName.textContent = `Placer: ${bh.placer_name || bh.placer}`;
                trumpCallerBadge.classList.remove("hidden");
            }
        } else {
            trumpSlotLabel.textContent = "CHOOSING TRUMP";
            trumpContainer.innerHTML = "";
            const backCard = createCardSVG("BACK");
            trumpContainer.appendChild(backCard);
            trumpContainer.title = "Choosing Bandh Hukum...";
            trumpSlotBox.classList.remove("trump-revealed-active");
            if (trumpCallerBadge) trumpCallerBadge.classList.add("hidden");
        }
    }

    // Top-Right Corner: Pot Accumulator Box (Mindis & Tricks)
    const potBox = document.getElementById("pot-accumulator-box");
    if (potBox) {
        potBox.classList.remove("hidden");
        potBox.style.display = "flex";
        const potTitle = potBox.querySelector(".pot-title");
        if (potTitle) potTitle.textContent = "MINDI & TRICKS";

        const potCardsVal = document.getElementById("pot-cards-val");
        const potTricksVal = document.getElementById("pot-tricks-val");
        const potStreak = document.getElementById("pot-streak");

        const teams = state.teams || {};
        const nsM = (teams.NS && teams.NS.mindis) || 0;
        const ewM = (teams.EW && teams.EW.mindis) || 0;
        const nsT = (teams.NS && teams.NS.tricks) || 0;
        const ewT = (teams.EW && teams.EW.tricks) || 0;

        const potCardsLbl = potBox.querySelectorAll(".pot-lbl")[0];
        if (potCardsLbl) potCardsLbl.textContent = "Mindis (NS:EW)";
        if (potCardsVal) potCardsVal.textContent = `${nsM} - ${ewM}`;

        const potTricksLbl = potBox.querySelectorAll(".pot-lbl")[1];
        if (potTricksLbl) potTricksLbl.textContent = "Tricks (NS:EW)";
        if (potTricksVal) potTricksVal.textContent = `${nsT} - ${ewT}`;

        if (potStreak) {
            const mTotal = nsM + ewM;
            potStreak.textContent = `Total 4 Mindis (${4 - mTotal} Left)`;
        }
    }

    // Center Area: Standard Trick Arena with Royal Cards (No center clutter)
    const trickArena = document.querySelector(".trick-arena");
    if (trickArena) trickArena.classList.remove("hidden");
    const centerArea = document.getElementById("center-area") || document.querySelector(".center-arena");
    if (centerArea) {
        const oldBcCenter = centerArea.querySelector(".bc-center");
        if (oldBcCenter) oldBcCenter.remove();
    }
    renderTableTrickCards(state.current_trick, state.last_completed_trick, state.last_trick_winner, state.last_trick_winning_card, 4);

    // Bandh Hukum selection modal — if I am the trump placer and phase = BANDH_HUKUM_SELECTION
    const bhModal = document.getElementById("modal-bandh-hukum");
    if (state.phase === "BANDH_HUKUM_SELECTION" && state.is_trump_placer && bhModal) {
        const handEl = document.getElementById("bandh-hukum-hand");
        const descEl = document.getElementById("bandh-hukum-desc");
        if (descEl) {
            descEl.innerHTML = `You are the <strong>Trump Placer</strong>. In Bandh Hukum mode, your first 5 cards are face-down. Pick <strong>1 card blindly</strong> to hide as the secret Trump. Nobody knows what the Hukum is until it is revealed during play!`;
        }
        if (handEl) {
            handEl.innerHTML = "";
            const count = (state.my_hand && state.my_hand.length) || 5;
            for (let idx = 0; idx < count; idx++) {
                const cardWrap = document.createElement("div");
                cardWrap.className = "blind-card-choice";
                cardWrap.style.cssText = `
                    display: flex;
                    flex-direction: column;
                    align-items: center;
                    cursor: pointer;
                    transition: transform 0.2s ease, filter 0.2s ease;
                    user-select: none;
                    padding: 2px;
                `;

                const cardEl = createCardSVG("BACK");
                cardEl.className = "playing-card-svg";
                cardEl.style.cssText = "width: 60px; height: 84px; border-radius: 6px; box-shadow: 0 4px 12px rgba(0,0,0,0.6);";

                const label = document.createElement("div");
                label.className = "blind-card-label";
                label.textContent = `#${idx + 1}`;
                label.style.cssText = `
                    margin-top: 6px;
                    font-size: 0.75rem;
                    font-weight: 700;
                    color: #94a3b8;
                    background: rgba(15,23,42,0.85);
                    padding: 2px 8px;
                    border-radius: 10px;
                    border: 1px solid rgba(255,255,255,0.15);
                    transition: all 0.2s ease;
                `;

                cardWrap.appendChild(cardEl);
                cardWrap.appendChild(label);

                cardWrap.onmouseenter = () => {
                    cardWrap.style.transform = "translateY(-6px) scale(1.08)";
                    label.style.color = "#ffd700";
                    label.style.borderColor = "#ffd700";
                };
                cardWrap.onmouseleave = () => {
                    cardWrap.style.transform = "translateY(0) scale(1)";
                    label.style.color = "#94a3b8";
                    label.style.borderColor = "rgba(255,255,255,0.15)";
                };

                cardWrap.onclick = async () => {
                    cardWrap.style.transform = "scale(0.92)";
                    bhModal.classList.add("hidden");
                    await submitBindiCoatBandhHukum(null, idx);
                };

                handEl.appendChild(cardWrap);
            }
        }
        bhModal.classList.remove("hidden");
    } else if (bhModal) {
        bhModal.classList.add("hidden");
    }

    // My hand
    const southHand = document.getElementById("hand-south") || document.getElementById("hand-P1");
    if (southHand) {
        southHand.innerHTML = "";
        const myHand = state.my_hand || [];
        const legalMoves = state.my_legal_moves || [];
        const isBhSelection = (state.phase === "BANDH_HUKUM_SELECTION");

        if (isBhSelection) {
            // Render face-down cards during Bandh Hukum Selection
            myHand.forEach((code, idx) => {
                const cardWrap = document.createElement("div");
                cardWrap.className = "card-wrapper";
                cardWrap.style.zIndex = idx + 1;
                const cardEl = createCardSVG("BACK");
                cardWrap.appendChild(cardEl);
                southHand.appendChild(cardWrap);
            });
        } else {
            const isMobile = window.innerWidth <= 768;
            let customMarginLeft = null;
            if (isMobile && myHand.length > 1) {
                const availWidth = Math.min(window.innerWidth - 16, 480);
                const cardWidth = Math.min(Math.max(40, Math.floor(window.innerWidth * 0.105)), 56);
                const neededStep = (availWidth - cardWidth - 8) / (myHand.length - 1);
                const maxStep = Math.min(cardWidth * 0.75, 34);
                const actualStep = Math.min(maxStep, Math.max(14, neededStep));
                customMarginLeft = -Math.round(cardWidth - actualStep);
            }

            myHand.forEach((code, index) => {
                const isLegal = state.is_my_turn && (legalMoves.length === 0 || legalMoves.includes(code));
                const cardWrap = document.createElement("div");
                cardWrap.className = "card-wrapper" + (isLegal ? " legal-card" : " illegal-card");
                cardWrap.style.zIndex = index + 1;
                if (index > 0 && customMarginLeft !== null) {
                    cardWrap.style.setProperty("margin-left", `${customMarginLeft}px`, "important");
                }
                const cardEl = createCardSVG(code);
                cardWrap.appendChild(cardEl);
                if (isLegal) {
                    cardWrap.onclick = () => submitBindiCoatPlay(code);
                }
                southHand.appendChild(cardWrap);
            });
        }
    }

    // Round summary
    if (state.phase === "ROUND_SUMMARY" && state.round_summary) {
        showBindiCoatSummary(state.round_summary);
    }

    // Trick reveal animation log
    if (bh.revealed && bh.reveal_trick === state.current_trick_number - 1) {
        showHukumKholoToast(bh.trump_suit_name);
    }

    renderGameLogs(state.logs);
}

function showHukumKholoToast(trumpName) {
    const toast = document.getElementById("hub-toast");
    if (!toast) return;
    toast.textContent = `🔓 HUKUM KHOLO! Trump: ${trumpName}`;
    toast.style.cssText = "position:fixed;top:80px;left:50%;transform:translateX(-50%);background:linear-gradient(135deg,#ff4444,#cc0000);color:#fff;padding:12px 32px;border-radius:12px;font-size:1.3rem;font-weight:700;z-index:9999;";
    toast.classList.remove("hidden");
    setTimeout(() => toast.classList.add("hidden"), 3000);
}

async function submitBindiCoatBandhHukum(cardCode, cardIndex = null) {
    try {
        const payload = { game_id: currentGameId, player_id: "P1" };
        if (cardIndex !== null && cardIndex !== undefined) {
            payload.card_index = cardIndex;
        } else if (cardCode) {
            payload.card_code = cardCode;
        }
        const res = await fetch(`${API_BASE}/api/bindi-coat/select-bandh-hukum`, {
            method: "POST", headers: { "Content-Type": "application/json" },
            body: JSON.stringify(payload)
        });
        if (!res.ok) {
            const err = await res.json();
            console.error("Bandh Hukum select error:", err);
            return;
        }
        const data = await res.json();
        const st = data.state || data;
        renderBindiCoatState(st);
        scheduleBindiCoatBotTurn(st);
    } catch (e) { console.error("Bandh Hukum select error:", e); }
}

async function submitBindiCoatPlay(cardCode) {
    try {
        const res = await fetch(`${API_BASE}/api/bindi-coat/play`, {
            method: "POST", headers: { "Content-Type": "application/json" },
            body: JSON.stringify({ game_id: currentGameId, player_id: "P1", card_code: cardCode })
        });
        if (!res.ok) { const e = await res.json(); alert(e.detail || "Play error"); return; }
        const data = await res.json();
        const st = data.state || data;
        renderBindiCoatState(st);
        scheduleBindiCoatBotTurn(st);
    } catch (e) { console.error("Bindi Coat play error:", e); }
}

function showBindiCoatSummary(summary) {
    const modal = document.getElementById("modal-bindicoat-summary");
    if (!modal) return;
    const winnerEl = document.getElementById("bindicoat-summary-winner");
    const detailsEl = document.getElementById("bindicoat-summary-details");
    const iconEl = document.getElementById("bindicoat-summary-icon");
    const titleEl = document.getElementById("bindicoat-summary-title");
    const vicType = summary.victory_type || "Regular";
    if (iconEl) iconEl.textContent = vicType === "WHITE_WASH" ? "💥" : vicType === "KOT" ? "🔥" : "🏆";
    if (titleEl) titleEl.textContent = vicType === "WHITE_WASH" ? "WHITE-WASH!" : vicType === "KOT" ? "KOT!" : "ROUND OVER!";
    if (winnerEl) winnerEl.textContent = `Team ${summary.winning_team} WINS!`;
    if (detailsEl) {
        detailsEl.innerHTML = `
            <div style="flex-direction:column;gap:8px;width:100%;text-align:center;">
                <div style="color:#4af;">🔵 NS: ${summary.ns_mindis} Mindis, ${summary.ns_tricks} Tricks</div>
                <div style="color:#f84;">🔴 EW: ${summary.ew_mindis} Mindis, ${summary.ew_tricks} Tricks</div>
                ${vicType !== "Regular" ? `<div style="color:#ffd700;font-weight:700;font-size:1.2rem;">${vicType}!</div>` : ""}
            </div>`;
    }
    modal.classList.remove("hidden");
}

function scheduleBindiCoatBotTurn(state) {
    if (!state || state.phase === "ROUND_SUMMARY") return;
    if (bindiCoatBotTimeout) { clearTimeout(bindiCoatBotTimeout); bindiCoatBotTimeout = null; }

    const needsBot = (state.phase === "BANDH_HUKUM_SELECTION" && !state.is_trump_placer) ||
        (state.phase === "PLAYING" && state.current_turn !== "P1");

    if (needsBot) {
        bindiCoatBotTimeout = setTimeout(triggerBindiCoatBotStep, 700);
    }
}

async function triggerBindiCoatBotStep() {
    bindiCoatBotTimeout = null;
    if (currentGameType !== "bindicoat") return;
    try {
        const res = await fetch(`${API_BASE}/api/bindi-coat/bot-step`, {
            method: "POST", headers: { "Content-Type": "application/json" },
            body: JSON.stringify({ game_id: currentGameId })
        });
        if (!res.ok) return;
        const data = await res.json();
        const st = data.state || data;
        renderBindiCoatState(st);
        scheduleBindiCoatBotTurn(st);
    } catch (e) { console.error("Bindi Coat bot step error:", e); }
}

// ── Wire up new game hub cards & start button ─────────────────────────────
(function wireNewGames() {
    // Jhuthaniya hub card
    const cardJh = document.getElementById("card-game-jhuthaniya");
    const btnGotoJh = document.getElementById("btn-goto-jhuthaniya");
    const onJhSelect = (e) => { e.stopPropagation(); switchActiveGame("jhuthaniya"); };
    if (cardJh) cardJh.addEventListener("click", onJhSelect);
    if (btnGotoJh) btnGotoJh.addEventListener("click", (e) => { e.stopPropagation(); onJhSelect(e); });

    // Bindi Coat hub card
    const cardBc = document.getElementById("card-game-bindicoat");
    const btnGotoBc = document.getElementById("btn-goto-bindicoat");
    const onBcSelect = (e) => { e.stopPropagation(); switchActiveGame("bindicoat"); };
    if (cardBc) cardBc.addEventListener("click", onBcSelect);
    if (btnGotoBc) btnGotoBc.addEventListener("click", (e) => { e.stopPropagation(); onBcSelect(e); });

    // Challenge modal buttons
    const btnCallBluff = document.getElementById("btn-jh-call-bluff");
    const btnPass = document.getElementById("btn-jh-pass");
    if (btnCallBluff) btnCallBluff.addEventListener("click", () => submitJhuthaniyaDecision("challenge"));
    if (btnPass) btnPass.addEventListener("click", () => submitJhuthaniyaDecision("pass"));

    // Jhuthaniya summary buttons
    const btnJhNewGame = document.getElementById("btn-jhuthaniya-new-game");
    const btnJhHome = document.getElementById("btn-jhuthaniya-go-home");
    if (btnJhNewGame) btnJhNewGame.addEventListener("click", async () => {
        document.getElementById("modal-jhuthaniya-summary").classList.add("hidden");
        await fetch(`${API_BASE}/api/jhuthaniya/new-game`, {
            method: "POST", headers: { "Content-Type": "application/json" },
            body: JSON.stringify({ game_id: currentGameId })
        }).then(r => r.json()).then(data => {
            renderJhuthaniyaState(data.state || data);
            scheduleJhuthaniyaBotTurn(data.state || data);
        });
    });
    if (btnJhHome) btnJhHome.addEventListener("click", () => {
        document.getElementById("modal-jhuthaniya-summary").classList.add("hidden");
        switchView("home");
    });

    // Bindi Coat summary buttons
    const btnBcNextRound = document.getElementById("btn-bindicoat-next-round");
    const btnBcHome = document.getElementById("btn-bindicoat-go-home");
    if (btnBcNextRound) btnBcNextRound.addEventListener("click", async () => {
        document.getElementById("modal-bindicoat-summary").classList.add("hidden");
        await fetch(`${API_BASE}/api/bindi-coat/next-round`, {
            method: "POST", headers: { "Content-Type": "application/json" },
            body: JSON.stringify({ game_id: currentGameId })
        }).then(r => r.json()).then(data => {
            const st = data.state || data;
            renderBindiCoatState(st);
            scheduleBindiCoatBotTurn(st);
        });
    });
    if (btnBcHome) btnBcHome.addEventListener("click", () => {
        document.getElementById("modal-bindicoat-summary").classList.add("hidden");
        switchView("home");
    });
})();

// ── Extend polling to include new games ───────────────────────────────────
// Patch into existing startSyncPolling by overriding fetchState
const _origFetchState = window.fetchCurrentState || null;
async function fetchCurrentState() {
    if (currentGameType === "tikdi") return fetchTikdiState();
    if (currentGameType === "jhuthaniya") return fetchJhuthaniyaState();
    if (currentGameType === "bindicoat") return fetchBindiCoatState();
    if (_origFetchState) return _origFetchState();
}
window.fetchCurrentState = fetchCurrentState;

// ==================== VIEW 4: ABOUT DEVELOPER PAGE (SAGAN PARIHARIYA) ====================
let aboutPreviousView = "home";

function openAboutDeveloperPage() {
    window.location.href = "about.html";
}
window.openAboutDeveloperPage = openAboutDeveloperPage;

function closeAboutDeveloperPage() {
    document.querySelectorAll(".view-container").forEach(v => v.classList.add("hidden"));
    if (aboutPreviousView === "table") {
        const viewTable = document.getElementById("view-table");
        if (viewTable) viewTable.classList.remove("hidden");
    } else {
        const viewHome = document.getElementById("view-home");
        if (viewHome) viewHome.classList.remove("hidden");
    }
}
window.closeAboutDeveloperPage = closeAboutDeveloperPage;

function toggleAboutLang() {
    const aboutBody = document.querySelector("#view-about .about-body");
    const btnLang = document.getElementById("btn-about-lang");
    if (aboutBody) {
        const isHi = aboutBody.classList.toggle("lang-hi");
        if (btnLang) {
            btnLang.textContent = isHi ? "🌐 EN" : "🌐 HI";
        }
    }
}
window.toggleAboutLang = toggleAboutLang;

