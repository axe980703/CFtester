

function grabTests() {
    const inp = Array.from(document.querySelectorAll('div.input pre')).map(x => x.innerText.trim());
    const out = Array.from(document.querySelectorAll('div.output pre')).map(x => x.innerText.trim());
    return {inp, out};
}

const tests = grabTests();
if (tests.inp.length > 0) {
    const api = typeof browser !== "undefined" ? browser : chrome;
    api.runtime.sendMessage({type: "CFTEST_GRAB", payload: tests});
}

