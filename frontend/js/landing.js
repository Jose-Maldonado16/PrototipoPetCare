// ==================== MENÚ MÓVIL ====================
const mobileMenuBtn = document.getElementById('mobileMenuBtn');
const navLinks = document.querySelector('.nav-links');

if (mobileMenuBtn) {
    mobileMenuBtn.addEventListener('click', () => {
        navLinks.classList.toggle('active');
    });
}

// ==================== SCROLL SUAVE ====================
document.querySelectorAll('a[href^="#"]').forEach(anchor => {
    anchor.addEventListener('click', function(e) {
        e.preventDefault();
        const target = document.querySelector(this.getAttribute('href'));
        if (target) {
            target.scrollIntoView({ behavior: 'smooth' });
            navLinks.classList.remove('active');
        }
    });
});

// ==================== REDIRIGIR AL LOGIN ====================
function irALogin() {
    window.location.href = 'login.html';
}

// Botones que redirigen al login
const btnLoginNav = document.getElementById('btnLoginNav');
const btnComenzar = document.getElementById('btnComenzar');
const btnComenzarFooter = document.getElementById('btnComenzarFooter');

if (btnLoginNav) btnLoginNav.addEventListener('click', irALogin);
if (btnComenzar) btnComenzar.addEventListener('click', irALogin);
if (btnComenzarFooter) btnComenzarFooter.addEventListener('click', irALogin);

// Botón "Saber más" - scroll a servicios
const btnSaberMas = document.getElementById('btnSaberMas');
if (btnSaberMas) {
    btnSaberMas.addEventListener('click', () => {
        document.getElementById('servicios').scrollIntoView({ behavior: 'smooth' });
    });
}

// ==================== ANIMACIONES AL SCROLL ====================
const observerOptions = {
    threshold: 0.1,
    rootMargin: '0px 0px -50px 0px'
};

const observer = new IntersectionObserver((entries) => {
    entries.forEach(entry => {
        if (entry.isIntersecting) {
            entry.target.style.opacity = '1';
            entry.target.style.transform = 'translateY(0)';
        }
    });
}, observerOptions);

document.querySelectorAll('.service-card, .benefit-card, .testimonial-card, .step').forEach(el => {
    el.style.opacity = '0';
    el.style.transform = 'translateY(30px)';
    el.style.transition = 'all 0.6s ease';
    observer.observe(el);
});

// ==================== NAVBAR SCROLL ====================
const navbar = document.querySelector('.navbar');
let lastScroll = 0;

window.addEventListener('scroll', () => {
    const currentScroll = window.pageYOffset;
    if (currentScroll > lastScroll && currentScroll > 100) {
        navbar.style.transform = 'translateY(-100%)';
    } else {
        navbar.style.transform = 'translateY(0)';
    }
    lastScroll = currentScroll;
});