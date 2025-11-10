/**
 * SUMMONERS REUNION - UI ANIMATIONS & VISUAL EFFECTS
 * Handles visual enhancements and interactive animations
 */

/**
 * Particle system for background effects
 */
class ParticleSystem {
    constructor() {
        this.particles = [];
        this.canvas = null;
        this.ctx = null;
        this.animationId = null;
        this.isEnabled = true;
    }

    init() {
        // Create canvas for particles
        this.canvas = document.createElement('canvas');
        this.canvas.style.position = 'fixed';
        this.canvas.style.top = '0';
        this.canvas.style.left = '0';
        this.canvas.style.width = '100%';
        this.canvas.style.height = '100%';
        this.canvas.style.pointerEvents = 'none';
        this.canvas.style.zIndex = '0';
        this.canvas.style.opacity = '0.3';

        document.body.insertBefore(this.canvas, document.body.firstChild);

        this.ctx = this.canvas.getContext('2d');
        this.resize();

        window.addEventListener('resize', () => this.resize());

        // Create initial particles
        this.createParticles(30);

        // Start animation
        this.animate();
    }

    resize() {
        this.canvas.width = window.innerWidth;
        this.canvas.height = window.innerHeight;
    }

    createParticles(count) {
        for (let i = 0; i < count; i++) {
            this.particles.push({
                x: Math.random() * this.canvas.width,
                y: Math.random() * this.canvas.height,
                size: Math.random() * 2 + 1,
                speedX: (Math.random() - 0.5) * 0.5,
                speedY: (Math.random() - 0.5) * 0.5,
                color: this.getRandomColor()
            });
        }
    }

    getRandomColor() {
        const colors = [
            'rgba(0, 255, 245, 0.6)',    // Cyan
            'rgba(178, 75, 243, 0.6)',   // Purple
            'rgba(77, 124, 254, 0.6)',   // Blue
            'rgba(255, 46, 151, 0.6)'    // Pink
        ];
        return colors[Math.floor(Math.random() * colors.length)];
    }

    animate() {
        if (!this.isEnabled) return;

        this.ctx.clearRect(0, 0, this.canvas.width, this.canvas.height);

        this.particles.forEach(particle => {
            // Update position
            particle.x += particle.speedX;
            particle.y += particle.speedY;

            // Wrap around screen
            if (particle.x < 0) particle.x = this.canvas.width;
            if (particle.x > this.canvas.width) particle.x = 0;
            if (particle.y < 0) particle.y = this.canvas.height;
            if (particle.y > this.canvas.height) particle.y = 0;

            // Draw particle
            this.ctx.beginPath();
            this.ctx.arc(particle.x, particle.y, particle.size, 0, Math.PI * 2);
            this.ctx.fillStyle = particle.color;
            this.ctx.fill();

            // Draw glow
            const gradient = this.ctx.createRadialGradient(
                particle.x, particle.y, 0,
                particle.x, particle.y, particle.size * 3
            );
            gradient.addColorStop(0, particle.color);
            gradient.addColorStop(1, 'transparent');
            this.ctx.fillStyle = gradient;
            this.ctx.fill();
        });

        this.animationId = requestAnimationFrame(() => this.animate());
    }

    destroy() {
        this.isEnabled = false;
        if (this.animationId) {
            cancelAnimationFrame(this.animationId);
        }
        if (this.canvas && this.canvas.parentNode) {
            this.canvas.parentNode.removeChild(this.canvas);
        }
    }
}

/**
 * Cursor trail effect
 */
class CursorTrail {
    constructor() {
        this.trail = [];
        this.maxTrailLength = 10;
        this.canvas = null;
        this.ctx = null;
        this.animationId = null;
        this.mouseX = 0;
        this.mouseY = 0;
    }

    init() {
        // Create canvas for cursor trail
        this.canvas = document.createElement('canvas');
        this.canvas.style.position = 'fixed';
        this.canvas.style.top = '0';
        this.canvas.style.left = '0';
        this.canvas.style.width = '100%';
        this.canvas.style.height = '100%';
        this.canvas.style.pointerEvents = 'none';
        this.canvas.style.zIndex = '9999';

        document.body.appendChild(this.canvas);

        this.ctx = this.canvas.getContext('2d');
        this.resize();

        window.addEventListener('resize', () => this.resize());
        window.addEventListener('mousemove', (e) => this.handleMouseMove(e));

        this.animate();
    }

    resize() {
        this.canvas.width = window.innerWidth;
        this.canvas.height = window.innerHeight;
    }

    handleMouseMove(e) {
        this.mouseX = e.clientX;
        this.mouseY = e.clientY;

        this.trail.push({
            x: this.mouseX,
            y: this.mouseY,
            life: 1
        });

        if (this.trail.length > this.maxTrailLength) {
            this.trail.shift();
        }
    }

