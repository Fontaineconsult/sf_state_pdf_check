select parent_uri from drupal_pdf_files
where parent_returns_404 = false
group by parent_uri;
