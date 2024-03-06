SELECT
    failure.site_id,
    failure.error_date,
    failure.error_message,
    failure.pdf_uri,
    failure.parent_uri
FROM failure WHERE failure.site_id = '{site_id}'




