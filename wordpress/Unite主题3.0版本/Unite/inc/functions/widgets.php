<?php 
// 最新文章
class newt_post extends WP_Widget {
     function newt_post() {
         $widget_ops = array('description' => '主题自带的最新文章小工具');
         $this->WP_Widget('newt_post', '主题&nbsp;&nbsp;最新文章', $widget_ops);
     }
     function widget($args, $instance) {
		extract($args);
		$title = apply_filters( 'widget_title', $instance['title'] );
		echo $before_widget;
		if ( ! empty( $title ) )
		echo $before_title . $title . $after_title;
		$number = strip_tags($instance['number']) ? absint( $instance['number'] ) : 5;
?>
			
<div class="new_cat" id="new_cat">
	<ul>
		
		<?php query_posts( array ( 'showposts' => $number, 'orderby' => date, 'caller_get_posts' => 1 ) );$i = 1; while ( have_posts() ) : the_post(); ?>
		<?php $post_title = mb_strimwidth(get_the_title(), 0, 26, '...');?>
		<span class="list-date"><?php the_time('m/d') ?></span><li>
		<span class='li-icon li-icon-<?php echo "$i";?>'><?php echo "$i.";?></span>
				<a href="<?php the_permalink(); ?>"  title="<?php the_title(); ?>"><?php echo "$post_title";?></a>
				
		</li>

		<?php $i++;endwhile;?>
	</ul>
</div>	
<div class="clear"></div>
<?php
	echo $after_widget;
	}
	function update( $new_instance, $old_instance ) {
		if (!isset($new_instance['submit'])) {
			return false;
		}
			$instance = $old_instance;
			$instance = array();
			$instance['title'] = strip_tags( $new_instance['title'] );
			$instance['number'] = strip_tags($new_instance['number']);
			return $instance;
		}
	function form($instance) {
		if ( isset( $instance[ 'title' ] ) ) {
			$title = $instance[ 'title' ];
		}
		else {
			$title = '最新文章';
		}
		global $wpdb;
		$instance = wp_parse_args((array) $instance, array('number' => '5'));
		$number = strip_tags($instance['number']);
?>
	<p><label for="<?php echo $this->get_field_id( 'title' ); ?>">标题：</label>
	<input class="widefat" id="<?php echo $this->get_field_id( 'title' ); ?>" name="<?php echo $this->get_field_name( 'title' ); ?>" type="text" value="<?php echo $title; ?>" /></p>
	<p><label for="<?php echo $this->get_field_id('number'); ?>">显示数量：</label>
	<input id="<?php echo $this->get_field_id( 'number' ); ?>" name="<?php echo $this->get_field_name( 'number' ); ?>" type="text" value="<?php echo $number; ?>" size="3" /></p>
	<input type="hidden" id="<?php echo $this->get_field_id('submit'); ?>" name="<?php echo $this->get_field_name('submit'); ?>" value="1" />
<?php }
}
add_action( 'widgets_init', create_function( '', 'register_widget( "newt_post" );' ) );


