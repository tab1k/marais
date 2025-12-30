// Placeholder for site JS
document.addEventListener('DOMContentLoaded', function () {
  const filterToggle = document.querySelector('[data-filter-toggle]');
  const filterPanel = document.querySelector('[data-filter-panel]');
  const filterBackdrop = document.querySelector('[data-filter-backdrop]');
  const filterClose = document.querySelector('[data-filter-close]');
  const burger = document.querySelector('[data-menu-toggle]');
  const mobileMenu = document.querySelector('[data-menu]');
  const mobileBackdrop = document.querySelector('[data-menu-backdrop]');
  const mobileLinks = mobileMenu?.querySelectorAll('.mobile-menu__link');
  const mobileClose = document.querySelector('[data-menu-close]');
  const galleryMainImg = document.querySelector('[data-gallery-main]');
  const galleryThumbs = document.querySelectorAll('[data-gallery-thumbs] .thumb');
  const galleryDots = document.querySelectorAll('[data-gallery-dots] .dot');
  const profileSheet = document.querySelector('[data-profile-settings]');
  const profileSheetOpen = document.querySelector('[data-profile-settings-open]');
  const profileSheetClose = document.querySelectorAll('[data-profile-settings-close]');
  const profileSheetBackdrop = document.querySelector('[data-profile-settings-backdrop]');
  const body = document.body;

  const syncBodyLock = () => {
    const filterOpen = filterPanel?.classList.contains('is-open');
    const menuOpen = mobileMenu?.classList.contains('is-open');
    const sheetOpen = profileSheet?.classList.contains('is-open');
    if (filterOpen || menuOpen || sheetOpen) {
      body.classList.add('no-scroll');
      document.documentElement.classList.add('no-scroll');
    } else {
      body.classList.remove('no-scroll');
      document.documentElement.classList.remove('no-scroll');
    }
  };

  const closeFilter = () => {
    filterPanel?.classList.remove('is-open');
    filterBackdrop?.classList.remove('is-visible');
    syncBodyLock();
  };

  const openFilter = () => {
    if (!filterPanel) return;
    filterPanel.classList.add('is-open');
    filterBackdrop?.classList.add('is-visible');
    syncBodyLock();
  };

  const openProfileSheet = () => {
    if (!profileSheet) return;
    profileSheet.classList.add('is-open');
    profileSheetBackdrop?.classList.add('is-visible');
    syncBodyLock();
  };

  const closeProfileSheet = () => {
    profileSheet?.classList.remove('is-open');
    profileSheetBackdrop?.classList.remove('is-visible');
    syncBodyLock();
  };

  const closeMenu = () => {
    mobileMenu?.classList.remove('is-open');
    burger?.classList.remove('is-active');
    syncBodyLock();
  };

  const openMenu = () => {
    if (!mobileMenu) return;
    mobileMenu.classList.add('is-open');
    burger?.classList.add('is-active');
    syncBodyLock();
  };

  filterToggle?.addEventListener('click', openFilter);
  filterClose?.addEventListener('click', closeFilter);
  filterBackdrop?.addEventListener('click', closeFilter);

  profileSheetOpen?.addEventListener('click', openProfileSheet);
  profileSheetClose?.forEach(btn => btn.addEventListener('click', closeProfileSheet));
  profileSheetBackdrop?.addEventListener('click', closeProfileSheet);

  const updateGallery = (src) => {
    if (galleryMainImg && src) {
      galleryMainImg.src = src;
    }
    galleryThumbs?.forEach(btn => btn.classList.toggle('active', btn.dataset.gallerySrc === src));
    galleryDots?.forEach(dot => dot.classList.toggle('active', dot.dataset.gallerySrc === src));
  };

  galleryThumbs?.forEach(btn => {
    btn.addEventListener('click', () => updateGallery(btn.dataset.gallerySrc));
  });

  galleryDots?.forEach(dot => {
    dot.addEventListener('click', () => updateGallery(dot.dataset.gallerySrc));
  });

  // Swipe support for gallery (mobile)
  const galleryItems = [...(galleryDots.length ? galleryDots : galleryThumbs)].map(el => el.dataset.gallerySrc);
  let touchStartX = null;

  const getCurrentIndex = () => {
    if (!galleryMainImg || !galleryItems.length) return 0;
    const currentSrc = galleryMainImg.getAttribute('src');
    const idx = galleryItems.findIndex(src => currentSrc.includes(src));
    return idx >= 0 ? idx : 0;
  };

  const showByIndex = (idx) => {
    if (!galleryItems.length) return;
    const wrapped = (idx + galleryItems.length) % galleryItems.length;
    updateGallery(galleryItems[wrapped]);
  };

  const handleTouchStart = (e) => {
    touchStartX = e.touches[0].clientX;
  };

  const handleTouchEnd = (e) => {
    if (touchStartX === null) return;
    const deltaX = e.changedTouches[0].clientX - touchStartX;
    const threshold = 40;
    if (Math.abs(deltaX) > threshold) {
      const current = getCurrentIndex();
      if (deltaX < 0) {
        showByIndex(current + 1);
      } else {
        showByIndex(current - 1);
      }
    }
    touchStartX = null;
  };

  if (galleryMainImg) {
    galleryMainImg.addEventListener('touchstart', handleTouchStart, { passive: true });
    galleryMainImg.addEventListener('touchend', handleTouchEnd, { passive: true });
  }

  burger?.addEventListener('click', () => {
    if (mobileMenu?.classList.contains('is-open')) {
      closeMenu();
    } else {
      openMenu();
    }
  });

  mobileBackdrop?.addEventListener('click', closeMenu);
  mobileLinks?.forEach(link => link.addEventListener('click', (e) => {
    // Don't close menu if clicking an accordion toggle
    if (link.tagName.toLowerCase() === 'summary') return;
    closeMenu();
  }));
  mobileClose?.addEventListener('click', closeMenu);

  window.addEventListener('keydown', (event) => {
    if (event.key === 'Escape') {
      closeFilter();
      closeMenu();
      closeProfileSheet();
    }
  });

  window.addEventListener('resize', () => {
    if (window.innerWidth > 1024) {
      closeFilter();
    }
    if (window.innerWidth > 768) {
      closeMenu();
    }
    if (window.innerWidth > 768) {
      closeProfileSheet();
    }
  });

  // Search Modal
  const searchTrigger = document.querySelector('[data-search-trigger]');
  const searchModal = document.querySelector('[data-search-modal]');
  const searchBackdrop = document.querySelector('[data-search-backdrop]');
  const searchClose = document.querySelector('[data-search-close]');
  const searchInput = document.querySelector('[data-search-input]');
  const searchResults = document.querySelector('[data-search-results]');

  const openSearch = () => {
    if (!searchModal) return;
    searchModal.classList.add('is-visible');
    searchBackdrop?.classList.add('is-visible');
    body.classList.add('no-scroll');
    setTimeout(() => searchInput?.focus(), 300);
    // Fetch random suggestions initially
    fetchSuggestions('');
  };

  const closeSearch = () => {
    searchModal?.classList.remove('is-visible');
    searchBackdrop?.classList.remove('is-visible');
    body.classList.remove('no-scroll');
  };

  searchTrigger?.addEventListener('click', (e) => {
    e.preventDefault(); // prevent anchor default if it were an anchor
    openSearch();
  });
  searchClose?.addEventListener('click', closeSearch);
  searchBackdrop?.addEventListener('click', closeSearch);

  const debounce = (func, wait) => {
    let timeout;
    return (...args) => {
      clearTimeout(timeout);
      timeout = setTimeout(() => func.apply(this, args), wait);
    };
  };

  const fetchSuggestions = async (query) => {
    // If query has length 1, probably don't fetch yet, 
    // BUT if it is empty string (''), we WANT to fetch random,
    // so we only return if length === 1.
    if (query && query.length === 1) {
      return;
    }

    try {
      const res = await fetch(`/catalog/search/suggestions/?q=${encodeURIComponent(query)}`);
      if (!res.ok) throw new Error('Network response was not ok');
      const data = await res.json();
      renderResults(data.results);
    } catch (err) {
      console.error(err);
    }
  };

  const renderResults = (results) => {
    if (!results.length) {
      searchResults.innerHTML = '<div style="padding:10px; color:#999;">Ничего не найдено</div>';
      return;
    }
    const html = results.map(item => `
      <a href="/catalog/detail/${item.slug}/" class="search-result-item">
        <img src="${item.image}" alt="${item.title}" class="search-item-thumb ${item.is_placeholder ? 'product-brand-placeholder' : ''}" ${item.is_placeholder ? 'style="padding: 10px; opacity: 0.8;"' : ''}>
        <div class="search-item-info">
          <div class="search-item-title">${item.title}</div>
          <div class="search-item-price">${item.price} ₸</div>
        </div>
      </a>
    `).join('');
    searchResults.innerHTML = html;
  };

  searchInput?.addEventListener('input', debounce((e) => {
    fetchSuggestions(e.target.value.trim());
  }, 300));

  // Product Sliders
  const setupSliders = () => {
    const sliders = document.querySelectorAll('.product-slider-wrapper');
    sliders.forEach(wrapper => {
      const track = wrapper.querySelector('.product-slider-track');
      const prevBtn = wrapper.querySelector('.slider-prev');
      const nextBtn = wrapper.querySelector('.slider-next');

      if (!track || !prevBtn || !nextBtn) return;

      prevBtn.addEventListener('click', () => {
        const itemWidth = track.firstElementChild?.clientWidth || 280;
        track.scrollBy({ left: -itemWidth, behavior: 'smooth' });
      });

      nextBtn.addEventListener('click', () => {
        const itemWidth = track.firstElementChild?.clientWidth || 280;
        track.scrollBy({ left: itemWidth, behavior: 'smooth' });
      });
    });
  };

  setupSliders();

  // Review Modal
  const reviewModal = document.querySelector('[data-review-modal]');
  const reviewModalTrigger = document.querySelector('[data-review-modal-trigger]');
  const reviewModalClose = document.querySelector('[data-review-modal-close]');
  const reviewModalBackdrop = document.querySelector('[data-review-modal-backdrop]');

  const openReviewModal = () => {
    if (!reviewModal) return;
    reviewModal.classList.add('is-visible');
    document.body.classList.add('no-scroll');
  };

  const closeReviewModal = () => {
    if (!reviewModal) return;
    reviewModal.classList.remove('is-visible');
    document.body.classList.remove('no-scroll');
  };

  if (reviewModalTrigger) {
    reviewModalTrigger.addEventListener('click', (e) => {
      e.preventDefault();
      openReviewModal();
    });
  }

  if (reviewModalClose) {
    reviewModalClose.addEventListener('click', closeReviewModal);
  }

  if (reviewModalBackdrop) {
    reviewModalBackdrop.addEventListener('click', closeReviewModal);
  }

  // Close modal on Escape key
  document.addEventListener('keydown', (e) => {
    if (e.key === 'Escape' && reviewModal?.classList.contains('is-visible')) {
      closeReviewModal();
    }
  });

  // Handle review form submission
  const reviewForm = document.getElementById('review-form');
  if (reviewForm) {
    reviewForm.addEventListener('submit', async (e) => {
      e.preventDefault();

      const formData = new FormData(reviewForm);

      try {
        const response = await fetch(window.location.href, {
          method: 'POST',
          body: formData,
          headers: {
            'X-Requested-With': 'XMLHttpRequest'
          }
        });

        const data = await response.json();

        if (data.success) {
          alert(data.message);
          reviewForm.reset();
          closeReviewModal();
        }
      } catch (error) {
        alert('Произошла ошибка при отправке отзыва. Попробуйте еще раз.');
      }
    });
  }
  // Newsletter Subscription
  window.subscribeNewsletter = async () => {
    const form = document.getElementById('newsletter-form');
    const input = document.getElementById('newsletter-email');
    const messageDiv = document.getElementById('newsletter-message');
    const csrfToken = document.querySelector('[name=csrfmiddlewaretoken]')?.value;

    if (!input || !input.value) return;

    messageDiv.textContent = 'Отправка...';
    messageDiv.style.color = '#666';

    try {
      const response = await fetch('/main/api/subscribe/', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'X-CSRFToken': csrfToken
        },
        body: JSON.stringify({ email: input.value })
      });

      const data = await response.json();

      if (response.ok && data.success) {
        messageDiv.textContent = data.message;
        messageDiv.style.color = 'green';
        input.value = '';
      } else {
        messageDiv.textContent = data.message || 'Ошибка при подписке';
        messageDiv.style.color = 'red';
      }
    } catch (error) {
      console.error(error);
      messageDiv.textContent = 'Произошла ошибка. Попробуйте позже.';
      messageDiv.style.color = 'red';
    }
  };

  // Header Scroll Effect
  const header = document.querySelector('.site-header');
  if (header) {
    window.addEventListener('scroll', () => {
      if (window.scrollY > 10) {
        header.classList.add('is-scrolled');
      } else {
        header.classList.remove('is-scrolled');
      }
    }, { passive: true });
  }
});

