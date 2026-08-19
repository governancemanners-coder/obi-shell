/*
 * OBI Obliteratus — public-PWA bridge config.
 * The app is a PWA served from GitHub Pages (or any static host). The *brain*
 * (the Python bridge) runs on YOUR device (phone/desktop) — OBI is a personal,
 * local-first tool. Set BRIDGE_URL to wherever your bridge is reachable.
 *
 * Defaults:
 *   - on the same device (phone):  http://localhost:8420
 *   - from another device on your LAN:  http://<phone-LAN-ip>:8420
 *   - tunneled:  paste your tunnel URL here
 */
window.OBI_CONFIG = {
  BRIDGE_URL: "http://localhost:8420",
  // set true to require X-OBI-Token on the bridge (must match OBI_TOKEN there)
  REQUIRE_TOKEN: false,
  TOKEN: ""
};