// 本站推荐
class hot_commend extends WP_Widget {
     function hot_commend() {
         $widget_ops = array('description' => '主题自带的本站推荐小工具');
         $this->WP_Widget('hot_commend', '主题&nbsp;&nbsp;本站推荐', $widget_ops);
     }
     function widget($args, $instance) {
		extract($args);
		$title = apply_filters( 'widget_title', $instance['title'] );
		echo $before_widget;
		if ( ! empty( $title ) )
		echo $before_title . $title . $after_title;
		$number = strip_tags($instance['number']) ? absint( $instance['number'] ) : 5;
?>
			<div id="hot" class="hot_commend">
				<ul>
				<?php query_posts( array ( 'meta_key' => 'hot', 'showposts' => $number, 'orderby' => rand, 'caller_get_posts' => 1 ) ); while ( have_posts() ) : the_post(); ?>
					<li>
						<figure class="thumbnail box-hide box-show">
							<?php get_template_part( 'inc/thumbnail' ); ?>		
						</figure>
						<div class="hot-title">
							<a href="<?php the_permalink(); ?>" rel="bookmark" title="<?php the_title(); ?>"><?php the_title(); ?></a>
						</div>
						<?php if( function_exists( 'the_views' ) ) { print '<div class="views">阅读 '; the_views(); print '</div>';  } ?>
						<div class="comment"><?php comments_popup_link( '评论 0', '评论 1', '评论 %' ); ?></div>
					</li>
					<?php endwhile;?>
						<div class="clear"></div>
					</ul>
				</div>
			<div class="clear"></div>
<?php
	echo $after_widget;
	}
	function update( $new_instance, $old_instance ) {
		if (!isset($new_instance['submit'])) {
			return false;
		}
			$instance = $old_instance;
			$instance = array();
			$instance['title'] = strip_tags( $new_instance['title'] );
			$instance['number'] = strip_tags($new_instance['number']);
			return $instance;
		}
	function form($instance) {
		if ( isset( $instance[ 'title' ] ) ) {
			$title = $instance[ 'title' ];
		}
		else {
			$title = '本站推荐';
		}
		global $wpdb;
		$instance = wp_parse_args((array) $instance, array('number' => '5'));
		$number = strip_tags($instance['number']);
?>
	<p><label for="<?php echo $this->get_field_id( 'title' ); ?>">标题：</label>
	<input class="widefat" id="<?php echo $this->get_field_id( 'title' ); ?>" name="<?php echo $this->get_field_name( 'title' ); ?>" type="text" value="<?php echo $title; ?>" /></p>
	<p><label for="<?php echo $this->get_field_id('number'); ?>">显示数量：</label>
	<input id="<?php echo $this->get_field_id( 'number' ); ?>" name="<?php echo $this->get_field_name( 'number' ); ?>" type="text" value="<?php echo $number; ?>" size="3" /></p>
	<input type="hidden" id="<?php echo $this->get_field_id('submit'); ?>" name="<?php echo $this->get_field_name('submit'); ?>" value="1" />
<?php }
}
add_action( 'widgets_init', create_function( '', 'register_widget( "hot_commend" );' ) );

// 热门文章
class hot_post extends WP_Widget {
     function hot_post() {
         $widget_ops = array('description' => '主题自带的热门文章小工具，使用前必须安装 wp-postviews 插件,并且有统计数据');
         $this->WP_Widget('hot_post', '主题&nbsp;&nbsp;热门文章', $widget_ops);
     }
     function widget($args, $instance) {
		extract($args);
		$title = apply_filters( 'widget_title', $instance['title'] );
		echo $before_widget;
		if ( ! empty( $title ) )
		echo $before_title . $title . $after_title;
		$number = strip_tags($instance['number']) ? absint( $instance['number'] ) : 5;
		$days = strip_tags($instance['days']) ? absint( $instance['days'] ) : 90;
?>

<div id="hot_post_widget">
	<ul>
	    <?php if (function_exists('get_most_viewed')): ?> 
	    <?php get_timespan_most_viewed('post',$number,$days, true, true); ?>
	    <?php endif; ?>
		<?php wp_reset_query(); ?>
	</ul>
</div>

<?php
	echo $after_widget;
	}
	function update( $new_instance, $old_instance ) {
		if (!isset($new_instance['submit'])) {
			return false;
		}
			$instance = $old_instance;
			$instance = array();
			$instance['title'] = strip_tags( $new_instance['title'] );
			$instance['number'] = strip_tags($new_instance['number']);
			$instance['days'] = strip_tags($new_instance['days']);
			return $instance;
		}
	function form($instance) {
		if ( isset( $instance[ 'title' ] ) ) {
			$title = $instance[ 'title' ];
		}
		else {
			$title = '热门文章';
		}
		global $wpdb;
		$instance = wp_parse_args((array) $instance, array('number' => '5'));
		$instance = wp_parse_args((array) $instance, array('days' => '90'));
		$number = strip_tags($instance['number']);
		$days = strip_tags($instance['days']);
 ?>
	<p><label for="<?php echo $this->get_field_id( 'title' ); ?>">标题：</label>
	<input class="widefat" id="<?php echo $this->get_field_id( 'title' ); ?>" name="<?php echo $this->get_field_name( 'title' ); ?>" type="text" value="<?php echo $title; ?>" /></p>
	<p><label for="<?php echo $this->get_field_id('number'); ?>">显示数量：</label>
	<input id="<?php echo $this->get_field_id( 'number' ); ?>" name="<?php echo $this->get_field_name( 'number' ); ?>" type="text" value="<?php echo $number; ?>" size="3" /></p>
	<p><label for="<?php echo $this->get_field_id('days'); ?>">时间限定（天）：</label>
	<input id="<?php echo $this->get_field_id( 'days' ); ?>" name="<?php echo $this->get_field_name( 'days' ); ?>" type="text" value="<?php echo $days; ?>" size="3" /></p>
	<input type="hidden" id="<?php echo $this->get_field_id('submit'); ?>" name="<?php echo $this->get_field_name('submit'); ?>" value="1" />
<?php }
}
add_action( 'widgets_init', create_function( '', 'register_widget( "hot_post" );' ) );

