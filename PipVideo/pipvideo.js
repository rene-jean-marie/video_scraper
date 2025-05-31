// Tests
// https://support.google.com/youtube/answer/171780?hl=en
// https://loco.gg/stream/90792a8a-8c53-47cb-a589-172116f238d1

const onMessage = (request, sender) => {
  if (request.method === 'playing') {
    chrome.action.setIcon({
      tabId: sender.tab.id,
      path: {
        '16': '/data/icons/16.png',
        '32': '/data/icons/32.png',
        '48': '/data/icons/48.png'
      }
    });
  }
};
chrome.runtime.onMessage.addListener(onMessage);

const sorting = (a, b) => {
  if (a.paused === false && b.paused) {
    return -1;
  }
  else if (b.paused === false && a.paused) {
    return 1;
  }
  else if (a.connected === false && b.connected) {
    return -1;
  }
  else if (b.connected === false && a.connected) {
    return 1;
  }
  else {
    return a.frameId - b.frameId;
  }
};

// This function is now registered via commands.onCommand instead of action.onClicked
// because action.onClicked won't fire when we have a popup
async function triggerPictureInPicture(tab) {
  try {
    const r = await chrome.scripting.executeScript({
      target: {
        tabId: tab.id,
        allFrames: true
      },
      func: () => {
        const es = new Set();
        // collect all videos
        if (typeof videos === 'object') {
          [...videos].forEach(v => es.add(v));
        }
        [...document.querySelectorAll('video')].forEach(v => es.add(v));
        // sort
        return Array.from(es).map(e => ({
          paused: e.paused,
          connected: e.isConnected
        }));
      }
    });
    const video = (r || []).map(o => o.result.map(v => {
      v.frameId = o.frameId;
      return v;
    })).flat().sort(sorting).shift();

    if (video) {
      // update icon
      onMessage({
        method: 'playing'
      }, {
        tab
      });
      // prevent the page from exiting PiP view for 2 seconds
      const prefs = await new Promise(resolve => chrome.storage.local.get({
        'block-pip': true
      }, resolve));
      if (prefs['block-pip']) {
        await chrome.scripting.executeScript({
          target: {
            tabId: tab.id,
            frameIds: [video.frameId]
          },
          func: () => {
            self.pipobj = self.pipobj || {
              pointer: Document.prototype.exitPictureInPicture
            };
            clearTimeout(self.pipobj.id);
            self.pipobj.id = setTimeout(() => {
              Document.prototype.exitPictureInPicture = self.pipobj.pointer;
            }, 2000);
            Document.prototype.exitPictureInPicture = new Proxy(Document.prototype.exitPictureInPicture, {
              apply() {
                return console.info('PiP View', 'Request to exit PiP is ignored');
              }
            });
          },
          world: 'MAIN'
        });
      }
      // detach
      await chrome.scripting.executeScript({
        target: {
          tabId: tab.id,
          frameIds: [video.frameId]
        },
        func: () => {
          /* global videos */
          const es = new Set();
          // collect all videos
          if (typeof videos === 'object') {
            [...videos].forEach(v => es.add(v));
          }
          [...document.querySelectorAll('video')].forEach(v => es.add(v));
          //
          const sorting = (a, b) => {
            if (a.paused === false && b.paused) {
              return -1;
            }
            else if (b.paused === false && a.paused) {
              return 1;
            }
            else if (a.connected === false && b.connected) {
              return -1;
            }
            else if (b.connected === false && a.connected) {
              return 1;
            }
          };
          const video = [...es].sort(sorting).shift();
          if (video) {
            video.requestPictureInPicture().catch(e => alert(e.message));
          }
        }
      });
    }
    else {
      throw Error('No player is detected');
    }
  }
  catch (e) {
    console.warn(e);
    chrome.action.setBadgeText({
      tabId: tab.id,
      text: 'E'
    });
    chrome.action.setTitle({
      tabId: tab.id,
      title: e.message
    });
  }
}

// Create a context menu item for PiP mode
chrome.runtime.onInstalled.addListener(() => {
  chrome.contextMenus.create({
    id: 'pip-video',
    title: 'Toggle Picture in Picture',
    contexts: ['action']
  });
});

// Handle context menu click
chrome.contextMenus.onClicked.addListener((info, tab) => {
  if (info.menuItemId === 'pip-video') {
    triggerPictureInPicture(tab);
  }
});

// Add keyboard command to toggle PiP
chrome.commands.onCommand.addListener((command) => {
  if (command === 'toggle-pip') {
    chrome.tabs.query({active: true, currentWindow: true}, tabs => {
      if (tabs.length > 0) {
        triggerPictureInPicture(tabs[0]);
      }
    });
  }
});

/* badge */
{
  const once = () => {
    if (once.ran) {
      return;
    }
    once.ran = true;
    chrome.action.setBadgeBackgroundColor({
      color: '#f10e08'
    });
  };
  chrome.runtime.onStartup.addListener(once);
  chrome.runtime.onInstalled.addListener(once);
}

/* FAQs & Feedback */
{
  const {management, runtime: {onInstalled, setUninstallURL, getManifest}, storage, tabs} = chrome;
  if (navigator.webdriver !== true) {
    const page = getManifest().homepage_url;
    const {name, version} = getManifest();
    onInstalled.addListener(({reason, previousVersion}) => {
      management.getSelf(({installType}) => installType === 'normal' && storage.local.get({
        'faqs': true,
        'last-update': 0
      }, prefs => {
        if (reason === 'install' || (prefs.faqs && reason === 'update')) {
          const doUpdate = (Date.now() - prefs['last-update']) / 1000 / 60 / 60 / 24 > 45;
          if (doUpdate && previousVersion !== version) {
            tabs.query({active: true, lastFocusedWindow: true}, tbs => tabs.create({
              url: page + '?version=' + version + (previousVersion ? '&p=' + previousVersion : '') + '&type=' + reason,
              active: reason === 'install',
              ...(tbs && tbs.length && {index: tbs[0].index + 1})
            }));
            storage.local.set({'last-update': Date.now()});
          }
        }
      }));
    });
    setUninstallURL(page + '?rd=feedback&name=' + encodeURIComponent(name) + '&version=' + version);
  }
}
