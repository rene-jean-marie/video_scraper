"""
Default CSS selectors for different video websites.
These selectors are used by the spider to extract information from HTML pages.
"""

# Default selectors for different video sites
DEFAULT_SELECTORS = {
    # Category page selectors
    'category_grid': '#categories, .categories, .category-list',
    'category_item': '.category-item, .cat-item, .thumb',
    'category_title': '.title::text, .name::text',
    'category_url': 'a::attr(href)',
    
    # Video grid selectors (for category pages and search results)
    'video_grid': '.mozaique, .videos-grid, .video-list, .grid',
    'video_item': '.thumb-block, .thumb-under, .video-item, .grid-item',
    'video_url': '.thumb-under a::attr(href), a::attr(href)',
    'video_title': '.title::text',
    'video_thumbnail': 'img::attr(src)',
    'video_duration': '.duration::text',
    'video_views': '.views::text',
    'next_page': '.next-page::attr(href), .pagination a.next-page::attr(href)',
    
    # Individual video page selectors
    'video_player': '#video-player-bg, #player, .video-wrapper',
    'video_info': '.video-info, .info-wrapper',
    'related_videos': '#related-videos .mozaique, .related-videos',
    'related_video_item': '.thumb-block',
    'related_video_url': '.thumb-under .title a::attr(href)',
    'related_video_title': '.thumb-under .title a::text'
}

# Website-specific selectors
WEBSITE_SELECTORS = {
    'xvideos': {
        'video_grid': '.mozaique',
        'video_item': '.thumb-block',
        'video_url': '.thumb-under a::attr(href)',
        'video_title': '.title a::text',
        'video_thumbnail': 'img::attr(src)',
        'video_duration': '.duration::text',
        'video_views': '.views::text',
        'next_page': '.pagination a.next-page::attr(href)',
        
        'video_player': '#video-player-bg',
        'video_info': '.video-metadata',
        'related_videos': '#related-videos .mozaique',
        'related_video_item': '.thumb-block',
        'related_video_url': '.thumb-under .title a::attr(href)',
        'related_video_title': '.thumb-under .title a::text'
    },
    
    'pornhub': {
        'video_grid': '.videos-list',
        'video_item': '.videoBox',
        'video_url': '.videoPreviewBg a::attr(href)',
        'video_title': '.title a::text',
        'video_thumbnail': 'img::attr(data-thumb_url)',
        'video_duration': '.duration::text',
        'video_views': '.views var::text',
        'next_page': '.page_next a::attr(href)',
        
        'video_player': '#player',
        'video_info': '.video-info-row',
        'related_videos': '.relatedVideos',
        'related_video_item': '.videoBox',
        'related_video_url': '.videoPreviewBg a::attr(href)',
        'related_video_title': '.title a::text'
    },
    
    # Add more website-specific selectors here
}


def get_selectors_for_website(url):
    """
    Get the appropriate selectors for a specific website based on the URL.
    
    Args:
        url (str): The URL of the website.
        
    Returns:
        dict: The selectors for the website.
    """
    # Default selectors
    selectors = DEFAULT_SELECTORS.copy()
    
    # Check for known websites
    for website, website_selectors in WEBSITE_SELECTORS.items():
        if website in url:
            # Update default selectors with website-specific ones
            selectors.update(website_selectors)
            break
    
    return selectors