// 热评文章
class hot_comment extends WP_Widget {
     function hot_comment() {
         $widget_ops = array('description' => '主题自带的热评文章小工具');
         $this->WP_Widget('hot_comment', '主题&nbsp;&nbsp;热评文章', $widget_ops);
     }
     function widget($args, $instance) {
		extract($args);
		$title = apply_filters( 'widget_title', $instance['title'] );
		echo $before_widget;
		if ( ! empty( $title ) )
		echo $before_title . $title . $after_title;
		$number = strip_tags($instance['number']) ? absint( $instance['number'] ) : 5;
		$days = strip_tags($instance['days']) ? absint( $instance['days'] ) : 90;
?>

<?php
function hot_comment_viewed($number, $days){
    global $wpdb;
    $sql = "SELECT ID , post_title , comment_count
           FROM $wpdb->posts
           WHERE post_type = 'post' AND post_status = 'publish' AND TO_DAYS(now()) - TO_DAYS(post_date) < $days
           ORDER BY comment_count DESC LIMIT 0 , $number ";
    $posts = $wpdb->get_results($sql);
	$i = 1;
    $output = "";
    foreach ($posts as $post){
		$post_title = mb_strimwidth($post->post_title, 0, 28, '...');
        $output .= "\n<span class=\"list-date\">".$post->comment_count."</span><li><span class='li-icon li-icon-$i'>$i.</span><a href= \"".get_permalink($post->ID)."\" rel=\"bookmark\" title=\"".$post->post_title." (".$post->comment_count."条评论)\" >$post_title</a></li>";
		$i++;
    }
    echo $output;
}
?>
<div id="hot_comment_widget">
	<ul>
		<?php hot_comment_viewed($number, $days); ?>
		<?php wp_reset_query(); ?>
	</ul>
</div>

<?php
	echo $after_widget;
	}
	function update( $new_instance, $old_instance ) {
		if (!isset($new_instance['submit'])) {
			return false;
		}
			$instance = $old_instance;
			$instance = array();
			$instance['title'] = strip_tags( $new_instance['title'] );
			$instance['number'] = strip_tags($new_instance['number']);
			$instance['days'] = strip_tags($new_instance['days']);
			return $instance;
		}
	function form($instance) {
		if ( isset( $instance[ 'title' ] ) ) {
			$title = $instance[ 'title' ];
		}
		else {
			$title = '热评文章';
		}
		global $wpdb;
		$instance = wp_parse_args((array) $instance, array('number' => '5'));
		$instance = wp_parse_args((array) $instance, array('days' => '90'));
		$number = strip_tags($instance['number']);
		$days = strip_tags($instance['days']);
 ?>
	<p><label for="<?php echo $this->get_field_id( 'title' ); ?>">标题：</label>
	<input class="widefat" id="<?php echo $this->get_field_id( 'title' ); ?>" name="<?php echo $this->get_field_name( 'title' ); ?>" type="text" value="<?php echo $title; ?>" /></p>
	<p><label for="<?php echo $this->get_field_id('number'); ?>">显示数量：</label>
	<input id="<?php echo $this->get_field_id( 'number' ); ?>" name="<?php echo $this->get_field_name( 'number' ); ?>" type="text" value="<?php echo $number; ?>" size="3" /></p>
	<p><label for="<?php echo $this->get_field_id('days'); ?>">时间限定（天）：</label>
	<input id="<?php echo $this->get_field_id( 'days' ); ?>" name="<?php echo $this->get_field_name( 'days' ); ?>" type="text" value="<?php echo $days; ?>" size="3" /></p>
	<input type="hidden" id="<?php echo $this->get_field_id('submit'); ?>" name="<?php echo $this->get_field_name('submit'); ?>" value="1" />
<?php }
}
add_action( 'widgets_init', create_function( '', 'register_widget( "hot_comment" );' ) );

