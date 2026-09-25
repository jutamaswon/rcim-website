const toggle = document.getElementById('menu-toggle');
const nav = document.getElementById('site-nav');

if (toggle && nav) {
  toggle.addEventListener('click', () => {
    const open = toggle.getAttribute('aria-expanded') !== 'true';
    toggle.setAttribute('aria-expanded', String(open));
    nav.classList.toggle('open', open);
  });
  document.addEventListener('keydown', (event) => {
    if (event.key === 'Escape') {
      nav.classList.remove('open');
      toggle.setAttribute('aria-expanded', 'false');
    }
  });
}

const archiveSearch = document.getElementById('archive-search');
if (archiveSearch) {
  const groups = [...document.querySelectorAll('.archive-year')];
  const empty = document.getElementById('archive-empty');
  archiveSearch.addEventListener('input', () => {
    const query = archiveSearch.value.trim().toLocaleLowerCase('th');
    let visible = 0;
    for (const group of groups) {
      let groupVisible = 0;
      for (const row of group.querySelectorAll('.archive-row')) {
        const match = row.textContent.toLocaleLowerCase('th').includes(query);
        row.hidden = !match;
        if (match) groupVisible++;
      }
      group.hidden = groupVisible === 0;
      visible += groupVisible;
    }
    if (empty) empty.hidden = visible !== 0;
  });
}
