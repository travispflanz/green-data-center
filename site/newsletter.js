// GreenCompute shared newsletter handler (all footer signup forms)
(function () {
  function init() {
    var forms = document.querySelectorAll('.footer-signup');
    if (!forms.length) return;

    forms.forEach(function (form) {
      var msg = form.querySelector('.footer-msg');
      var emailInput = form.querySelector('input[type="email"]');
      var btn = form.querySelector('button[type="submit"]');
      var source = form.querySelector('input[name="source"]');
      var page = source ? source.value : 'footer';

      form.addEventListener('submit', async function (e) {
        e.preventDefault();
        if (!emailInput || !emailInput.value) return;
        btn.disabled = true;
        btn.innerText = 'Submitting...';
        try {
          var res = await fetch('/api/subscribe', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ email: emailInput.value, source: page })
          });
          var data = await res.json();
          msg.style.display = 'block';
          msg.style.color = data.success ? 'var(--primary)' : 'red';
          msg.innerText = data.message;
          if (data.success) form.reset();
        } catch (err) {
          msg.style.display = 'block';
          msg.style.color = 'red';
          msg.innerText = 'Network error communicating with Cloudflare edge worker.';
        } finally {
          btn.disabled = false;
          btn.innerText = 'Subscribe';
        }
      });
    });
  }

  if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', init);
  } else {
    init();
  }
})();
