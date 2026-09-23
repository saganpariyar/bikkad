// Localization (i18n) Dictionary and Controller for Bikkad Card Game
// Full bilingual support: English (en) & conversational Hinglish / Hindi in Latin script (hi)

const translations = {
    en: {
        // Brand & Subtitle
        brandTitle: "DESI CARD GAMES",
        brandSubtitle: "Traditional Indian & Rajasthani Card Games Hub",
        developedBy: "Owned & Developed by",
        devCredit: "Owned & Developed by <strong>Sobha IT Solutions</strong> · Founded by <strong>Sagan & Anita Parihariya</strong>",
        devCreditTop: "Owned by <strong>Sobha IT Solutions</strong>",
        rulesAndAbout: "📜 Games & Features",

        // Games Hub Bar
        hubTitle: "DESI CARD GAMES COLLECTION",
        hubSub: "Select any traditional Indian or Rajasthani card game below — Bikkad is live now with more classics arriving soon!",
        hubPill: "6 Games",
        statusLive: "🟢 LIVE NOW",
        statusSoon: "🔒 COMING SOON",
        btnPlayBikkad: "▶ Play Bikkad",
        comingSoonBadge: "Coming Soon",
        toastComingSoon: "{game} is coming soon to the Desi Card Games Hub! Stay tuned.",
        genreBikkad: "Pot Sweep & Ladder",
        genreJhuthaniya: "Bluff & Deception",
        genreGadhaBaji: "Donkey Card Elimination",
        genreSarkari: "Rule-Bound Trump Clash",
        genreBindiCoat: "Point Coat & Sweeps",
        genreTikdi: "Tri-Card Rajasthani Arena",

        // Home Hero Section (Generic Portal)
        heroBadge: "🏜️ TRADITIONAL DESI & RAJASTHANI CARD GAMES HUB",
        heroTitle: "Play Classic Desi Card Games <span class=\"highlight-gold\">Online with Friends</span>",
        heroLead: "Apne Rajasthan aur Bharat ke sabse lokpriya aur shandar traditional card games ka digital adda! Experience authentic regional rules preserved faithfully, royal court cards, smart bots, and private rooms with friends. Start playing <strong>Bikkad</strong> right now, or explore our upcoming games like Jhuthaniya, Gadha Baji, Sarkari, Bindi Coat, and Tikdi!",
        
        rulePlatformTitle1: "Authentic Regional Rules",
        rulePlatformDesc1: "Traditional rules, scoring ladders, and trick formats preserved faithfully from real village card traditions.",
        rulePlatformTitle2: "Classic Royal Playing Cards",
        rulePlatformDesc2: "High-resolution vector cards with traditional reversible Jack, Queen, and King royal artwork.",
        rulePlatformTitle3: "Multiplayer & Smart BOTs",
        rulePlatformDesc3: "Create instant 4-digit code rooms to play with friends, or enjoy smart solo play against adaptive bots.",
        rulePlatformTitle4: "Cultural Heritage Mission",
        rulePlatformDesc4: "Crafted with love by Sobha IT Solutions to preserve, celebrate, and digitize traditional desi card games.",

        activeGameBannerBadge: "Now playing Bikkad:",
        activeGameBannerDesc: "Set up your match below — Play Solo vs BOTs or invite friends using a simple 4-digit Room Code!",
        footerBrandText: "🏜️ <strong>Desi Card Games Hub</strong> · Traditional Indian & Rajasthani Card Games Collection",

        // Setup & Lobby Card
        yourPlayerNameLabel: "👤 Your Player Name:",
        yourPlayerNamePlaceholder: "Enter your name",
        tabCreateGame: "🎮 Create New Game",
        tabJoinGame: "🔗 Join Game with Code",
        gameNameLabel: "Game Name:",
        setupModeLabel: "Group & BOT Setup:",
        setupMode13: "1 Human + 3 BOTs (Solo vs Bots)",
        setupMode22: "2 Humans + 2 BOTs (Host + Partner vs Bots)",
        setupMode31: "3 Humans + 1 BOT (3 Humans vs 1 Bot)",
        setupMode40: "4 Humans + 0 BOTs (All 4 Humans)",
        trumpHiderLabel: "🃏 Player to Hide Trump & Start First Deal:",
        trumpHiderRandom: "🎲 Random (Player 1, 2, 3, or 4 chosen randomly)",
        roomIdLabel: "ROOM ID / CODE:",
        btnCopyCode: "📋 Copy Code",
        btnCopied: "Copied! ✓",
        shareCodeHint: "Share this code with friends so they can join!",
        seatAllocTitle: "👥 Team & Seat Allocation (Host Chooses P2, P3, P4)",
        seatAllocSub: "Assign partner and opponents as either Joined Friends or BOTs:",
        teamAHeader: "🏆 Team A (Your Team)",
        teamBHeader: "🛡️ Team B (Opponents)",
        hostBadge: "HOST (You)",
        partnerBadge: "PARTNER",
        oppBadge1: "OPPONENT 1",
        oppBadge2: "OPPONENT 2",
        optBot: "BOT",
        optHuman: "Human Friend",
        btnStartMatch: "🚀 Start Match",

        // Join Tab
        joinTitle: "Join an Existing Game",
        joinSub: "Enter the Unique Game ID provided by the host:",
        joinCodeLabel: "Game ID / Code:",
        btnJoinRoom: "🔗 Join Game Room",

        // Home Footer
        footerTagline: "🏜️ <strong>Apna Rajasthan Ka Bikkad</strong>",
        footerDev: "Owned & Developed with passion by <strong>Sobha IT Solutions</strong> (Sagan & Anita Parihariya)",
        footerKnowDev: "👑 About: <strong>Sobha IT Solutions</strong>",
        sidebarKnowDev: "👑 About: <strong>Sobha IT Solutions</strong>",

        // Game Arena Header Actions
        btnNewGame: "New Game",
        btnRestartDeal: "Restart Deal",
        btnNextDeal: "Next Deal",
        btnScore: "Score",
        btnSound: "Sound",
        btnSettings: "Settings",

        // Status Badges
        contractRegular: "Contract: 🃏 Regular",
        contractTera: "Contract: 🔥 TERA",
        contractDoubleTera: "Contract: ⚡ DOUBLE TERA",
        dealerLabel: "Dealer",
        turnLabel: "Turn",
        yourTurn: "Your Turn! (Play a Card)",
        waitingFor: "Waiting for",
        selectHiddenTrump: "Select Hidden Trump (Click 1 Card Below)",
        dealFinished: "Round Finished! (Click Next Deal)",
        roundCompleteWin: "Won the Deal! Click ⏭ Next Deal to Continue",

        // Seat & Role Badges
        youTag: "(You)",
        partnerTag: "(Partner)",
        dealerRole: "🎴 DEALER (Gives Cards)",
        hidesTrumpRole: "🃏 HIDES TRUMP",
        playsFirstRole: "PLAYS FIRST",
        dealWinnerRole: "🏆 DEAL WINNER",
        sitsOutRole: "💤 SITS OUT (Solo)",
        cardsCount: "cards",

        // Card Names & Suits
        suitSpades: "SPADES",
        suitHearts: "HEARTS",
        suitDiamonds: "DIAMONDS",
        suitClubs: "CLUBS",
        rankAce: "Ace",
        rankKing: "King",
        rankQueen: "Queen",
        rankJack: "Jack",

        // Center Arena & Pot
        hiddenTrump: "HIDDEN TRUMP",
        runtimeTrump: "RUNTIME TRUMP",
        selectingTrump: "SELECTING...",
        noHiddenTrump: "NO HIDDEN TRUMP",
        openTrumpBtn: "🔓 Open Trump",
        pickTrumpBtn: "🎯 Pick Trump",
        askTrumpBtn: "🎺 Ask Trump",
        centerPotTitle: "CENTER POT",
        cardsLabel: "Cards",
        tricksLabel: "Tricks",
        streakLabel: "Streak",
        streakNone: "Streak: None",

        // Banners & Notifications
        eldestHandTitle: "🃏 YOU ARE ELDEST HAND:",
        eldestHandSub: "First 5 cards dealt! Click 1 card below to hide as the Trump Card.",
        trumpRevealedTag: "RANG KHUL GAYA • TRUMP REVEALED",
        demandedTrumpShow: "demanded Trump Show!",
        activeTrumpLbl: "Active Trump:",

        // Contract Declaration Bar
        declareContractPrompt: "🏆 Declare Contract:",
        btnGoTera: "🔥 Tera",
        btnGoDoubleTera: "⚡ Double Tera",

        // Controls
        botsAutoPlaying: "🤖 BOTs: Auto-Playing",
        botsPaused: "🤖 BOTs: Paused",
        pauseBotsBtn: "⏸ Pause BOTs",
        resumeBotsBtn: "▶ Resume BOTs",
        speedLabel: "Speed:",

        // Sidebar Scoreboard
        scoreDrawerTitle: "📊 Scoreboard & Ledger",
        scoreboardTitle: "🏆 Scoreboard & Ladder",
        matchLedgerTitle: "📜 Round Match Ledger",
        activeDealer: "Active Dealer:",
        dealerBurdenScore: "Dealer Burden Score:",

        // Modals
        modalTrumpSelectTitle: "🎺 SELECT TRUMP SUIT",
        modalTrumpSelectDesc: "A void occurred! As Declarer, choose the Trump Suit for this round:",
        modalSettingsTitle: "⚙ Lobby & Player Settings",
        matchTypeLabel: "Match Type Setup:",
        saveSettingsBtn: "Save Settings",
        closeBtn: "Close",
        dealOverTitle: "DEAL OVER!",

        // Tikdi (3-2-5)
        btnPlayTikdi: "▶ Play Tikdi (3P)",
        gameTabBikkad: "🂠 1. Bikkad (4P)",
        gameTabTikdi: "🔺 6. Tikdi (3-2-5)",
        tikdiTitle: "Tikdi (Teen Do Paanch / 3-2-5)",
        tikdiSetupSub: "3-Player Classic: P1 Dealer (Quota 2), P2 Trump Chooser (Quota 5), P3 Bystander (Quota 3)",
        tikdiMode12: "1 Human + 2 BOTs (Solo vs Bots)",
        tikdiMode21: "2 Humans + 1 BOT",
        tikdiMode30: "3 Humans (All 3 Friends)",
        tikdiQuotaBadge: "Quota: {quota} | Won: {won}",
        tikdiPenaltyTitle: "⚡ TIKDI PENALTY CARD SETTLEMENT",
        tikdiPenaltyPullPrompt: "{puller} won extra tricks! Click a face-down card from {target}'s hand to PULL blindly:",
        tikdiPenaltyReturnPrompt: "Pulled {card}! Now select a card from your hand to RETURN to {target}:",
        tikdiReturnConfirm: "Return Card",
        tikdiRoundOver: "TIKDI ROUND OVER!",
        tikdiNextRoundBtn: "Next Tikdi Round ⏭",

        // Voice Calls
        voiceHukumDikhao: "Hukum dikhao!",
        voiceAkka: "Akka!",
        voiceTera: "{player} ki Tera!",
        voiceDoubleTera: "{player} ki Double Tera!",
        mustPlayTrumpToast: "You asked for Trump! You must play a Trump card from your hand.",
        mustFollowSuit: "Must follow led suit!"
    },

    hi: {
        // Brand & Subtitle (Hinglish / Hindi in Latin script)
        // Brand & Subtitle (Hinglish / Hindi in Latin script)
        brandTitle: "DESI TAAS KHEL",
        brandSubtitle: "Traditional Indian & Rajasthani Taas Khel Hub",
        developedBy: "Swamitva",
        devCredit: "स्वामित्व एवं निर्माण: <strong>शोभा आईटी सॉल्यूशंस</strong> (सगन एवं अनिता परिहारिया)",
        devCreditTop: "Owned by <strong>Sobha IT Solutions</strong>",
        rulesAndAbout: "📜 Khel aur Niyam",

        // Games Hub Bar
        hubTitle: "DESI TAAS KHEL COLLECTION",
        hubSub: "Desi taas ka koi bhi khel chuno — Bikkad abhi chalu hai aur baaki naye khel jald hi aa rahe hain!",
        hubPill: "6 Khel",
        statusLive: "🟢 CHALU HAI",
        statusSoon: "🔒 JALD HI",
        btnPlayBikkad: "▶ Bikkad Khelein",
        comingSoonBadge: "Jald Hi",
        toastComingSoon: "{game} jald hi Desi Taas Hub par aa raha hai! Abhi Bikkad active hai.",
        genreBikkad: "Beech Ki Pot aur Seedi",
        genreJhuthaniya: "Jhooth aur Chaalaki",
        genreGadhaBaji: "Gadha Baji Daav",
        genreSarkari: "Sarkari Hukum Niyam",
        genreBindiCoat: "Bindi Coat aur Sweep",
        genreTikdi: "Teen Patta Tikdi",

        // Home Hero Section (Generic Portal)
        heroBadge: "🏜️ TRADITIONAL DESI AUR RAJASTHANI TAAS KHEL HUB",
        heroTitle: "Asli Desi Taas Khel <span class=\"highlight-gold\">Dosto Ke Saath Khelein</span>",
        heroLead: "Apne Rajasthan aur Bharat ke sabse lokpriya aur shandar traditional taas ke khel ek hi jagah! Asli desi niyam, shandar royal patte, smart bots, aur private room code se dosto ke saath khelne ki suvidha. <strong>Bikkad</strong> abhi khelein, aur dekhein aane wale naye khel jaise Jhuthaniya, Gadha Baji, Sarkari, Bindi Coat, aur Tikdi!",
        
        rulePlatformTitle1: "Asli Desi Niyam",
        rulePlatformDesc1: "Gaon aur dharohar se jude pakke niyam, scoring seedi, aur traditional trick niyam.",
        rulePlatformTitle2: "Shandar Royal Taas Patte",
        rulePlatformDesc2: "High-definition vector patte asli Raja, Rani, aur Gulaam ki classic kala ke saath.",
        rulePlatformTitle3: "Multiplayer aur Smart BOTs",
        rulePlatformDesc3: "Aasan 4-digit room code se dosto ke saath khelein ya smart BOTs ke khilaf solo daav lagayein.",
        rulePlatformTitle4: "सांस्कृतिक विरासत मिशन",
        rulePlatformDesc4: "राजस्थान और भारत के पारंपरिक ताश के खेलों को डिजिटल रूप में सहेजने का आधुनिक प्रयास।",

        activeGameBannerBadge: "Abhi chalu khel: Bikkad:",
        activeGameBannerDesc: "Neeche apna match set karein — BOTs ke saath akele khelein ya 4-digit Room Code se dosto ko bulayein!",
        footerBrandText: "🏜️ <strong>Desi Taas Khel Hub</strong> · Traditional Indian & Rajasthani Taas Collection",

        // Setup & Lobby Card
        yourPlayerNameLabel: "👤 Aapka Naam:",
        yourPlayerNamePlaceholder: "Apna naam daalein",
        tabCreateGame: "🎮 Naya Khel Banao",
        tabJoinGame: "🔗 Room Code Se Judey",
        gameNameLabel: "Khel Ka Naam:",
        setupModeLabel: "Khiladi aur BOT Chunav:",
        setupMode13: "1 Insaan + 3 BOTs (Akele vs BOTs)",
        setupMode22: "2 Insaan + 2 BOTs (Aap + Saathi vs BOTs)",
        setupMode31: "3 Insaan + 1 BOT (3 Dost vs 1 Bot)",
        setupMode40: "4 Insaan + 0 BOTs (Sabhi 4 Dost)",
        trumpHiderLabel: "🃏 Pehli Baant Me Hukum Kaun Chhupayega:",
        trumpHiderRandom: "🎲 Random (Kisi bhi khiladi se shuru)",
        roomIdLabel: "ROOM ID / CODE:",
        btnCopyCode: "📋 Code Copy Karein",
        btnCopied: "Copy Ho Gaya! ✓",
        shareCodeHint: "Dosto ko ye code bhejo taaki wo jud sakein!",
        seatAllocTitle: "👥 Team aur Seat Batwara (Host Chunta Hai P2, P3, P4)",
        seatAllocSub: "Apne saathi aur virodhi ko dost ya BOT ke roop me chuno:",
        teamAHeader: "🏆 Team A (Aapki Team)",
        teamBHeader: "🛡️ Team B (Virodhi Team)",
        hostBadge: "HOST (Aap)",
        partnerBadge: "SAATHI",
        oppBadge1: "VIRODHI 1",
        oppBadge2: "VIRODHI 2",
        optBot: "BOT",
        optHuman: "Dost (Online)",
        btnStartMatch: "🚀 Khel Shuru Karein",

        // Join Tab
        joinTitle: "Pehle se bane Khel me Judey",
        joinSub: "Host dwara diya gaya Unique Game Code daalein:",
        joinCodeLabel: "Game ID / Code:",
        btnJoinRoom: "🔗 Khel Room Me Judey",

        // Home Footer
        footerTagline: "🏜️ <strong>Apna Rajasthan Ka Bikkad</strong>",
        footerDev: "शोभा आईटी सॉल्यूशंस (सगन एवं अनिता परिहारिया) द्वारा विकसित",
        footerKnowDev: "👑 अबाउट: <strong>शोभा आईटी सॉल्यूशंस</strong>",
        sidebarKnowDev: "👑 अबाउट: <strong>शोभा आईटी सॉल्यूशंस</strong>",

        // Game Arena Header Actions
        btnNewGame: "Naya Khel",
        btnRestartDeal: "Dobara Baanto",
        btnNextDeal: "Agli Baant",
        btnScore: "Score",
        btnSound: "Awaaz",
        btnSettings: "Settings",

        // Status Badges
        contractRegular: "Khel: 🃏 Sadharan",
        contractTera: "Khel: 🔥 TERA",
        contractDoubleTera: "Khel: ⚡ DOUBLE TERA",
        dealerLabel: "Baantnewala",
        turnLabel: "Chaali",
        yourTurn: "Aapki Chaali! (Patta Chalo)",
        waitingFor: "Intezaar:",
        selectHiddenTrump: "Hukum Chhupao (Neeche se 1 Patta Chuno)",
        dealFinished: "Baant Poori! (Agli Baant par click karein)",
        roundCompleteWin: "Baant Jeet Gaye! Agli Baant par click karein",

        // Seat & Role Badges
        youTag: "(Aap)",
        partnerTag: "(Saathi)",
        dealerRole: "🎴 PATTE BAANTNE WALA",
        hidesTrumpRole: "🃏 HUKUM CHHUPANE WALA",
        playsFirstRole: "PEHLI CHAALI",
        dealWinnerRole: "🏆 BAANT JEETA",
        sitsOutRole: "💤 BAITHA HAI (Solo Daav)",
        cardsCount: "patte",

        // Card Names & Suits (Traditional Indian / Rajasthani)
        suitSpades: "HUKUM",
        suitHearts: "PAAN",
        suitDiamonds: "EENT",
        suitClubs: "CHIDI",
        rankAce: "Akka",
        rankKing: "Badshah",
        rankQueen: "Begum",
        rankJack: "Ghulam",

        // Center Arena & Pot
        hiddenTrump: "BANDH HUKUM",
        runtimeTrump: "CHALTI HUKUM",
        selectingTrump: "CHUN RAHE HAIN...",
        noHiddenTrump: "KOI BANDH HUKUM NAHI",
        openTrumpBtn: "🔓 Hukum Dikhao",
        pickTrumpBtn: "🎯 Hukum Chuno",
        askTrumpBtn: "🎺 Hukum Poochho",
        centerPotTitle: "BEECH KI POT",
        cardsLabel: "Patte",
        tricksLabel: "Haath/Chaali",
        streakLabel: "Lagatar",
        streakNone: "Lagatar: Koi nahi",

        // Banners & Notifications
        eldestHandTitle: "🃏 AAP ELDEST HAND HAIN:",
        eldestHandSub: "Pehle 5 patte mile! Neeche se 1 patta Bandh Hukum ke liye chuno.",
        trumpRevealedTag: "RANG KHUL GAYA • HUKUM SAMNE",
        demandedTrumpShow: "ne Hukum Dikhaane ko kaha!",
        activeTrumpLbl: "Khula Hukum:",

        // Contract Declaration Bar
        declareContractPrompt: "🏆 Boli Lagao:",
        btnGoTera: "🔥 Tera",
        btnGoDoubleTera: "⚡ Double Tera",

        // Controls
        botsAutoPlaying: "🤖 BOTs: Khel Rahe Hain",
        botsPaused: "🤖 BOTs: Ruke Hue Hain",
        pauseBotsBtn: "⏸ Roko",
        resumeBotsBtn: "▶ Shuru Karo",
        speedLabel: "Raftaar:",

        // Sidebar Scoreboard
        scoreDrawerTitle: "📊 Scoreboard aur Khata",
        scoreboardTitle: "🏆 Scoreboard aur Seedi",
        matchLedgerTitle: "📜 Khel Ka Khata (Ledger)",
        activeDealer: "Patte Baantne Wala:",
        dealerBurdenScore: "Dealer Ka Bojh Score:",

        // Modals
        modalTrumpSelectTitle: "🎺 HUKUM KA RANG CHUNO",
        modalTrumpSelectDesc: "Patta toot gaya! Tera lene wale, is daav ke liye Hukum ka Rang chuno:",
        modalSettingsTitle: "⚙ Khel aur AI Settings",
        matchTypeLabel: "Khel Ka Setup:",
        saveSettingsBtn: "Settings Bachao",
        closeBtn: "Band Karein",
        dealOverTitle: "BAANT POORI!",

        // Tikdi (3-2-5)
        btnPlayTikdi: "▶ Tikdi Khelein (3P)",
        gameTabBikkad: "🂠 1. Bikkad (4P)",
        gameTabTikdi: "🔺 6. Tikdi (3-2-5)",
        tikdiTitle: "Tikdi (Teen Do Paanch / 3-2-5)",
        tikdiSetupSub: "3 Khiladiyon ka Khel: P1 Dealer (Quota 2), P2 Hukum Chune (Quota 5), P3 Saathi (Quota 3)",
        tikdiMode12: "1 Insaan + 2 BOTs (Solo Khelein)",
        tikdiMode21: "2 Insaan + 1 BOT",
        tikdiMode30: "3 Insaan (Teeno Dost)",
        tikdiQuotaBadge: "Kharid: {quota} | Haath: {won}",
        tikdiPenaltyTitle: "⚡ TIKDI DAND AUR PATTA CHUNAV",
        tikdiPenaltyPullPrompt: "{puller} ne quota se zyada haath jeete! {target} ke patton me se ek anjan patta khicho:",
        tikdiPenaltyReturnPrompt: "Khicha gaya patta {card}! Ab apne haath se ek patta {target} ko wapas dene ke liye chuno:",
        tikdiReturnConfirm: "Patta Wapas Do",
        tikdiRoundOver: "TIKDI ROUND POORA HUA!",
        tikdiNextRoundBtn: "Agla Tikdi Round ⏭",

        // Voice Calls
        voiceHukumDikhao: "Hukum dikhao!",
        voiceAkka: "Akka!",
        voiceTera: "{player} ki Tera!",
        voiceDoubleTera: "{player} ki Double Tera!",
        mustPlayTrumpToast: "Hukum (Trump) maanga hai! Haath se Trump card hi chalna hoga.",
        mustFollowSuit: "Jo rang chala hai wahi chalna padega!"
    }
};

