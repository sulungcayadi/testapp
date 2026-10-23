// Copy buttons for templates and code blocks.
document.addEventListener("click", function (e) {
  var btn = e.target.closest(".copy-btn");
  if (!btn) return;
  var pre = btn.parentElement.querySelector("pre");
  var text = pre ? pre.innerText : "";
  function done(ok) {
    btn.textContent = ok ? "Copied!" : "Select and copy";
    setTimeout(function () { btn.textContent = "Copy"; }, 2000);
  }
  if (navigator.clipboard && window.isSecureContext) {
    navigator.clipboard.writeText(text).then(function () { done(true); }, function () { done(fallback()); });
  } else {
    done(fallback());
  }
  function fallback() {
    var ta = document.createElement("textarea");
    ta.value = text;
    ta.setAttribute("readonly", "");
    ta.style.position = "absolute";
    ta.style.left = "-9999px";
    document.body.appendChild(ta);
    ta.select();
    var ok = false;
    try { ok = document.execCommand("copy"); } catch (err) { ok = false; }
    document.body.removeChild(ta);
    return ok;
  }
});
