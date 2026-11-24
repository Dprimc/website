document.addEventListener('DOMContentLoaded', () => {
    const navToggle = document.querySelector('.nav-toggle');
    const nav = document.getElementById('site-nav');

    const closeNav = () => {
        if (!nav || !navToggle) return;
        nav.classList.remove('is-open');
        navToggle.setAttribute('aria-expanded', 'false');
    };

    const openNav = () => {
        if (!nav || !navToggle) return;
        nav.classList.add('is-open');
        navToggle.setAttribute('aria-expanded', 'true');
    };

    if (navToggle && nav) {
        navToggle.addEventListener('click', () => {
            const isExpanded = navToggle.getAttribute('aria-expanded') === 'true';
            isExpanded ? closeNav() : openNav();
        });

        nav.querySelectorAll('a').forEach(link => {
            link.addEventListener('click', () => closeNav());
        });

        document.addEventListener('click', event => {
            if (!nav.contains(event.target) && !navToggle.contains(event.target)) closeNav();
        });
    }

    const links = nav ? Array.from(nav.querySelectorAll('a')) : [];
    const setActive = () => {
        const currentPath = window.location.pathname;
        const currentHash = window.location.hash;
        links.forEach(link => {
            const url = new URL(link.getAttribute('href'), window.location.origin);
            const matchesPath = url.pathname === currentPath;
            const matchesHash = url.hash && url.hash === currentHash;
            link.classList.toggle('is-active', matchesPath && (matchesHash || (!url.hash && !currentHash)));
        });
    };
    setActive();
    window.addEventListener('hashchange', setActive);

    document.addEventListener('keydown', event => {
        if (event.key === 'Escape' && nav && nav.classList.contains('is-open')) {
            const focusWasInNav = nav.contains(document.activeElement);
            closeNav();
            if (focusWasInNav) navToggle.focus();
        }
    });
});
