SELECT
    COUNT(*) AS total_pdf_instances,
    COUNT(DISTINCT drupal_pdf_files.file_hash) AS total_unique_pdfs,
    SUM(
            CASE
                WHEN pdf_report.tagged = 0 THEN 1
                WHEN pdf_report.pdf_text_type = 'Image Only' THEN 1
                WHEN ROUND(pdf_report.failed_checks * 1.0 / NULLIF(pdf_report.page_count, 0)) > 20 THEN 1
                WHEN pdf_report.has_form = 1 AND ROUND(pdf_report.failed_checks * 1.0 / NULLIF(pdf_report.page_count, 0)) > 3 THEN 1
                ELSE 0
                END
    ) AS total_high_priority
FROM drupal_pdf_files
         JOIN drupal_site ON drupal_pdf_files.drupal_site_id = drupal_site.id
         JOIN pdf_report ON drupal_pdf_files.file_hash = pdf_report.pdf_hash
WHERE drupal_pdf_files.parent_uri NOT LIKE '%/node/%'
  AND drupal_pdf_files.parent_uri NOT LIKE '%/index.php/%'
  AND drupal_pdf_files.pdf_returns_404 = 0
  AND drupal_pdf_files.parent_returns_404 = 0;
