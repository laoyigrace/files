<title><?php 
if ( is_home() ) { bloginfo('name');_e(' - ');$paged = get_query_var('paged'); if ( $paged > 1 ) printf('第%s页 - ',$paged); bloginfo('description');

}elseif ( is_search() ) {
	_e('搜索"');$allsearch = &new WP_Query("s=$s&showposts=-1"); $key = wp_specialchars($s, 1); $count = $allsearch->post_count; _e(''); _e($key.'"'); _e('的结果 - ');$paged = get_query_var('paged'); if ( $paged > 1 ) printf('第%s页 - ',$paged); bloginfo('name'); wp_reset_query();
}elseif ( is_404() ) {
	_e('404 Not Found(页面未找到) - '); bloginfo('name');
}elseif ( is_author() ) {
	_e('"');_e(trim(wp_title('',0)));_e('"的文章归档 - ');bloginfo('name');
}elseif ( is_single() ){
	_e(trim(wp_title('',0)));_e(' - ');$category = get_the_category();echo $category[0]->cat_name;_e(' - ');bloginfo('name');
}elseif(is_page()){
		_e(trim(wp_title('',0)));_e(' - ');$paged = get_query_var('paged'); if ( $paged > 1 ) printf('第%s页 - ',$paged); bloginfo('name');
}elseif ( is_category() ) { 
		_e(trim(wp_title('',0)));_e(' - ');$paged = get_query_var('paged'); if ( $paged > 1 ) printf('第%s页 - ',$paged); bloginfo('name');
}elseif ( is_month() ) {
	the_time('Y年n月');_e('的文章归档');_e(' - ');$paged = get_query_var('paged'); if ( $paged > 1 ) printf('第%s页 - ',$paged); bloginfo('name');
}elseif ( is_day() ) {
	the_time('Y年n月j日');_e('的文章归档');_e(' - ');$paged = get_query_var('paged'); if ( $paged > 1 ) printf('第%s页 - ',$paged); bloginfo('name');
}elseif (function_exists('is_tag')){
	if ( is_tag() ) {
		_e('标签为"');single_tag_title("", true);_e('"的文章');_e(' - ');$paged = get_query_var('paged'); if ( $paged > 1 ) printf('第%s页 - ',$paged); bloginfo('name');
	}
}
?>
</title>
<?php
    $description = "运营笔记是运营管理学习平台，深度解读品牌运营、产品运营、运营管理、产品推广、产品营销，专注于为用户提供最新的运营资讯，带你解读运营背后的世界。";
    $keywords = "运营,运营笔记,产品运营,运营管理,品牌运营,产品推广,产品营销";
 if (is_home()){
    $description = "运营笔记是运营管理学习平台，深度解读品牌运营、产品运营、运营管理、产品推广、产品营销，专注于为用户提供最新的运营资讯，带你解读运营背后的世界。";
    $keywords = "运营,运营笔记,产品运营,运营管理,品牌运营,产品推广,产品营销";
} elseif ( is_category() ) { 
	if(is_category('news')){
	    $description = "运营频道是运营笔记汇集最新原创运营资讯、人物专访、热点追踪、深度分析、深度观察的频道，关注热点运营资讯，呈现每日最新观点。";
    $keywords = "运营,运营笔记,运营资讯,运营热点";
	}elseif(is_category('talkpic')){
	    $description = "图说频道是运营笔记专注信息图表达的频道，用数据可视化，用简明的图表，让您轻松了解运营之道。";
    $keywords = "运营,运营笔记,图说运营";
	}elseif(is_category('website')){
	    $description = "观站频道是运营笔记网站分析的频道，专注为中小网站提供网站分析、网站优化、优化建议等服务。";
    $keywords = "运营,运营笔记,网站分析,网站优化,优化建议";
	}elseif(is_category('salon')){
	    $description = "沙龙频道是运营笔记举办的运营交流沙龙活动，为促进运营者交流，定期举办各种丰富多彩的运营沙龙活动";
    $keywords = "运营,运营笔记,运营交流,沙龙活动,运营沙龙";
	}
} elseif (is_single()){
    if ($post->post_excerpt) {
        $description     = $post->post_excerpt;
    } else {
        $description = wp_trim_words( $post->post_content, 80,'......' ); 
    }
	$keywords="运营笔记";
	if(wp_get_post_tags($post->ID)){
		$tags = wp_get_post_tags($post->ID);
		foreach ($tags as $tag ) {
        $keywords = $tag->name.",".$keywords;
    }
	}else{
    $keywords = "运营,运营笔记,产品运营,运营管理,品牌运营,产品推广,产品营销";      
    }
    
} elseif ( is_page() ) {
	if ( $post->ID == 2) {
		$description = "运营笔记是运营管理学习平台，深度解读品牌运营、产品运营、运营管理、产品推广、产品营销，专注于为用户提供最新的运营资讯，带你解读运营背后的世界。";
		$keywords = "运营,运营笔记,产品运营,运营管理,品牌运营,产品推广,产品营销";
	} elseif ($post->ID == 3) {
	  $description = "运营笔记联系我们频道，咨询信息，解决问题，或者是对我们的服务提出建议,为您提供在线服务,远程服务,邮件,电话等多种支持方式。";
	  $keywords = "运营,运营笔记,产品运营,运营管理,品牌运营,产品推广,产品营销";
	 } elseif ($post->ID == 4) {
	  $description = "运营笔记版权声明频道，凡本网注明“来源：运营笔记”的所有作品,未经运营笔记网授权不得转载、摘编或利用其它方式使用作品。";
	  $keywords = "运营,运营笔记,产品运营,运营管理,品牌运营,产品推广,产品营销";
	 } elseif ($post->ID == 5) {
	  $description = "运营笔记商务服务频道，运营笔记网提供商务合作，网站评测及其他商务活动合作，欢迎有意向公司或个人前来洽谈。";
	  $keywords = "运营,运营笔记,产品运营,运营管理,品牌运营,产品推广,产品营销";
	 } elseif ($post->ID == 6) {
	  $description = "运营笔记留言反馈频道，关于产品运营、策划、营销方面的问题可以在此留言，交流各方面运营管理见解，讨论及研究运营管理。";
	  $keywords = "运营,运营笔记,产品运营,运营管理,品牌运营,产品推广,产品营销";
	 } elseif ($post->ID == 7) {
	  $description = "运营笔记友情链接频道，运营笔记内容原创多，更新频率快，质量高，欢迎各类网站与运营笔记交换友情链接。";
	  $keywords = "运营,运营笔记,产品运营,运营管理,品牌运营,产品推广,产品营销";
	 } 
} elseif(function_exists('is_tag')){
 if( is_tag() ) {
		$description =  "标签为“".trim(wp_title('',0))."”的文章 - 运营笔记";
    	$keywords = "运营,运营笔记,产品运营,运营管理,品牌运营,产品推广,产品营销";
		$keywords = trim(wp_title('',0)).",".$keywords;
	}
}if ( is_search() ) {$allsearch = &new WP_Query("s=$s&showposts=-1"); $key = wp_specialchars($s, 1); $count = $allsearch->post_count;
	$description = "搜索“".$key."”的结果 - 运营笔记"; wp_reset_query();
    	$keywords = "运营,运营笔记,产品运营,运营管理,品牌运营,产品推广,产品营销";
}
?>
	
	<meta name="description" content="<?=$description?>" />
	<meta name="keywords" content="<?=$keywords?>" />