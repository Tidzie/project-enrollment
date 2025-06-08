// Initialize Google Map
function initMap() {
    const preschoolLocation = { lat: 40.7128, lng: -74.0060 }; // Replace with actual coordinates
    const map = new google.maps.Map(document.getElementById('map'), {
        zoom: 15,
        center: preschoolLocation,
    });
    
    const marker = new google.maps.Marker({
        position: preschoolLocation,
        map: map,
        title: 'BrightBeginnings Preschool'
    });
}

// Contact Form Handling
document.addEventListener('DOMContentLoaded', function() {
    const contactForm = document.getElementById('contactForm');
    if (contactForm) {
        contactForm.addEventListener('submit', function(e) {
            e.preventDefault();
            
            // Get form data
            const formData = new FormData(contactForm);
            const data = Object.fromEntries(formData);
            
            // Here you would typically send the data to your backend
            // For now, we'll just show a success message
            alert('Thank you for your message! We will get back to you soon.');
            contactForm.reset();
        });
    }
});

// Smooth scrolling for navigation links
document.querySelectorAll('a[href^="#"]').forEach(anchor => {
    anchor.addEventListener('click', function (e) {
        e.preventDefault();
        const target = document.querySelector(this.getAttribute('href'));
        if (target) {
            target.scrollIntoView({
                behavior: 'smooth',
                block: 'start'
            });
        }
    });
});

// Animate elements when they come into view
const animateOnScroll = () => {
    const elements = document.querySelectorAll('.feature-card, .testimonial-card');
    
    elements.forEach(element => {
        const elementTop = element.getBoundingClientRect().top;
        const elementBottom = element.getBoundingClientRect().bottom;
        
        if (elementTop < window.innerHeight && elementBottom > 0) {
            element.style.opacity = '1';
            element.style.transform = 'translateY(0)';
        }
    });
};

// Add scroll event listener
window.addEventListener('scroll', animateOnScroll);

// Initial check for elements in view
animateOnScroll();

// Add loading animation to CTA button
const ctaButton = document.querySelector('.cta-button');
if (ctaButton) {
    ctaButton.addEventListener('click', function(e) {
        if (!this.classList.contains('loading')) {
            e.preventDefault();
            this.classList.add('loading');
            this.innerHTML = '<i class="fas fa-spinner fa-spin"></i> Redirecting...';
            
            // Simulate loading delay
            setTimeout(() => {
                window.location.href = this.getAttribute('href');
            }, 1000);
        }
    });
} 