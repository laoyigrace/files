<?php get_header();?>
<div id="content" class="site-content">	
<div class="clear"></div>
	<div id="primary" class="content-area">
		<main id="main" class="site-main" role="main">
<?php while ( have_posts() ) : the_post(); ?>
			
<article id="post-<?php the_ID(); ?>" <?php post_class(); ?>>

	<header class="entry-header">
		<h1 class="entry-title"><?php the_title(); ?></h1>
		<div class="single_info">
					<span class="date"><?php the_time( 'Y-m-d H:i' ) ?><span class="xiaoshi"><?php if ( get_post_meta($post->ID, 'wzzz', true) ) : ?>
			<?php $wzzz = get_post_meta($post->ID, 'wzzz', true); ?>
			&nbsp;&nbsp;来源：
			<?php if(get_post_meta($post->ID, 'wzurl', true)){$wzurl = get_post_meta($post->ID, 'wzurl', true); ?>
			<a href="<?php echo $wzurl; ?>" rel="nofollow" target="_blank"><?php echo $wzzz; ?></a>
			<?php }else{?>
			<?php echo $wzzz; }?>
			<?php endif; ?></span></span>
					<span class="views"><?php if( function_exists( 'the_views' ) ) { print '  阅读 '; the_views(); print ' 次  ';  } ;?></span>
			<span class="comment"><?php comments_popup_link( ' 评论 0 条', ' 评论 1 条', ' 评论 % 条' ); ?></span>	<span class="edit"><?php edit_post_link('编辑', '  ', '  '); ?></span>
				</div>		
	</header><!-- .entry-header -->

<?php if (get_option('ygj_g_single') == '关闭') { ?>
	<?php { echo ''; } ?>
	<?php } 
	else { include(TEMPLATEPATH . '/inc/ad/ad_single.php'); } ?>
	
	<div class="entry-content">
					<div class="single-content">			
	<?php the_content(); ?>
	<?php wp_link_pages(array('before' => '<div class="page-links">', 'after' => '', 'next_or_number' => 'next', 'previouspagelink' => '<span>上一页</span>', 'nextpagelink' => "")); ?><?php wp_link_pages(array('before' => '', 'after' => '', 'next_or_number' => 'number', 'link_before' =>'<span>', 'link_after'=>'</span>')); ?>
					<?php wp_link_pages(array('before' => '', 'after' => '</div>', 'next_or_number' => 'next', 'previouspagelink' => '', 'nextpagelink' => "<span>下一页</span>")); ?>			
			</div>
	<div class="clear"></div>
	<?php get_template_part( 'inc/social' ); ?>
	<div class="xiaoshi">
		<div class="single_banquan">	
			<strong>版权声明：</strong>本文著作权归原作者所有，欢迎分享本文，谢谢支持！<br/>
			<strong>转载请注明：</strong><a href="<?php the_permalink() ?>" rel="bookmark" title="本文固定链接 <?php the_permalink() ?>"><?php the_title(); ?> </a> | <a href="<?php bloginfo('home'); ?>"><?php bloginfo('name');?></a>
		</div>
	</div>
		
	<?php include('inc/file.php'); ?>
	<div class="clear"></div>
		<div class="single_info_w">
			<span class="s_cat"><strong>分类：</strong><?php the_category( ', ' ) ?></span>
			<span class="xiaoshi"><span class="s_tag"><strong>标签：</strong><?php the_tags('', ', ', ''); ?></span></span>
		</div>
	</div><!-- .entry-content -->
	</article><!-- #post -->
														
		<?php if (get_option('ygj_adt') == '关闭') { ?>
		<?php { echo ''; } ?>
	<?php } else { include(TEMPLATEPATH . '/inc/ad/ad_single_d.php'); } ?>

	<nav class="nav-single">
		<?php previous_post_link('<strong>上一篇：</strong> %link','%title',true,'') ?>
		<?php next_post_link('<br/><strong>下一篇：</strong> %link','%title',true,'') ?>		
		<div class="clear"></div>				
	</nav>
	<?php if (get_option('ygj_tuijian') == '关闭') { ?>
		<?php { echo ''; } ?>
	<?php } else { include(TEMPLATEPATH . '/inc/tuijian.php');}?>

	<?php if (get_option('ygj_zwdb') == '关闭') { ?>
		<?php { echo ''; } ?>
	<?php } else { ?>
		<div id="single-widget">
		<?php dynamic_sidebar( 'sidebar-3' ); ?>
		<div class="clear"></div>
	</div>
	<?php } ?>
	<?php comments_template( '', true ); ?>			
			<?php endwhile; ?>
		</main><!-- .site-main -->
	</div><!-- .content-area -->
<?php get_sidebar();?>
<div class="clear"></div>
</div><!-- .site-content -->
<?php get_footer();?>