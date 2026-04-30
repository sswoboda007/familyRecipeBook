// Progressive enhancement: AJAX for thumbs-up and rating so the page
// doesn't need to reload. Falls back to a normal form POST on error.

function postForm(url, formData) {
    return fetch(url, {
        method: 'POST',
        body: formData,
        credentials: 'same-origin',
        headers: { 'X-Requested-With': 'fetch' },
    });
}

// Thumbs-up toggle
document.querySelectorAll('.thumbs-form').forEach((form) => {
    form.addEventListener('submit', async (event) => {
        const btn = form.querySelector('.thumbs-btn');
        if (!btn || btn.disabled) return;
        event.preventDefault();
        btn.disabled = true;
        try {
            const res = await postForm(form.action, new FormData(form));
            if (!res.ok) throw new Error('request failed');
            const data = await res.json();
            btn.classList.toggle('active', !!data.active);
            const count = btn.querySelector('.thumbs-count');
            if (count) count.textContent = data.count;
        } catch (err) {
            form.submit();
            return;
        } finally {
            btn.disabled = false;
        }
    });
});

// Star ratings: hover preview + AJAX submit
document.querySelectorAll('.rate-form').forEach((form) => {
    const stars = Array.from(form.querySelectorAll('.star'));
    if (!stars.length) return;

    const paint = (count, cls) => {
        stars.forEach((s, i) => s.classList.toggle(cls, i < count));
    };

    stars.forEach((star, idx) => {
        star.addEventListener('mouseenter', () => paint(idx + 1, 'hover'));
        star.addEventListener('mouseleave', () => paint(0, 'hover'));
    });

    form.addEventListener('submit', async (event) => {
        const submitter = event.submitter;
        if (!submitter || submitter.disabled) return;
        event.preventDefault();
        const value = parseInt(submitter.value, 10);
        const fd = new FormData();
        fd.append('stars', String(value));
        try {
            const res = await postForm(form.action, fd);
            if (!res.ok) throw new Error('request failed');
            const data = await res.json();
            paint(data.stars, 'on');
            const ratingBox = form.closest('.rating');
            if (ratingBox) {
                const avg = ratingBox.querySelector('.avg');
                if (avg) avg.textContent = data.average.toFixed(1);
            }
        } catch (err) {
            form.submit();
        }
    });
});