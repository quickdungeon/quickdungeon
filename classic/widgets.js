// Minimal stand-ins for the Shortcodes Ultimate tabs/spoiler widgets used on the original site.
document.querySelectorAll('.su-spoiler-title').forEach(t =>
  t.addEventListener('click', () => t.parentElement.classList.toggle('su-spoiler-closed')));
document.querySelectorAll('.su-tabs').forEach(tabs => {
  const navs = tabs.querySelectorAll(':scope > .su-tabs-nav > span');
  const panes = tabs.querySelectorAll(':scope > .su-tabs-panes > .su-tabs-pane');
  const show = i => { navs.forEach((n, k) => n.classList.toggle('su-tabs-current', k === i));
                      panes.forEach((p, k) => p.classList.toggle('su-tabs-current', k === i)); };
  navs.forEach((n, i) => n.addEventListener('click', () => show(i)));
  show(Math.max(0, (parseInt(tabs.dataset.active, 10) || 1) - 1));
});
