<?php if (get_option('ygj_home') == '杂志布局') { ?>
<?php include('cms.php'); ?>
<?php } else if(get_option('ygj_home') == '博客导航') { include(TEMPLATEPATH . '/daohang.php'); ?>
<?php } else { include(TEMPLATEPATH . '/blog.php'); } ?>