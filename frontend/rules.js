// =========================================================================
// ==================== RULES SYSTEM =======================================
// =========================================================================

var currentRulesGame = "bikkad";
var currentRulesTab = "objective";
var currentRulesLang = "en";

// ── Rules Data (Bilingual: EN + HI) ──────────────────────────────────────

const RULES_DATA = {
    bikkad: {
        icon: "🂠",
        name: "Bikkad",
        tagline_en: "Apna Rajasthan ka traditional pot-sweep trick-taking card game",
        tagline_hi: "राजस्थान का अपना पारंपरिक पॉट-स्वीप ट्रिक-टेकिंग कार्ड गेम",
        meta: "4 Players · 52 Cards · Hidden Trump · Partnership",
        objective: {
            en: `<div class="rules-highlight-box">
                    <div class="hl-title">🎯 Objective</div>
                    <p>Win tricks to score points. The team that avoids being the <strong>loser (Gadha)</strong> wins. Each deal, players bid by choosing how many tricks they expect to win. Exceed your quota to score; fall short and you take a burden.</p>
                </div>
                <div class="rules-card">
                    <p><strong>Win Condition:</strong> Reach the agreed target score (usually 0 or highest positive) without crossing the penalty threshold (usually -52 or -100).</p>
                    <p><strong>Special:</strong> A player can declare <strong>Tera (Solo Contract)</strong> — bet they'll win all 13 tricks solo. Succeed = massive bonus; fail = big penalty.</p>
                </div>`,
            hi: `<div class="rules-highlight-box">
                    <div class="hl-title">🎯 उद्देश्य</div>
                    <p>ट्रिक जीतकर पॉइंट स्कोर करें। जो टीम <strong>हारने वाली (गधा)</strong> बनने से बचे, वो जीतती है। हर डील में खिलाड़ी बोली लगाते हैं कि वो कितनी ट्रिक जीतेंगे।</p>
                </div>
                <div class="rules-card">
                    <p><strong>जीत की शर्त:</strong> टारगेट स्कोर तक पहुंचें बिना पेनल्टी थ्रेशहोल्ड (-52 या -100) पार किए।</p>
                    <p><strong>खास बात:</strong> कोई खिलाड़ी <strong>तेरा (सोलो कॉन्ट्रैक्ट)</strong> डिक्लेयर कर सकता है — अकेले सभी 13 ट्रिक जीतने का दांव।</p>
                </div>`
        },
        rules: {
            en: `<div class="rules-section">
                    <div class="rules-section-title">🃏 Setup & Deal</div>
                    <div class="rules-card">
                        <ul>
                            <li>4 players, standard 52-card deck. No jokers.</li>
                            <li>Deal 13 cards to each player.</li>
                            <li><strong>Trump Hider</strong> (dealer or chosen player) receives their cards first and secretly selects 1 card as the hidden trump. This card's suit is the trump for the entire deal.</li>
                            <li>The trump card is placed face-down. Its identity is revealed only when a player is void in the led suit.</li>
                        </ul>
                    </div>
                </div>
                <div class="rules-section">
                    <div class="rules-section-title">🎮 Playing a Trick</div>
                    <div class="rules-card">
                        <ul>
                            <li>Trump Hider leads the first trick by playing any card.</li>
                            <li>Other players must <strong>follow suit</strong> if they can.</li>
                            <li>If void in led suit, player may play any card — but if they play a trump (of any suit), the <strong>hidden trump is revealed</strong>.</li>
                            <li>Highest trump wins; if no trump played, highest card of led suit wins.</li>
                            <li>Trick winner leads next trick.</li>
                        </ul>
                    </div>
                </div>
                <div class="rules-section">
                    <div class="rules-section-title">📊 Scoring</div>
                    <div class="rules-card">
                        <p>Points are based on tricks won vs. your quota. Exact scoring depends on game variant configured. Standard:</p>
                        <ul>
                            <li>Win more tricks than quota: <strong>+1 per extra trick</strong></li>
                            <li>Win fewer tricks than quota: <strong>-2 per missed trick</strong></li>
                            <li>Tera success: <strong>+52 points</strong></li>
                            <li>Tera failure: <strong>-52 points</strong></li>
                        </ul>
                    </div>
                </div>`,
            hi: `<div class="rules-section">
                    <div class="rules-section-title">🃏 सेटअप और बांटना</div>
                    <div class="rules-card">
                        <ul>
                            <li>4 खिलाड़ी, 52 कार्ड की डेक। कोई जोकर नहीं।</li>
                            <li>हर खिलाड़ी को 13 कार्ड बांटें।</li>
                            <li><strong>ट्रम्प हाइडर</strong> अपने कार्ड में से 1 कार्ड गुप्त रूप से ट्रम्प के रूप में चुनता है। उस कार्ड का सूट पूरी डील के लिए ट्रम्प होता है।</li>
                            <li>ट्रम्प कार्ड उल्टा रखा जाता है। उसकी पहचान तब होती है जब कोई खिलाड़ी लेड सूट में कार्ड न हो।</li>
                        </ul>
                    </div>
                </div>
                <div class="rules-section">
                    <div class="rules-section-title">🎮 ट्रिक खेलना</div>
                    <div class="rules-card">
                        <ul>
                            <li>ट्रम्प हाइडर पहली ट्रिक में कोई भी कार्ड खेलकर शुरू करता है।</li>
                            <li>बाकी खिलाड़ियों को <strong>सूट फॉलो</strong> करना होगा अगर उनके पास है।</li>
                            <li>अगर लेड सूट का कार्ड नहीं है, तो कोई भी कार्ड खेल सकते हैं — ट्रम्प सूट खेलने पर <strong>हुकुम खुलता है</strong>।</li>
                            <li>सबसे ऊंचा ट्रम्प जीतता है; ट्रम्प नहीं तो लेड सूट का सबसे ऊंचा कार्ड।</li>
                        </ul>
                    </div>
                </div>`
        },
        howtoplay: {
            en: `<div class="rules-section">
                    <div class="rules-section-title">🖥️ Getting Started</div>
                    <div class="rules-card">
                        <div class="rules-step"><div class="rules-step-num">1</div><div class="rules-step-content"><strong>Select Bikkad</strong><p>Click "Bikkad" in the game selector strip and choose your setup settings below.</p></div></div>
                        <div class="rules-step"><div class="rules-step-num">2</div><div class="rules-step-content"><strong>Enter Your Name</strong><p>Type your player name. This is how others will see you in the game.</p></div></div>
                        <div class="rules-step"><div class="rules-step-num">3</div><div class="rules-step-content"><strong>Choose Players</strong><p>Select how many humans are playing. Set 1 for Solo vs Bots. Select specific seats for additional humans.</p></div></div>
                        <div class="rules-step"><div class="rules-step-num">4</div><div class="rules-step-content"><strong>Start or Share Room Code</strong><p>Click "Start Match" to begin. Share the 4-digit Room Code with friends so they can join via "Join Game".</p></div></div>
                    </div>
                </div>
                <div class="rules-section">
                    <div class="rules-section-title">🃏 Playing Your Turn</div>
                    <div class="rules-card">
                        <ul>
                            <li>Your cards appear at the <strong>bottom of the screen</strong> (South position).</li>
                            <li>When it's your turn, <strong>click a card</strong> to play it. Only legal cards are highlighted.</li>
                            <li>If you are the Trump Hider, you'll be asked to <strong>select the hidden trump card</strong> at the start.</li>
                            <li>If void in led suit, any card lights up — play a trump to reveal Hukum.</li>
                            <li>Bots play automatically after your turn with a short delay.</li>
                        </ul>
                    </div>
                </div>`,
            hi: `<div class="rules-section">
                    <div class="rules-section-title">🖥️ शुरुआत कैसे करें</div>
                    <div class="rules-card">
                        <div class="rules-step"><div class="rules-step-num">1</div><div class="rules-step-content"><strong>Bikkad चुनें</strong><p>गेम सिलेक्टर में "Bikkad" पर क्लिक करें और नीचे सेटअप सेटिंग्स चुनें।</p></div></div>
                        <div class="rules-step"><div class="rules-step-num">2</div><div class="rules-step-content"><strong>अपना नाम डालें</strong><p>अपना प्लेयर नाम टाइप करें।</p></div></div>
                        <div class="rules-step"><div class="rules-step-num">3</div><div class="rules-step-content"><strong>खिलाड़ी चुनें</strong><p>कितने इंसान खेलेंगे? Solo vs Bots के लिए 1 चुनें।</p></div></div>
                        <div class="rules-step"><div class="rules-step-num">4</div><div class="rules-step-content"><strong>शुरू करें या कोड शेयर करें</strong><p>"Start Match" दबाएं। दोस्तों को 4-अंकीय Room Code शेयर करें।</p></div></div>
                    </div>
                </div>`
        },
        tips: {
            en: `<div class="rules-tip"><div class="rules-tip-icon">💡</div><p><strong>Hide a strong trump:</strong> Pick a mid-value trump card to hide — save your Ace or King for playing.</p></div>
                 <div class="rules-tip"><div class="rules-tip-icon">🎯</div><p><strong>Follow the leader:</strong> If your partner leads, throw your highest card to support them.</p></div>
                 <div class="rules-tip"><div class="rules-tip-icon">🔮</div><p><strong>Count remaining trumps:</strong> Once hukum is revealed, track how many trumps have been played.</p></div>
                 <div class="rules-tip"><div class="rules-tip-icon">⚡</div><p><strong>Tera is risky:</strong> Only declare Tera if you have 5+ strong trumps and a very strong hand.</p></div>`,
            hi: `<div class="rules-tip"><div class="rules-tip-icon">💡</div><p><strong>मजबूत ट्रम्प छुपाएं:</strong> मध्यम ट्रम्प कार्ड छुपाएं — Ace या King खेलने के लिए बचाएं।</p></div>
                 <div class="rules-tip"><div class="rules-tip-icon">🎯</div><p><strong>पार्टनर का साथ दें:</strong> अगर पार्टनर लीड करे, तो सबसे ऊंचा कार्ड फेंकें।</p></div>
                 <div class="rules-tip"><div class="rules-tip-icon">⚡</div><p><strong>तेरा जोखिम भरा है:</strong> तेरा तभी बोलें जब 5+ मजबूत ट्रम्प हों।</p></div>`
        }
    },

    jhuthaniya: {
        icon: "🃏",
        name: "Jhuthaniya",
        tagline_en: "The bluff card game — play face-down and dare others to call JHUTH!",
        tagline_hi: "झूठ का खेल — पत्ते उल्टे रखो और झूठ पकड़ो!",
        meta: "2–7 Players · 52 Cards · No Trump · Elimination",
        objective: {
            en: `<div class="rules-highlight-box">
                    <div class="hl-title">🎯 Objective</div>
                    <p>Get rid of all your cards. The <strong>last player holding cards loses</strong> — they are the Jhuthaniya (the Liar / the Loser).</p>
                </div>
                <div class="rules-card">
                    <p>Players place 1–4 cards face-down and declare a rank (e.g., "Three Kings"). Others can <strong>challenge (JHUTH!)</strong> or pass. If caught lying, you pick up the entire pot. If challenged wrongly, the challenger picks it up.</p>
                </div>`,
            hi: `<div class="rules-highlight-box">
                    <div class="hl-title">🎯 उद्देश्य</div>
                    <p>अपने सारे पत्ते निकाल दो। <strong>आखिर में जिसके पास पत्ते बचें वो झुठनिया (हारने वाला)</strong> कहलाता है।</p>
                </div>
                <div class="rules-card">
                    <p>खिलाड़ी 1-4 पत्ते उल्टे रखकर कोई रैंक बताते हैं (जैसे "तीन बादशाह")। दूसरे <strong>JHUTH!</strong> बोल सकते हैं या पास कर सकते हैं।</p>
                </div>`
        },
        rules: {
            en: `<div class="rules-section">
                    <div class="rules-section-title">🃏 Basic Rules</div>
                    <div class="rules-card">
                        <ul>
                            <li>52-card deck dealt equally among all players.</li>
                            <li>Active player places 1–4 cards <strong>face-down</strong> and declares a rank (e.g., "Two Queens").</li>
                            <li>The declared count must match the number of cards placed.</li>
                            <li>Cards can be <strong>any suit</strong> — the rank is all that's declared.</li>
                        </ul>
                    </div>
                </div>
                <div class="rules-section">
                    <div class="rules-section-title">🚨 Challenge Window</div>
                    <div class="rules-card">
                        <ul>
                            <li>After a claim, each other player in turn order can say <strong>JHUTH!</strong> (challenge) or <strong>Pass</strong>.</li>
                            <li><strong>If challenged:</strong> Cards are revealed.
                                <ul>
                                    <li>Claimant was lying → Claimant picks up the entire center pot.</li>
                                    <li>Claimant was truthful → Challenger picks up the entire center pot.</li>
                                </ul>
                            </li>
                            <li>If all pass: Cards stay in pot, next player's turn begins.</li>
                        </ul>
                    </div>
                </div>
                <div class="rules-section">
                    <div class="rules-section-title">✅ Exiting (Going Safe)</div>
                    <div class="rules-card">
                        <ul>
                            <li>If you play your last cards and no one challenges (or a challenge proves you told the truth), you are <strong>SAFE</strong> and out of the game as a winner.</li>
                            <li>If caught bluffing on your last play, you pick up the pot and continue.</li>
                        </ul>
                    </div>
                </div>`,
            hi: `<div class="rules-section">
                    <div class="rules-section-title">🃏 बुनियादी नियम</div>
                    <div class="rules-card">
                        <ul>
                            <li>52 पत्तों की डेक सभी खिलाड़ियों में बराबर बांटी जाती है।</li>
                            <li>बारी वाला खिलाड़ी 1-4 पत्ते <strong>उल्टे</strong> रखकर एक रैंक बताता है।</li>
                            <li>जितने पत्ते रखे, उतने ही बताने होंगे।</li>
                            <li>कोई भी सूट हो सकता है — सिर्फ रैंक बताना जरूरी है।</li>
                        </ul>
                    </div>
                </div>
                <div class="rules-section">
                    <div class="rules-section-title">🚨 JHUTH बोलने का नियम</div>
                    <div class="rules-card">
                        <ul>
                            <li>दावे के बाद, बाकी खिलाड़ी बारी-बारी <strong>JHUTH!</strong> या <strong>Pass</strong> बोल सकते हैं।</li>
                            <li><strong>JHUTH! बोलने पर:</strong> पत्ते पलटे जाते हैं।
                                <ul>
                                    <li>झूठ था → दावेदार पूरा पॉट उठाता है।</li>
                                    <li>सच था → JHUTH! बोलने वाला पूरा पॉट उठाता है।</li>
                                </ul>
                            </li>
                            <li>सबने Pass किया → पत्ते पॉट में रहें, अगली बारी।</li>
                        </ul>
                    </div>
                </div>`
        },
        howtoplay: {
            en: `<div class="rules-section">
                    <div class="rules-section-title">🖥️ How to Play in App</div>
                    <div class="rules-card">
                        <div class="rules-step"><div class="rules-step-num">1</div><div class="rules-step-content"><strong>Select Jhuthaniya</strong><p>Click "Jhuthaniya" in the game selector and hit "Start Match".</p></div></div>
                        <div class="rules-step"><div class="rules-step-num">2</div><div class="rules-step-content"><strong>Your Hand (Bottom)</strong><p>Your cards show at the bottom. Click 1–4 cards to select them (they highlight in gold).</p></div></div>
                        <div class="rules-step"><div class="rules-step-num">3</div><div class="rules-step-content"><strong>Declare a Rank</strong><p>A play panel appears below your hand. Choose a rank from the dropdown, then click "Play Cards".</p></div></div>
                        <div class="rules-step"><div class="rules-step-num">4</div><div class="rules-step-content"><strong>Challenge Window</strong><p>When it's your turn to decide, a popup asks: "JHUTH? Do you believe them?" — click 🚨 JHUTH! to challenge or ✓ Pass to let it go.</p></div></div>
                        <div class="rules-step"><div class="rules-step-num">5</div><div class="rules-step-content"><strong>Bots Auto-Play</strong><p>Bot players take their turns automatically with a short delay. Watch the game log at the bottom for updates.</p></div></div>
                    </div>
                </div>`,
            hi: `<div class="rules-section">
                    <div class="rules-section-title">🖥️ ऐप में कैसे खेलें</div>
                    <div class="rules-card">
                        <div class="rules-step"><div class="rules-step-num">1</div><div class="rules-step-content"><strong>Jhuthaniya चुनें</strong><p>गेम सिलेक्टर में "Jhuthaniya" पर क्लिक करें।</p></div></div>
                        <div class="rules-step"><div class="rules-step-num">2</div><div class="rules-step-content"><strong>अपने पत्ते (नीचे)</strong><p>1-4 पत्ते चुनें — चुने हुए पत्ते सुनहरे हो जाएंगे।</p></div></div>
                        <div class="rules-step"><div class="rules-step-num">3</div><div class="rules-step-content"><strong>रैंक बताएं</strong><p>नीचे का पैनल आएगा। Dropdown से रैंक चुनें, फिर "Play Cards" दबाएं।</p></div></div>
                        <div class="rules-step"><div class="rules-step-num">4</div><div class="rules-step-content"><strong>JHUTH! या Pass</strong><p>जब आपकी बारी हो, तो पॉपअप आएगा — 🚨 JHUTH! या ✓ Pass चुनें।</p></div></div>
                    </div>
                </div>`
        },
        tips: {
            en: `<div class="rules-tip"><div class="rules-tip-icon">🎭</div><p><strong>Bluff strategically:</strong> Bluff when the pot is small. Avoid bluffing with a huge pot at stake.</p></div>
                 <div class="rules-tip"><div class="rules-tip-icon">🧮</div><p><strong>Count cards:</strong> If you have 3 of a rank, the opponent can have at most 1 — any claim of 3+ is almost certainly a bluff!</p></div>
                 <div class="rules-tip"><div class="rules-tip-icon">🏁</div><p><strong>Watch final plays:</strong> If someone plays their last cards, always consider challenging — they might be bluffing to escape!</p></div>
                 <div class="rules-tip"><div class="rules-tip-icon">💼</div><p><strong>Small claims are safer:</strong> Claiming 1 card is harder to challenge since it could always be true.</p></div>`,
            hi: `<div class="rules-tip"><div class="rules-tip-icon">🎭</div><p><strong>सोच-समझकर झूठ बोलें:</strong> छोटे पॉट में झूठ बोलें। बड़े पॉट में जोखिम है।</p></div>
                 <div class="rules-tip"><div class="rules-tip-icon">🧮</div><p><strong>पत्ते गिनें:</strong> अगर आपके पास 3 एक रैंक के हैं, तो दूसरे के पास 1 ही बचता है — 3+ का दावा झूठ होगा!</p></div>
                 <div class="rules-tip"><div class="rules-tip-icon">🏁</div><p><strong>आखिरी पत्तों पर नजर:</strong> जब कोई आखिरी पत्ते खेले, JHUTH! बोलने पर विचार करें।</p></div>`
        }
    },

    bindicoat: {
        icon: "🔴",
        name: "Bindi Coat (Mindikot)",
        tagline_en: "4-player partnership trick game with a hidden trump — capture the Mindis!",
        tagline_hi: "4 खिलाड़ियों का जोड़ी गेम — छुपे हुए हुकुम के साथ मिंडी पकड़ो!",
        meta: "4 Players · 52 Cards · Hidden Trump · Partnership (NS vs EW)",
        objective: {
            en: `<div class="rules-highlight-box">
                    <div class="hl-title">🎯 Objective</div>
                    <p>Win the four <strong>Mindis (10s)</strong>. The team that captures more Mindis wins the round. A tie (2-2) is broken by tricks: 7+ tricks wins.</p>
                </div>
                <div class="rules-card">
                    <p><strong>Partnerships:</strong> Team NS = P1 (South) + P3 (North) | Team EW = P2 (East) + P4 (West)</p>
                    <p><strong>Special Wins:</strong></p>
                    <ul>
                        <li><strong>KOT:</strong> Capture all 4 Mindis + 7+ tricks.</li>
                        <li><strong>White-Wash:</strong> Capture all 4 Mindis + all 13 tricks.</li>
                    </ul>
                </div>`,
            hi: `<div class="rules-highlight-box">
                    <div class="hl-title">🎯 उद्देश्य</div>
                    <p>चारों <strong>मिंडी (10 वाले पत्ते)</strong> जीतो। जो टीम ज्यादा मिंडी पकड़े, वो राउंड जीतती है। 2-2 की बराबरी पर 7+ ट्रिक जीतने वाली टीम जीतती है।</p>
                </div>
                <div class="rules-card">
                    <p><strong>जोड़ियां:</strong> NS टीम = P1 + P3 | EW टीम = P2 + P4</p>
                    <p><strong>खास जीत:</strong> <strong>KOT</strong> = 4 मिंडी + 7+ ट्रिक | <strong>White-Wash</strong> = 4 मिंडी + सभी 13 ट्रिक</p>
                </div>`
        },
        rules: {
            en: `<div class="rules-section">
                    <div class="rules-section-title">🃏 Dealing (Two Stages)</div>
                    <div class="rules-card">
                        <ul>
                            <li><strong>Stage 1:</strong> Each player receives 5 cards.</li>
                            <li><strong>Bandh Hukum Selection:</strong> The Trump Placer (player left of dealer) secretly selects 1 card from their 5 and places it <strong>face-down</strong> as the hidden trump. That card's suit is the trump for the deal.</li>
                            <li><strong>Stage 2:</strong> Remaining 8 cards are dealt to each player (Trump Placer gets 9 to compensate for the 1 placed).</li>
                            <li>Trump Placer leads Trick 1.</li>
                        </ul>
                    </div>
                </div>
                <div class="rules-section">
                    <div class="rules-section-title">🔓 Hukum Kholo! (Trump Reveal)</div>
                    <div class="rules-card">
                        <p>The trump suit is <strong>hidden</strong> until someone is void in the led suit and plays a different suit — this reveals the Bandh Hukum card.</p>
                        <p>When revealed, the Trump Placer <strong>takes their Bandh Hukum card back</strong> into their hand and plays it normally.</p>
                    </div>
                </div>
                <div class="rules-section">
                    <div class="rules-section-title">🎮 Playing Tricks</div>
                    <div class="rules-card">
                        <ul>
                            <li>Must follow the led suit if you have it.</li>
                            <li>Void in led suit → play any card.</li>
                            <li>Highest trump wins; if no trump, highest of led suit.</li>
                            <li>Trick winner leads next trick.</li>
                        </ul>
                    </div>
                </div>`,
            hi: `<div class="rules-section">
                    <div class="rules-section-title">🃏 बांटना (दो चरण)</div>
                    <div class="rules-card">
                        <ul>
                            <li><strong>पहला चरण:</strong> हर खिलाड़ी को 5 पत्ते।</li>
                            <li><strong>बंद हुकुम चुनना:</strong> ट्रम्प प्लेसर (डीलर के बाएं) अपने 5 पत्तों में से 1 चुनकर <strong>उल्टा</strong> रखता है। वो सूट हुकुम बनता है।</li>
                            <li><strong>दूसरा चरण:</strong> बाकी 8 पत्ते बांटे जाते हैं।</li>
                            <li>ट्रम्प प्लेसर पहली ट्रिक शुरू करता है।</li>
                        </ul>
                    </div>
                </div>
                <div class="rules-section">
                    <div class="rules-section-title">🔓 हुकुम खोलो!</div>
                    <div class="rules-card">
                        <p>हुकुम तब खुलता है जब कोई खिलाड़ी लेड सूट में पत्ता नहीं रखता और अलग सूट खेलता है।</p>
                        <p>खुलने पर ट्रम्प प्लेसर को अपना बंद हुकुम का पत्ता वापस मिल जाता है।</p>
                    </div>
                </div>`
        },
        howtoplay: {
            en: `<div class="rules-section">
                    <div class="rules-section-title">🖥️ How to Play in App</div>
                    <div class="rules-card">
                        <div class="rules-step"><div class="rules-step-num">1</div><div class="rules-step-content"><strong>Select Bindi Coat</strong><p>Choose "Bindi Coat" in the selector. You play as P1 (South, Team NS with P3).</p></div></div>
                        <div class="rules-step"><div class="rules-step-num">2</div><div class="rules-step-content"><strong>Bandh Hukum Selection</strong><p>If you are the Trump Placer, a popup shows your 5 cards. Click one to place it face-down as hidden trump.</p></div></div>
                        <div class="rules-step"><div class="rules-step-num">3</div><div class="rules-step-content"><strong>Playing Cards</strong><p>Your hand shows at the bottom. Legal cards are highlighted in gold. Click to play. Illegal cards appear dimmed.</p></div></div>
                        <div class="rules-step"><div class="rules-step-num">4</div><div class="rules-step-content"><strong>Trump Revealed!</strong><p>When a bot or you play a card of a different suit while void, a 🔓 HUKUM KHOLO! toast appears announcing the trump suit.</p></div></div>
                        <div class="rules-step"><div class="rules-step-num">5</div><div class="rules-step-content"><strong>Round End</strong><p>After 13 tricks, a summary popup shows who won (Mindis + tricks). Click "Next Round" to play again with rotated dealer.</p></div></div>
                    </div>
                </div>`,
            hi: `<div class="rules-section">
                    <div class="rules-section-title">🖥️ ऐप में कैसे खेलें</div>
                    <div class="rules-card">
                        <div class="rules-step"><div class="rules-step-num">1</div><div class="rules-step-content"><strong>Bindi Coat चुनें</strong><p>आप P1 (South, NS टीम) के रूप में खेलते हैं।</p></div></div>
                        <div class="rules-step"><div class="rules-step-num">2</div><div class="rules-step-content"><strong>बंद हुकुम चुनें</strong><p>अगर आप ट्रम्प प्लेसर हैं, तो पॉपअप आएगा — 5 पत्तों में से एक पर क्लिक करें।</p></div></div>
                        <div class="rules-step"><div class="rules-step-num">3</div><div class="rules-step-content"><strong>पत्ते खेलें</strong><p>कानूनी पत्ते सुनहरे रोशनी में दिखेंगे। क्लिक करके खेलें।</p></div></div>
                        <div class="rules-step"><div class="rules-step-num">4</div><div class="rules-step-content"><strong>हुकुम खुला!</strong><p>जब हुकुम खुलेगा, ऊपर 🔓 HUKUM KHOLO! का मैसेज आएगा।</p></div></div>
                    </div>
                </div>`
        },
        tips: {
            en: `<div class="rules-tip"><div class="rules-tip-icon">🔴</div><p><strong>Pick a strong trump suit:</strong> When selecting Bandh Hukum, choose a card from your strongest suit to maximize trump power.</p></div>
                 <div class="rules-tip"><div class="rules-tip-icon">🤝</div><p><strong>Feed Mindis to partner:</strong> If your partner is winning a trick, throw your 10 to them — they'll secure the Mindi for your team!</p></div>
                 <div class="rules-tip"><div class="rules-tip-icon">🔒</div><p><strong>Delay revealing trump:</strong> Don't play trump early — make opponents guess. Reveal only when necessary.</p></div>
                 <div class="rules-tip"><div class="rules-tip-icon">📊</div><p><strong>Track Mindis:</strong> Watch the NS/EW score panel mid-game — if opponents have 3 Mindis, be aggressive to stop their 4th.</p></div>`,
            hi: `<div class="rules-tip"><div class="rules-tip-icon">🔴</div><p><strong>मजबूत हुकुम चुनें:</strong> बंद हुकुम के लिए अपने सबसे मजबूत सूट का पत्ता चुनें।</p></div>
                 <div class="rules-tip"><div class="rules-tip-icon">🤝</div><p><strong>मिंडी पार्टनर को दें:</strong> अगर पार्टनर ट्रिक जीत रहा हो, तो अपना 10 उनको दें।</p></div>
                 <div class="rules-tip"><div class="rules-tip-icon">🔒</div><p><strong>हुकुम देर से खोलें:</strong> ट्रम्प जल्दी मत खोलें — दुश्मन को अंदाजा न लगने दें।</p></div>`
        }
    },

    tikdi: {
        icon: "🔺",
        name: "Tikdi (3-2-5 / Teen Do Paanch)",
        tagline_en: "3-player trick quota game — meet your contract or pay the penalty!",
        tagline_hi: "3 खिलाड़ियों का कोटा गेम — कॉन्ट्रैक्ट पूरा करो या पेनल्टी भुगतो!",
        meta: "3 Players · 30 Cards (A-8 only) · Runtime Trump Choice",
        objective: {
            en: `<div class="rules-highlight-box">
                    <div class="hl-title">🎯 Objective</div>
                    <p>Meet your trick quota. Each player has a fixed target: <strong>Chooser: 5, Bystander: 3, Dealer: 2</strong>. Win more than your quota to earn points; win less to take a penalty.</p>
                </div>
                <div class="rules-card">
                    <p><strong>Deck:</strong> Only 30 cards are used (8 through Ace in all 4 suits × 30 combinations based on the game format).</p>
                    <p><strong>Trump:</strong> The Chooser selects the trump suit after seeing their hand.</p>
                </div>`,
            hi: `<div class="rules-highlight-box">
                    <div class="hl-title">🎯 उद्देश्य</div>
                    <p>अपना ट्रिक कोटा पूरा करो। हर खिलाड़ी का टारगेट है: <strong>चूजर: 5, बाइस्टैंडर: 3, डीलर: 2</strong>।</p>
                </div>
                <div class="rules-card">
                    <p><strong>डेक:</strong> सिर्फ 30 पत्ते इस्तेमाल होते हैं (8 से Ace तक)।</p>
                    <p><strong>ट्रम्प:</strong> Chooser अपना हाथ देखकर ट्रम्प सूट चुनता है।</p>
                </div>`
        },
        rules: {
            en: `<div class="rules-section">
                    <div class="rules-section-title">🃏 Setup</div>
                    <div class="rules-card">
                        <ul>
                            <li>3 players, 30-card deck (8, 9, 10, J, Q, K, A in all 4 suits + 8 cards of 2 extra → varies by variant).</li>
                            <li><strong>Dealer</strong> gets 10 cards, <strong>Chooser</strong> gets 12 cards, <strong>Bystander</strong> gets 8 cards.</li>
                            <li>Dealer can "give" 3 cards to Chooser and receive 3 back (the exchange phase).</li>
                            <li>Chooser selects the trump suit and leads Trick 1.</li>
                        </ul>
                    </div>
                </div>
                <div class="rules-section">
                    <div class="rules-section-title">📊 Quotas & Scoring</div>
                    <div class="rules-card">
                        <ul>
                            <li><strong>Chooser quota: 5</strong> | <strong>Bystander quota: 3</strong> | <strong>Dealer quota: 2</strong></li>
                            <li>Exceed quota → earn 1 point per extra trick</li>
                            <li>Miss quota → the deficit is carried as a "debt" (penalty cards for next round)</li>
                        </ul>
                    </div>
                </div>`,
            hi: `<div class="rules-section">
                    <div class="rules-section-title">🃏 सेटअप</div>
                    <div class="rules-card">
                        <ul>
                            <li>3 खिलाड़ी, 30 पत्तों की डेक।</li>
                            <li><strong>डीलर:</strong> 10 पत्ते | <strong>Chooser:</strong> 12 पत्ते | <strong>Bystander:</strong> 8 पत्ते</li>
                            <li>Chooser ट्रम्प सूट चुनता है और पहली ट्रिक खेलता है।</li>
                        </ul>
                    </div>
                </div>
                <div class="rules-section">
                    <div class="rules-section-title">📊 कोटा और स्कोरिंग</div>
                    <div class="rules-card">
                        <ul>
                            <li><strong>Chooser: 5</strong> | <strong>Bystander: 3</strong> | <strong>Dealer: 2</strong></li>
                            <li>कोटा से ज्यादा → अतिरिक्त ट्रिक का 1 पॉइंट</li>
                            <li>कोटा से कम → अगले राउंड में पेनल्टी पत्ते</li>
                        </ul>
                    </div>
                </div>`
        },
        howtoplay: {
            en: `<div class="rules-section">
                    <div class="rules-section-title">🖥️ How to Play in App</div>
                    <div class="rules-card">
                        <div class="rules-step"><div class="rules-step-num">1</div><div class="rules-step-content"><strong>Select Tikdi</strong><p>Choose "Tikdi (3-2-5)" from the selector. You play as P1 (Dealer, Quota 2).</p></div></div>
                        <div class="rules-step"><div class="rules-step-num">2</div><div class="rules-step-content"><strong>Trump Selection</strong><p>The Chooser (P2 Bot or Human) picks a trump suit. A popup may appear for you to confirm or a banner announces the suit.</p></div></div>
                        <div class="rules-step"><div class="rules-step-num">3</div><div class="rules-step-content"><strong>Play Cards</strong><p>Your hand is at the bottom. Legal cards glow gold. Click to play. Must follow suit; if void, play any card.</p></div></div>
                        <div class="rules-step"><div class="rules-step-num">4</div><div class="rules-step-content"><strong>Round End</strong><p>After all 10 tricks, a summary shows quotas met/missed. Penalty settlement happens before the next round starts.</p></div></div>
                    </div>
                </div>`,
            hi: `<div class="rules-section">
                    <div class="rules-section-title">🖥️ ऐप में कैसे खेलें</div>
                    <div class="rules-card">
                        <div class="rules-step"><div class="rules-step-num">1</div><div class="rules-step-content"><strong>Tikdi चुनें</strong><p>आप P1 (डीलर, कोटा 2) के रूप में खेलते हैं।</p></div></div>
                        <div class="rules-step"><div class="rules-step-num">2</div><div class="rules-step-content"><strong>ट्रम्प चुनना</strong><p>Chooser ट्रम्प सूट चुनता है — एक बैनर या पॉपअप में दिखेगा।</p></div></div>
                        <div class="rules-step"><div class="rules-step-num">3</div><div class="rules-step-content"><strong>पत्ते खेलें</strong><p>कानूनी पत्ते सुनहरे। क्लिक करके खेलें। सूट फॉलो करना जरूरी है।</p></div></div>
                    </div>
                </div>`
        },
        tips: {
            en: `<div class="rules-tip"><div class="rules-tip-icon">🔺</div><p><strong>As Chooser:</strong> Pick a trump suit where you have the most cards and high honors (A, K).</p></div>
                 <div class="rules-tip"><div class="rules-tip-icon">⚖️</div><p><strong>As Dealer (Quota 2):</strong> Play conservatively. Winning 3-4 tricks gives you extra points; losing 0-1 is a big penalty.</p></div>
                 <div class="rules-tip"><div class="rules-tip-icon">👀</div><p><strong>Watch the exchange:</strong> Cards Chooser gives Dealer reveal something about their hand strength.</p></div>
                 <div class="rules-tip"><div class="rules-tip-icon">🎯</div><p><strong>Go for your quota first:</strong> Secure your minimum before trying for extras.</p></div>`,
            hi: `<div class="rules-tip"><div class="rules-tip-icon">🔺</div><p><strong>Chooser के रूप में:</strong> वो ट्रम्प सूट चुनें जिसमें सबसे ज्यादा और ऊंचे पत्ते हों।</p></div>
                 <div class="rules-tip"><div class="rules-tip-icon">⚖️</div><p><strong>डीलर के रूप में (कोटा 2):</strong> सावधानी से खेलें। 3-4 ट्रिक = बोनस। 0-1 = बड़ी पेनल्टी।</p></div>
                 <div class="rules-tip"><div class="rules-tip-icon">🎯</div><p><strong>पहले कोटा पूरा करें:</strong> एक्स्ट्रा से पहले अपना मिनिमम सुनिश्चित करें।</p></div>`
        }
    }
};

