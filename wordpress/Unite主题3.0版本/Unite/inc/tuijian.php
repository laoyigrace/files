<div class="recommend-items"> 
	<?php
	if (get_option('ygj_tj_lx') == '推荐') { 
	query_posts(array('meta_key' => 'tuijian','orderby' => 'rand', 'showposts' => 4, 'caller_get_posts' => 4));
	}else{
	query_posts(array('orderby' => 'rand', 'showposts' => 4, 'caller_get_posts' => 4));	
	}
	if (have_posts()) :
	while (have_posts()) : the_post();?>
	<div class="item"> 
		<a href="<?php the_permalink(); ?>" target="_blank" title="<?php the_title(); ?>">
			<?php if (has_post_thumbnail()) { the_post_thumbnail('thumbnail', array('alt' => get_the_title()));
			} else { ?>
				<img class="home-thumb" src="<?php echo catch_image() ?>" alt="<?php the_title(); ?>" />
			<?php } ?>	
			<span class="txt"><?php echo cut_str($post->post_title,30); ?></span>
		</a> 
	</div>
	<?php endwhile;endif; ?>
	<?php wp_reset_query();?>
 </div>
