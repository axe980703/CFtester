const api = typeof browser !== "undefined" ? browser : chrome;
const RETRY_MS = 200;

const payload = {
    inp: Array.from(document.querySelectorAll('div.input pre')).map(x => x.innerText.trim()),
    out: Array.from(document.querySelectorAll('div.output pre')).map(x => x.innerText.trim())
};

let delivered = false;
let running = false;

async function isEnabled() {
    const { enabled } = await api.storage.local.get("enabled");
    return enabled ?? true;
}

async function send() {
    try {
        const reply = await api.runtime.sendMessage({ type: "CFTEST_GRAB", payload });
        return reply?.ok === true;
    } catch (e) {
        return false;
    }
}


async function attempt() {
    if (delivered || running) return;
    running = true;
    while (!delivered && await isEnabled()) {
        delivered = await send();
        if (!delivered) await new Promise(r => setTimeout(r, RETRY_MS));
    }
    running = false;
}


api.storage.onChanged.addListener((changes) => {
    if (changes.enabled?.newValue === true) attempt();
});

if (payload.inp.length > 0) attempt();