    animate() {
        this.ctx.clearRect(0, 0, this.canvas.width, this.canvas.height);

        // Update and draw trail
        this.trail.forEach((point, index) => {
            point.life -= 0.05;

            if (point.life > 0) {
                const size = 8 * point.life;
                const gradient = this.ctx.createRadialGradient(
                    point.x, point.y, 0,
                    point.x, point.y, size
                );
                gradient.addColorStop(0, `rgba(0, 255, 245, ${point.life * 0.5})`);
                gradient.addColorStop(1, 'transparent');

                this.ctx.fillStyle = gradient;
                this.ctx.beginPath();
                this.ctx.arc(point.x, point.y, size, 0, Math.PI * 2);
                this.ctx.fill();
            }
        });

        // Remove dead points
        this.trail = this.trail.filter(point => point.life > 0);

        this.animationId = requestAnimationFrame(() => this.animate());
    }

    destroy() {
        if (this.animationId) {
            cancelAnimationFrame(this.animationId);
        }
        if (this.canvas && this.canvas.parentNode) {
            this.canvas.parentNode.removeChild(this.canvas);
        }
    }
}

/**
 * Add glitch effect to text
 */
function addGlitchEffect(element) {
    const originalText = element.textContent;
    const glitchChars = '!<>-_\\/[]{}—=+*^?#________';

    let iterations = 0;
    const maxIterations = originalText.length;

    const interval = setInterval(() => {
        element.textContent = originalText
            .split('')
            .map((char, index) => {
                if (index < iterations) {
                    return originalText[index];
                }
                return glitchChars[Math.floor(Math.random() * glitchChars.length)];
            })
            .join('');

        iterations += 1;

        if (iterations > maxIterations) {
            clearInterval(interval);
            element.textContent = originalText;
        }
    }, 30);
}

/**
 * Add ripple effect on click
 */
function addRippleEffect(element) {
    element.addEventListener('click', function(e) {
        const ripple = document.createElement('span');
        const rect = this.getBoundingClientRect();
        const size = Math.max(rect.width, rect.height);
        const x = e.clientX - rect.left - size / 2;
        const y = e.clientY - rect.top - size / 2;

        ripple.style.width = ripple.style.height = size + 'px';
        ripple.style.left = x + 'px';
        ripple.style.top = y + 'px';
        ripple.style.position = 'absolute';
        ripple.style.borderRadius = '50%';
        ripple.style.background = 'rgba(0, 255, 245, 0.5)';
        ripple.style.transform = 'scale(0)';
        ripple.style.animation = 'ripple 0.6s ease-out';
        ripple.style.pointerEvents = 'none';

        this.style.position = 'relative';
        this.style.overflow = 'hidden';
        this.appendChild(ripple);

        setTimeout(() => ripple.remove(), 600);
    });
}

// Add ripple animation CSS
const rippleStyle = document.createElement('style');
rippleStyle.textContent = `
    @keyframes ripple {
        to {
            transform: scale(4);
            opacity: 0;
        }
    }
`;
document.head.appendChild(rippleStyle);

/**
 * Add hover glow to buttons
 */
function enhanceButtons() {
    const buttons = document.querySelectorAll('button, .cta-button');

    buttons.forEach(button => {
        addRippleEffect(button);

        // Add glow on hover
        button.addEventListener('mouseenter', function() {
            this.style.transition = 'all 0.3s ease';
        });
    });
}

/**
 * Initialize smooth scrolling
 */
function initSmoothScroll() {
    const messagesWrapper = document.getElementById('messagesWrapper');
    if (messagesWrapper) {
        messagesWrapper.style.scrollBehavior = 'smooth';
    }
}

/**
 * Add loading shimmer effect
 */
function createShimmerEffect(element) {
    element.style.background = 'linear-gradient(90deg, rgba(26,26,46,0.8) 25%, rgba(0,255,245,0.1) 50%, rgba(26,26,46,0.8) 75%)';
    element.style.backgroundSize = '200% 100%';
    element.style.animation = 'shimmer 2s infinite';
}

// Add shimmer animation CSS
const shimmerStyle = document.createElement('style');
shimmerStyle.textContent = `
    @keyframes shimmer {
        0% { background-position: 200% 0; }
        100% { background-position: -200% 0; }
    }
`;
document.head.appendChild(shimmerStyle);

/**
 * Initialize all UI enhancements
 */
function initializeUI() {
    console.log('Initializing UI effects...');

    // Initialize particle system (optional - can be disabled for performance)
    const particleSystem = new ParticleSystem();
    particleSystem.init();

    // Initialize cursor trail (optional)
    // const cursorTrail = new CursorTrail();
    // cursorTrail.init();

    // Enhance buttons
    enhanceButtons();

    // Smooth scrolling
    initSmoothScroll();

    // Add glitch effect to logo title on load
    const logoTitle = document.querySelector('.logo-title');
    if (logoTitle) {
        setTimeout(() => addGlitchEffect(logoTitle), 500);
    }

    // Add entrance animation to welcome message
    const welcomeMessage = document.querySelector('.welcome-message');
    if (welcomeMessage) {
        welcomeMessage.style.opacity = '0';
        setTimeout(() => {
            welcomeMessage.style.transition = 'opacity 0.5s ease-in';
            welcomeMessage.style.opacity = '1';
        }, 300);
    }

    console.log('UI effects initialized');
}

// Initialize UI when DOM is ready
if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', initializeUI);
} else {
    initializeUI();
}

// Export for use in other scripts
window.UIEffects = {
    addGlitchEffect,
    addRippleEffect,
    createShimmerEffect
};
