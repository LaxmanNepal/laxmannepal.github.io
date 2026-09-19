# PostgreSQL Data Model v1

## Editorial
- authors(id, name, slug, bio, avatar_url, created_at, updated_at)
- articles(id, author_id, type, status, title, slug, excerpt, cover_media_id, published_at, updated_at, created_at)
- article_sections(id, article_id, position, section_type, heading, body, media_id, data_json)
- categories(id, parent_id, name, slug, description)
- tags(id, name, slug)
- article_categories(article_id, category_id)
- article_tags(article_id, tag_id)
- media(id, type, url, width, height, alt_text, caption, credit, created_at)
- redirects(id, source_path, destination_path, status_code, created_at)

## Products
- brands(id, name, slug, logo_media_id, website_url)
- product_categories(id, parent_id, name, slug)
- products(id, brand_id, category_id, name, slug, model, description, release_date, status)
- product_variants(id, product_id, name, sku, region, storage, color, created_at)
- spec_groups(id, name, position)
- specifications(id, group_id, key, label, value_type, position)
- product_spec_values(id, product_id, variant_id, specification_id, value_text, value_number, value_json)
- retailers(id, name, slug, website_url)
- prices(id, product_variant_id, retailer_id, currency, amount, url, checked_at)
- price_history(id, price_id, amount, currency, recorded_at)
- reviews(id, product_id, author_id, rating, title, body, published_at, status)
- article_products(article_id, product_id)

## Tools
- tool_categories(id, name, slug)
- tools(id, category_id, name, slug, description, url, icon_media_id, status)

## YouTube
- youtube_channels(id, platform_id, handle, name, slug, url, avatar_url, subscribers)
- youtube_videos(id, channel_id, platform_id, title, slug, url, published_at, duration_seconds, thumbnail_url)
- youtube_snapshots(id, channel_id, captured_at, subscribers, views, video_count)
- youtube_video_snapshots(id, video_id, captured_at, views, likes, comments)

## Community
- users(id, name, email, password_hash, role, created_at, updated_at)
- comments(id, user_id, article_id, parent_id, body, status, created_at)
- newsletter_subscribers(id, email, status, subscribed_at)

## Required indexes
Unique public slugs; article status/published_at; product brand/category; price history by variant/date; YouTube snapshots by channel/date; full-text indexes for article/product titles; indexes for foreign keys.

## Data rules
Keep normalized specifications rather than HTML blobs. Keep historical prices and YouTube snapshots append-only. Store source URLs for imported external data.