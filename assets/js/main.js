// Calmora · 모바일 내비게이션 토글 (경량, 렌더 차단 없음)
(function () {
  document.addEventListener('click', function (e) {
    var toggle = e.target.closest('[data-nav-toggle]');
    if (toggle) {
      var nav = toggle.closest('.nav');
      if (nav) {
        var open = nav.classList.toggle('open');
        toggle.setAttribute('aria-expanded', open ? 'true' : 'false');
      }
      return;
    }
    var nav = document.querySelector('.nav.open');
    if (nav && !e.target.closest('.nav')) nav.classList.remove('open');
  });
})();
