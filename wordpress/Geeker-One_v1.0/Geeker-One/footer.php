</section>
<?php wp_reset_query(); if ( is_home()) { ?>
<?php } ?>
<footer id="footer">


  <div class="footer_content"> &copy;2015-<?php echo date('Y'); ?>&nbsp;<a href="<?php bloginfo('url'); ?>">
    <?php bloginfo('name'); ?> 
    </a>
  </div>


</footer>
<?php include 'share.php'; ?>
<?php wp_footer(); ?>
<script>
var _hmt = _hmt || [];
(function() {
  var hm = document.createElement("script");
  hm.src = "//hm.baidu.com/hm.js?ed441c948ef36ed832a2f2ff16c3d76a";
  var s = document.getElementsByTagName("script")[0]; 
  s.parentNode.insertBefore(hm, s);
})();
</script>

</body><?php if( dopt('d_footcode_b') ) echo dopt('d_footcode'); ?>
</html>