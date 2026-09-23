// Desi Card Games - Playing Card Engine
// Supports both Royal Desert (Rajasthani Parchment & Miniature) and Classic Vector decks.

const SVG_NS = "http://www.w3.org/2000/svg";
const STORAGE_KEY_DECK_THEME = "DESI_GAMES_DECK_THEME";

const SUIT_SYMBOLS = { 'S': '♠', 'H': '♥', 'D': '♦', 'C': '♣' };
const SUIT_COLORS = { 'S': '#0f172a', 'H': '#dc2626', 'D': '#dc2626', 'C': '#0f172a' };

// Pip coordinates for number cards (2-10) using percentage positions
const PIP_LAYOUTS = {
    '2': [{x:50, y:22}, {x:50, y:78, inv:true}],
    '3': [{x:50, y:22}, {x:50, y:50}, {x:50, y:78, inv:true}],
    '4': [{x:28, y:24}, {x:72, y:24}, {x:28, y:76, inv:true}, {x:72, y:76, inv:true}],
    '5': [{x:28, y:24}, {x:72, y:24}, {x:50, y:50}, {x:28, y:76, inv:true}, {x:72, y:76, inv:true}],
    '6': [{x:28, y:24}, {x:72, y:24}, {x:28, y:50}, {x:72, y:50}, {x:28, y:76, inv:true}, {x:72, y:76, inv:true}],
    '7': [{x:28, y:24}, {x:72, y:24}, {x:50, y:37}, {x:28, y:50}, {x:72, y:50}, {x:28, y:76, inv:true}, {x:72, y:76, inv:true}],
    '8': [{x:28, y:24}, {x:72, y:24}, {x:50, y:37}, {x:28, y:50}, {x:72, y:50}, {x:50, y:63, inv:true}, {x:28, y:76, inv:true}, {x:72, y:76, inv:true}],
    '9': [{x:28, y:20}, {x:72, y:20}, {x:28, y:40}, {x:72, y:40}, {x:50, y:50}, {x:28, y:60, inv:true}, {x:72, y:60, inv:true}, {x:28, y:80, inv:true}, {x:72, y:80, inv:true}],
    '10': [{x:28, y:20}, {x:72, y:20}, {x:50, y:30}, {x:28, y:40}, {x:72, y:40}, {x:28, y:60, inv:true}, {x:72, y:60, inv:true}, {x:50, y:70, inv:true}, {x:28, y:80, inv:true}, {x:72, y:80, inv:true}]
};

function getDeckTheme() {
    try {
        const saved = localStorage.getItem(STORAGE_KEY_DECK_THEME);
        if (saved === "classic" || saved === "royal") return saved;
    } catch (e) {}
    return "royal"; // Premier default: Royal Desert (Rajasthani)
}

function setDeckTheme(theme) {
    try {
        localStorage.setItem(STORAGE_KEY_DECK_THEME, theme);
    } catch (e) {}
}

function getCardSrc(cardCode) {
    if (getDeckTheme() === "royal") {
        if (!cardCode || cardCode === "BACK") {
            return "assets/cards/bandhani-back.svg";
        }
    }
    if (!cardCode || cardCode === "BACK") {
        return "cards/BLUE_BACK.svg";
    }
    const clean = cardCode.trim().toUpperCase();
    return `cards/${clean}.svg`;
}

/**
 * Creates the appropriate card element based on active deck theme.
 * Returns either a modular layered Royal Desert card or a classic vector card.
 */
function createCardSVG(cardCode) {
    if (getDeckTheme() === "royal") {
        return createRoyalCardElement(cardCode);
    }
    return createClassicCardElement(cardCode);
}

/**
 * Constructs a modular, layered Royal Desert (Rajasthani) playing card component.
 */
