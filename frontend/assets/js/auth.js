/**
 * OCEAN SENTINEL - AUTHENTICATION
 * Validation conforme ANSSI 2026 et RGAA 5.0
 */

document.addEventListener('DOMContentLoaded', function() {
  
  const form = document.getElementById('register-form');
  if (!form) return;
  
  const emailInput = document.getElementById('email');
  const passwordInput = document.getElementById('password');
  const consentCheckbox = document.getElementById('consent');
  const submitBtn = document.getElementById('submit-btn');
  
  // ============================================
  // POLITIQUE DE MOT DE PASSE ANSSI 2026
  // ============================================
  
  const PASSWORD_POLICY = {
    minLength: 12,
    requireUppercase: true,
    requireLowercase: true,
    requireNumbers: true,
    requireSpecialChars: true,
    specialChars: '!@#$%^&*()_+-=[]{}|;:,.<>?',
    
    forbiddenPatterns: [
      /^(.)\1+$/,
      /^(012|123|234|345|456|567|678|789|890)+/,
      /^(abc|bcd|cde|def|efg|fgh|ghi|hij|ijk|jkl|klm|lmn|mno|nop|opq|pqr|qrs|rst|stu|tuv|uvw|vwx|wxy|xyz)+/i
    ],
    
    blacklist: [
      'password', 'motdepasse', '123456', 'azerty', 'qwerty',
      'admin', 'root', 'user', 'ocean', 'sentinel', 'oceansentinel'
    ]
  };
  
  // ============================================
  // VALIDATION EMAIL
  // ============================================
  
  emailInput.addEventListener('blur', validateEmail);
  emailInput.addEventListener('input', () => clearError('email'));
  
  function validateEmail() {
    const email = emailInput.value.trim();
    const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
    
    if (!email) {
      showError('email', 'L\'adresse email est obligatoire');
      return false;
    }
    
    if (!emailRegex.test(email)) {
      showError('email', 'Veuillez saisir une adresse email valide (ex: nom@domaine.fr)');
      return false;
    }
    
    if (email.length > 255) {
      showError('email', 'L\'adresse email est trop longue (maximum 255 caractères)');
      return false;
    }
    
    clearError('email');
    return true;
  }
  
  // ============================================
  // VALIDATION MOT DE PASSE
  // ============================================
  
  const passwordRequirements = {
    length: { 
      regex: new RegExp(`.{${PASSWORD_POLICY.minLength},}`), 
      element: document.getElementById('req-length') 
    },
    uppercase: { 
      regex: /[A-Z]/, 
      element: document.getElementById('req-uppercase') 
    },
    lowercase: { 
      regex: /[a-z]/, 
      element: document.getElementById('req-lowercase') 
    },
    number: { 
      regex: /[0-9]/, 
      element: document.getElementById('req-number') 
    },
    special: { 
      regex: new RegExp(`[${PASSWORD_POLICY.specialChars.replace(/[-[\]{}()*+?.,\\^$|#\s]/g, '\\$&')}]`), 
      element: document.getElementById('req-special') 
    }
  };
  
  passwordInput.addEventListener('input', function() {
    validatePassword();
    updatePasswordStrength();
  });
  
  function validatePassword() {
    const password = passwordInput.value;
    let validCount = 0;
    let errors = [];
    
    for (const [key, requirement] of Object.entries(passwordRequirements)) {
      const isValid = requirement.regex.test(password);
      
      if (isValid) {
        requirement.element.classList.add('valid');
        validCount++;
      } else {
        requirement.element.classList.remove('valid');
      }
    }
    
    if (password && validCount < 5) {
      showError('password', 'Le mot de passe ne respecte pas tous les critères de sécurité ANSSI 2026');
      return false;
    }
    
    for (const pattern of PASSWORD_POLICY.forbiddenPatterns) {
      if (pattern.test(password)) {
        showError('password', 'Le mot de passe contient une séquence interdite (caractères répétés ou suite)');
        return false;
      }
    }
    
    const lowerPassword = password.toLowerCase();
    for (const forbidden of PASSWORD_POLICY.blacklist) {
      if (lowerPassword.includes(forbidden)) {
        showError('password', `Le mot de passe ne doit pas contenir "${forbidden}"`);
        return false;
      }
    }
    
    clearError('password');
    return validCount === 5;
  }
  
  function updatePasswordStrength() {
    const password = passwordInput.value;
    const strengthFill = document.querySelector('.strength-fill');
    const strengthText = document.querySelector('.strength-text strong');
    
    if (!strengthFill || !strengthText) return;
    
    let strength = 0;
    let strengthLabel = 'Aucune';
    
    if (password.length >= PASSWORD_POLICY.minLength) strength++;
    if (/[A-Z]/.test(password) && /[a-z]/.test(password)) strength++;
    if (/[0-9]/.test(password)) strength++;
    if (new RegExp(`[${PASSWORD_POLICY.specialChars.replace(/[-[\]{}()*+?.,\\^$|#\s]/g, '\\$&')}]`).test(password)) strength++;
    
    if (password.length >= 16) strength = Math.min(4, strength + 1);
    
    switch(strength) {
      case 0:
        strengthLabel = 'Aucune';
        break;
      case 1:
        strengthLabel = 'Très faible';
        break;
      case 2:
        strengthLabel = 'Faible';
        break;
      case 3:
        strengthLabel = 'Moyenne';
        break;
      case 4:
        strengthLabel = 'Bonne';
        break;
      case 5:
        strengthLabel = 'Excellente';
        break;
    }
    
    strengthFill.setAttribute('data-strength', strength);
    strengthText.textContent = strengthLabel;
  }
  
  // ============================================
  // TOGGLE VISIBILITÉ MOT DE PASSE
  // ============================================
  
  window.togglePassword = function() {
    const toggleBtn = document.querySelector('.toggle-password');
    if (!toggleBtn) return;
    
    const isPressed = toggleBtn.getAttribute('aria-pressed') === 'true';
    
    if (isPressed) {
      passwordInput.type = 'password';
      toggleBtn.setAttribute('aria-pressed', 'false');
      toggleBtn.setAttribute('aria-label', 'Afficher le mot de passe');
    } else {
      passwordInput.type = 'text';
      toggleBtn.setAttribute('aria-pressed', 'true');
      toggleBtn.setAttribute('aria-label', 'Masquer le mot de passe');
    }
  };
  
  // ============================================
  // VALIDATION CONSENTEMENT
  // ============================================
  
  consentCheckbox.addEventListener('change', function() {
    if (!this.checked) {
      showError('consent', 'Vous devez accepter les CGU et la Politique de confidentialité pour créer un compte');
    } else {
      clearError('consent');
    }
  });
  
  // ============================================
  // SOUMISSION FORMULAIRE
  // ============================================
  
  form.addEventListener('submit', async function(e) {
    e.preventDefault();
    
    const isEmailValid = validateEmail();
    const isPasswordValid = validatePassword();
    const isConsentValid = consentCheckbox.checked;
    
    if (!isConsentValid) {
      showError('consent', 'Vous devez accepter les CGU et la Politique de confidentialité');
    }
    
    if (!isEmailValid || !isPasswordValid || !isConsentValid) {
      announceToScreenReader('Le formulaire contient des erreurs. Veuillez les corriger avant de continuer.');
      
      const firstError = form.querySelector('.error-message:not(:empty)');
      if (firstError) {
        const errorInput = firstError.previousElementSibling || firstError.closest('.form-group').querySelector('input');
        if (errorInput) errorInput.focus();
      }
      
      return;
    }
    
    submitBtn.disabled = true;
    document.querySelector('.btn-text').style.display = 'none';
    document.querySelector('.btn-loader').style.display = 'inline-block';
    
    try {
      const response = await fetch('/api/auth/register', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          email: emailInput.value.trim(),
          password: passwordInput.value,
          consent: true,
          consentTimestamp: new Date().toISOString(),
          consentIpAddress: await getClientIP()
        })
      });
      
      const data = await response.json();
      
      if (response.ok) {
        announceToScreenReader('Inscription réussie. Redirection en cours...');
        
        localStorage.setItem('access_token', data.accessToken);
        localStorage.setItem('refresh_token', data.refreshToken);
        
        window.location.href = '/portal';
      } else {
        throw new Error(data.message || 'Une erreur est survenue lors de l\'inscription');
      }
      
    } catch (error) {
      announceToScreenReader('Erreur : ' + error.message);
      
      showError('email', error.message);
      
      submitBtn.disabled = false;
      document.querySelector('.btn-text').style.display = 'inline';
      document.querySelector('.btn-loader').style.display = 'none';
    }
  });
  
  // ============================================
  // FONCTIONS UTILITAIRES
  // ============================================
  
  function showError(fieldName, message) {
    const errorElement = document.getElementById(`${fieldName}-error`);
    if (errorElement) {
      errorElement.textContent = message;
      errorElement.setAttribute('role', 'alert');
    }
    
    const inputElement = document.getElementById(fieldName);
    if (inputElement) {
      inputElement.setAttribute('aria-invalid', 'true');
      inputElement.classList.add('error');
    }
  }
  
  function clearError(fieldName) {
    const errorElement = document.getElementById(`${fieldName}-error`);
    if (errorElement) {
      errorElement.textContent = '';
      errorElement.removeAttribute('role');
    }
    
    const inputElement = document.getElementById(fieldName);
    if (inputElement) {
      inputElement.setAttribute('aria-invalid', 'false');
      inputElement.classList.remove('error');
    }
  }
  
  function announceToScreenReader(message) {
    const announcement = document.createElement('div');
    announcement.setAttribute('role', 'status');
    announcement.setAttribute('aria-live', 'polite');
    announcement.className = 'sr-only';
    announcement.textContent = message;
    document.body.appendChild(announcement);
    
    setTimeout(() => {
      document.body.removeChild(announcement);
    }, 1000);
  }
  
  async function getClientIP() {
    try {
      const response = await fetch('https://api.ipify.org?format=json');
      const data = await response.json();
      return data.ip;
    } catch (error) {
      return null;
    }
  }
  
  // ============================================
  // VÉRIFICATION HAVE I BEEN PWNED (Optionnel)
  // ============================================
  
  async function checkPwnedPassword(password) {
    try {
      const encoder = new TextEncoder();
      const data = encoder.encode(password);
      const hashBuffer = await crypto.subtle.digest('SHA-1', data);
      const hashArray = Array.from(new Uint8Array(hashBuffer));
      const hashHex = hashArray.map(b => b.toString(16).padStart(2, '0')).join('').toUpperCase();
      
      const prefix = hashHex.substring(0, 5);
      const suffix = hashHex.substring(5);
      
      const response = await fetch(`https://api.pwnedpasswords.com/range/${prefix}`);
      const text = await response.text();
      
      const hashes = text.split('\n');
      for (const hash of hashes) {
        const [hashSuffix, count] = hash.split(':');
        if (hashSuffix === suffix) {
          return parseInt(count, 10);
        }
      }
      
      return 0;
    } catch (error) {
      console.error('Erreur vérification HIBP:', error);
      return 0;
    }
  }
  
  passwordInput.addEventListener('blur', async function() {
    const password = passwordInput.value;
    if (password.length < PASSWORD_POLICY.minLength) return;
    
    const pwnedCount = await checkPwnedPassword(password);
    if (pwnedCount > 0) {
      showError('password', 
        `⚠️ Ce mot de passe a été compromis dans ${pwnedCount.toLocaleString()} fuites de données. ` +
        'Veuillez en choisir un autre pour votre sécurité.'
      );
    }
  });
  
});