let currentLang = localStorage.getItem("bikkad_lang") || "en";

function t(key) {
    if (translations[currentLang] && translations[currentLang][key]) {
        return translations[currentLang][key];
    }
    if (translations.en && translations.en[key]) {
        return translations.en[key];
    }
    return key;
}

function getCurrentLanguage() {
    return currentLang;
}

function setLanguage(lang) {
    if (translations[lang]) {
        currentLang = lang;
        localStorage.setItem("bikkad_lang", lang);
        applyLanguageToDOM();
    }
}

function toggleLanguage() {
    const nextLang = (currentLang === "en") ? "hi" : "en";
    setLanguage(nextLang);
    return nextLang;
}

function applyLanguageToDOM() {
    const isHi = (currentLang === "hi");

    // 1. Language Toggle Buttons
    const langBtns = [document.getElementById("btn-lang-toggle"), document.getElementById("btn-home-lang-toggle")];
    langBtns.forEach(btn => {
        if (btn) {
            btn.textContent = isHi ? "🌐 EN" : "🌐 HI";
            btn.title = isHi ? "Switch to English" : "Switch to Hinglish / Hindi";
        }
    });

    // 2. Generic [data-i18n] elements
    document.querySelectorAll("[data-i18n]").forEach(el => {
        const key = el.getAttribute("data-i18n");
        if (key && translations[currentLang] && translations[currentLang][key]) {
            el.innerHTML = t(key);
        }
    });

    // 2b. Games Hub Bar Elements
    const hubTitleEl = document.getElementById("games-hub-title");
    if (hubTitleEl) hubTitleEl.textContent = t("hubTitle");

    const hubSubEl = document.getElementById("games-hub-sub");
    if (hubSubEl) hubSubEl.textContent = t("hubSub");

    const hubPillEl = document.getElementById("hub-pill");
    if (hubPillEl) hubPillEl.textContent = t("hubPill");

    const statusLiveEl = document.getElementById("status-live-pill");
    if (statusLiveEl) statusLiveEl.textContent = t("statusLive");

    document.querySelectorAll(".status-soon").forEach(el => {
        el.textContent = t("statusSoon");
    });

    const btnGotoBikkad = document.getElementById("btn-goto-bikkad");
    if (btnGotoBikkad) btnGotoBikkad.textContent = t("btnPlayBikkad");

    document.querySelectorAll(".coming-soon-badge").forEach(el => {
        el.textContent = t("comingSoonBadge");
    });

    const gBikkad = document.getElementById("genre-bikkad");
    if (gBikkad) gBikkad.textContent = t("genreBikkad");
    const gJhuthaniya = document.getElementById("genre-jhuthaniya");
    if (gJhuthaniya) gJhuthaniya.textContent = t("genreJhuthaniya");
    const gGadhaBaji = document.getElementById("genre-gadhabaji");
    if (gGadhaBaji) gGadhaBaji.textContent = t("genreGadhaBaji");
    const gSarkari = document.getElementById("genre-sarkari");
    if (gSarkari) gSarkari.textContent = t("genreSarkari");
    const gBindiCoat = document.getElementById("genre-bindicoat");
    if (gBindiCoat) gBindiCoat.textContent = t("genreBindiCoat");
    const gTikdi = document.getElementById("genre-tikdi");
    if (gTikdi) gTikdi.textContent = t("genreTikdi");

    // 3. HOME VIEW ELEMENTS
    // Header Brand & Links
    const homeBrandTitle = document.getElementById("home-brand-title");
    if (homeBrandTitle) homeBrandTitle.textContent = t("brandTitle");
    const homeBrandSub = document.getElementById("home-brand-sub");
    if (homeBrandSub) homeBrandSub.textContent = t("brandSubtitle");

    const homeRulesLink = document.querySelector(".home-nav-actions a[href='#rules-section']");
    if (homeRulesLink) homeRulesLink.textContent = t("rulesAndAbout");

    // Hero Section
    const heroTitle = document.querySelector(".hero-title");
    if (heroTitle) heroTitle.innerHTML = t("heroTitle");

    const heroLead = document.querySelector(".hero-lead");
    if (heroLead) heroLead.innerHTML = t("heroLead");

    const heroBadge = document.querySelector(".hero-badge");
    if (heroBadge) heroBadge.textContent = t("heroBadge");

    const heroDevCredit = document.querySelector(".hero-dev-credit span:last-child");
    if (heroDevCredit) heroDevCredit.innerHTML = t("devCredit");

    // Platform Highlights Grid
    const ruleCards = document.querySelectorAll(".rules-highlight-grid .rule-card");
    if (ruleCards.length >= 4) {
        const h0 = ruleCards[0].querySelector("h4");
        const p0 = ruleCards[0].querySelector("p");
        if (h0) h0.textContent = t("rulePlatformTitle1");
        if (p0) p0.textContent = t("rulePlatformDesc1");

        const h1 = ruleCards[1].querySelector("h4");
        const p1 = ruleCards[1].querySelector("p");
        if (h1) h1.textContent = t("rulePlatformTitle2");
        if (p1) p1.textContent = t("rulePlatformDesc2");

        const h2 = ruleCards[2].querySelector("h4");
        const p2 = ruleCards[2].querySelector("p");
        if (h2) h2.textContent = t("rulePlatformTitle3");
        if (p2) p2.textContent = t("rulePlatformDesc3");

        const h3 = ruleCards[3].querySelector("h4");
        const p3 = ruleCards[3].querySelector("p");
        if (h3) h3.textContent = t("rulePlatformTitle4");
        if (p3) p3.textContent = t("rulePlatformDesc4");
    }

    // Active Game Banner & Footer Brand
    const activeGameBadge = document.getElementById("active-game-banner-badge");
    if (activeGameBadge) activeGameBadge.textContent = t("activeGameBannerBadge");
    const activeGameDesc = document.getElementById("active-game-banner-desc");
    if (activeGameDesc) activeGameDesc.textContent = t("activeGameBannerDesc");

    const homeFooterBrand = document.getElementById("home-footer-brand");
    if (homeFooterBrand) homeFooterBrand.innerHTML = t("footerBrandText");

    // Identity Box
    const identityLabel = document.querySelector("label[for='input-your-name']");
    if (identityLabel) identityLabel.textContent = t("yourPlayerNameLabel");
    const inputYourName = document.getElementById("input-your-name");
    if (inputYourName) inputYourName.placeholder = t("yourPlayerNamePlaceholder");

    // Tabs
    const tabCreate = document.getElementById("tab-btn-create");
    if (tabCreate) tabCreate.textContent = t("tabCreateGame");
    const tabJoin = document.getElementById("tab-btn-join");
    if (tabJoin) tabJoin.textContent = t("tabJoinGame");

    // Form Labels
    const lblGameName = document.querySelector("label[for='input-game-name']");
    if (lblGameName) lblGameName.textContent = t("gameNameLabel");

    const lblSetupMode = document.querySelector("label[for='select-setup-mode']");
    if (lblSetupMode) lblSetupMode.textContent = t("setupModeLabel");

    const selectSetupMode = document.getElementById("select-setup-mode");
    if (selectSetupMode) {
        const o1 = selectSetupMode.querySelector("option[value='1-3 com']");
        if (o1) o1.textContent = t("setupMode13");
        const o2 = selectSetupMode.querySelector("option[value='2-2 com']");
        if (o2) o2.textContent = t("setupMode22");
        const o3 = selectSetupMode.querySelector("option[value='3-1 com']");
        if (o3) o3.textContent = t("setupMode31");
        const o4 = selectSetupMode.querySelector("option[value='4-0 com']");
        if (o4) o4.textContent = t("setupMode40");
    }

    const lblTrumpHider = document.querySelector("label[for='select-trump-hider']");
    if (lblTrumpHider) lblTrumpHider.textContent = t("trumpHiderLabel");

    const selectTrumpHider = document.getElementById("select-trump-hider");
    if (selectTrumpHider) {
        const optRand = selectTrumpHider.querySelector("option[value='random']");
        if (optRand) optRand.textContent = t("trumpHiderRandom");
    }

    // Room ID Banner
    const roomIdLbl = document.querySelector(".room-id-label");
    if (roomIdLbl) roomIdLbl.textContent = t("roomIdLabel");

    const btnCopyRoom = document.getElementById("btn-copy-room-id");
    if (btnCopyRoom && !btnCopyRoom.textContent.includes("✓")) {
        btnCopyRoom.textContent = t("btnCopyCode");
    }

    const roomHint = document.querySelector(".room-id-hint");
    if (roomHint) roomHint.textContent = t("shareCodeHint");

    // Seat Allocation
    const seatAllocH4 = document.querySelector(".seat-allocation-header h4");
    if (seatAllocH4) seatAllocH4.textContent = t("seatAllocTitle");

    const seatSubtext = document.querySelector(".seat-subtext");
    if (seatSubtext) seatSubtext.textContent = t("seatAllocSub");

    const teamABoxHeader = document.querySelector(".team-a-box .team-box-header");
    if (teamABoxHeader) teamABoxHeader.textContent = t("teamAHeader");

    const teamBBoxHeader = document.querySelector(".team-b-box .team-box-header");
    if (teamBBoxHeader) teamBBoxHeader.textContent = t("teamBHeader");

    const hostBadge = document.querySelector(".host-badge");
    if (hostBadge) hostBadge.textContent = t("hostBadge");

    const partnerBadge = document.querySelector(".partner-badge");
    if (partnerBadge) partnerBadge.textContent = t("partnerBadge");

    const oppBadges = document.querySelectorAll(".opp-badge");
    if (oppBadges.length >= 2) {
        oppBadges[0].textContent = t("oppBadge1");
        oppBadges[1].textContent = t("oppBadge2");
    }

    // Select type options in seat cards
    document.querySelectorAll(".seat-type-select").forEach(sel => {
        const optAi = sel.querySelector("option[value='ai']");
        if (optAi) optAi.textContent = t("optBot");
        const optHuman = sel.querySelector("option[value='human']");
        if (optHuman) optHuman.textContent = t("optHuman");
    });

    const btnStartGame = document.getElementById("btn-start-game");
    if (btnStartGame) btnStartGame.textContent = t("btnStartMatch");

    // Join Game Tab Content
    const joinH3 = document.querySelector(".join-form-box h3");
    if (joinH3) joinH3.textContent = t("joinTitle");

    const joinSub = document.querySelector(".join-sub");
    if (joinSub) joinSub.textContent = t("joinSub");

    const lblJoinId = document.querySelector("label[for='input-join-id']");
    if (lblJoinId) lblJoinId.textContent = t("joinCodeLabel");

    const btnSubmitJoin = document.getElementById("btn-submit-join");
    if (btnSubmitJoin) btnSubmitJoin.textContent = t("btnJoinRoom");

    // Footer & Sidebar About Developer
    const footerDev = document.querySelector(".footer-dev");
    if (footerDev) footerDev.innerHTML = t("footerDev");
    const footerAbout = document.getElementById("footer-about-btn");
    if (footerAbout) footerAbout.innerHTML = t("footerKnowDev");
    const sidebarAbout = document.getElementById("sidebar-about-btn");
    if (sidebarAbout) sidebarAbout.innerHTML = t("sidebarKnowDev");

    // Sync About Developer View Language
    const btnAboutLang = document.getElementById("btn-about-lang");
    if (btnAboutLang) btnAboutLang.textContent = isHi ? "🌐 EN" : "🌐 HI";
    const aboutBody = document.querySelector(".about-body");
    if (aboutBody) aboutBody.classList.toggle("lang-hi", isHi);

    // 4. TABLE VIEW ELEMENTS
    // Header Action Buttons
    const lblNewGame = document.querySelector("#btn-header-new-game .btn-label");
    if (lblNewGame) lblNewGame.textContent = t("btnNewGame");

    const lblRestartDeal = document.querySelector("#btn-restart-deal .btn-label");
    if (lblRestartDeal) lblRestartDeal.textContent = t("btnRestartDeal");

    const lblNextDeal = document.querySelector("#btn-next-deal .btn-label");
    if (lblNextDeal) lblNextDeal.textContent = t("btnNextDeal");

    // Banners
    const eldestTitle = document.querySelector("#trump-hide-banner .banner-title");
    if (eldestTitle) eldestTitle.textContent = t("eldestHandTitle");

    const eldestSub = document.querySelector("#trump-hide-banner .banner-sub");
    if (eldestSub) eldestSub.textContent = t("eldestHandSub");

    // Contract Bar
    const contractPrompt = document.querySelector(".contract-prompt");
    if (contractPrompt) contractPrompt.textContent = t("declareContractPrompt");

    const btnTera = document.getElementById("btn-bid-tera");
    if (btnTera) btnTera.textContent = t("btnGoTera");

    const btnDoubleTera = document.getElementById("btn-bid-double-tera");
    if (btnDoubleTera) btnDoubleTera.textContent = t("btnGoDoubleTera");

    // Arena Action Buttons
    const btnOpenTrump = document.getElementById("btn-demand-cut");
    if (btnOpenTrump) btnOpenTrump.textContent = t("openTrumpBtn");

    const btnPickTrump = document.getElementById("btn-declare-runtime-trump");
    if (btnPickTrump) btnPickTrump.textContent = t("pickTrumpBtn");

    const btnAskTrump = document.getElementById("btn-ask-trump");
    if (btnAskTrump) btnAskTrump.textContent = t("askTrumpBtn");

    // Center Pot
    const potTitle = document.querySelector(".pot-title");
    if (potTitle) potTitle.textContent = t("centerPotTitle");

    const potCardLbl = document.querySelectorAll(".pot-lbl");
    if (potCardLbl.length >= 2) {
        potCardLbl[0].textContent = t("cardsLabel");
        potCardLbl[1].textContent = t("tricksLabel");
    }

    // Bot Controls
    const botStatusText = document.getElementById("bot-status-text");
    if (botStatusText) {
        if (window.isBotPlayPaused) {
            botStatusText.textContent = t("botsPaused");
        } else {
            botStatusText.textContent = t("botsAutoPlaying");
        }
    }

    const btnPauseBots = document.getElementById("btn-pause-bots");
    if (btnPauseBots) {
        btnPauseBots.textContent = window.isBotPlayPaused ? t("resumeBotsBtn") : t("pauseBotsBtn");
    }

    const speedLbl = document.querySelector(".speed-control label");
    if (speedLbl) speedLbl.textContent = t("speedLabel");

    // Sidebar Scoreboard
    const drawerTitle = document.querySelector(".drawer-title");
    if (drawerTitle) drawerTitle.textContent = t("scoreDrawerTitle");

    const scoreCardH3 = document.querySelector(".scoreboard-card h3");
    if (scoreCardH3) scoreCardH3.textContent = t("scoreboardTitle");

    const logsCardH3 = document.querySelector(".logs-card h3");
    if (logsCardH3) logsCardH3.textContent = t("matchLedgerTitle");

    const ladderRows = document.querySelectorAll(".ladder-row span:first-child");
    if (ladderRows.length >= 2) {
        ladderRows[0].textContent = t("activeDealer");
        ladderRows[1].textContent = t("dealerBurdenScore");
    }

    // Modals
    const trumpSelectH2 = document.querySelector("#modal-trump-select h2");
    if (trumpSelectH2) trumpSelectH2.textContent = t("modalTrumpSelectTitle");

    const trumpSelectP = document.querySelector("#modal-trump-select p");
    if (trumpSelectP) trumpSelectP.textContent = t("modalTrumpSelectDesc");

    const configH2 = document.querySelector("#modal-config h2");
    if (configH2) configH2.textContent = t("modalSettingsTitle");

    const btnSaveConfig = document.getElementById("btn-save-config");
    if (btnSaveConfig) btnSaveConfig.textContent = t("saveSettingsBtn");

    const btnCloseConfig = document.getElementById("btn-close-config");
    if (btnCloseConfig) btnCloseConfig.textContent = t("closeBtn");

    const dealOverH2 = document.getElementById("deal-complete-title");
    if (dealOverH2) dealOverH2.textContent = t("dealOverTitle");

    const btnModalNext = document.getElementById("btn-modal-next-deal");
    if (btnModalNext) btnModalNext.textContent = t("btnNextDeal");

    const btnModalNew = document.getElementById("btn-modal-new-game");
    if (btnModalNew) btnModalNew.textContent = t("btnModalNewGame");

    // 5. Dynamic dropdowns & State Refresh
    if (typeof window.updateTrumpHiderOptionLabels === "function") {
        window.updateTrumpHiderOptionLabels();
    }

    if (window.renderState && window.gameState) {
        window.renderState(window.gameState);
    }
}
