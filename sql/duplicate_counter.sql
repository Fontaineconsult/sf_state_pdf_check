SELECT d.id,
       d.pdf_uri,
       d.parent_uri,
       d.file_hash,
       d.scanned_date
FROM drupal_pdf_files d
         JOIN drupal_site s ON d.drupal_site_id = s.id
         JOIN pdf_report p ON d.file_hash = p.pdf_hash
         JOIN (
    SELECT pdf_uri, parent_uri, file_hash
    FROM drupal_pdf_files
    GROUP BY pdf_uri, parent_uri, file_hash
    HAVING COUNT(*) > 1
) dup ON d.pdf_uri = dup.pdf_uri
    AND d.parent_uri = dup.parent_uri
    AND d.file_hash = dup.file_hash
WHERE s.domain_name = '{site_name}';
