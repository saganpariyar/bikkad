// Desi Card Games - PWA Registration & Install Controller

let deferredInstallPrompt = null;

// Register Service Worker
if ("serviceWorker" in navigator) {
    window.addEventListener("load", () => {
        navigator.serviceWorker.register("sw.js")
            .then((registration) => {
                console.log("PWA ServiceWorker registered with scope:", registration.scope);
            })
            .catch((err) => {
                console.warn("PWA ServiceWorker registration failed:", err);
            });
    });
}

// Handle PWA Install Prompt
window.addEventListener("beforeinstallprompt", (e) => {
    // Prevent standard browser infobar
    e.preventDefault();
    deferredInstallPrompt = e;

    // Show Install App button in navbar
    const installBtn = document.getElementById("btn-install-pwa");
    if (installBtn) {
        installBtn.classList.remove("hidden");
        installBtn.addEventListener("click", triggerPwaInstall);
    }
});

async function triggerPwaInstall() {
    if (!deferredInstallPrompt) return;

    // Show native prompt
    deferredInstallPrompt.prompt();

    const choiceResult = await deferredInstallPrompt.userChoice;
    console.log("User install prompt response:", choiceResult.outcome);

    if (choiceResult.outcome === "accepted") {
        const installBtn = document.getElementById("btn-install-pwa");
        if (installBtn) installBtn.classList.add("hidden");
    }
    deferredInstallPrompt = null;
}

window.addEventListener("appinstalled", () => {
    console.log("Desi Card Games PWA successfully installed!");
    const installBtn = document.getElementById("btn-install-pwa");
    if (installBtn) installBtn.classList.add("hidden");
    deferredInstallPrompt = null;
});
