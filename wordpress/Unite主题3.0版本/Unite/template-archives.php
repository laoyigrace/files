<?php
/*
Template Name: 文章归档
*/
?>
<?php get_header(); ?>

<?php get_template_part( 'inc/functions/archives' ); ?>
	<div id="content" class="site-content shadow">
		
<div class="clear"></div>

	<div id="primary" class="content-area">
		<main id="main" class="site-main" role="main">

			
				<article id="post-<?php the_ID(); ?>" <?php post_class(); ?>>

					<div class="expand_collapse" style="cursor: pointer;">展开收缩</div>
	<?php while ( have_posts() ) : the_post(); ?>
					<header class="entry-header">
						<h1 class="single-title">文章归档</h1>
						<div class="single_info">
				<?php echo $count_categories = wp_count_terms('category'); ?>个分类&nbsp;&nbsp;
				<?php echo $count_tags = wp_count_terms('post_tag'); ?>个标签&nbsp;&nbsp;
				<?php $count_posts = wp_count_posts(); echo $published_posts = $count_posts->publish;?> 篇文章&nbsp;&nbsp;
				<?php echo $wpdb->get_var("SELECT COUNT(*) FROM $wpdb->comments");?>条留言&nbsp;&nbsp;
				更新时间：<?php $last = $wpdb->get_results("SELECT MAX(post_modified) AS MAX_m FROM $wpdb->posts WHERE (post_type = 'post' OR post_type = 'page') AND (post_status = 'publish' OR post_status = 'private')");$last = date('Y年m月d日', strtotime($last[0]->MAX_m));echo $last; ?>					
						</div>
					</header>

					<div class="archives"><?php archives_list_cx(); ?></div>
				<?php endwhile; ?>
				</article><!-- #page -->

			
		</main><!-- .site-main -->
	</div><!-- .content-area -->

<script type="text/javascript">
$(document).ready(function(){
	$('.expand_collapse, .archives-yearmonth').css({cursor:"pointer"});
	$('.archives ul li ul.archives-monthlisting').hide();
	$('.archives ul li ul.archives-monthlisting:first').show();
	$('.archives ul li span.archives-yearmonth').click(function(){$(this).next().slideToggle('fast');return false;});
	$(".expand_collapse").click(function(){
		$(".archives ul li ul.archives-monthlisting").slideToggle("slow");
		$('.archives ul li ul.archives-monthlisting:first').slideToggle("fast");
		return false;
	});
});
</script>

<?php get_sidebar();?>
<div class="clear"></div>
</div><!-- .site-content -->			
<?php get_footer();?>