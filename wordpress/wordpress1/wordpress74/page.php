<?php
/*
Template Name: 默认页面模板
*/
?>
<?php get_header(); ?>
<div id="main">
				<div class="mainContent clear">
					<div class="pageNav leftFloat">
						<div class="aboutMenu">
							<h3><span>About</span><a class="pageIndex" href="<?php bloginfo('url'); ?>/about">关于我们</a></h3>
						</div>
						<div class="aboutMenu">
							<h3><span>Contact Us</span><a href="<?php bloginfo('url'); ?>/about/contactus">联系我们</a></h3>
						</div>
						<div class="aboutMenu">
							<h3><span>Copyright</span><a href="<?php bloginfo('url'); ?>/about/copyright">版权声明</a></h3>
						</div>
						<div class="aboutMenu">
							<h3><span>Service</span><a href="<?php bloginfo('url'); ?>/about/service">商务服务</a></h3>
						</div>
						<div class="aboutMenu">
							<h3><span>Guestbook</span><a href="<?php bloginfo('url'); ?>/about/guestbook">留言反馈</a></h3>
						</div>
						<div class="aboutMenu">
							<h3><span>Link</span><a href="<?php bloginfo('url'); ?>/about/link">友情链接</a></h3>
						</div>
					</div>
					<div class="pageContainer rightFloat">
						<h2 class="pageTitel"><?php the_title(); ?></h2>
        				<div class="pageContent">
							<?php the_content(); ?>
        				</div>
						<?php if (comments_open()) comments_template( '', true ); ?>
					</div>			
				</div>
				
			</div>
<?php get_footer(); ?>