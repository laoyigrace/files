<?php get_header();?>
	<div id="content" class="site-content">
	<div class="clear"></div>
	<?php if (get_option('ygj_ddad') == '关闭') { ?>
				<?php { echo ''; } ?>
				<?php } else { echo stripslashes(get_option('ygj_addd_c'));  } ?>
		<div id="primary" class="content-area">
		<main id="main" class="site-main" role="main">
		<?php if (get_option('ygj_hdpkg') == '关闭') { ?>
		<?php { echo ''; } ?>
		<?php } else { include (TEMPLATEPATH . '/inc/slider.php');} ?>
	<?php if (get_option('ygj_new_p') == '关闭') { ?>
	<?php { echo ''; } ?>
	<?php } else { include(TEMPLATEPATH . '/inc/new_post.php'); } ?>
	
<div class="clear"></div>	
	<?php if (get_option('ygj_tuijiancms') == '关闭') { ?>
		<?php { echo ''; } ?>
	<?php } else { include(TEMPLATEPATH . '/inc/tuijian.php');}?>
	
	<?php if (get_option('ygj_adhx') == '关闭') { ?>
	<?php { echo ''; } ?>
	<?php } else { include(TEMPLATEPATH . '/inc/ad/ad_hx.php'); } ?>
<?php if (get_option('ygj_syytsl') == '关闭') { ?>
	<?php { echo ''; } ?>
	<?php } else {	?>	
	<div class="line-big">
		<?php 
		$display_categories = explode(',', get_option('ygj_catldt') ); 
		foreach ($display_categories as $category) { 
			query_posts( array(
				'showposts' => 1,
				'cat' => $category,
				'post_not_in' => $do_not_duplicate
				)
			);
		?>
		<div class="xl3 xm3">
			<div class="cat-box">
				<?php while (have_posts()) : the_post(); ?>
				<h3 class="cat-title"><span class="syfl">|&nbsp;<?php single_cat_title(); ?></span><span class="catmore"><a href="<?php echo get_category_link($category);?>" title="更多<?php single_cat_title(); ?>文章">More></a></span></h3>
				<div class="clear"></div>
				<div class="cat-site">
					<h2 class="entry-title"><a href="<?php the_permalink(); ?>" title="<?php the_title(); ?>"><?php echo cut_str($post->post_title,48); ?></a></h2>			
					<figure class="thumbnail box-hide box-show">
						<?php include('inc/thumbnail.php'); ?>		
					</figure>
					<div class="cat-main">					
						<?php echo mb_strimwidth(strip_tags(apply_filters('the_content', $post->post_content)), 0, 180,"..."); ?>
					</div>
					<?php endwhile; ?>
					<div class="clear"></div>
					<ul class="cat-list">
					<?php
					query_posts( array(
						'showposts' => get_option('ygj_cat_nddt'),
						'cat' => $category,
						'offset' => 1,
						'post_not_in' => $do_not_duplicate
						)
		 			);
					?>
					<?php while (have_posts()) : the_post(); ?>
						<span class="list-date"><?php the_time('m/d') ?></span>					
						<li class="list-title"><a href="<?php the_permalink(); ?>" title="<?php the_title(); ?>"><?php echo cut_str($post->post_title,50); ?></a></li>	
					<?php endwhile; ?>						
					</ul>

				</div>
			</div>
		</div>
		<?php } ?>
		
		<?php 
		$display_categories = explode(',', get_option('ygj_catrdt') ); 
		foreach ($display_categories as $category) { 
			query_posts( array(
				'showposts' => 1,
				'cat' => $category,
				'post_not_in' => $do_not_duplicate
				)
			);
		?>
		<div class="xl3 xm3">
			<div class="cat-box">
				<?php while (have_posts()) : the_post(); ?>
				<h3 class="cat-title"><span class="syfl">|&nbsp;<?php single_cat_title(); ?></span><span class="catmore"><a href="<?php echo get_category_link($category);?>" title="更多<?php single_cat_title(); ?>文章">More></a></span></h3>
				<div class="clear"></div>
				<div class="cat-site">
					<h2 class="entry-title"><a href="<?php the_permalink(); ?>" title="<?php the_title(); ?>"><?php echo cut_str($post->post_title,48); ?></a></h2>			
					<figure class="thumbnail box-hide box-show">
						<?php include('inc/thumbnail.php'); ?>		
					</figure>
					<div class="cat-main">
						<?php echo mb_strimwidth(strip_tags(apply_filters('the_content', $post->post_content)), 0, 180,"..."); ?>
					</div>
					<?php endwhile; ?>
					<div class="clear"></div>
					<ul class="cat-list">
							<?php
					query_posts( array(
						'showposts' => get_option('ygj_cat_nddt'),
						'cat' => $category,
						'offset' => 1,
						'post_not_in' => $do_not_duplicate
						)
		 			);
					?>
					<?php while (have_posts()) : the_post(); ?>
						<span class="list-date"><?php the_time('m/d') ?></span>					
						<li class="list-title"><a href="<?php the_permalink(); ?>" title="<?php the_title(); ?>"><?php echo cut_str($post->post_title,50); ?></a></li>	
						<?php endwhile; ?>
					</ul>
				</div>
			</div>
		</div>
		<?php } ?>
		<div class="clear"></div>	
	</div>
<?php } ?>
<?php if (get_option('ygj_sywtsl') == '关闭') { ?>
	<?php { echo ''; } ?>
	<?php } else {	?>	
	<div class="line-big">
	<?php 
		$display_categories = explode(',', get_option('ygj_catld') ); 
		foreach ($display_categories as $category) { 
			query_posts( array(
				'showposts' => 1,
				'cat' => $category,
				'post_not_in' => $do_not_duplicate
				)
			);
		?>
		<div class="xl3 xm3">
			<div class="cat-box">
			<?php while (have_posts()) : the_post(); ?>
				<h3 class="cat-title"><span class="syfl">|&nbsp;<?php single_cat_title(); ?></span><span class="catmore"><a href="<?php echo get_category_link($category);?>" title="更多<?php single_cat_title(); ?>文章">More></a></span></h3>
				<?php endwhile; ?>
				<div class="clear"></div>
				<div class="cat-site">
					<ul class="cat-list">
					<?php
					query_posts( array(
						'showposts' => get_option('ygj_cat_ndt'),
						'cat' => $category,
						'post_not_in' => $do_not_duplicate
						)
		 			);
					?>
					<?php while (have_posts()) : the_post(); ?>
						<span class="list-date"><?php the_time('m/d') ?></span>					
						<li class="list-title"><a href="<?php the_permalink(); ?>" title="<?php the_title(); ?>"><?php echo cut_str($post->post_title,50); ?></a></li>	
						<?php endwhile; ?>						
					</ul>
				</div>
			</div>
		</div>
		<?php } ?>
		<?php 
		$display_categories = explode(',', get_option('ygj_catrd') ); 
		foreach ($display_categories as $category) { 
			query_posts( array(
				'showposts' => 1,
				'cat' => $category,
				'post_not_in' => $do_not_duplicate
				)
			);
		?>
		<div class="xl3 xm3">
			<div class="cat-box">
			<?php while (have_posts()) : the_post(); ?>
				<h3 class="cat-title"><span class="syfl">|&nbsp;<?php single_cat_title(); ?></span><span class="catmore"><a href="<?php echo get_category_link($category);?>" title="更多<?php single_cat_title(); ?>文章">More></a></span></h3>
				<?php endwhile; ?>
				<div class="clear"></div>
				<div class="cat-site">
					<ul class="cat-list">
					<?php
					query_posts( array(
						'showposts' => get_option('ygj_cat_ndt'),
						'cat' => $category,
						'post_not_in' => $do_not_duplicate
						)
		 			);
					?>
					<?php while (have_posts()) : the_post(); ?>
						<span class="list-date"><?php the_time('m/d') ?></span>					
						<li class="list-title"><a href="<?php the_permalink(); ?>" title="<?php the_title(); ?>"><?php echo cut_str($post->post_title,50); ?></a></li>	
						<?php endwhile; ?>
					</ul>
				</div>
			</div>
		</div>
		<?php } ?>
		<div class="clear"></div>	
	</div>
	<?php } ?>
		<div class="clear"></div>			
		</main><!-- .site-main -->
	</div><!-- .content-area -->

<?php get_sidebar(); ?>
<div class="clear"></div>
	</div><!-- .site-content -->				
<?php get_footer();?>