select domain_name, count(drupal_pdf_files.drupal_site_id) as pdf_count from drupal_site
    join drupal_pdf_files on drupal_site.id = drupal_pdf_files.drupal_site_id
group by domain_name;