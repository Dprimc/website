document.addEventListener('DOMContentLoaded', () => {
    const navToggle = document.querySelector('.nav-toggle');
    const nav = document.getElementById('site-nav');

    if (!navToggle || !nav) {
        return;
    }

    const closeNav = () => {
        nav.classList.remove('is-open');
        navToggle.setAttribute('aria-expanded', 'false');
    };

    const openNav = () => {
        nav.classList.add('is-open');
        navToggle.setAttribute('aria-expanded', 'true');
    };

    navToggle.addEventListener('click', () => {
        const isExpanded = navToggle.getAttribute('aria-expanded') === 'true';
        if (isExpanded) {
            closeNav();
        } else {
            openNav();
        }
    });

    nav.querySelectorAll('a').forEach(link => {
        link.addEventListener('click', () => {
            closeNav();
        });
    });

    document.addEventListener('click', event => {
        if (!nav.contains(event.target) && !navToggle.contains(event.target)) {
            closeNav();
        }
    });

    document.addEventListener('keydown', event => {
        if (event.key === 'Escape') {
            closeNav();
        }
    });
});
