SELECT
    drupal_pdf_files.pdf_uri,
    drupal_pdf_files.parent_uri,
    drupal_pdf_files.scanned_date,
    drupal_pdf_files.file_hash,
    drupal_pdf_files.pdf_is_archived

FROM
    drupal_pdf_files
        JOIN
    drupal_site ON drupal_pdf_files.drupal_site_id = drupal_site.id
        JOIN
    pdf_report ON drupal_pdf_files.file_hash = pdf_report.pdf_hash

WHERE parent_uri NOT LIKE '%/node/%' AND parent_uri NOT LIKE '%/index.php/%'
  AND parent_returns_404 is FALSE
  AND pdf_returns_404 is FALSE
  AND removed is FALSE
  AND pdf_is_archived is True

