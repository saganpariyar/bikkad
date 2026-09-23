// Web Audio API Synthesizer for Card SFX
class SoundEffects {
    constructor() {
        this.ctx = null;
        this.enabled = true;
    }

    init() {
        if (!this.ctx) {
            const AudioContext = window.AudioContext || window.webkitAudioContext;
            if (AudioContext) {
                this.ctx = new AudioContext();
            }
        }
    }

    playDeal() {
        if (!this.enabled) return;
        this.init();
        if (!this.ctx) return;

        const osc = this.ctx.createOscillator();
        const gain = this.ctx.createGain();
        osc.type = 'triangle';
        osc.frequency.setValueAtTime(400, this.ctx.currentTime);
        osc.frequency.exponentialRampToValueAtTime(120, this.ctx.currentTime + 0.08);

        gain.gain.setValueAtTime(0.3, this.ctx.currentTime);
        gain.gain.linearRampToValueAtTime(0.01, this.ctx.currentTime + 0.08);

        osc.connect(gain);
        gain.connect(this.ctx.destination);

        osc.start();
        osc.stop(this.ctx.currentTime + 0.08);
    }

    playCard() {
        if (!this.enabled) return;
        this.init();
        if (!this.ctx) return;

        const osc = this.ctx.createOscillator();
        const gain = this.ctx.createGain();
        osc.type = 'sine';
        osc.frequency.setValueAtTime(300, this.ctx.currentTime);
        osc.frequency.exponentialRampToValueAtTime(150, this.ctx.currentTime + 0.06);

        gain.gain.setValueAtTime(0.4, this.ctx.currentTime);
        gain.gain.linearRampToValueAtTime(0.01, this.ctx.currentTime + 0.06);

        osc.connect(gain);
        gain.connect(this.ctx.destination);

        osc.start();
        osc.stop(this.ctx.currentTime + 0.06);
    }

    playTrumpFlip() {
        if (!this.enabled) return;
        this.init();
        if (!this.ctx) return;

        const osc = this.ctx.createOscillator();
        const gain = this.ctx.createGain();
        osc.type = 'square';
        osc.frequency.setValueAtTime(520, this.ctx.currentTime);
        osc.frequency.exponentialRampToValueAtTime(880, this.ctx.currentTime + 0.15);

        gain.gain.setValueAtTime(0.2, this.ctx.currentTime);
        gain.gain.linearRampToValueAtTime(0.01, this.ctx.currentTime + 0.15);

        osc.connect(gain);
        gain.connect(this.ctx.destination);

        osc.start();
        osc.stop(this.ctx.currentTime + 0.15);
    }

    playPotSweep() {
        if (!this.enabled) return;
        this.init();
        if (!this.ctx) return;

        const now = this.ctx.currentTime;
        const notes = [523.25, 659.25, 783.99, 1046.50]; // C5, E5, G5, C6 arpeggio
        notes.forEach((freq, i) => {
            const osc = this.ctx.createOscillator();
            const gain = this.ctx.createGain();
            osc.type = 'sine';
            osc.frequency.setValueAtTime(freq, now + i * 0.06);

            gain.gain.setValueAtTime(0.3, now + i * 0.06);
            gain.gain.linearRampToValueAtTime(0.01, now + i * 0.06 + 0.12);

            osc.connect(gain);
            gain.connect(this.ctx.destination);

            osc.start(now + i * 0.06);
            osc.stop(now + i * 0.06 + 0.12);
        });
    }

    // Voice announcement helper using SpeechSynthesis
    speakVoice(text, lang = 'hi-IN') {
        if (!this.enabled || !window.speechSynthesis) return;
        try {
            window.speechSynthesis.cancel();
            const utterance = new SpeechSynthesisUtterance(text);
            utterance.lang = lang;
            utterance.rate = 1.08;
            utterance.pitch = 1.1;
            utterance.volume = 0.9;

            // Try to pick an Indian English or Hindi voice if available
            const voices = window.speechSynthesis.getVoices();
            if (voices && voices.length > 0) {
                const indianVoice = voices.find(v => v.lang.includes('hi') || v.lang.includes('IN'));
                if (indianVoice) utterance.voice = indianVoice;
            }
            window.speechSynthesis.speak(utterance);
        } catch (e) {
            console.warn("Speech synthesis error:", e);
        }
    }