// 近期评论
class recent_comments extends WP_Widget {
     function recent_comments() {
         $widget_ops = array('description' => '主题自带的近期评论小工具');
         $this->WP_Widget('recent_comments', '主题&nbsp;&nbsp;近期评论', $widget_ops);
     }
     function widget($args, $instance) {
		extract($args);
		$title = apply_filters( 'widget_title', $instance['title'] );
		echo $before_widget;
		if ( ! empty( $title ) )
		echo $before_title . $title . $after_title;
		$number = strip_tags($instance['number']) ? absint( $instance['number'] ) : 5;
?>

<div id="message" class="message-widget">
	<ul>	
		<?php
		$show_comments = $number;
		$my_email = get_bloginfo ('admin_email');
		$i = 1;
		$comments = get_comments('number=200&status=approve&type=comment');
		foreach ($comments as $my_comment) {
			if ($my_comment->comment_author_email != $my_email) {
				?>
				<li>					
					<span class="comment_author"><strong><?php echo $my_comment->comment_author; ?>：</strong></span><br/>
					<a href="<?php echo get_permalink($my_comment->comment_post_ID); ?>#comment-<?php echo $my_comment->comment_ID; ?>" title="<?php echo $my_comment->comment_author; ?>在《<?php echo get_the_title($my_comment->comment_post_ID); ?>》发表的评论" >
						<?php echo convert_smilies($my_comment->comment_content); ?>
					</a>
				</li>
				<?php
				if ($i == $show_comments) break;
				$i++;
			}
		}
		?>
	</ul>
</div>

<?php
	echo $after_widget;
	}
	function update( $new_instance, $old_instance ) {
		if (!isset($new_instance['submit'])) {
			return false;
		}
			$instance = $old_instance;
			$instance = array();
			$instance['title'] = strip_tags( $new_instance['title'] );
			$instance['number'] = strip_tags($new_instance['number']);
			return $instance;
		}
	function form($instance) {
		if ( isset( $instance[ 'title' ] ) ) {
			$title = $instance[ 'title' ];
		}
		else {
			$title = '近期评论';
		}
		global $wpdb;
		$instance = wp_parse_args((array) $instance, array('number' => '5'));
		$number = strip_tags($instance['number']);
?>
	<p><label for="<?php echo $this->get_field_id( 'title' ); ?>">标题：</label>
	<input class="widefat" id="<?php echo $this->get_field_id( 'title' ); ?>" name="<?php echo $this->get_field_name( 'title' ); ?>" type="text" value="<?php echo $title; ?>" /></p>
	<p><label for="<?php echo $this->get_field_id('number'); ?>">显示数量：</label>
	<input id="<?php echo $this->get_field_id( 'number' ); ?>" name="<?php echo $this->get_field_name( 'number' ); ?>" type="text" value="<?php echo $number; ?>" size="3" /></p>
	<input type="hidden" id="<?php echo $this->get_field_id('submit'); ?>" name="<?php echo $this->get_field_name('submit'); ?>" value="1" />
<?php }
}
add_action( 'widgets_init', create_function( '', 'register_widget( "recent_comments" );' ) );

// 随机文章
class random_post extends WP_Widget {
     function random_post() {
         $widget_ops = array('description' => '主题自带的随机文章小工具，主要用于正文下方的小工具');
         $this->WP_Widget('random_post', '主题&nbsp;&nbsp;随机文章', $widget_ops);
     }
     function widget($args, $instance) {
		extract($args);
		$title = apply_filters( 'widget_title', $instance['title'] );
		echo $before_widget;
		if ( ! empty( $title ) )
		echo $before_title . $title . $after_title;
		$number = strip_tags($instance['number']) ? absint( $instance['number'] ) : 5;
?>

<div id="random_post_widget">
	<ul>
		<?php query_posts( array ( 'orderby' => 'rand', 'showposts' => $number, 'caller_get_posts' => 10 ) ); while ( have_posts() ) : the_post(); ?>
			<li><a href="<?php the_permalink() ?>" rel="bookmark" title="<?php the_title(); ?>"><?php the_title(); ?></a></li>
		<?php endwhile; ?>
		<?php wp_reset_query(); ?>
	</ul>
</div>

<?php
	echo $after_widget;
	}
	function update( $new_instance, $old_instance ) {
		if (!isset($new_instance['submit'])) {
			return false;
		}
			$instance = $old_instance;
			$instance = array();
			$instance['title'] = strip_tags( $new_instance['title'] );
			$instance['number'] = strip_tags($new_instance['number']);
			return $instance;
		}
	function form($instance) {
		if ( isset( $instance[ 'title' ] ) ) {
			$title = $instance[ 'title' ];
		}
		else {
			$title = '随机文章';
		}
		global $wpdb;
		$instance = wp_parse_args((array) $instance, array('number' => '5'));
		$number = strip_tags($instance['number']);
?>
	<p><label for="<?php echo $this->get_field_id( 'title' ); ?>">标题：</label>
	<input class="widefat" id="<?php echo $this->get_field_id( 'title' ); ?>" name="<?php echo $this->get_field_name( 'title' ); ?>" type="text" value="<?php echo $title; ?>" /></p>
	<p><label for="<?php echo $this->get_field_id('number'); ?>">显示数量：</label>
	<input id="<?php echo $this->get_field_id( 'number' ); ?>" name="<?php echo $this->get_field_name( 'number' ); ?>" type="text" value="<?php echo $number; ?>" size="3" /></p>
	<input type="hidden" id="<?php echo $this->get_field_id('submit'); ?>" name="<?php echo $this->get_field_name('submit'); ?>" value="1" />
<?php }
}
add_action( 'widgets_init', create_function( '', 'register_widget( "random_post" );' ) );

