// Handles the popup UI for the playlist functionality

document.addEventListener('DOMContentLoaded', function() {
  // Initialize UI
  loadPlaylist();
  
  // Event listeners
  document.getElementById('add-current').addEventListener('click', addCurrentVideo);
  document.getElementById('clear-all').addEventListener('click', clearPlaylist);
  
  // Load playlist from storage
  function loadPlaylist() {
    chrome.storage.local.get({ 'video-playlist': [] }, function(result) {
      const playlist = result['video-playlist'];
      renderPlaylist(playlist);
    });
  }
  
  // Render playlist items in UI
  function renderPlaylist(playlist) {
    const container = document.getElementById('playlist-container');
    
    if (playlist.length === 0) {
      container.innerHTML = '<div class="empty-message">No videos in playlist</div>';
      return;
    }
    
    container.innerHTML = '';
    
    playlist.forEach((video, index) => {
      const item = document.createElement('div');
      item.className = 'video-item';
      
      const title = document.createElement('div');
      title.className = 'video-title';
      title.textContent = video.title || video.url;
      title.title = video.url; // For tooltip on hover
      
      const actions = document.createElement('div');
      actions.className = 'action-buttons';
      
      const playBtn = document.createElement('button');
      playBtn.textContent = 'Play';
      playBtn.addEventListener('click', () => playVideo(index));
      
      const pipBtn = document.createElement('button');
      pipBtn.textContent = 'PiP';
      pipBtn.addEventListener('click', () => pipVideo(index));
      
      const removeBtn = document.createElement('button');
      removeBtn.textContent = '×';
      removeBtn.addEventListener('click', () => removeVideo(index));
      
      actions.appendChild(playBtn);
      actions.appendChild(pipBtn);
      actions.appendChild(removeBtn);
      
      item.appendChild(title);
      item.appendChild(actions);
      container.appendChild(item);
    });
  }
  
  // Add current video to playlist
  function addCurrentVideo() {
    chrome.tabs.query({active: true, currentWindow: true}, function(tabs) {
      if (tabs.length === 0) return;
      
      const currentTab = tabs[0];
      
      // Send message to content script to get video info
      chrome.tabs.sendMessage(currentTab.id, {action: "getVideoInfo"}, function(response) {
        if (chrome.runtime.lastError) {
          // Content script not ready, need to inject it first
          chrome.scripting.executeScript({
            target: {tabId: currentTab.id},
            files: ['content.js']
          }, () => {
            // Retry after injection
            setTimeout(() => {
              chrome.tabs.sendMessage(currentTab.id, {action: "getVideoInfo"}, handleVideoInfo);
            }, 100);
          });
        } else {
          handleVideoInfo(response);
        }
      });
      
      function handleVideoInfo(response) {
        if (!response || !response.success) {
          alert('No video found on current page');
          return;
        }
        
        const videoInfo = {
          url: currentTab.url,
          title: currentTab.title,
          timestamp: response.currentTime || 0,
          added: new Date().toISOString()
        };
        
        // Add to storage
        chrome.storage.local.get({ 'video-playlist': [] }, function(result) {
          const playlist = result['video-playlist'];
          
          // Check if URL already exists
          const exists = playlist.some(v => v.url === videoInfo.url);
          
          if (!exists) {
            playlist.push(videoInfo);
            chrome.storage.local.set({ 'video-playlist': playlist }, function() {
              loadPlaylist();
            });
          } else {
            alert('This video is already in your playlist');
          }
        });
      }
    });
  }
  
  // Remove video from playlist
  function removeVideo(index) {
    chrome.storage.local.get({ 'video-playlist': [] }, function(result) {
      const playlist = result['video-playlist'];
      playlist.splice(index, 1);
      chrome.storage.local.set({ 'video-playlist': playlist }, function() {
        loadPlaylist();
      });
    });
  }
  
  // Clear entire playlist
  function clearPlaylist() {
    if (confirm('Are you sure you want to clear the entire playlist?')) {
      chrome.storage.local.set({ 'video-playlist': [] }, function() {
        loadPlaylist();
      });
    }
  }
  
  // Open and play a video
  function playVideo(index) {
    chrome.storage.local.get({ 'video-playlist': [] }, function(result) {
      const playlist = result['video-playlist'];
      const video = playlist[index];
      
      if (video) {
        const url = video.url + (video.timestamp ? `#t=${Math.floor(video.timestamp)}` : '');
        chrome.tabs.create({ url });
      }
    });
  }
  
  // Open video in PiP mode
  function pipVideo(index) {
    chrome.storage.local.get({ 'video-playlist': [] }, function(result) {
      const playlist = result['video-playlist'];
      const video = playlist[index];
      
      if (video) {
        chrome.tabs.create({ url: video.url }, function(tab) {
          // Wait for page to load before triggering PiP
          setTimeout(() => {
            chrome.tabs.sendMessage(tab.id, { action: 'triggerPip', timestamp: video.timestamp });
          }, 3000); // 3 second delay to allow page to load
        });
      }
    });
  }
});