// Share Cart Logic
const shareCartBtn = document.getElementById('share-cart-btn');
if (shareCartBtn) {
  shareCartBtn.addEventListener('click', async (e) => {
    e.preventDefault();

    const items = Array.from(document.querySelectorAll('.cart-item')).map(item => {
      const title = item.querySelector('.cart-item__title')?.textContent.trim();
      const price = item.querySelector('.cart-item__price')?.textContent.trim();
      return `- ${title} (${price})`;
    });

    const text = 'Я выбрал эти украшения в MARAIS:\n\n' + items.join('\n') + '\n\nПосмотрите на сайте: ' + window.location.origin;

    if (navigator.share) {
      try {
        await navigator.share({
          title: 'Моя корзина MARAIS',
          text: text,
          url: window.location.origin
        });
      } catch (err) {
        console.log('Error sharing:', err);
      }
    } else {
      // Fallback: Use textarea hack for better compatibility (e.g. non-HTTPS)
      const textArea = document.createElement('textarea');
      textArea.value = text;
      textArea.style.position = 'fixed'; // Avoid scrolling to bottom
      textArea.style.left = '-9999px';
      document.body.appendChild(textArea);
      textArea.focus();
      textArea.select();

      try {
        const successful = document.execCommand('copy');
        const msg = successful ? 'Список товаров скопирован!' : 'Не удалось скопировать';
        alert(msg);
      } catch (err) {
        console.error('Fallback copy failed', err);
        alert('Не удалось скопировать список');
      }

      document.body.removeChild(textArea);
    }
  });
}

// Contact Modal Logic (Header Phone Icon)
const contactTrigger = document.getElementById('contact-modal-trigger');
const contactModal = document.getElementById('contact-modal');

if (contactTrigger && contactModal) {
  contactTrigger.addEventListener('click', (e) => {
    e.stopPropagation(); // prevent document click from immediately closing
    contactModal.classList.toggle('is-visible');
  });

  // Close when clicking outside
  document.addEventListener('click', (e) => {
    if (contactModal.classList.contains('is-visible') &&
      !contactModal.contains(e.target) &&
      e.target !== contactTrigger) {
      contactModal.classList.remove('is-visible');
    }
  });

  // Close on Escape key
  document.addEventListener('keydown', (e) => {
    if (e.key === 'Escape' && contactModal.classList.contains('is-visible')) {
      contactModal.classList.remove('is-visible');
    }
  });
}
