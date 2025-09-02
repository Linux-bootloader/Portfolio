document.addEventListener("DOMContentLoaded", () => {
  const mobileMessage = document.querySelector('.mobile-message');
  const ipadPortraitMessage = document.querySelector('.ipad-portrait-message');

  const ua = navigator.userAgent || navigator.vendor || window.opera;

// Detect *only* phones
const isPhone = /iPhone|Android.+Mobile|Windows Phone/i.test(ua);

// Detect *only* iPad
const isIPad = (
  (/iPad/.test(ua)) ||                                // Real iPad UA
  ((/Macintosh/.test(ua)) && navigator.maxTouchPoints > 1 && !/iPhone/.test(ua)) // iPadOS desktop emulation but rule out iPhones
);

  function checkDevice() {
    console.log("isPhone:", isPhone, "isIPad:", isIPad, "orientation portrait:", window.matchMedia("(orientation: portrait)").matches);

    if (isPhone) {
      // 📱 Show block message
      mobileMessage.style.display = "flex";
      ipadPortraitMessage.style.display = "none";

      document.querySelectorAll("body > *:not(.mobile-message)").forEach(
        (el) => (el.style.display = "none")
      );
    } else if (isIPad && window.matchMedia("(orientation: portrait)").matches) {
      // 📲 iPad portrait → show rotate warning
      ipadPortraitMessage.style.display = "flex";
      mobileMessage.style.display = "none";

      document.querySelectorAll("body > *:not(.ipad-portrait-message)").forEach(
        (el) => (el.style.display = "none")
      );
    } else {
      // 💻 Desktop or iPad landscape → show full site
      mobileMessage.style.display = "none";
      ipadPortraitMessage.style.display = "none";

      document.querySelectorAll("body > *").forEach((el) => {
        if (!el.classList.contains("mobile-message") && !el.classList.contains("ipad-portrait-message")) {
          el.style.display = "";
        }
      });
    }
  }

  // Run on load
  checkDevice();

  // Re-run on orientation & resize changes
  window.addEventListener("resize", checkDevice);
  window.addEventListener("orientationchange", checkDevice);
});