// ── Explore Tab Content (with guide images) ───────────────────────────────
// Shared image paths
const GUIDE_IMGS = {
    setup:        "assets/guide/guide_setup_screen.jpg",
    table:        "assets/guide/guide_game_table.jpg",
    playerTypes:  "assets/guide/guide_player_types.jpg",
    jhuthaniya:   "assets/guide/guide_jhuthaniya_bluff.jpg",
    bindiCoat:    "assets/guide/guide_bindi_coat_bandh.jpg"
};

// Shared "explore" HTML builder
function buildExploreHTML(sections) {
    return sections.map(s => `
        <div class="rules-section">
            <div class="rules-section-title">${s.title}</div>
            ${s.img ? `<div class="guide-img-wrap"><img src="${s.img}" alt="${s.alt || s.title}" class="guide-img" loading="lazy"></div>` : ""}
            <div class="rules-card">${s.body}</div>
        </div>`).join("");
}

// Explore content for each game
const EXPLORE_DATA = {
    bikkad: {
        en: () => buildExploreHTML([
            {
                title: "🖥️ Step 1 — Choose Your Game & Setup",
                img: GUIDE_IMGS.setup,
                alt: "Game setup screen guide",
                body: `<ul>
                    <li>Open the app — you'll land on the <strong>Home Screen</strong>.</li>
                    <li>Click <strong>"Bikkad"</strong> in the Game Selector Strip (it glows gold when selected).</li>
                    <li>Each card also has a <strong>📖 Rules</strong> button — that's where you are now!</li>
                    <li>Enter your <strong>player name</strong> in the text field.</li>
                    <li>Click <strong>🚀 Start Match</strong> to begin solo vs bots.</li>
                </ul>`
            },
            {
                title: "👥 Step 2 — Selecting Players (Human vs Bot)",
                img: GUIDE_IMGS.playerTypes,
                alt: "Player types and selection guide",
                body: `<ul>
                    <li><strong>How many humans?</strong> Click 1 (Solo), 2, 3, or 4.</li>
                    <li>If 2+ humans: A <strong>Seat Picker</strong> appears. Click North / West / East to assign human seats.</li>
                    <li><strong>Bot players</strong> fill the rest automatically (AI plays instantly).</li>
                    <li>To invite a friend: Share the <strong>4-digit Room Code</strong>. Friend opens app → "Join Game" → enters code → joins instantly.</li>
                    <li>Bikkad allows up to <strong>4 players</strong> (4P game).</li>
                </ul>`
            },
            {
                title: "🃏 Step 3 — The Game Table",
                img: GUIDE_IMGS.table,
                alt: "Game table annotated guide",
                body: `<ul>
                    <li><strong>YOUR HAND</strong> appears at the bottom (South position). Click any card to play it.</li>
                    <li>Legal cards glow <strong>gold</strong>. Dimmed cards cannot be played (must follow suit).</li>
                    <li>At the start, if you're the <strong>Trump Hider</strong>, a popup asks you to select 1 card to hide as the secret trump.</li>
                    <li>The <strong>center</strong> shows the current trick (cards played by all 4 players).</li>
                    <li>Top bar shows: Game name, current turn, dealer, scores. Use <strong>🏠 Home</strong> to exit or <strong>📊 Score</strong> to see the ladder.</li>
                </ul>`
            }
        ]),
        hi: () => buildExploreHTML([
            {
                title: "🖥️ कदम 1 — गेम चुनें और सेटअप करें",
                img: GUIDE_IMGS.setup,
                alt: "गेम सेटअप स्क्रीन गाइड",
                body: `<ul>
                    <li>ऐप खोलें — आप <strong>होम स्क्रीन</strong> पर होंगे।</li>
                    <li>गेम सिलेक्टर में <strong>"Bikkad"</strong> पर क्लिक करें (सुनहरा रंग = चुना हुआ)।</li>
                    <li>अपना <strong>प्लेयर नाम</strong> डालें।</li>
                    <li><strong>🚀 Start Match</strong> दबाएं।</li>
                </ul>`
            },
            {
                title: "👥 कदम 2 — खिलाड़ी चुनें",
                img: GUIDE_IMGS.playerTypes,
                alt: "खिलाड़ी चुनाव गाइड",
                body: `<ul>
                    <li>कितने इंसान? 1 (Solo), 2, 3, या 4 दबाएं।</li>
                    <li>2+ इंसान: <strong>Seat Picker</strong> आएगा — North/West/East में से चुनें।</li>
                    <li>दोस्त को जोड़ने के लिए: <strong>4-अंकीय Room Code</strong> शेयर करें।</li>
                </ul>`
            },
            {
                title: "🃏 कदम 3 — गेम टेबल",
                img: GUIDE_IMGS.table,
                alt: "गेम टेबल गाइड",
                body: `<ul>
                    <li>आपके <strong>पत्ते नीचे</strong> (South) दिखते हैं। खेलने के लिए क्लिक करें।</li>
                    <li>कानूनी पत्ते <strong>सुनहरे</strong> रंग में चमकते हैं।</li>
                    <li>ट्रम्प हाइडर होने पर पहले एक पत्ता चुनना होगा।</li>
                </ul>`
            }
        ])
    },

    jhuthaniya: {
        en: () => buildExploreHTML([
            {
                title: "🖥️ Step 1 — Setup (Jhuthaniya Supports 2–7 Players)",
                img: GUIDE_IMGS.setup,
                alt: "Game setup screen guide",
                body: `<ul>
                    <li>Select <strong>"Jhuthaniya"</strong> from the Game Selector Strip.</li>
                    <li>Set how many human players (1 for Solo vs 3 Bots).</li>
                    <li>Jhuthaniya <strong>supports 2–7 players</strong> — all positions can be human or bot.</li>
                    <li>Hit <strong>🚀 Start Match</strong>. Cards are dealt equally.</li>
                </ul>`
            },
            {
                title: "🃏 Step 2 — How Bluffing Works",
                img: GUIDE_IMGS.jhuthaniya,
                alt: "Jhuthaniya bluff mechanics guide",
                body: `<ul>
                    <li><strong>Select 1–4 cards</strong> from your hand (they glow gold when tapped).</li>
                    <li>A play panel appears: choose a <strong>Claim Rank</strong> from the dropdown (any rank — truth or lie!).</li>
                    <li>Click <strong>▶ Play Cards</strong> — cards go face-down to the center pot.</li>
                    <li>Other players see a <strong>🚨 JHUTH? popup</strong> — they decide to challenge or pass.</li>
                    <li>If challenged and caught lying → <strong>you pick up the entire pot</strong>.</li>
                    <li>If challenged and you were truthful → <strong>challenger picks up the pot</strong>.</li>
                </ul>`
            },
            {
                title: "🏆 Step 3 — Winning (Going Safe)",
                img: GUIDE_IMGS.table,
                alt: "Game table guide",
                body: `<ul>
                    <li>Play all your cards down to 0 and survive a challenge → you go <strong>✅ SAFE</strong>.</li>
                    <li>Safe players are ranked: 1st safe = Winner, 2nd safe = Runner-up, etc.</li>
                    <li>The last player with cards remaining = <strong>JHUTHANIYA (Loser)</strong>.</li>
                    <li>Watch the <strong>Center Pot size</strong> in the game header — large pot = risky to bluff!</li>
                </ul>`
            }
        ]),
        hi: () => buildExploreHTML([
            {
                title: "🖥️ कदम 1 — सेटअप",
                img: GUIDE_IMGS.setup,
                alt: "सेटअप स्क्रीन",
                body: `<ul>
                    <li>गेम सिलेक्टर में <strong>"Jhuthaniya"</strong> चुनें।</li>
                    <li>2-7 खिलाड़ी हो सकते हैं।</li>
                    <li><strong>🚀 Start Match</strong> दबाएं।</li>
                </ul>`
            },
            {
                title: "🃏 कदम 2 — झूठ कैसे बोलें",
                img: GUIDE_IMGS.jhuthaniya,
                alt: "झुठनिया ब्लफ मैकेनिक्स",
                body: `<ul>
                    <li>1-4 पत्ते चुनें (सुनहरे रंग में चमकेंगे)।</li>
                    <li>Dropdown से <strong>कोई भी रैंक</strong> चुनें (सच या झूठ!)।</li>
                    <li><strong>▶ Play Cards</strong> दबाएं।</li>
                    <li>🚨 JHUTH? पॉपअप आएगा — दूसरे चुनेंगे।</li>
                    <li>झूठ पकड़ा → आप पूरा पॉट उठाते हैं।</li>
                </ul>`
            }
        ])
    },

    bindicoat: {
        en: () => buildExploreHTML([
            {
                title: "🖥️ Step 1 — Setup (4-Player Partnership)",
                img: GUIDE_IMGS.setup,
                alt: "Game setup screen",
                body: `<ul>
                    <li>Select <strong>"Bindi Coat"</strong> from the selector. You are always <strong>P1 (South, Team NS)</strong>.</li>
                    <li>Your partner is <strong>P3 (North)</strong>. Opponents: P2 (East) and P4 (West).</li>
                    <li>Set seats 2, 3, or 4 as human if friends are joining.</li>
                    <li>Hit <strong>🚀 Start Match</strong>. Cards are dealt in 2 stages.</li>
                </ul>`
            },
            {
                title: "🔒 Step 2 — Bandh Hukum (Hidden Trump System)",
                img: GUIDE_IMGS.bindiCoat,
                alt: "Bandh Hukum hidden trump guide",
                body: `<ul>
                    <li>After Stage 1 deal (5 cards each), the <strong>Trump Placer</strong> sees a popup showing their 5 cards.</li>
                    <li>Click one card to place it <strong>face-down</strong> as the hidden trump (Bandh Hukum).</li>
                    <li>That card's suit becomes trump for the entire round — but nobody knows which suit!</li>
                    <li>When someone is void in led suit and plays a different suit → <strong>🔓 HUKUM KHOLO!</strong> toast appears.</li>
                    <li>Trump Placer gets their hidden card back and plays normally from then on.</li>
                </ul>`
            },
            {
                title: "🔴 Step 3 — The Game Table & Mindis",
                img: GUIDE_IMGS.table,
                alt: "Game table with NS/EW teams",
                body: `<ul>
                    <li>Your hand is at <strong>bottom (South)</strong>. Legal cards glow gold — click to play.</li>
                    <li>Center shows the current trick with player names color-coded: <span style="color:#4af">🔵 NS Blue</span> vs <span style="color:#f84">🔴 EW Orange</span>.</li>
                    <li>Team scores show in the center: <strong>NS: X Mindis / Y Tricks</strong> vs <strong>EW: X Mindis / Y Tricks</strong>.</li>
                    <li>Win 3+ Mindis (10s) to win the round. Win all 4 = KOT. Win all 13 tricks = White-Wash!</li>
                    <li>After 13 tricks, a round summary popup shows. Click <strong>⏭ Next Round</strong> to continue.</li>
                </ul>`
            }
        ]),
        hi: () => buildExploreHTML([
            {
                title: "🖥️ कदम 1 — सेटअप",
                img: GUIDE_IMGS.setup,
                alt: "सेटअप स्क्रीन",
                body: `<ul>
                    <li><strong>"Bindi Coat"</strong> चुनें। आप P1 (South, NS टीम) हैं।</li>
                    <li>आपका साथी P3 (North)। दुश्मन: P2 और P4।</li>
                    <li><strong>🚀 Start Match</strong> दबाएं।</li>
                </ul>`
            },
            {
                title: "🔒 कदम 2 — बंद हुकुम (Hidden Trump)",
                img: GUIDE_IMGS.bindiCoat,
                alt: "बंद हुकुम गाइड",
                body: `<ul>
                    <li>5 पत्ते बंटने के बाद, ट्रम्प प्लेसर को पॉपअप आता है।</li>
                    <li>एक पत्ता चुनें — वो <strong>बंद हुकुम</strong> बन जाता है।</li>
                    <li>जब कोई लेड सूट में पत्ता नहीं खेलता → <strong>🔓 हुकुम खुलता है!</strong></li>
                </ul>`
            },
            {
                title: "🔴 कदम 3 — गेम टेबल और मिंडी",
                img: GUIDE_IMGS.table,
                alt: "गेम टेबल गाइड",
                body: `<ul>
                    <li>आपके पत्ते नीचे। सुनहरे पत्ते क्लिक करें।</li>
                    <li>3+ मिंडी (10) जीतने वाली टीम राउंड जीतती है।</li>
                    <li>सभी 4 मिंडी = KOT. सभी 13 ट्रिक = White-Wash!</li>
                </ul>`
            }
        ])
    },

    tikdi: {
        en: () => buildExploreHTML([
            {
                title: "🖥️ Step 1 — Setup (3 Players)",
                img: GUIDE_IMGS.setup,
                alt: "Game setup screen",
                body: `<ul>
                    <li>Select <strong>"Tikdi (3-2-5)"</strong>. The 4th player button is hidden — Tikdi is <strong>3-player only</strong>.</li>
                    <li>You play as <strong>P1 (Dealer, Quota 2)</strong>. P2 = Chooser (Quota 5). P3 = Bystander (Quota 3).</li>
                    <li>Set 1, 2, or 3 humans. Hit <strong>🚀 Start Match</strong>.</li>
                    <li>Only 30 cards are used (8, 9, 10, J, Q, K, A in all 4 suits).</li>
                </ul>`
            },
            {
                title: "🃏 Step 2 — The Card Exchange & Trump",
                img: GUIDE_IMGS.table,
                alt: "Game table guide",
                body: `<ul>
                    <li>After deal, the Chooser (P2) passes 3 cards to the Dealer (P1) and receives 3 back.</li>
                    <li>Chooser picks the <strong>Trump Suit</strong> — announced in the game banner.</li>
                    <li>Your hand updates after exchange. You now have your 10 cards.</li>
                    <li>Chooser leads Trick 1. Must follow suit or play any card if void.</li>
                </ul>`
            },
            {
                title: "📊 Step 3 — Quotas & Round Summary",
                img: GUIDE_IMGS.table,
                alt: "Game table guide",
                body: `<ul>
                    <li>Play all 10 tricks. Watch the turn badge to know whose turn it is.</li>
                    <li>After all tricks, a <strong>Round Summary popup</strong> shows who met/missed their quota.</li>
                    <li>Miss your quota? You owe "debt cards" — given to the player who beat you next round before play starts.</li>
                    <li><strong>Penalty Settlement popup</strong> appears at the start of next round — blind card exchange happens.</li>
                    <li>Game header shows current trick count. Bots play after your turn automatically.</li>
                </ul>`
            }
        ]),
        hi: () => buildExploreHTML([
            {
                title: "🖥️ कदम 1 — सेटअप (3 खिलाड़ी)",
                img: GUIDE_IMGS.setup,
                alt: "सेटअप स्क्रीन",
                body: `<ul>
                    <li><strong>"Tikdi"</strong> चुनें। 4th सीट बटन छुपा रहेगा।</li>
                    <li>आप P1 (डीलर, कोटा 2) हैं।</li>
                    <li>1, 2, या 3 इंसान चुनें। <strong>🚀 Start Match</strong> दबाएं।</li>
                </ul>`
            },
            {
                title: "🃏 कदम 2 — पत्ता-बदली और ट्रम्प",
                img: GUIDE_IMGS.table,
                alt: "गेम टेबल गाइड",
                body: `<ul>
                    <li>Chooser (P2) 3 पत्ते डीलर को देता है, 3 वापस लेता है।</li>
                    <li>Chooser <strong>ट्रम्प सूट</strong> चुनता है।</li>
                    <li>10 ट्रिक खेली जाती हैं।</li>
                </ul>`
            },
            {
                title: "📊 कदम 3 — कोटा और राउंड",
                img: GUIDE_IMGS.table,
                alt: "गेम टेबल गाइड",
                body: `<ul>
                    <li>राउंड के बाद <strong>Summary Popup</strong> आता है।</li>
                    <li>कोटा मिस? अगले राउंड में <strong>पेनल्टी पत्ते</strong> देने होंगे।</li>
                    <li>Bots अपनी बारी खुद खेलते हैं।</li>
                </ul>`
            }
        ])
    }
};


