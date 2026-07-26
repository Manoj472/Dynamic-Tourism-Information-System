document.addEventListener('DOMContentLoaded', () => {
  const carousel = document.getElementById('rk-carousel');
  const slides = document.querySelectorAll('.rk-slide');
  const prevBtn = document.getElementById('rk-prevBtn');
  const nextBtn = document.getElementById('rk-nextBtn');
  let currentIndex = 0;
  const totalSlides = slides.length;
  let autoSlideInterval;

  function goToSlide(index) {
    currentIndex = (index + totalSlides) % totalSlides;
    carousel.style.transform = `translateX(-${currentIndex * 100}%)`;
  }

  function nextSlide() {
    goToSlide(currentIndex + 1);
  }

  function prevSlide() {
    goToSlide(currentIndex - 1);
  }

  function startAutoSlide() {
    autoSlideInterval = setInterval(nextSlide, 5000);
  }

  function stopAutoSlide() {
    clearInterval(autoSlideInterval);
  }

  prevBtn.addEventListener('click', () => {
    stopAutoSlide();
    prevSlide();
    startAutoSlide();
  });

  nextBtn.addEventListener('click', () => {
    stopAutoSlide();
    nextSlide();
    startAutoSlide();
  });

  carousel.addEventListener('mouseenter', stopAutoSlide);
  carousel.addEventListener('mouseleave', startAutoSlide);

  startAutoSlide();
});