function createRoyalCardElement(cardCode) {
    if (!cardCode || cardCode === "BACK") {
        const backImg = document.createElement("img");
        backImg.className = "playing-card-svg royal-card-back";
        backImg.alt = "Bandhani Card Back";
        backImg.draggable = false;
        backImg.src = "assets/cards/bandhani-back.svg";
        return backImg;
    }

    const clean = cardCode.trim().toUpperCase();
    const suit = clean.slice(-1); // 'S', 'H', 'D', 'C'
    const rank = clean.slice(0, -1); // 'A', '2'-'10', 'J', 'Q', 'K'
    const symbol = SUIT_SYMBOLS[suit] || '';

    const card = document.createElement("div");
    card.className = `playing-card-svg royal-card suit-${suit} rank-${rank}`;
    card.setAttribute("data-card", clean);

    const inner = document.createElement("div");
    inner.className = "card-inner";

    // Corner Indices (Top-Left and Inverted Bottom-Right)
    const topLeft = document.createElement("div");
    topLeft.className = "corner-index top-left";
    topLeft.innerHTML = `<span class="rank">${rank}</span><span class="suit-icon">${symbol}</span>`;

    const bottomRight = document.createElement("div");
    bottomRight.className = "corner-index bottom-right";
    bottomRight.innerHTML = `<span class="rank">${rank}</span><span class="suit-icon">${symbol}</span>`;

    // Center Card Content
    const center = document.createElement("div");
    center.className = "card-center";

    if (rank === "J") {
        // Jack / Kotwal: Exact Rajasthani Kathputli puppet figure with pagri, moustache & strings
        const art = document.createElement("img");
        art.className = "center-art face-art";
        art.src = "assets/cards/kathputli-puppet.svg";
        art.alt = "Kotwal Puppet";
        art.draggable = false;
        art.onerror = function() {
            this.style.display = "none";
            const fb = document.createElement("span");
            fb.className = "face-fallback-symbol";
            fb.textContent = "⚔️";
            center.appendChild(fb);
        };
        center.appendChild(art);
    } else if (rank === "K") {
        // King: Rajput Maharaja
        const art = document.createElement("img");
        art.className = "center-art face-art";
        art.src = "assets/cards/royal-raja.svg";
        art.alt = "Rajput Raja";
        art.draggable = false;
        art.onerror = function() {
            this.style.display = "none";
            const fb = document.createElement("span");
            fb.className = "face-fallback-symbol";
            fb.textContent = "🤴";
            center.appendChild(fb);
        };
        center.appendChild(art);
    } else if (rank === "Q") {
        // Queen: Rajput Maharani with traditional borla
        const art = document.createElement("img");
        art.className = "center-art face-art";
        art.src = "assets/cards/royal-rani.svg";
        art.alt = "Rajput Rani";
        art.draggable = false;
        art.onerror = function() {
            this.style.display = "none";
            const fb = document.createElement("span");
            fb.className = "face-fallback-symbol";
            fb.textContent = "👑";
            center.appendChild(fb);
        };
        center.appendChild(art);
    } else if (rank === "A") {
        // Ace: Golden Howdah Camel (Spades/Hukum) or Royal Elephant (Hearts, Diamonds, Clubs)
        const art = document.createElement("img");
        art.className = "center-art face-art";
        art.src = (suit === "S") ? "assets/cards/royal-camel.svg" : "assets/cards/royal-elephant.svg";
        art.alt = (suit === "S") ? "Royal Camel" : "Royal Elephant";
        art.draggable = false;
        art.onerror = function() {
            this.style.display = "none";
            const fb = document.createElement("span");
            fb.className = "ace-fallback-symbol";
            fb.textContent = symbol;
            center.appendChild(fb);
        };
        center.appendChild(art);
    } else {
        // Number Cards (2-10): Jharokha Arch Watermark + Arranged Suit Pips
        const watermark = document.createElement("img");
        watermark.className = "watermark-arch";
        watermark.src = "assets/cards/jharokha-watermark.svg";
        watermark.alt = "Jharokha Arch";
        watermark.draggable = false;
        watermark.onerror = function() { this.style.display = "none"; };
        center.appendChild(watermark);

        const pipMatrix = createPipMatrix(rank, symbol);
        center.appendChild(pipMatrix);
    }

    inner.appendChild(topLeft);
    inner.appendChild(center);
    inner.appendChild(bottomRight);
    card.appendChild(inner);

    return card;
}