let rulesPreviousView = "home";

function openRulesPage(gameKey, lang) {
    const tableEl = document.getElementById("view-table");
    if (tableEl && !tableEl.classList.contains("hidden")) {
        rulesPreviousView = "table";
    } else {
        rulesPreviousView = "home";
    }

    currentRulesGame = gameKey || (typeof currentGameType !== "undefined" && currentGameType) || (typeof activeSelectedGame !== "undefined" && activeSelectedGame) || "bikkad";
    currentRulesLang = lang || (typeof getCurrentLanguage === "function" && getCurrentLanguage() === "hi" ? "hi" : "en");
    currentRulesTab = "howtoplay";

    const data = RULES_DATA[currentRulesGame];
    if (!data) { console.warn("No rules data for:", currentRulesGame); return; }

    // Update banner
    const bIcon = document.getElementById("rules-banner-icon");
    const gIcon = document.getElementById("rules-game-icon");
    const gNav = document.getElementById("rules-game-name-nav");
    const bName = document.getElementById("rules-banner-name");
    const bTag = document.getElementById("rules-banner-tagline");
    const bMeta = document.getElementById("rules-banner-meta");

    if (bIcon) bIcon.textContent = data.icon;
    if (gIcon) gIcon.textContent = data.icon;
    if (gNav) gNav.textContent = data.name;
    if (bName) bName.textContent = data.name;
    if (bTag) bTag.textContent = currentRulesLang === "hi" ? data.tagline_hi : data.tagline_en;
    if (bMeta) bMeta.textContent = data.meta;

    // Set language class on body
    const contentArea = document.getElementById("rules-content-area");
    if (contentArea) {
        contentArea.className = "rules-content-area rules-lang-" + currentRulesLang;
    }

    // Update lang button
    const langBtn = document.getElementById("btn-rules-lang");
    if (langBtn) langBtn.textContent = currentRulesLang === "en" ? "🌐 हिंदी" : "🌐 EN";

    // Render howtoplay tab first
    switchRulesTab("howtoplay");

    // Switch to rules view
    document.querySelectorAll(".view-container").forEach(v => v.classList.add("hidden"));
    const viewRules = document.getElementById("view-rules");
    if (viewRules) viewRules.classList.remove("hidden");
}
window.openRulesPage = openRulesPage;

