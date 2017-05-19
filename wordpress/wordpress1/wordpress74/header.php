<!DOCTYPE html PUBLIC "-//W3C//DTD XHTML 1.0 Transitional//EN" "http://www.w3.org/TR/xhtml1/DTD/xhtml1-transitional.dtd">
<html xmlns="http://www.w3.org/1999/xhtml">
<head profile="http://gmpg.org/xfn/11">
	<?php include_once("description.php"); ?>
	<meta http-equiv="Content-Type" content="<?php bloginfo('html_type'); ?>; charset=<?php bloginfo('charset'); ?>" />	
	<link rel="stylesheet" type="text/css"  href="<?php bloginfo('stylesheet_url'); ?>" media="screen" />
	<meta name="baidu-site-verification" content="fuqotl6Po9" />
	<?php wp_head(); ?>
	<script type="text/javascript" src="<?php bloginfo('template_directory'); ?>/js/ccoooo.js"></script>
	<script type="text/javascript">
//<![CDATA[
if (typeof jQuery == 'undefined') {
  document.write(unescape("%3Cscript src='/wp-includes/js/jquery/jquery.js' type='text/javascript'%3E%3C/script%3E")); 
}
// ]]>
</script>
</head>
	<body>
		<div id="wrapper">
			<div id="header">
				<div class="headerTop">
					<div class="navBar clear">
						<ul class="rightFloat">
						<?php
							$current_user = wp_get_current_user();
							if ( 0 == $current_user->ID ) {
						?>
							<li><a href="/register">注册（邀请码）</a></li>
							<li><a href="/login">登录</a></li>
						<?php
							} else {
						?>
							<li>你好，<?php echo $current_user->display_name;?></li>
							<li><a href="<?php bloginfo('url'); ?>/author/<?php echo $current_user->user_login;?>">个人中心</a></li>
							<?php
							if( $current_user->roles[0] == 'administrator'|| $current_user->roles[0] == 'editor') {
							?>
							<li><a href="<?php bloginfo('url'); ?>/wp-admin">高级管理</a></li>
							<?php
							}
							?>
							<li><a href="<?php echo wp_logout_url( get_permalink() ); ?>" title="Logout">注销</a></li>
						<?php
							}
						?> 
						</ul>
					</div>
				</div>
				<div class="headerMain">
					<div class="logo">
						<h1>
							<a title="运营笔记" href="<?php bloginfo('url'); ?>">
								<img border="0" alt="运营笔记" src="<?php bloginfo('template_directory'); ?>/images/logo.png" />
							</a>
						</h1>
					</div>
					<div class="nav clear">
        				<ul>
		                    <li class="navIndex">
		                    	<a title="Home" hidefocus="true" href="<?php bloginfo('url'); ?>">首页<span>Home</span></a>
		                    </li>
		                    <li>
		                    	<a title="Operate" hidefocus="true" href="<?php bloginfo('url'); ?>/news">运营<span>News</span></a>
		                    </li>
		                    <li>
		                    	<a title="TalkPic" hidefocus="true" href="<?php bloginfo('url'); ?>/talkpic">图说<span>TalkPic</span></a>
		                    </li>
							<li>
		                    	<a title="Opinion" hidefocus="true" href="<?php bloginfo('url'); ?>/website">观站<span>Website</span></a>
		                    </li>
		                    <li>
		                    	<a title="Salotto" hidefocus="true" href="<?php bloginfo('url'); ?>/event">活动<span>event</span></a>
		                    </li>
		                    <li>
		                    	<a title="Service" hidefocus="true" href="<?php bloginfo('url'); ?>/about/service">服务<span>Service</span></a>
		                    </li>
                  		</ul>
      				</div>
				</div>
			</div>