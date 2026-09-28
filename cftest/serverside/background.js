const api = typeof browser !== "undefined" ? browser : chrome;
const SERVER_URL = "http://127.0.0.1:8765";
const RETRY_INTERVAL_MS = 200;

let pendingPayload = null;


async function isEnabled() {
    const { enabled } = await api.storage.local.get("enabled");
    return enabled ?? true;
}


api.action.onClicked.addListener(async () => {
    const enabled = await isEnabled();
    await api.storage.local.set({enabled: !enabled});
    api.action.setTitle({title: `cftest: auto-grab ${!enabled ? "ON" : "OFF"}` });
});


api.storage.onChanged.addListener((changes) => {
    if (changes.enabled && changes.enabled.newValue == true && pendingPayload) {
    sendToServer(pendingPayload);
}
});


async function sendToServer(payload) {
    pendingPayload = payload;

    const enabled = await isEnabled();
    if (!enabled) return;

    try {
        const res = await fetch(SERVER_URL, {
            method: "POST",
            headers: {"Content-Type": "application/json"},
            body: JSON.stringify(payload)
        });
        if (!res.ok) throw new Error("bad response");
        pendingPayload = null;
    } catch (e) {
        setTimeout(() => sendToServer(payload), RETRY_INTERVAL_MS);
    }
}

api.runtime.onMessage.addListener((message) => {
    if (message.type == "CFTEST_GRAB") {
        sendToServer(message.payload);
    }
});