    // Ace (Akka) played audio: Dramatic power chord + "Akka!" voice
    playAkka() {
        if (!this.enabled) return;
        this.init();
        if (this.ctx) {
            const now = this.ctx.currentTime;
            // Power brass chord: C4, G4, C5, E5
            const chord = [261.63, 392.00, 523.25, 659.25];
            chord.forEach(freq => {
                const osc = this.ctx.createOscillator();
                const gain = this.ctx.createGain();
                osc.type = 'triangle';
                osc.frequency.setValueAtTime(freq, now);
                osc.frequency.exponentialRampToValueAtTime(freq * 0.98, now + 0.35);

                gain.gain.setValueAtTime(0.25, now);
                gain.gain.exponentialRampToValueAtTime(0.001, now + 0.35);

                osc.connect(gain);
                gain.connect(this.ctx.destination);

                osc.start(now);
                osc.stop(now + 0.35);
            });
        }
        // Vocal call
        setTimeout(() => this.speakVoice("Akka!", "hi-IN"), 40);
    }

    // Demand Trump (Hukum Dikhao) audio: Fanfare bugle + "Hukum dikhao!" voice
    playHukumDikhao() {
        if (!this.enabled) return;
        this.init();
        if (this.ctx) {
            const now = this.ctx.currentTime;
            // Bugle notes: G4 (392), C5 (523.25), E5 (659.25), G5 (783.99)
            const fanfare = [
                { f: 392.00, t: 0, d: 0.10 },
                { f: 523.25, t: 0.10, d: 0.10 },
                { f: 659.25, t: 0.20, d: 0.12 },
                { f: 783.99, t: 0.32, d: 0.28 }
            ];
            fanfare.forEach(n => {
                const osc = this.ctx.createOscillator();
                const gain = this.ctx.createGain();
                osc.type = 'sawtooth';
                osc.frequency.setValueAtTime(n.f, now + n.t);

                gain.gain.setValueAtTime(0.2, now + n.t);
                gain.gain.exponentialRampToValueAtTime(0.01, now + n.t + n.d);

                osc.connect(gain);
                gain.connect(this.ctx.destination);

                osc.start(now + n.t);
                osc.stop(now + n.t + n.d);
            });
        }
        // Vocal call
        setTimeout(() => this.speakVoice("Hukum dikhao!", "hi-IN"), 60);
    }

    // Tera declaration: Fanfare chord + "${playerName}, Tera!" voice
    playTera(playerName = "Player") {
        if (!this.enabled) return;
        this.init();
        if (this.ctx) {
            const now = this.ctx.currentTime;
            // Ascending power fanfare: C4 (261.63), E4 (329.63), G4 (392.00), C5 (523.25)
            const notes = [
                { f: 261.63, t: 0, d: 0.12 },
                { f: 329.63, t: 0.10, d: 0.12 },
                { f: 392.00, t: 0.20, d: 0.14 },
                { f: 523.25, t: 0.32, d: 0.40 }
            ];
            notes.forEach(n => {
                const osc = this.ctx.createOscillator();
                const gain = this.ctx.createGain();
                osc.type = 'sawtooth';
                osc.frequency.setValueAtTime(n.f, now + n.t);

                gain.gain.setValueAtTime(0.25, now + n.t);
                gain.gain.exponentialRampToValueAtTime(0.005, now + n.t + n.d);

                osc.connect(gain);
                gain.connect(this.ctx.destination);

                osc.start(now + n.t);
                osc.stop(now + n.t + n.d);
            });
        }
        const cleanName = (playerName || "Player").split('(')[0].trim();
        setTimeout(() => this.speakVoice(`${cleanName} ki Tera!`, "hi-IN"), 80);
    }

    // Double Tera declaration: Double trumpet blast fanfare + "${playerName} ki Double Tera!" voice
    playDoubleTera(playerName = "Player") {
        if (!this.enabled) return;
        this.init();
        if (this.ctx) {
            const now = this.ctx.currentTime;
            // Double trumpet blast: E4, G4, C5, E5, G5
            const notes = [
                { f: 329.63, t: 0, d: 0.10 },
                { f: 392.00, t: 0.08, d: 0.10 },
                { f: 523.25, t: 0.18, d: 0.12 },
                { f: 659.25, t: 0.28, d: 0.15 },
                { f: 783.99, t: 0.42, d: 0.50 }
            ];
            notes.forEach(n => {
                const osc = this.ctx.createOscillator();
                const gain = this.ctx.createGain();
                osc.type = 'sawtooth';
                osc.frequency.setValueAtTime(n.f, now + n.t);

                gain.gain.setValueAtTime(0.28, now + n.t);
                gain.gain.exponentialRampToValueAtTime(0.005, now + n.t + n.d);

                osc.connect(gain);
                gain.connect(this.ctx.destination);

                osc.start(now + n.t);
                osc.stop(now + n.t + n.d);
            });
        }
        const cleanName = (playerName || "Player").split('(')[0].trim();
        setTimeout(() => this.speakVoice(`${cleanName} ki Double Tera!`, "hi-IN"), 80);
    }
}

const sfx = new SoundEffects();