/**
 * Builds the arranged suit pip grid for number cards (2-10).
 */
function createPipMatrix(rank, symbol) {
    const container = document.createElement("div");
    container.className = "pip-matrix";

    const coords = PIP_LAYOUTS[rank] || [];
    coords.forEach(pt => {
        const pip = document.createElement("span");
        pip.className = `pip-item ${pt.inv ? 'inverted' : ''}`;
        pip.textContent = symbol;
        pip.style.position = "absolute";
        pip.style.left = `${pt.x}%`;
        pip.style.top = `${pt.y}%`;
        pip.style.transform = `translate(-50%, -50%) ${pt.inv ? 'rotate(180deg)' : ''}`;
        container.appendChild(pip);
    });

    return container;
}

/**
 * Classic Vector Card fallback.
 */
function createClassicCardElement(cardCode) {
    const img = document.createElement("img");
    img.className = "playing-card-svg";
    img.alt = cardCode || "Card";
    img.draggable = false;
    img.src = getCardSrc(cardCode);

    img.onerror = function() {
        const fallback = createFallbackCardSVG(cardCode);
        if (img.parentNode) {
            img.parentNode.replaceChild(fallback, img);
        }
    };

    return img;
}

function createFallbackCardSVG(cardCode) {
    const svg = document.createElementNS(SVG_NS, "svg");
    svg.setAttribute("viewBox", "0 0 100 140");
    svg.setAttribute("class", "playing-card-svg");

    if (!cardCode || cardCode === "BACK") {
        svg.innerHTML = `
            <rect x="2" y="2" width="96" height="136" rx="8" fill="#142c44" stroke="#ca8a04" stroke-width="2"/>
            <circle cx="50" cy="70" r="20" fill="#1e3a8a" stroke="#facc15" stroke-width="1.5"/>
            <text x="50" y="75" font-size="12" font-weight="bold" fill="#fef08a" text-anchor="middle" font-family="'Cinzel', serif">BIKKAD</text>
        `;
        return svg;
    }

    const suit = cardCode.slice(-1);
    const rank = cardCode.slice(0, -1);
    const symbol = SUIT_SYMBOLS[suit] || '';
    const color = SUIT_COLORS[suit] || '#000000';

    svg.innerHTML = `
        <rect x="2" y="2" width="96" height="136" rx="8" fill="#f7ebda" stroke="#b38343" stroke-width="2"/>
        <text x="12" y="22" font-size="14" font-weight="bold" fill="${color}" font-family="'Cinzel', serif" text-anchor="middle">${rank}</text>
        <text x="12" y="34" font-size="11" fill="${color}" font-family="'Cinzel', serif" text-anchor="middle">${symbol}</text>
        <text x="50" y="78" font-size="36" fill="${color}" font-family="'Cinzel', serif" text-anchor="middle" opacity="0.95">${symbol}</text>
        <g transform="rotate(180 88 118)">
            <text x="88" y="112" font-size="14" font-weight="bold" fill="${color}" font-family="'Cinzel', serif" text-anchor="middle">${rank}</text>
            <text x="88" y="124" font-size="11" fill="${color}" font-family="'Cinzel', serif" text-anchor="middle">${symbol}</text>
        </g>
    `;

    return svg;
}

// Global exports
window.getDeckTheme = getDeckTheme;
window.setDeckTheme = setDeckTheme;
window.createCardSVG = createCardSVG;
window.createRoyalCardElement = createRoyalCardElement;
window.getCardSrc = getCardSrc;
