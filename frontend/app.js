document.addEventListener('DOMContentLoaded', () => {
  const connectBtn = document.getElementById('connectBtn');
  const disconnectBtn = document.getElementById('disconnectBtn');
  const statusText = document.getElementById('statusText');
  const pulseDot = document.querySelector('.pulse-dot');
  const videoPlaceholder = document.getElementById('videoPlaceholder');
  const videoStream = document.getElementById('videoStream');

  // URL pointing to the Compute Container running the Python MJPEG proxy
  // Local development fallback: http://localhost:8000/stream
  const backendUrl = window.PUBLIC_INSFORGE_URL 
      ? `${window.PUBLIC_INSFORGE_URL}/stream` 
      : 'http://localhost:8080/stream';
      // In production we would proxy it through InsForge or use the absolute compute URL

  // We set an environment variable via InsForge Deployments later:
  // e.g. VITE_BACKEND_URL or just dynamically fetch from window.location

  // Since we are hosting the frontend on Deployments and Compute on Fly, 
  // we will replace this URL with the deployed compute URL later.
  let activeStreamUrl = '';

  const updateUI = (state) => {
    if (state === 'connected') {
      statusText.textContent = 'Live';
      statusText.className = 'status-indicator connected';
      pulseDot.classList.add('active');
      connectBtn.disabled = true;
      disconnectBtn.disabled = false;
      videoPlaceholder.classList.add('hidden');
      videoStream.classList.remove('hidden');
    } else if (state === 'connecting') {
      statusText.textContent = 'Connecting...';
      statusText.className = 'status-indicator';
      connectBtn.disabled = true;
      disconnectBtn.disabled = true;
    } else {
      // disconnected
      statusText.textContent = 'Disconnected';
      statusText.className = 'status-indicator disconnected';
      pulseDot.classList.remove('active');
      connectBtn.disabled = false;
      disconnectBtn.disabled = true;
      videoPlaceholder.classList.remove('hidden');
      videoStream.classList.add('hidden');
      videoStream.src = '';
    }
  };

  connectBtn.addEventListener('click', () => {
    updateUI('connecting');
    // Compute container URL will be provided dynamically when deployed
    // Example: https://rtsp-proxy.fly.dev/stream
    
    // We append a timestamp to prevent browser caching of the MJPEG stream
    activeStreamUrl = `https://camera-rtsp-proxy-29ac726b.fly.dev/stream?t=${new Date().getTime()}`;
    
    // Test if image loads successfully
    videoStream.onload = () => updateUI('connected');
    videoStream.onerror = () => {
      alert("Failed to connect to the backend stream proxy. Make sure the proxy is deployed and running.");
      updateUI('disconnected');
    };
    
    videoStream.src = activeStreamUrl;
  });

  disconnectBtn.addEventListener('click', () => {
    updateUI('disconnected');
  });
});