// 相关文章
class related_post extends WP_Widget {
     function related_post() {
         $widget_ops = array('description' => '主题自带的相关文章小工具，主要用于正文下方的小工具');
         $this->WP_Widget('related_post', '主题&nbsp;&nbsp;相关文章', $widget_ops);
     }
     function widget($args, $instance) {
		extract($args);
		$title = apply_filters( 'widget_title', $instance['title'] );
		echo $before_widget;
		if ( ! empty( $title ) )
		echo $before_title . $title . $after_title;
		$number = strip_tags($instance['number']) ? absint( $instance['number'] ) : 5;
?>

<div id="related_post_widget">
	<ul>
		<?php
			$post_num = $number;
			global $post;
			$tmp_post = $post;
			$tags = ''; $i = 0;
			if ( get_the_tags( $post->ID ) ) {
			foreach ( get_the_tags( $post->ID ) as $tag ) $tags .= $tag->name . ',';
			$tags = strtr(rtrim($tags, ','), ' ', '-');
			$myposts = get_posts('numberposts='.$post_num.'&tag='.$tags.'&exclude='.$post->ID);
			foreach($myposts as $post) {
			setup_postdata($post);
		?>
		<li><a href="<?php the_permalink(); ?>"><?php the_title(); ?></a></li>
		<?php
			$i += 1;
			}
			}
			if ( $i < $post_num ) {
			$post = $tmp_post; setup_postdata($post);
			$cats = ''; $post_num -= $i;
			foreach ( get_the_category( $post->ID ) as $cat ) $cats .= $cat->cat_ID . ',';
			$cats = strtr(rtrim($cats, ','), ' ', '-');
			$myposts = get_posts('numberposts='.$post_num.'&category='.$cats.'&exclude='.$post->ID);
			foreach($myposts as $post) {
			setup_postdata($post);
		?>
		<li><a href="<?php the_permalink(); ?>"  title="<?php the_title(); ?>"><?php the_title(); ?></a></li>
		<?php
		}
		}
		$post = $tmp_post; setup_postdata($post);
		?>
	</ul>
</div>

<?php
	echo $after_widget;
	}
	function update( $new_instance, $old_instance ) {
		if (!isset($new_instance['submit'])) {
			return false;
		}
			$instance = $old_instance;
			$instance = array();
			$instance['title'] = strip_tags( $new_instance['title'] );
			$instance['number'] = strip_tags($new_instance['number']);
			return $instance;
		}
	function form($instance) {
		if ( isset( $instance[ 'title' ] ) ) {
			$title = $instance[ 'title' ];
		}
		else {
			$title = '相关文章';
		}
		global $wpdb;
		$instance = wp_parse_args((array) $instance, array('number' => '5'));
		$number = strip_tags($instance['number']);
?>
	<p><label for="<?php echo $this->get_field_id( 'title' ); ?>">标题：</label>
	<input class="widefat" id="<?php echo $this->get_field_id( 'title' ); ?>" name="<?php echo $this->get_field_name( 'title' ); ?>" type="text" value="<?php echo $title; ?>" /></p>
	<p><label for="<?php echo $this->get_field_id('number'); ?>">显示数量：</label>
	<input id="<?php echo $this->get_field_id( 'number' ); ?>" name="<?php echo $this->get_field_name( 'number' ); ?>" type="text" value="<?php echo $number; ?>" size="3" /></p>
	<input type="hidden" id="<?php echo $this->get_field_id('submit'); ?>" name="<?php echo $this->get_field_name('submit'); ?>" value="1" />
<?php }
}
add_action( 'widgets_init', create_function( '', 'register_widget( "related_post" );' ) );
