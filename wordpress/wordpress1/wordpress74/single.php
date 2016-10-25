<?php get_header(); ?>
<div id="main">
				<div class="mainContent clear">
					<div class="artContainer leftFloat" id="post-<?php the_ID(); ?>">
					<?php while(have_posts()) : the_post(); ?>
					<?php setPostViews(get_the_ID()); ?>
						<div class="artTop">
							<div class="artCommentNumber">
								<span class="commentNumber"> 
          							<a><?php comments_popup_link('0', '1', '%', '', '0'); ?></a> 
          						</span>
								<span class="corner"></span>
							</div>
							<h1 class="artTitle"><?php the_title(); ?></h1>
							<p class="artMeta">
								<?php the_author_posts_link(); ?>
								<a class="artTime"><?php the_time('Y-m-d G:i') ?></a>
								共 <em class="artViews"><?php echo getPostViews(get_the_ID()); ?> </em>人围观
        					</p>
						</div>
						<div class="summary">
        					<div>
        						<strong>简介 :</strong><?php 
									if ($post->post_excerpt) {
										_e(wp_trim_words( $post->post_excerpt, 80,'......' ));
									} else {
										_e(wp_trim_words( $post->post_content, 80,'......' )); 
									}
									?>
        					</div>
        				</div>
        				<div class="artContent">
							<?php the_content(); ?>
        				</div>
        				<div class="frontback clear">
  	   						<div class="artPre">
  	   							<em class=""><?php if (get_previous_post()) { previous_post_link('上一篇: %link','%title',true);} else { echo "没有了，已经是最后文章";} ?></em>
  	   						</div>
    						<div class="artNext">
    							<em class=""><?php if (get_next_post()) { next_post_link('下一篇: %link','%title',true);} else { echo "没有了，已经是最新文章";} ?> </em>
    						</div>
						</div>
						<div class="artCopyright">
							<h2 style="margin-top:18px;">版权声明</h2>
							<p>
							<?php
							$custom_fields = get_post_custom_keys($post_id);
							if (!in_array ('post_copyright', $custom_fields)) :
							?>
								<span>本文仅代表作者观点，不代表运营笔记立场。</span><br>
								<span>本文系作者授权运营笔记发表，未经许可，不得转载。</span>
							<?php else: ?>
							<?php
							$custom = get_post_custom($post_id);
							$custom_value = $custom['post_copyright'];
							?>
								<span>本文仅代表作者观点，不代表运营笔记立场。</span><br>
								<span>本文系参考<a target="_blank" rel="nofollow" href="<?php echo $custom_value[0] ?>" >互联网(原文链接)</a>编辑，由运营笔记整理编辑。</span>
							<?php endif; ?>
							</p>
						</div>
						<?php comments_template( '', true ); ?>
					<?php endwhile; ?>
					</div>
					<?php include_once("sidebarIndex.php"); ?>
				</div>
				
			</div>
<?php get_footer(); ?>