// Content script to interact with videos on the page

// Listen for messages from popup or background
chrome.runtime.onMessage.addListener(function(request, sender, sendResponse) {
  if (request.action === "getVideoInfo") {
    // Get all video elements on the page
    const videos = document.querySelectorAll('video');
    const videoList = Array.from(videos);
    
    // Find the first playing video or first video
    const playingVideo = videoList.find(v => !v.paused) || videoList[0];
    
    if (playingVideo) {
      sendResponse({
        success: true,
        currentTime: playingVideo.currentTime,
        duration: playingVideo.duration,
        paused: playingVideo.paused
      });
    } else {
      sendResponse({
        success: false,
        message: "No video found on the page"
      });
    }
    return true; // Keep the messaging channel open for async response
  }
  
  if (request.action === "triggerPip") {
    // Set video to the requested timestamp
    if (request.timestamp) {
      setTimeout(() => {
        const videos = document.querySelectorAll('video');
        const videoList = Array.from(videos);
        const video = videoList[0];
        
        if (video) {
          video.currentTime = request.timestamp;
          video.play();
          
          // Attempt to trigger PiP mode
          setTimeout(() => {
            if (document.pictureInPictureEnabled) {
              video.requestPictureInPicture()
                .catch(e => console.error("PiP failed:", e));
            }
          }, 500);
        }
      }, 2000); // Wait for video to be available
    }
    
    return true;
  }
});
