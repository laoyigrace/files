<?php get_header(); ?>
<div id="main">
				<div class="mainTop clear">
					<div class="imageRotation leftFloat"> 
	 					<div class="imageBox">
	 						<a href="http://sc.chinaz.com" target="_blank"><img src="<?php bloginfo('template_directory'); ?>/images/ad/1.jpg" /></a>
	 						<a href="http://sc.chinaz.com" target="_blank"><img src="<?php bloginfo('template_directory'); ?>/images/ad/2.jpg" /></a>
	 						<a href="http://sc.chinaz.com" target="_blank"><img src="<?php bloginfo('template_directory'); ?>/images/ad/3.jpg" /></a>
	 						<a href="http://sc.chinaz.com" target="_blank"><img src="<?php bloginfo('template_directory'); ?>/images/ad/4.jpg" /></a>
	        				<a href="http://sc.chinaz.com" target="_blank"><img src="<?php bloginfo('template_directory'); ?>/images/ad/5.jpg" /></a>
	 					</div>
	    				<div class="titleBox">
	     					<p class="active"><span>第一张图片标题</span></p>
	        				<p>第二张图片标题</p>
	        				<p>第三张图片标</p>
	        				<p>第四张图片标题</p>
	        				<p>第五张图片标题</p>
	    				</div>
	 					<div class="icoBox">
	 						<span class="active" rel="1">1</span>
	 						<span rel="2">2</span>
	 						<span rel="3">3</span>
	 						<span rel="4">4</span>
	        				<span rel="5">5</span>
	 					</div>
					</div>
					<div class="hotNews rightFloat">
						<div class="tops">热点 </div>
						<ul>
						<?php $posts = query_posts($query_string . '&orderby=date&showposts=4&cat=1'); ?>
						<?php while(have_posts()) : the_post(); ?>
							<li class="clear">
								<h3>
									<a target="_blank" title="<?php the_title(); ?>" href="<?php the_permalink(); ?>"><?php the_title(); ?></a>
								</h3>
								<p><?php _e(wp_trim_words( $post->post_content, 25,'......' ));?></p>
								<span>
									<a href="<?php the_permalink(); ?>">[详细]</a>
								</span>
							</li>
						<?php endwhile; ?>
						</ul>
					</div>
				</div>
				<div class="mainContent clear">
					<div class="articleList leftFloat">
						<div class="postList clear">
							<div class="articleListTitle">
   								<h3>沙龙活动</h3>
    							<div class="articleListMore">
     						 		<a href="<?php bloginfo('url'); ?>/salon">往期回顾</a>
    							</div>
							</div>
							<ul>
							<?php $posts = query_posts($query_string . '&orderby=date&showposts=1&cat=1'); ?>
							<?php while(have_posts()) : the_post(); ?>
								<li style="border-bottom:0;">
									<div class="entryImg">
										<a title="<?php the_title(); ?>" target="_blank" href="<?php the_permalink(); ?>">
											<img width="235" height="152" alt="<?php the_title(); ?>" src="<?php echo catch_that_image() ?>">
										</a>
										<span class="entryCopyright">热门</span>
									</div>
									<h3 class="entryTitle">
										<a title="<?php the_title(); ?>" target="_blank" href="<?php the_permalink(); ?>"><?php the_title(); ?></a>
									</h3>
									<p class="entryContent"><?php _e(wp_trim_words( $post->post_content, 80,'......' ));?></p>
									<div class="entryMeta">
										<div class="entryAuthor"><?php the_author_posts_link(); ?></div>
										<em class="entryDate"> / <?php the_time('Y-m-d') ?></em>
									</div>
									<div class="entryEvents">
										<a href="<?php the_permalink(); ?>"> 参与活动 <em style="padding: 0 0 0 6px; font-size: 14px;">〉</em>	</a>
									</div>
								</li>
							<?php endwhile; ?>
							</ul>
						</div>
						<div class="postList clear">
							<div class="articleListTitle">
   								<h3>运营笔记</h3>
    							<div class="articleListMore">
     						 		<a href="<?php bloginfo('url'); ?>/news">查看更多</a>
    							</div>
							</div>
							<ul>
							<?php $posts = query_posts($query_string . '&orderby=date&showposts=5&cat=1'); ?>
							<?php while(have_posts()) : the_post(); ?>
								<li>
									<div class="entryImg">
										<a title="<?php the_title(); ?>" target="_blank" href="<?php the_permalink(); ?>">
											<img width="235" height="152" alt="<?php the_title(); ?>" src="<?php echo catch_that_image() ?>">
										</a>
										<?php
										$custom_fields = get_post_custom_keys($post_id);
										if (!in_array ('post_copyright', $custom_fields)) :
										?>
										<span class="entryCopyright">原创</span>
										<?php else: ?>
										<span class="entryCopyright">精选</span>
										<?php endif; ?>
									</div>
									<h3 class="entryTitle">
										<a title="<?php the_title(); ?>" target="_blank" href="<?php the_permalink(); ?>"><?php the_title(); ?></a>
									</h3>
									<p class="entryContent"><?php 
									if ($post->post_excerpt) {
										_e(wp_trim_words( $post->post_excerpt, 80,'......' ));
									} else {
										_e(wp_trim_words( $post->post_content, 80,'......' )); 
									}
									?></p>
									<div class="entryMeta">
										<?php the_author_posts_link(); ?>
										<em class="entryDate"> / <?php the_time('Y-m-d') ?></em>
									</div>
									<div class="entryCover">
										<em class="entryViews ml2"><?php echo getPostViews(get_the_ID()); ?></em>
										<em class="entryReplys ml2"><?php comments_popup_link('0', '1', '%', '', '0'); ?></em>
									</div>
								</li>
							<?php endwhile; ?>
							</ul>
						</div>
					</div>
					<?php include_once("sidebarIndex.php"); ?>
				</div>
				<div class="mainPic clear">
					<div class="articleListTitle">
   							<h3>图说运营</h3>
   							<div class="articleListMore">
     						 		<a href="<?php bloginfo('url'); ?>/talkpic">查看更多</a>
    							</div>
					</div>
					<div class="picList ">
						<div class="picOne leftFloat">
							<ul>
							<?php $posts = query_posts($query_string . '&orderby=date&showposts=1&cat=2'); ?>
							<?php while(have_posts()) : the_post();?>
								<li>
									<a class="img" title="<?php the_title(); ?>" href="<?php the_permalink(); ?>">
										<img width="460" height="300"  alt="<?php the_title(); ?>" src="<?php echo catch_that_image() ?>">
										<span><?php the_title(); ?></span>
									</a>
								</li>
							<?php endwhile; ?>
							</ul>
						</div>
						<div class="picMoer rightFloat">
							<ul>
							<?php $posts = query_posts($query_string . '&orderby=date&showposts=2&cat=2&offset=1'); ?>
							<?php while(have_posts()) : the_post();?>
								<li>
									<a target="_blank" title="<?php the_title(); ?>" href="<?php the_permalink(); ?>">
										<img width="250" height="150" alt="<?php the_title(); ?>" src="<?php echo catch_that_image() ?>">
										<span><?php the_title(); ?></span>
									</a>
								</li>
							<?php endwhile; ?>
							<?php $posts = query_posts($query_string . '&orderby=date&showposts=2&cat=1&offset=3'); ?>
							<?php while(have_posts()) : the_post();?>
								<li>
									<a target="_blank" title="<?php the_title(); ?>" href="<?php the_permalink(); ?>">
										<img width="250" height="150" alt="<?php the_title(); ?>" src="<?php echo catch_that_image() ?>">
										<span><?php the_title(); ?></span>
									</a>
								</li>
							<?php endwhile; ?>
							</ul>
						</div>
					</div>
				</div>
				<div class="linkShow clear">
					<div class="articleListTitle">
   							<h3>友情链接</h3>
   							<span style="padding: 0 0 0 10px; color: #999999; line-height: 30px;">[ 申请友情链接，请联系站长QQ：1217561765 ]</span>
					</div>
					<div class="friendLink clear">
						<ul>
							<li><a target="_blank" title="站长素材" href="http://sc.chinaz.com/">微营销手册</a></li>
							<li><a {target}="" href="#">百度</a></li>
							<li><a {target}="" href="#">新浪</a></li>
							<li><a {target}="" href="#">腾讯</a></li>
							<li><a {target}="" href="#">友情链接</a></li>
							<li><a {target}="" href="#">友情链接</a></li>
							<li><a {target}="" href="#">友情链接</a></li>
							<li><a {target}="" href="#">友情链接</a></li>
							<li><a {target}="" href="#">友情链接</a></li>
							<li><a {target}="" href="#">友情链接</a></li>
							<li><a {target}="" href="#">友情链接</a></li>
							<li><a {target}="" href="#">友情链接</a></li>
							<li><a {target}="" href="#">友情链接</a></li>
							<li><a {target}="" href="#">友情链接</a></li>
							<li><a {target}="" href="#">友情链接</a></li>
						</ul>
					</div>
				</div>
			</div>
<?php get_footer(); ?>