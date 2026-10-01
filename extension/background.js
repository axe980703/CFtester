const api = typeof browser !== "undefined" ? browser : chrome;
const SERVER_URL = "http://127.0.0.1:8765";



async function isEnabled() {
    const { enabled } = await api.storage.local.get("enabled");
    return enabled ?? true;
}


async function refreshBadge() {
      const enabled = await isEnabled();
      api.action.setBadgeText({ text: enabled ? "ON" : "OFF" });
      api.action.setBadgeBackgroundColor({ color: enabled ? "#2e9d4f" : "#c0392b" });
      api.action.setTitle({ title: `cftest auto-grab: ${enabled ? "ON" : "OFF"} (click to toggle)` });
}


api.action.onClicked.addListener(async () => {
    const enabled = await isEnabled();
    await api.storage.local.set({enabled: !enabled});
    refreshBadge();
});


api.runtime.onMessage.addListener((message, sender, sendResponse) => {
    if (message.type !== "CFTEST_GRAB") return;

    fetch(SERVER_URL, {
        method: "POST",
        headers: {"Content-Type": "application/json"},
        body: JSON.stringify(message.payload)
    })
     .then(res => sendResponse({ok: res.ok}))
     .catch(() => sendResponse({ok: false})); 

    return true;
});

refreshBadge();
