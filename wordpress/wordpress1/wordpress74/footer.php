<div id="footer" >
				<div class="footerMain clear">
					<div class="footerInfo leftFloat">
						<a class="footerLogo leftFloat" href="http://www.ccoooo.com"></a>
						<div class="footerTitle leftFloat">
							<p>运营笔记，国内最有价值的运营管理学习平台! </p>
       						<p>Here,we offering the best operating way ever.</p>
						</div>
					</div>
					<div class="footerList rightFloat">
						<div class="footerNav">
							<a target="_blank" href="<?php bloginfo('url'); ?>/about">关于我们</a>
							<a target="_blank" href="<?php bloginfo('url'); ?>/about/contactus">联系我们</a>
							<a target="_blank" href="<?php bloginfo('url'); ?>/about/copyright">版权声明</a>
							
							<a target="_blank" href="<?php bloginfo('url'); ?>/about/service">商务服务</a>
							<a id="qaurl" href="<?php bloginfo('url'); ?>/about/guestbook">留言反馈</a>
							<a target="_blank" href="<?php bloginfo('url'); ?>/about/link">友情链接</a>
							<a style="display:none;"><script type="text/javascript">var cnzz_protocol = (("https:" == document.location.protocol) ? " https://" : " http://");document.write(unescape("%3Cspan id='cnzz_stat_icon_1255525366'%3E%3C/span%3E%3Cscript src='" + cnzz_protocol + "s95.cnzz.com/stat.php%3Fid%3D1255525366' type='text/javascript'%3E%3C/script%3E"));</script></a>
						</div>
						<p style="color: #CECECE; text-align: right;" class="copyright">Copyright&nbsp;&copy;&nbsp;2015&nbsp;运营笔记.&nbsp;Powered&nbsp;by&nbsp;<a href="http://www.theme.cc">WordPress</a>&nbsp;Theme&nbsp;By&nbsp;<a target="_blank" href="http://www.ccoooo.com/">COOFocus</a>.</p>
              			<div class="shares">
         					<a href="#" style="margin-top:4px; width:84px;" target="_blank"><img width="83" height="30" src="<?php bloginfo('template_directory'); ?>/images/hy_83x30.png" style="border: medium none;" alt="安全联盟认证"></a>
         					<a target="_blank" href="#" title="ucloud" class="shares-ucloud"></a>
         					<a target="_blank" href="#" title="新浪微博" class="shares-sina"></a>
      						<a target="_blank" href="#" title="腾讯微博" class="shares-ten"></a>
					         <a target="_blank" href="javascript:;" id="wx" class="shares-weixin"><div id="ft-wx-show"><div class="wx-show-txt"></div><i></i></div></a>
					         <a target="_blank" href="#" class="shares-dib"></a>
					    </div>
					</div>
				</div>
				<?php if(is_single()):?>
<link rel="stylesheet" href="<?php bloginfo('template_url'); ?>/highslide/highslide.css" type="text/css" />
<script type="text/javascript" src="<?php bloginfo('template_url'); ?>/highslide/highslide.js"></script>
<script type="text/javascript">
jQuery(document).ready(function($) {
    hs.graphicsDir = "<?php bloginfo('template_url'); ?>/highslide/graphics/";
    hs.outlineType = "rounded-white";
    hs.dimmingOpacity = 0.8;
    hs.outlineWhileAnimating = true;
    hs.showCredits = false;
    hs.captionEval = "this.thumb.alt";
    hs.numberPosition = "caption";
    hs.align = "center";
    hs.transitions = ["expand", "crossfade"];
    hs.addSlideshow({
        interval: 5000,
        repeat: true,
        useControls: true,
        fixedControls: "fit",
        overlayOptions: {
            opacity: 0.75,
            position: "bottom center",
            hideOnMouseOut: true
 
        }
 
    });
});
</script>
<?php endif;?>
			</div>
		</div>
	</body>
</html>