function closeRulesPage() {
    document.querySelectorAll(".view-container").forEach(v => v.classList.add("hidden"));
    if (rulesPreviousView === "table") {
        const viewTable = document.getElementById("view-table");
        if (viewTable) viewTable.classList.remove("hidden");
    } else {
        const viewHome = document.getElementById("view-home");
        if (viewHome) viewHome.classList.remove("hidden");
    }
}
window.closeRulesPage = closeRulesPage;

function toggleRulesLang() {
    currentRulesLang = currentRulesLang === "en" ? "hi" : "en";
    const langBtn = document.getElementById("btn-rules-lang");
    if (langBtn) langBtn.textContent = currentRulesLang === "en" ? "🌐 हिंदी" : "🌐 EN";

    const data = RULES_DATA[currentRulesGame];
    if (data) {
        document.getElementById("rules-banner-tagline").textContent =
            currentRulesLang === "hi" ? data.tagline_hi : data.tagline_en;
    }

    const contentArea = document.getElementById("rules-content-area");
    if (contentArea) {
        contentArea.className = "rules-content-area rules-lang-" + currentRulesLang;
    }

    // Re-render current tab in new language
    switchRulesTab(currentRulesTab);
}
window.toggleRulesLang = toggleRulesLang;

function switchRulesTab(tabKey) {
    currentRulesTab = tabKey;
    const tabs = ["objective", "rules", "explore", "howtoplay", "tips"];
    tabs.forEach(t => {
        const btn = document.getElementById("rtab-" + t);
        if (btn) btn.classList.toggle("active", t === tabKey);
    });

    const contentArea = document.getElementById("rules-content-area");
    if (!contentArea) return;

    // Explore tab uses EXPLORE_DATA (function-based generators)
    if (tabKey === "explore") {
        const exploreGame = EXPLORE_DATA[currentRulesGame];
        if (!exploreGame) {
            contentArea.innerHTML = "<p style='color:#888;padding:20px'>Explore guide coming soon for this game.</p>";
            return;
        }
        const langFn = currentRulesLang === "hi" ? exploreGame.hi : exploreGame.en;
        const html = langFn ? langFn() : (exploreGame.en ? exploreGame.en() : "");
        contentArea.innerHTML = html;
        return;
    }

    // Standard tabs from RULES_DATA
    const data = RULES_DATA[currentRulesGame];
    if (!data || !data[tabKey]) {
        contentArea.innerHTML = "<p style='color:#888;padding:20px'>Content coming soon.</p>";
        return;
    }

    const tabData = data[tabKey];
    const enContent = tabData.en || "";
    const hiContent = tabData.hi || tabData.en || "";

    contentArea.innerHTML = `
        <div class="en-content">${enContent}</div>
        <div class="hi-content">${hiContent}</div>`;
}
window.switchRulesTab = switchRulesTab;

// Init: highlight bikkad on page load
document.addEventListener("DOMContentLoaded", function() {
    // Default gsel-card highlight
    const defaultCard = document.querySelector('.gsel-card[data-game="bikkad"]');
    if (defaultCard) defaultCard.classList.add("gsel-active");

    // Guide image lightbox — click any .guide-img-wrap to expand
    document.addEventListener("click", function(e) {
        const wrap = e.target.closest(".guide-img-wrap");
        if (wrap) {
            const img = wrap.querySelector("img");
            if (!img) return;
            const lb = document.createElement("div");
            lb.className = "guide-lightbox";
            lb.innerHTML = `<button class="guide-lightbox-close" title="Close">✕</button>
                            <img src="${img.src}" alt="${img.alt}">`;
            lb.addEventListener("click", () => lb.remove());
            document.body.appendChild(lb);
        }
    });
});
