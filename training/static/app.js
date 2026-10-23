// Copy buttons for templates and code blocks. Labels come from the page's
// language (data-copy, data-copied and data-copyfail on the html element).
(function () {
  var root = document.documentElement;
  var L = {
    copy: root.getAttribute("data-copy") || "Copy",
    copied: root.getAttribute("data-copied") || "Copied!",
    fail: root.getAttribute("data-copyfail") || "Select and copy"
  };
  document.querySelectorAll(".copy-btn").forEach(function (b) { b.textContent = L.copy; });

  document.addEventListener("click", function (e) {
    var btn = e.target.closest(".copy-btn");
    if (!btn) return;
    var pre = btn.parentElement.querySelector("pre");
    var text = pre ? pre.innerText : "";
    function done(ok) {
      btn.textContent = ok ? L.copied : L.fail;
      setTimeout(function () { btn.textContent = L.copy; }, 2000);
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
    if (navigator.clipboard && window.isSecureContext) {
      navigator.clipboard.writeText(text).then(function () { done(true); }, function () { done(fallback()); });
    } else {
      done(fallback());
    }
  });

  // Switch language as soon as one is picked.
  var sel = document.getElementById("lang-select");
  if (sel) sel.addEventListener("change", function () { sel.form.submit(); });
})();
