function main(splash, args)
    -- Configure splash
    splash:set_user_agent('Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36')
    splash.private_mode_enabled = false
    splash.images_enabled = true
    splash:set_viewport_size(1920, 1080)
    
    -- Navigate to URL
    local ok, reason = splash:go(args.url)
    if not ok then
        return {
            info = {
                error = reason,
                url = args.url,
                status = 0,
                title = ''
            },
            html = ''
        }
    end
    
    -- Wait for dynamic content
    splash:wait(3)
    
    -- Scroll to load more content
    for _ = 1, 3 do
        splash:evaljs("window.scrollTo(0, document.body.scrollHeight)")
        splash:wait(1)
    end
    
    -- Click load more button if present
    local clicked = splash:evaljs([[
        (function() {
            var loadMoreBtn = document.querySelector('.show-more-related, .load-more-related');
            if (loadMoreBtn && loadMoreBtn.style.display !== 'none') {
                loadMoreBtn.click();
                return true;
            }
            return false;
        })()
    ]])
    
    if clicked then
        splash:wait(2)
    end
    
    -- Get page source
    local html = splash:html()
    
    -- Return a simple response structure that scrapy_splash expects
    return {
        info = {
            error = nil,
            url = splash:url(),
            status = 200,
            title = splash:evaljs("document.title")
        },
        html = html
    }
end

return {
    main = main
}
